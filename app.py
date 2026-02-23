import asyncio
import datetime
import logging
import os
import time
import traceback

import edge_tts
import gradio as gr
import librosa
import torch
from fairseq import checkpoint_utils
from fairseq.data.dictionary import Dictionary  # <-- untuk allowlist

from config import Config
from lib.infer_pack.models import (
    SynthesizerTrnMs256NSFsid,
    SynthesizerTrnMs256NSFsid_nono,
    SynthesizerTrnMs768NSFsid,
    SynthesizerTrnMs768NSFsid_nono,
)
from rmvpe import RMVPE
from vc_infer_pipeline import VC

logging.getLogger("fairseq").setLevel(logging.WARNING)
logging.getLogger("numba").setLevel(logging.WARNING)
logging.getLogger("markdown_it").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

limitation = os.getenv("SYSTEM") == "spaces"
config = Config()

edge_output_filename = "edge_output.mp3"
tts_voice_list = None
tts_voices = None

async def _load_tts_voices_async():
    global tts_voice_list, tts_voices
    if tts_voices is None:
        tts_voice_list = await edge_tts.list_voices()
        tts_voices = [v['ShortName'] for v in tts_voice_list]
    return tts_voices


def _load_tts_voices():
    """Load TTS voices, handling async context properly."""
    return _call_async_from_sync(_load_tts_voices_async())

model_root = "weights"
models = [d for d in os.listdir(model_root) if os.path.isdir(os.path.join(model_root, d))]
if len(models) == 0:
    raise ValueError("No model found in `weights` folder")
models.sort()


def model_data(model_name):
    pth_files = [
        os.path.join(model_root, model_name, f)
        for f in os.listdir(os.path.join(model_root, model_name))
        if f.endswith(".pth")
    ]
    if len(pth_files) == 0:
        raise ValueError(f"No pth file found in {model_root}/{model_name}")
    pth_path = pth_files[0]
    print(f"Loading {pth_path}")
    cpt = torch.load(pth_path, map_location="cpu")
    tgt_sr = cpt["config"][-1]
    cpt["config"][-3] = cpt["weight"]["emb_g.weight"].shape[0]  # n_spk
    if_f0 = cpt.get("f0", 1)
    version = cpt.get("version", "v1")
    if version == "v1":
        if if_f0 == 1:
            net_g = SynthesizerTrnMs256NSFsid(*cpt["config"], is_half=config.is_half)
        else:
            net_g = SynthesizerTrnMs256NSFsid_nono(*cpt["config"])
    elif version == "v2":
        if if_f0 == 1:
            net_g = SynthesizerTrnMs768NSFsid(*cpt["config"], is_half=config.is_half)
        else:
            net_g = SynthesizerTrnMs768NSFsid_nono(*cpt["config"])
    else:
        raise ValueError("Unknown version")
    del net_g.enc_q
    net_g.load_state_dict(cpt["weight"], strict=False)
    print("Model loaded")
    net_g.eval().to(config.device)
    if config.is_half:
        net_g = net_g.half()
    else:
        net_g = net_g.float()
    vc = VC(tgt_sr, config)

    index_files = [
        os.path.join(model_root, model_name, f)
        for f in os.listdir(os.path.join(model_root, model_name))
        if f.endswith(".index")
    ]
    if len(index_files) == 0:
        print("No index file found")
        index_file = ""
    else:
        index_file = index_files[0]
        print(f"Index file found: {index_file}")

    return tgt_sr, net_g, vc, version, index_file, if_f0


def load_hubert():
    global hubert_model
    # Patch untuk fairseq lama: allowlist Dictionary agar torch.load bisa unpickle
    with torch.serialization.safe_globals([Dictionary]):
        models, _, _ = checkpoint_utils.load_model_ensemble_and_task(
            ["hubert_base.pt"],
            suffix="",
            strict=False
        )
    hubert_model = models[0]
    hubert_model = hubert_model.to(config.device)
    if config.is_half:
        hubert_model = hubert_model.half()
    else:
        hubert_model = hubert_model.float()
    return hubert_model.eval()


