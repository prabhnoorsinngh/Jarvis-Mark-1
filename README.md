# 🤖 JARVIS Mark I - Ultimate Edition

![JARVIS Banner](https://img.shields.io/badge/JARVIS-MARK%20I-00FFFF?style=for-the-badge&logo=python) 
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge) 

**JARVIS Mark I** is an advanced, fully autonomous personal AI assistant built with Python. It features a cinematic Iron Man-style Graphical User Interface (HUD), complete system automation, real-time internet searches, and human-like voice synthesis.

Engineered by **Mr. Prabhnoor Singh** of **Singh Industries**.

---

## ✨ Key Features

- **Real-Time Online AI:** Powered by advanced language models with live internet access (via OpenRouter) to answer any general knowledge or coding question accurately.
- **Cinematic HUD GUI:** A stunning, animated Arc Reactor interface with real-time system monitoring (CPU, RAM, Disk, Uptime) and a sleek dark-mode aesthetic.
- **System Automation:** Control your PC completely—adjust volume, lock the screen, take screenshots, manage files, and execute shell commands.
- **Music & Media Control:** Search and play music seamlessly from YouTube with full playback controls.
- **WhatsApp Integration:** Automate sending messages and making calls completely hands-free.
- **VS Code Integration:** Automatically generate, write, and execute code within your IDE.
- **Human-Like TTS:** High-quality voice synthesis with natural pacing, multi-language support, and adjustable speech rates.
- **Contextual Memory:** JARVIS remembers the context of your conversation, easily resolving pronouns like "it", "that", and "this".

---

## 🛠️ Installation

### 1. Prerequisites
- Python 3.9 or higher
- Windows / macOS / Linux

### 2. Setup
Clone the repository and install the dependencies:

```bash
git clone https://github.com/cws2024/Jarvis-Mark-1.git
cd Jarvis-Mark-1
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the `MAIN_JARVIS_SOFTWARE` directory and add your API keys:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
WEATHER_API_KEY=your_rapidapi_weather_key_here
```

*(Note: Never commit your `.env` file. It is already included in `.gitignore`)*

---

## 🚀 Usage

To launch the ultimate JARVIS experience with the GUI:

```bash
python MAIN_JARVIS_SOFTWARE/jarvisgui.py
```

### Modes of Operation
- **Text Mode:** Type commands directly into the GUI input bar.
- **Voice Mode:** Click the "Voice" button or say the hotword ("JARVIS") to initiate voice listening.

---

## 🛡️ Safety & Confirmations
JARVIS is equipped with a comprehensive safety layer. High-risk operations like deleting files, shutting down the computer, or executing arbitrary code will automatically prompt you for confirmation before proceeding.

---

*© 2024 Singh Industries | Engineered by Mr. Prabhnoor Singh*
