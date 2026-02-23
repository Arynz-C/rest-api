<div align="center">

# 🚀 Universal OCR REST API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-2.7-blue?style=for-the-badge&logo=paddlepaddle)](https://github.com/PaddlePaddle/PaddleOCR)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-red?style=for-the-badge)](LICENSE)
[![Linux](https://img.shields.io/badge/Linux-Friendly-green?style=for-the-badge&logo=linux)](https://www.linux.org/)
[![macOS](https://img.shields.io/badge/macOS-Compatible-grey?style=for-the-badge&logo=apple)](https://www.apple.com/)

---

<img src="https://media.giphy.com/media/L8K62iTDkzGX6/giphy.gif" width="300" alt="OCR Animation">

**Lightweight & Powerful OCR REST API** built with **FastAPI** and **PaddleOCR**

*Transform documents into text with ease* 📝✨

</div>

---

## 📋 Quick Overview

Supports multiple file formats for comprehensive document processing:

* 🖼️ **Images**: `jpg`, `png`, `jpeg`, `webp`
* 📄 **PDF** files (multi-page)
* 📝 **DOC / DOCX** documents

**Perfect for:**

* ✅ Local deployment
* ✅ GitHub Codespaces
* ✅ Self-hosted AI pipelines
* ✅ Automation & OSINT workflows
* ✅ Enterprise document processing

---

## ✨ Features

<table>
  <tr>
    <td>⚡ FastAPI high-performance API</td>
    <td>📚 Multi-page PDF support</td>
  </tr>
  <tr>
    <td>🧠 PaddleOCR deep learning</td>
    <td>📝 DOCX → PDF auto conversion</td>
  </tr>
  <tr>
    <td>🐧 Linux friendly</td>
    <td>📖 Paragraph reconstruction</td>
  </tr>
  <tr>
    <td>🍎 macOS compatible</td>
    <td>☁️ Codespaces ready</td>
  </tr>
</table>

---

## 🧠 Tech Stack

```
┌─────────────────────────────────────┐
│     Universal OCR REST API          │
├─────────────────────────────────────┤
│  🔵 FastAPI          - API Framework │
│  🧠 PaddleOCR        - OCR Engine    │
│  🏹 PaddlePaddle     - ML Framework  │
│  📷 OpenCV           - Image Proc    │
│  📄 pdf2image        - PDF Convert   │
│  🖋️  LibreOffice      - Doc Convert  │
│  ⚙️  Poppler          - PDF Tools    │
└─────────────────────────────────────┘
```

---

## 📦 Supported Formats

| Format | Status | Notes |
|--------|--------|-------|
| JPG 🖼️  | ✅ Supported | Recommended |
| PNG 🖼️  | ✅ Supported | Lossless |
| WEBP 🖼️ | ✅ Supported | Modern format |
| JPEG 🖼️ | ✅ Supported | Compatible |
| PDF 📄  | ✅ Supported | Multi-page |
| DOC 📝  | ✅ Supported | Auto-convert |
| DOCX 📝 | ✅ Supported | Auto-convert |

---

## 🖥️ Installation Guide

### 📥 Clone Repository

```bash
git clone https://github.com/yourusername/universal-ocr-api.git
cd universal-ocr-api
```

---

## 🐧 Linux Installation

### 🏹 **Arch Linux**

Install system dependencies:

```bash
sudo pacman -S python python-pip poppler libreoffice-fresh
```

Create virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install Python packages:

```bash
pip install -U pip
pip install -r requirements.txt
```

Run API:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

### 🟣 **Ubuntu / Debian**

Install dependencies:

```bash
sudo apt update
sudo apt install -y python3 python3-venv poppler-utils libreoffice
```

Setup environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🍎 macOS Installation

Install Homebrew first: https://brew.sh

Install dependencies:

```bash
brew install poppler libreoffice
```

Setup Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## ☁️ GitHub Codespaces

Create new Codespace and run:

```bash
sudo apt update
sudo apt install -y poppler-utils libreoffice
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Access API documentation:

```
https://PORT-preview.app.github.dev/docs
```

---

## 🌐 API Usage

### 📍 Home Endpoint

**GET** `/`

Check if API is running:

```json
{
  "message": "Universal OCR API Ready"
}
```

---

### 🔍 OCR Endpoint

**POST** `/ocr`

Upload file using multipart form data for OCR processing.

**Supported Files:**
- Images (jpg, png, jpeg, webp)
- PDF files
- DOC/DOCX documents

---

### 💻 Example CURL Commands

**Process PDF:**
```bash
curl -X POST \
  -F "file=@document.pdf" \
  http://localhost:8000/ocr
```

**Process Image:**
```bash
curl -X POST \
  -F "file=@photo.jpg" \
  http://localhost:8000/ocr
```

**Process Document:**
```bash
curl -X POST \
  -F "file=@report.docx" \
  http://localhost:8000/ocr
```

---

## 📤 API Response Example

```json
{
  "filename": "document.pdf",
  "total_pages": 1,
  "pages": [
    {
      "page": 1,
      "text": "Detected paragraph text reconstructed and organized here..."
    }
  ]
}
```

---

## 📁 Project Structure

```
.
├── main.py                          # FastAPI application
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
└── __pycache__/                     # Python cache
```

---

## ⚠️ System Requirements

**Python:** 3.10 or higher (3.11+ recommended)

**Hardware:**
- ✅ CPU-only mode supported
- ⭐ GPU optional (CUDA/cuDNN for speedup)
- 💾 Minimum 4GB RAM
- 🔄 SSD recommended for better performance

**Storage:**
- ~2GB for model downloads
- ~1GB for dependencies

---

## 🧩 Troubleshooting

### ❌ numpy / cv2 Error

Recreate environment from scratch:

```bash
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### ❌ PDF Processing Not Working

Ensure Poppler is installed:

**Arch Linux:**
```bash
sudo pacman -S poppler
```

**Ubuntu/Debian:**
```bash
sudo apt install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

---

### ❌ DOCX File Not Processing

Ensure LibreOffice is installed:

**Arch Linux:**
```bash
sudo pacman -S libreoffice-fresh
```

**Ubuntu/Debian:**
```bash
sudo apt install libreoffice
```

**macOS:**
```bash
brew install libreoffice
```

---

### ❌ Port Already in Use

Use different port:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

---

## 🚀 Roadmap

- [ ] 🎯 Layout detection
- [ ] 📊 Table OCR
- [ ] 📦 Batch processing
- [ ] 🗄️ Vector database export
- [ ] 🔗 RAG pipeline integration
- [ ] 🌐 Multi-language support
- [ ] 📱 Mobile API client
- [ ] 🐳 Docker containerization

---

## 🔐 Security Best Practices

- Use environment variables for sensitive config
- Validate file uploads (type & size)
- Run behind reverse proxy (nginx/Apache)
- Implement rate limiting
- Use HTTPS in production
- Set appropriate file size limits

---

## 📊 Performance Tips

- Use GPU if available (significant speedup)
- Batch process files for better throughput
- Adjust PDF DPI for quality vs speed tradeoff
- Cache model in memory between requests
- Consider async processing for large files

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📜 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions...
```

---

## ⭐ Show Your Support

If this project helped you, please consider:

- ⭐ **Star** the repository
- 🍴 **Fork** and build upon it
- 💬 **Share** with others
- 🚀 **Contribute** improvements
- 🐛 **Report** bugs & issues

**Your support drives development!** 💪

---

## 📞 Support & Contact

- 📧 Email: your-email@example.com
- 🐙 GitHub Issues: [Report Issues](https://github.com/yourusername/universal-ocr-api/issues)
- 💬 Discussions: [Join Discussion](https://github.com/yourusername/universal-ocr-api/discussions)

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [Python Best Practices](https://pep8.org/)
- [REST API Design](https://restfulapi.net/)

---

<div align="center">

### Built with ❤️ for the Community

Made with 🚀 by Rynz

⬆️ [Back to Top](#-universal-ocr-rest-api)

</div>