def _call_async_from_sync(coro):
    """Call async coroutine from sync context, handling existing event loops."""
    try:
        # Try to get running loop (will raise if no loop in current thread)
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        return asyncio.run(coro)
    else:
        # We're already in an event loop (e.g., from FastAPI)
        # We can't use asyncio.run(), so we need a workaround
        import concurrent.futures
        import threading
        
        # Run in a new thread with its own event loop
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()


print("Loading hubert model...")
hubert_model = load_hubert()
print("Hubert model loaded.")

print("Loading rmvpe model...")
rmvpe_model = RMVPE("rmvpe.pt", config.is_half, config.device)
print("rmvpe model loaded.")

print("Loading TTS voices...")
tts_voices = _load_tts_voices()
print(f"Loaded {len(tts_voices)} TTS voices")


async def _run_edge_tts(tts_text, tts_voice, speed_str, edge_output_filename):
    """Helper to run edge-tts async. Can be called from sync or async context."""
    await edge_tts.Communicate(
        tts_text, tts_voice, rate=speed_str
    ).save(edge_output_filename)



def tts(
    model_name,
    speed,
    tts_text,
    tts_voice,
    f0_up_key,
    f0_method,
    index_rate,
    protect,
    filter_radius=3,
    resample_sr=0,
    rms_mix_rate=0.25,
):
    print("------------------")
    print(datetime.datetime.now())
    print("tts_text:")
    print(tts_text)
    print(f"tts_voice: {tts_voice}")
    print(f"Model name: {model_name}")
    print(f"F0: {f0_method}, Key: {f0_up_key}, Index: {index_rate}, Protect: {protect}")
    try:
        if limitation and len(tts_text) > 280:
            print("Error: Text too long")
            return (
                f"Text characters should be at most 280 in this huggingface space, but got {len(tts_text)} characters.",
                None,
                None,
            )
        tgt_sr, net_g, vc, version, index_file, if_f0 = model_data(model_name)
        t0 = time.time()
        speed_str = f"+{speed}%" if speed >= 0 else f"{speed}%"
        _call_async_from_sync(
            _run_edge_tts(tts_text, tts_voice, speed_str, edge_output_filename)
        )
        t1 = time.time()
        edge_time = t1 - t0
        audio, sr = librosa.load(edge_output_filename, sr=16000, mono=True)
        duration = len(audio) / sr
        print(f"Audio duration: {duration}s")
        if limitation and duration >= 20:
            print("Error: Audio too long")
            return (
                f"Audio should be less than 20 seconds in this huggingface space, but got {duration}s.",
                edge_output_filename,
                None,
            )

        f0_up_key = int(f0_up_key)
        if not hubert_model:
            load_hubert()
        if f0_method == "rmvpe":
            vc.model_rmvpe = rmvpe_model
        times = [0, 0, 0]
        audio_opt = vc.pipeline(
            hubert_model,
            net_g,
            0,
            audio,
            edge_output_filename,
            times,
            f0_up_key,
            f0_method,
            index_file,
            index_rate,
            if_f0,
            filter_radius,
            tgt_sr,
            resample_sr,
            rms_mix_rate,
            version,
            protect,
            None,
        )
        if tgt_sr != resample_sr >= 16000:
            tgt_sr = resample_sr
        info = f"Success. Time: edge-tts: {edge_time}s, npy: {times[0]}s, f0: {times[1]}s, infer: {times[2]}s"
        print(info)
        return info, edge_output_filename, (tgt_sr, audio_opt)
    except EOFError:
        info = (
            "It seems that the edge-tts output is not valid. "
            "This may occur when the input text and the speaker do not match. "
            "For example, maybe you entered Japanese (without alphabets) text but chose non-Japanese speaker?"
        )
        print(info)
        return info, None, None
    except:
        info = traceback.format_exc()
        print(info)
        return info, None, None


