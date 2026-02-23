from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import uuid
import time
import pathlib
import io
import asyncio
import edge_tts

from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import soundfile as sf

# import tts function from app (app.launch is guarded by __main__)
from app import tts, models

app = FastAPI(title="RVC TTS API")

OUT_DIR = pathlib.Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

app.mount("/outputs", StaticFiles(directory=str(OUT_DIR)), name="outputs")

# Cache for voices list (to avoid repeated async calls)
_voices_cache = None

async def get_available_voices():
    """Get list of available edge-tts voices with caching."""
    global _voices_cache
    if _voices_cache is None:
        try:
            voice_list = await edge_tts.list_voices()
            _voices_cache = [
                {
                    "name": v.get("ShortName", ""),
                    "gender": v.get("Gender", ""),
                    "language": v.get("Locale", "").split("-")[0],
                    "locale": v.get("Locale", ""),
                    "display_name": v.get("DisplayName", ""),
                    "friendly_name": f"{v.get('ShortName', '')}-{v.get('Gender', '')}"
                }
                for v in voice_list
            ]
        except Exception as e:
            _voices_cache = []
    return _voices_cache


class SynthesizeRequest(BaseModel):
    model: str = Field(..., description="Model name from weights folder")
    speed: int = Field(0, ge=-100, le=100, description="Speech speed percent")
    text: str = Field(..., description="Input text to synthesize")
    voice: str = Field(..., description="Edge-tts voice string, e.g. ja-JP-NanamiNeural-Female")
    transpose: int = Field(0, description="F0 transpose / key up")
    f0_method: str = Field("rmvpe", description="Pitch extraction method: 'pm' or 'rmvpe'")
    index_rate: float = Field(1.0, ge=0.0, le=1.0, description="Index rate")
    protect: float = Field(0.33, ge=0.0, le=0.5, description="Protect slider value")
    filter_radius: Optional[int] = Field(3, description="Filter radius")
    resample_sr: Optional[int] = Field(0, description="Resample sample rate, 0 to keep")
    rms_mix_rate: Optional[float] = Field(0.25, description="RMS mix rate")


@app.post("/synthesize")
async def synthesize(req: SynthesizeRequest):
    """
    Synthesize voice and return audio file directly (audio/wav).
    Can be played directly in browser or downloaded.
    """
    if req.model not in models:
        return JSONResponse(status_code=400, content={"error": "Unknown model name"})

    info, edge_path, audio_tuple = tts(
        req.model,
        req.speed,
        req.text,
        req.voice,
        req.transpose,
        req.f0_method,
        req.index_rate,
        req.protect,
        filter_radius=req.filter_radius or 3,
        resample_sr=req.resample_sr or 0,
        rms_mix_rate=req.rms_mix_rate or 0.25,
    )

    if not audio_tuple or not isinstance(audio_tuple, tuple):
        return JSONResponse(status_code=500, content={"error": info})

    try:
        tgt_sr, audio_np = audio_tuple
        
        # Write to memory buffer (in-memory, not to disk)
        buffer = io.BytesIO()
        sf.write(buffer, audio_np, int(tgt_sr), format='WAV')
        buffer.seek(0)
        
        # Return audio file directly
        filename = f"synthesized_{int(time.time())}.wav"
        return StreamingResponse(
            buffer,
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to generate audio: {str(e)}"})


@app.post("/synthesize/info")
async def synthesize_with_info(req: SynthesizeRequest):
    """
    Synthesize voice and return JSON response with audio URL and info.
    Useful for getting synthesis metadata and audio download link.
    """
    if req.model not in models:
        return JSONResponse(status_code=400, content={"error": "Unknown model name"})

    info, edge_path, audio_tuple = tts(
        req.model,
        req.speed,
        req.text,
        req.voice,
        req.transpose,
        req.f0_method,
        req.index_rate,
        req.protect,
        filter_radius=req.filter_radius or 3,
        resample_sr=req.resample_sr or 0,
        rms_mix_rate=req.rms_mix_rate or 0.25,
    )

    out_url = None
    out_file = None
    if audio_tuple and isinstance(audio_tuple, tuple):
        try:
            tgt_sr, audio_np = audio_tuple
            filename = f"output_{int(time.time())}_{uuid.uuid4().hex}.wav"
            out_file = OUT_DIR / filename
            sf.write(str(out_file), audio_np, int(tgt_sr))
            out_url = f"/outputs/{filename}"
        except Exception as e:
            out_url = None

    return {
        "info": info,
        "edge_tts_path": edge_path,
        "output_audio_url": out_url,
    }


@app.get("/voices")
async def list_voices():
    """
    Get list of available edge-tts voices.
    Returns JSON array with voice details.
    """
    voices = await get_available_voices()
    return {
        "total": len(voices),
        "voices": voices
    }


@app.get("/synthesize")
async def synthesize_get(
    text: str = Query(..., description="Text to synthesize"),
    voice: str = Query("en-US-AriaNeural-Female", description="Voice name"),
    model: str = Query("models", description="Model name"),
    speed: int = Query(0, ge=-100, le=100, description="Speech speed percent"),
    transpose: int = Query(0, description="F0 transpose"),
    f0_method: str = Query("rmvpe", description="Pitch extraction method: 'pm' or 'rmvpe'"),
    index_rate: float = Query(1.0, ge=0.0, le=1.0, description="Index rate"),
    protect: float = Query(0.33, ge=0.0, le=0.5, description="Protect slider value"),
):
    """
    Synthesize voice and return audio file via GET request.
    Quick endpoint for simple synthesis (use POST /synthesize for advanced options).
    """
    if model not in models:
        return JSONResponse(status_code=400, content={"error": f"Unknown model: {model}"})

    info, edge_path, audio_tuple = tts(
        model,
        speed,
        text,
        voice,
        transpose,
        f0_method,
        index_rate,
        protect,
        filter_radius=3,
        resample_sr=0,
        rms_mix_rate=0.25,
    )

    if not audio_tuple or not isinstance(audio_tuple, tuple):
        return JSONResponse(status_code=500, content={"error": info})

    try:
        tgt_sr, audio_np = audio_tuple
        buffer = io.BytesIO()
        sf.write(buffer, audio_np, int(tgt_sr), format='WAV')
        buffer.seek(0)
        filename = f"synthesized_{int(time.time())}.wav"
        return StreamingResponse(
            buffer,
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to generate audio: {str(e)}"})


@app.get("/")
def root():
    return {
        "msg": "RVC TTS API",
        "endpoints": {
            "GET /": "This help message",
            "GET /docs": "Interactive API documentation (Swagger UI)",
            "GET /voices": "List all available edge-tts voices",
            "GET /synthesize": "Quick synthesis via query parameters",
            "POST /synthesize": "Full-featured synthesis with JSON body (returns audio)",
            "POST /synthesize/info": "Synthesis with JSON response containing metadata"
        }
    }
