# RVC Text-to-Speech WebUI

This is a text-to-speech Gradio webui for [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) models, using [edge-tts](https://github.com/rany2/edge-tts).

[🤗 Online Demo](https://huggingface.co/spaces/litagin/rvc_okiba_TTS)

This can run on CPU without GPU (but slow).

![Screenshot](assets/screenshot.jpg)

## Install

Requirements: Tested for Python 3.10 on Windows 11. Python 3.11 is probably not supported, so please use Python 3.10.

```bash
git clone https://github.com/litagin02/rvc-tts-webui.git
cd rvc-tts-webui

# Download models in root directory
curl -L -O https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt
curl -L -O https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt

# Make virtual environment
python -m venv venv
# Activate venv (for Windows)
venv\Scripts\activate

# Install PyTorch manually if you want to use NVIDIA GPU (Windows)
# See https://pytorch.org/get-started/locally/ for more details
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install requirements
pip install -r requirements.txt
```

## Locate RVC models

Place your RVC models in `weights/` directory as follows:

```bash
weights
├── model1
│   ├── my_model1.pth
│   └── my_index_file_for_model1.index
└── model2
    ├── my_model2.pth
    └── my_index_file_for_model2.index
...
```

Each model directory should contain exactly one `.pth` file and at most one `.index` file. Directory names are used as model names.

It seems that non-ASCII characters in path names gave faiss errors (like `weights/モデル1/index.index`), so please avoid them.

## Launch

### Gradio WebUI (GUI)

```bash
# Activate venv (for Windows/Linux)
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

python app.py
```

Open `http://localhost:7860` in your browser.

### FastAPI Server (API)

The project also includes a **FastAPI server** for programmatic access via REST API.

#### Start the API Server:

```bash
# Activate venv (for Windows/Linux)
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

python run_api.py
```

API will be available at `http://localhost:7861`

#### Interactive API Documentation:
- Swagger UI: http://localhost:7861/docs
- ReDoc: http://localhost:7861/redoc

---

## API Documentation

The FastAPI server provides the following endpoints:

### **1. GET `/voices`** — List Available Voices

Returns all 322+ available edge-tts voices.

**Request:**
```bash
curl http://127.0.0.1:7861/voices
```

**Response:**
```json
{
  "total": 322,
  "voices": [
    {
      "name": "id-ID-GadisNeural",
      "gender": "Female",
      "language": "id",
      "locale": "id-ID",
      "friendly_name": "id-ID-GadisNeural-Female"
    },
    ...
  ]
}
```

---

### **2. GET `/synthesize`** — Quick Synthesis (Query Parameters)

Synthesize voice and stream audio directly. Best for simple use cases.

**Request:**
```bash
# Minimal
curl "http://127.0.0.1:7861/synthesize?text=Hello%20world&voice=en-US-AriaNeural" \
  --output audio.wav

# With all parameters
curl "http://127.0.0.1:7861/synthesize?text=Halo%20dunia&voice=id-ID-GadisNeural&model=models&speed=10&transpose=5&f0_method=rmvpe&index_rate=0.8&protect=0.33" \
  --output audio.wav
```

**Query Parameters:**
- `text` (required): Text to synthesize
- `voice` (optional, default: `en-US-AriaNeural`): Voice name from `/voices`
- `model` (optional, default: `models`): Model folder name from `weights/`
- `speed` (optional, default: `0`): Speech speed percent (-100 to 100)
- `transpose` (optional, default: `0`): F0 transpose in semitones
- `f0_method` (optional, default: `rmvpe`): Pitch extraction method (`pm` or `rmvpe`)
- `index_rate` (optional, default: `1.0`): Index rate (0.0 to 1.0)
- `protect` (optional, default: `0.33`): Protect slider value (0.0 to 0.5)

**Response:** Audio file (WAV format, 16-bit PCM)

**Usage Example - Browser Audio Player:**
```html
<audio controls style="width: 100%;">
  <source src="http://127.0.0.1:7861/synthesize?text=Halo%20dunia&voice=id-ID-GadisNeural&f0_method=pm" type="audio/wav">
  Your browser doesn't support audio playback
</audio>
```

---

### **3. POST `/synthesize`** — Full Synthesis (JSON Body)

Synthesize with full parameters via JSON POST request. Returns audio file directly.

**Request:**
```bash
curl -X POST http://127.0.0.1:7861/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "model": "models",
    "text": "Halo dunia",
    "voice": "id-ID-GadisNeural",
    "speed": 0,
    "transpose": 0,
    "f0_method": "rmvpe",
    "index_rate": 1,
    "protect": 0.33,
    "filter_radius": 3,
    "resample_sr": 0,
    "rms_mix_rate": 0.25
  }' \
  --output audio.wav
```

**JSON Body Parameters:**
- `model` (required): Model name
- `text` (required): Text to synthesize
- `voice` (required): Voice name
- `speed` (optional): Speech speed percent
- `transpose` (optional): F0 transpose
- `f0_method` (optional): Pitch extraction method
- `index_rate` (optional): Index rate
- `protect` (optional): Protect value
- `filter_radius` (optional): Filter radius
- `resample_sr` (optional): Resample sample rate (0 = no resampling)
- `rms_mix_rate` (optional): RMS mix rate

**Response:** Audio file (WAV format)

---

### **4. POST `/synthesize/info`** — Synthesis with Metadata

Returns JSON response with synthesis info and audio download URL.

**Request:**
```bash
curl -X POST http://127.0.0.1:7861/synthesize/info \
  -H "Content-Type: application/json" \
  -d '{
    "model": "models",
    "text": "Halo dunia",
    "voice": "id-ID-GadisNeural",
    "f0_method": "pm"
  }'
```

**Response:**
```json
{
  "info": "Success. Time: edge-tts: 0.76s, npy: 1.07s, f0: 0.01s, infer: 5.44s",
  "edge_tts_path": "edge_output.mp3",
  "output_audio_url": "/outputs/output_1771841646_4554f211ce454a1fb642bae80fe5b080.wav"
}
```

---

## JavaScript Examples

### Example 1: Simple Synthesis with HTML Audio Element

```html
<!DOCTYPE html>
<html>
<head>
  <title>RVC TTS</title>
  <style>
    body { font-family: Arial; max-width: 600px; margin: 50px auto; }
    input, select, button { padding: 8px; margin: 5px; }
    audio { width: 100%; margin-top: 20px; }
  </style>
</head>
<body>
  <h1>🎤 RVC Text-to-Speech</h1>
  
  <input type="text" id="textInput" placeholder="Enter text..." value="Halo dunia" style="width: 300px;">
  
  <select id="voiceSelect">
    <option value="id-ID-GadisNeural">Indonesian - Female (Gadis)</option>
    <option value="id-ID-ArdiNeural">Indonesian - Male (Ardi)</option>
    <option value="en-US-AriaNeural">English - Female (Aria)</option>
    <option value="en-US-AndrewNeural">English - Male (Andrew)</option>
  </select>
  
  <button onclick="synthesize()">🎵 Synthesize</button>
  
  <audio id="player" controls></audio>
  
  <script>
    async function synthesize() {
      const text = document.getElementById('textInput').value;
      const voice = document.getElementById('voiceSelect').value;
      
      if (!text) {
        alert('Please enter some text');
        return;
      }
      
      const url = new URL('http://127.0.0.1:7861/synthesize');
      url.searchParams.append('text', text);
      url.searchParams.append('voice', voice);
      url.searchParams.append('f0_method', 'pm');
      
      document.getElementById('player').src = url.toString();
      document.getElementById('player').play();
    }
    
    // Allow Enter key to trigger synthesis
    document.getElementById('textInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') synthesize();
    });
  </script>
</body>
</html>
```

### Example 2: React Component

```jsx
import React, { useState } from 'react';

export default function TTSComponent() {
  const [text, setText] = useState('Hello world');
  const [voice, setVoice] = useState('en-US-AriaNeural');
  const [loading, setLoading] = useState(false);
  const audioRef = React.useRef();

  const synthesize = async () => {
    setLoading(true);
    try {
      const url = new URL('http://127.0.0.1:7861/synthesize');
      url.searchParams.append('text', text);
      url.searchParams.append('voice', voice);
      url.searchParams.append('f0_method', 'pm');
      
      const response = await fetch(url.toString());
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      audioRef.current.src = audioUrl;
      audioRef.current.play();
    } catch (error) {
      console.error('Error:', error);
      alert('Synthesis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '50px auto' }}>
      <h1>🎤 RVC TTS</h1>
      <input 
        type="text" 
        value={text} 
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text..."
        style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
      />
      <select 
        value={voice} 
        onChange={(e) => setVoice(e.target.value)}
        style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
      >
        <option value="en-US-AriaNeural">English - Female</option>
        <option value="en-US-AndrewNeural">English - Male</option>
        <option value="id-ID-GadisNeural">Indonesian - Female</option>
      </select>
      <button 
        onClick={synthesize} 
        disabled={loading}
        style={{ padding: '8px 20px', cursor: 'pointer' }}
      >
        {loading ? 'Synthesizing...' : 'Synthesize'}
      </button>
      <audio ref={audioRef} controls style={{ width: '100%', marginTop: '20px' }} />
    </div>
  );
}
```

### Example 3: Python Client

```python
import requests
from pathlib import Path

API_URL = "http://127.0.0.1:7861"

# Get available voices
def get_voices():
    response = requests.get(f"{API_URL}/voices")
    return response.json()

# Synthesize and save
def synthesize(text, voice, output_file="output.wav"):
    url = f"{API_URL}/synthesize"
    params = {
        "text": text,
        "voice": voice,
        "f0_method": "pm",
        "model": "models"
    }
    response = requests.get(url, params=params)
    
    with open(output_file, "wb") as f:
        f.write(response.content)
    
    return output_file

# Example usage
if __name__ == "__main__":
    # List available voices
    voices = get_voices()
    print(f"Total voices: {voices['total']}")
    
    # Find Indonesian voices
    id_voices = [v for v in voices['voices'] if v['locale'].startswith('id-ID')]
    print(f"Indonesian voices: {id_voices}")
    
    # Synthesize
    output = synthesize("Halo dunia", "id-ID-GadisNeural")
    print(f"Saved to: {output}")
```

---

## Requirements

### Gradio WebUI
- Python 3.10
- PyTorch (GPU optional)
- CUDA Toolkit (if using GPU)

### FastAPI Server
Same as Gradio WebUI, plus:
- FastAPI
- Uvicorn
- python-multipart

All dependencies are listed in `requirements.txt`



## Update

```bash
git pull
venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

Both Gradio WebUI and FastAPI server will be updated automatically.

## Comparison: WebUI vs API

| Feature | Gradio WebUI | FastAPI API |
|---------|---------|---------|
| **Usage** | Interactive GUI | Programmatic REST API |
| **Port** | 7860 | 7861 |
| **Best for** | Manual testing, UI usage | Integration, automation, client apps |
| **Response Type** | Web interface | Audio file or JSON metadata |
| **Voice Selection** | Dropdown menu | List endpoint + parameter |
| **Batch Processing** | Manual | Automatic via scripts/API clients |
| **Mobile Friendly** | Yes | Yes (with custom client) |

## Troubleshooting

### General Issues

```
error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for fairseq
Failed to build fairseq
ERROR: Could not build wheels for fairseq, which is required to install pyproject.toml-based projects
```

Maybe fairseq needs Microsoft C++ Build Tools.
[Download installer](https://visualstudio.microsoft.com/ja/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16) and install it.

---

### API Server Issues

#### **Port already in use**

If you get `Address already in use` error when starting the API:

```bash
# Kill the existing process
# On Linux/Mac:
pkill -f "python.*run_api"
sleep 2

# On Windows:
netstat -ano | findstr :7861
taskkill /PID <PID> /F

# Then restart
python run_api.py
```

#### **asyncio.run() error when using API**

If you get `RuntimeError: asyncio.run() cannot be called from a running event loop`, this means the server is already running. The fix has been applied in the latest version. Just make sure you're using the latest code.

#### **Voice not found**

If synthesis fails with voice not found, get the list of available voices first:

```bash
curl http://127.0.0.1:7861/voices | python3 -m json.tool | grep -A 5 "id-ID"
```

#### **Models not loaded**

If you see "No model found" error:

1. Make sure you have a folder in `weights/` directory with at least one `.pth` file
2. The folder name must match the `model` parameter in API requests
3. Example: `weights/models/model.pth` → use `model: "models"` in requests

#### **Slow synthesis on CPU**

RVC models are large and synthesis is computationally intensive. On CPU:
- First run takes 30-60 seconds for model loading
- Subsequent runs take 10-30 seconds
- Consider using GPU for faster synthesis (pass GPU device in `config.py`)

---

## File Structure

```
rvc-tts-webui/
├── app.py                 # Gradio WebUI
├── run_api.py            # FastAPI server launcher
├── api.py                # FastAPI application & endpoints
├── vc_infer_pipeline.py  # RVC inference pipeline
├── config.py             # Configuration
├── requirements.txt      # Python dependencies
├── weights/              # RVC model directory
│   └── models/
│       ├── model.pth
│       └── model.index
├── outputs/              # API audio output directory
├── lib/                  # Library modules
├── hubert_base.pt        # HuBERT model
├── rmvpe.pt             # RMVPE F0 predictor model
└── assets/              # UI assets & screenshots
```

---

## License

This project uses [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) models and other open-source projects. Please refer to their respective licenses.
