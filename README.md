# 🎤 RVC Text-to-Speech WebUI & API

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.2-009485?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Gradio](https://img.shields.io/badge/Gradio-3.38.0-FF6B35?style=flat-square&logo=gradio)](https://gradio.app)
[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![PyTorch](https://img.shields.io/badge/PyTorch-Latest-ee4c2c?style=flat-square&logo=pytorch)](https://pytorch.org)

**🚀 Transform Text into Natural-Sounding Speech with AI Voice Conversion**

> Advanced **Real-time Voice Conversion** using RVC models + **Interactive Web UI** + **Production-Ready REST API**

[🤗 Online Demo](https://huggingface.co/spaces/litagin/rvc_okiba_TTS) • [📖 Documentation](#-api-documentation) • [🛠️ Installation](#-install)

</div>

---

## ✨ Features

- 🎯 **Easy-to-Use Web Interface** - Gradio WebUI for interactive synthesis
- ⚡ **High-Performance FastAPI** - REST API with streaming audio support  
- 🗣️ **322+ Voices** - Edge-TTS integration with multilingual support
- 🔊 **Real-time Voice Conversion** - Advanced RVC AI model integration
- 💻 **CPU/GPU Support** - Works on both CPU and NVIDIA GPU
- 🌍 **Multi-Language** - Indonesian, English, Japanese, Arabic, and 100+
- 📱 **API-First Design** - Perfect for mobile apps, web services, and integrations
- ⚙️ **Customizable** - F0 extraction, pitch control, index rate tuning
- 🎨 **Multiple Output Formats** - Direct audio streaming and JSON responses
- 📊 **Production Ready** - Error handling, caching, logging included

---

## 🎬 Quick Demo

### Interactive Web UI
```bash
python app.py
# Open http://localhost:7860
```

### REST API
```bash
python run_api.py
# API: http://localhost:7861/docs
```

### Quick Test
```bash
curl "http://127.0.0.1:7861/synthesize?text=Hello&voice=en-US-AriaNeural&f0_method=pm" --output hello.wav
ffplay hello.wav
```

---

## 🛠️ Install

### Requirements 📋

- **Python 3.10** (recommended; 3.11 may have compatibility issues)
- **PyTorch** (CPU or CUDA)
- **Git** for cloning the repository
- **4GB+ RAM** (8GB+ recommended for faster synthesis)
- **GPU optional** but recommended for real-time synthesis

### Setup Instructions 🚀

```bash
# 1️⃣ Clone repository
git clone https://github.com/litagin02/rvc-tts-webui.git
cd rvc-tts-webui

# 2️⃣ Create virtual environment
python -m venv venv

# 3️⃣ Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4️⃣ Download AI models (required)
curl -L -O https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt
curl -L -O https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt

# 5️⃣ (Optional) Install PyTorch for NVIDIA GPU
# See: https://pytorch.org/get-started/locally/ for CUDA support
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 6️⃣ Install dependencies
pip install -r requirements.txt

# ✅ Done! Ready to use!
```

---

## 🎵 Setup RVC Models

Place your RVC voice models in the `weights/` directory. Each model folder should contain at least one `.pth` file.

**📁 Directory Structure:**
```
weights/
├── model1/
│   ├── model.pth          ✅ Required
│   └── model.index        (Optional)
└── model2/
    ├── model.pth          ✅ Required
    └── model.index        (Optional)
```

⚠️ **Important Notes:**
- Each folder = one model (name must match parameter in API requests)
- Exactly one `.pth` file per folder (model weights)
- At most one `.index` file per folder (optional - for improved quality)
- **Avoid non-ASCII characters** in folder names (causes errors)
- Download models from: [RVC-Project](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)

---

## 🚀 Launch

### 🖥️ Gradio WebUI (Interactive GUI)

```bash
# Activate venv (for Windows/Linux)
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

python app.py
```

🌐 **Open browser:** http://localhost:7860

### ⚡ FastAPI Server (REST API)

Production-ready REST API for integration with web apps, mobile apps, or services.

**Start the API Server:**
```bash
# Activate venv
# Windows: venv\Scripts\activate
# Linux:  source venv/bin/activate

python run_api.py
```

🚀 **API ready at:** http://localhost:7861

📚 **Interactive Documentation:**
- Swagger UI: [http://localhost:7861/docs](http://localhost:7861/docs) ⭐
- ReDoc: http://localhost:7861/redoc

---

## 📖 API Documentation

Advanced REST API with support for streaming audio, JSON responses, and batch processing.

### 🎙️ **1. GET `/voices`** — List Available Voices

Get all 322+ available voices from edge-tts with metadata.

**Example:**
```bash
curl http://127.0.0.1:7861/voices | jq '.voices[] | select(.locale | startswith("id"))'
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

Synthesize voice and stream audio directly. Best for simple/quick use cases.

**Quick Examples:**
```bash
# 🚀 Minimal (just text)
curl "http://127.0.0.1:7861/synthesize?text=Hello" --output hello.wav

# 🌍 With Indonesian voice
curl "http://127.0.0.1:7861/synthesize?text=Halo%20dunia&voice=id-ID-GadisNeural&f0_method=pm" \
  --output hello_id.wav

# 🎵 All parameters (advanced)
curl "http://127.0.0.1:7861/synthesize?text=Halo&voice=id-ID-GadisNeural&model=models&speed=10&transpose=5&f0_method=rmvpe&index_rate=0.8&protect=0.33" \
  --output advanced.wav
```

**📋 Query Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `text` | string | ❌ required | - | Text to synthesize |
| `voice` | string | `en-US-AriaNeural` | - | Voice name from `/voices` |
| `model` | string | `models` | - | Model folder in `weights/` |
| `speed` | int | `0` | -100 to 100 | Speech speed percent |
| `transpose` | int | `0` | - | F0 transpose (semitones) |
| `f0_method` | string | `rmvpe` | `pm`, `rmvpe` | Pitch extraction method |
| `index_rate` | float | `1.0` | 0.0-1.0 | Index rate (vector quality) |
| `protect` | float | `0.33` | 0.0-0.5 | Protect unvoiced consonants |

**📤 Response:** Audio file (WAV, 16-bit PCM, 48kHz)

**🌐 Browser Audio Player Example:**

```html
<audio controls style="width: 100%;">
  <source src="http://127.0.0.1:7861/synthesize?text=Halo%20dunia&voice=id-ID-GadisNeural&f0_method=pm" type="audio/wav">
  Your browser doesn't support audio playback
</audio>
```

---

### 🎚️ **2. POST `/synthesize`** — Full Synthesis (JSON Body)

Advanced synthesis with full control over all parameters. Returns audio file directly (streaming).

**Example:**
```bash
curl -X POST http://127.0.0.1:7861/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "model": "models",
    "text": "Halo dunia",
    "voice": "id-ID-GadisNeural",
    "speed": 0,
    "transpose": 5,
    "f0_method": "rmvpe",
    "index_rate": 0.8,
    "protect": 0.33,
    "filter_radius": 3,
    "resample_sr": 0,
    "rms_mix_rate": 0.25
  }' \
  --output audio.wav
```

**📋 Request Body Parameters:** Same as GET `/synthesize` + advanced options

**📤 Response:** Audio file (WAV, 16-bit PCM)

---

### � **3. POST `/synthesize/info`** — Synthesis with Metadata

Returns JSON with synthesis info, timing, and audio download URL. Useful for logging and metadata tracking.

**Example:**
```bash
curl -X POST http://127.0.0.1:7861/synthesize/info \
  -H "Content-Type: application/json" \
  -d '{
    "model": "models",
    "text": "Halo dunia",
    "voice": "id-ID-GadisNeural",
    "speed": 0,
    "f0_method": "pm"
  }'
```

**📚 Request Body Parameters:**
- `model` (required): Model name in `weights/`
- `text` (required): Text to synthesize
- `voice` (required): Voice name
- `speed` (optional): Speech speed percent
- `transpose` (optional): F0 transpose
- `f0_method` (optional): `pm` (fast) or `rmvpe` (quality)
- `index_rate` (optional): Index weight (0.0-1.0)
- `protect` (optional): Protect unvoiced (0.0-0.5)
- `filter_radius` (optional): Filter radius (default: 3)
- `resample_sr` (optional): Resample SR (0=no resampling)
- `rms_mix_rate` (optional): RMS mix (default: 0.25)

**✅ Response:**
```json
{
  "info": "Success. Time: edge-tts: 0.76s, npy: 1.07s, f0: 0.01s, infer: 5.44s",
  "edge_tts_path": "edge_output.mp3",
  "output_audio_url": "/outputs/output_1771841646_4554f211ce454a1fb642bae80fe5b080.wav"
}
```



**✅ Response:**
```json
{
  "info": "Success. Time: edge-tts: 0.76s, npy: 1.07s, f0: 0.01s, infer: 5.44s",
  "edge_tts_path": "edge_output.mp3",
  "output_audio_url": "/outputs/output_1771841646_4554f211ce454a1fb642bae80fe5b080.wav"
}
```

---

## 💻 Code Examples

Pick your language and get started! All examples are production-ready.

### 🌐 **Example 1: HTML + Vanilla JavaScript**

Simple web UI with audio player - copy & paste to HTML file.

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

### ⚛️ **Example 2: React Component**

Modern React component with state management, error handling, and loading states.

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

### 🐍 **Example 3: Python Client**

Command-line/script interface for batch processing and automation.

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

## 📦 Requirements

### For Gradio WebUI
- ✅ Python 3.10+
- ✅ PyTorch (CPU or GPU)
- ✅ 4GB+ RAM
- ✅ (Optional) NVIDIA GPU + CUDA Toolkit

### For FastAPI Server
Same as above + dependencies in `requirements.txt`:
- FastAPI (REST framework)
- Uvicorn (ASGI server)
- SoundFile (audio I/O)

---

## 🔄 Update

Keep your installation up-to-date with improvements and bug fixes:

```bash
# Pull latest changes
git pull

# Update dependencies
venv\Scripts\activate (Windows) or source venv/bin/activate (Linux)
pip install -r requirements.txt --upgrade
```

Both Gradio WebUI and FastAPI server update automatically.

---

## 🎯 WebUI vs API Comparison

Choose based on your use case:

| Feature | 🖥️ Gradio WebUI | ⚡ FastAPI API |
|---------|---------|---------|
| **Interface** | Interactive Web UI | REST Endpoints |
| **Port** | 7860 | 7861 |
| **Best For** | Manual testing, live demo | App integration, automation |
| **Response** | Web page + audio player | Audio file or JSON |
| **Voices** | Dropdown selector | `/voices` endpoint |
| **Batch Processing** | ❌ Manual | ✅ Automatic |
| **Mobile App** | ✅ Web browser | ✅ Native SDK |
| **Performance** | Single user | Multi-user (scalable) |
| **Deploy** | Development | Production |

---

## 🐛 Troubleshooting & FAQ

### ⚠️ Installation Issues

#### Microsoft C++ Build Tools Error (Windows)

**Problem:** `error: Microsoft Visual C++ 14.0 or greater is required`

**Solution:**
1. Download [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Run installer and select "Desktop development with C++"
3. Retry: `pip install -r requirements.txt`

---

### ⚠️ API Server Issues

#### 🔴 **Port Already In Use**

**Problem:** `Address already in use` when starting API

**Solution:**
```bash
# Linux/Mac:
pkill -f "python.*run_api"
sleep 2
python run_api.py

# Windows:
netstat -ano | findstr :7861
taskkill /PID <PID> /F
python run_api.py
```

---

#### 🔴 **asyncio Event Loop Error**

**Problem:** `RuntimeError: asyncio.run() cannot be called from a running event loop`

**Solution:** This is fixed in latest version. Update your code:
```bash
git pull
pip install -r requirements.txt --upgrade
```

---

#### 🔴 **Voice Recognition Failed**

**Problem:** `Voice not found` or synthesis fails

**Solution:**
1. Get available voices: `curl http://127.0.0.1:7861/voices`
2. Use exact voice name from list
3. Example: `id-ID-GadisNeural` (not `GadisNeural`)

---

### ⚠️ Model & Performance Issues

#### 🔴 **No Models Found**

**Problem:** `No model found in weights folder`

**Solution:**
1. Create folder: `mkdir -p weights/models`
2. Add `.pth` file: `cp path/to/voice.pth weights/models/model.pth`
3. Optionally add `.index` file for quality boost
4. Restart API/WebUI

---

#### 🔴 **Slow Synthesis**

**Problem:** Synthesis takes >30 seconds

**Cause:** Running on CPU (normal for RVC models)

**Solutions:**
- Use GPU: Install PyTorch with CUDA support
- Use faster` F0 extraction: `f0_method=pm` instead of `rmvpe`
- Accept that CPU synthesis takes 10-30 seconds per request

---

#### 🔴 **Out of Memory**

**Problem:** `CUDA out of memory` or system freeze on synthesis

**Solution:**
1. Reduce batch size/model size
2. Use CPU instead of GPU (slower but works)
3. Close other memory-intensive applications
4. Install more RAM if persistent

---

## 📁 Project Structure

Overview of the codebase:

```
rvc-tts-webui/
├── 🎤 app.py                    # Gradio WebUI application
├── ⚡ run_api.py                 # FastAPI server launcher
├── 📡 api.py                     # FastAPI endpoints & routes
├── 🔊 vc_infer_pipeline.py       # RVC voice conversion pipeline
├── ⚙️ config.py                  # Configuration settings
├── 📋 requirements.txt           # Python dependencies
│
├── 🎵 weights/                   # RVC Voice Models (user-provided)
│   └── models/
│       ├── model.pth             # Voice model weights
│       └── model.index           # Voice vector index (optional)
│
├── 📤 outputs/                   # API output audio files (auto-generated)
├── 📚 lib/                       # Library modules & utilities
├── 🧠 hubert_base.pt            # HuBERT feature encoder model
├── 🎚️ rmvpe.pt                  # RMVPE pitch extractor model
└── 🎨 assets/                    # Screenshots & UI assets
```


---

## 📚 Additional Resources

- [RVC Project](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) - Voice conversion AI models
- [edge-tts](https://github.com/rany2/edge-tts) - Text-to-speech synthesis
- [FastAPI Documentation](https://fastapi.tiangolo.com) - REST API framework
- [Gradio Docs](https://gradio.app) - Web UI framework

---

## 📄 License

This project uses [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) models and other open-source projects. Please refer to their respective licenses.

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs and issues
- Request new features
- Submit pull requests
- Improve documentation

---

## ⭐ Show Your Support

If this project helps you, please give it a ⭐ on GitHub!

Made with ❤️ for the open-source community