initial_md = """
# RVC text-to-speech webui

This is a text-to-speech webui of RVC models.

Input text ➡[(edge-tts)](https://github.com/rany2/edge-tts)➡ Speech mp3 file ➡[(RVC)](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)➡ Final output
"""

app = gr.Blocks()
with app:
    gr.Markdown(initial_md)
    with gr.Row():
        with gr.Column():
            model_name = gr.Dropdown(label="Model", choices=models, value=models[0])
            f0_key_up = gr.Number(
                label="Transpose (the best value depends on the models and speakers)",
                value=0,
            )
        with gr.Column():
            f0_method = gr.Radio(
                label="Pitch extraction method (pm: very fast, low quality, rmvpe: a little slow, high quality)",
                choices=["pm", "rmvpe"],
                value="rmvpe",
                interactive=True,
            )
            index_rate = gr.Slider(minimum=0, maximum=1, label="Index rate", value=1, interactive=True)
            protect0 = gr.Slider(minimum=0, maximum=0.5, label="Protect", value=0.33, step=0.01, interactive=True)
    with gr.Row():
        with gr.Column():
            tts_voice = gr.Dropdown(
                label="Edge-tts speaker (format: language-Country-Name)",
                choices=tts_voices,
                allow_custom_value=False,
                value="ja-JP-NanamiNeural",
            )
            speed = gr.Slider(minimum=-100, maximum=100, label="Speech speed (%)", value=0, step=10, interactive=True)
            tts_text = gr.Textbox(label="Input Text", value="これは日本語テキストから音声への変換デモです。")
        with gr.Column():
            but0 = gr.Button("Convert", variant="primary")
            info_text = gr.Textbox(label="Output info")
        with gr.Column():
            edge_tts_output = gr.Audio(label="Edge Voice", type="filepath")
            tts_output = gr.Audio(label="Result")
        but0.click(tts, [model_name, speed, tts_text, tts_voice, f0_key_up, f0_method, index_rate, protect0],
                   [info_text, edge_tts_output, tts_output])
    with gr.Row():
        examples = gr.Examples(
            examples_per_page=100,
            examples=[
                ["これは日本語テキストから音声への変換デモです。", "ja-JP-NanamiNeural"],
                ["This is an English text to speech conversation demo.", "en-US-AriaNeural"],
                ["这是一个中文文本到语音的转换演示。", "zh-CN-XiaoxiaoNeural"],
                ["한국어 텍스트에서 음성으로 변환하는 데모입니다.", "ko-KR-SunHiNeural"],
                ["Il s'agit d'une démo de conversion du texte français à la parole.", "fr-FR-DeniseNeural"],
                ["Dies ist eine Demo zur Umwandlung von Deutsch in Sprache.", "de-DE-AmalaNeural"],
                ["Tämä on suomenkielinen tekstistä puheeksi -esittely.", "fi-FI-NooraNeural"],
                ["Это демонстрационный пример преобразования русского текста в речь.", "ru-RU-SvetlanaNeural"],
                ["Αυτή είναι μια επίδειξη μετατροπής ελληνικού κειμένου σε ομιλία.", "el-GR-AthinaNeural"],
                ["Esta es una demostración de conversión de texto a voz en español.", "es-ES-ElviraNeural"],
                ["Questa è una dimostrazione di sintesi vocale in italiano.", "it-IT-ElsaNeural"],
                ["Esta é uma demonstração de conversão de texto em fala em português.", "pt-PT-RaquelNeural"],
                ["Це демонстрація тексту до мовлення українською мовою.", "uk-UA-PolinaNeural"],
                ["هذا عرض توضيحي عربي لتحويل النص إلى كلام.", "ar-EG-SalmaNeural"],
                ["இது தமிழ் உரையிலிருந்து பேச்சு மாற்ற டெமோ.", "ta-IN-PallaviNeural"],
            ],
            inputs=[tts_text, tts_voice],
        )

if __name__ == "__main__":
    app.launch(inbrowser=True)
