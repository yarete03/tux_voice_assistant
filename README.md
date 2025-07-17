Based on the codebase context, you're asking for a README.md for the Tux Voice Assistant repository (`yarete03/tux_voice_assistant`), which is a Spanish voice-controlled automation system with multiple external service integrations. 

# Tux Voice Assistant

A Python-based voice-controlled automation system that processes Spanish voice commands through wake word detection and executes actions across multiple external services. [1](#0-0) 

## What This App Does

The Tux Voice Assistant listens for the Spanish wake word "asistente" and processes voice commands to control: [2](#0-1) 

- **Media Control**: Play/pause/skip music using playerctl [3](#0-2) 
- **YouTube Music**: Search and play music via YouTube Music API [4](#0-3) 
- **WhatsApp Messaging**: Send messages through WhatsApp Web automation [5](#0-4) 
- **Phone Calls**: Make and manage calls via Bluetooth HFP [6](#0-5) 
- **System Control**: Lock screen and power off system [7](#0-6) 
- **Time Queries**: Get current time via voice [8](#0-7) 

## Dependencies

### Python Dependencies
Install via `pip install -r requirements.txt`: [9](#0-8) 

**Core Voice Processing:**
- `faster-whisper==1.1.1` - Speech recognition
- `pvporcupine==3.0.5` - Wake word detection
- `PyAudio==0.2.14` - Audio capture
- `fuzzywuzzy==0.18.0` - Command pattern matching

**External Service Integration:**
- `ytmusicapi==1.10.2` - YouTube Music API
- `playwright==1.50.0` - WhatsApp Web automation
- `dbus-python==1.3.2` - Phone call management
- `gTTS==2.5.4` - Text-to-speech

### System Dependencies

**Audio System:**
- PulseAudio server
- `pactl` command (usually in `pulseaudio-utils` package)

**Media Control:**
- `playerctl` - Universal media player control

**System Control:**
- `i3lock-fancy` - Screen locking
- `poweroff` command (systemd)

**Telephony (Optional):**
- Ofono daemon for Bluetooth HFP
- Bluetooth stack with HFP profile support

### Third-Party Services

**YouTube Music Integration:** [10](#0-9) 
- YouTube Music API OAuth credentials
- Requires `oauth.json` file and API tokens in `api_token.py`

**WhatsApp Integration:**
- WhatsApp Web access (browser-based)
- Persistent browser session storage

**Phone Integration:** [11](#0-10) 
- Bluetooth phone with HFP support
- `contacts.vcf` file for contact resolution

## Installation & Configuration

### 1. Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt install pulseaudio-utils playerctl i3lock-fancy ofono

# Install Playwright browsers
playwright install chromium
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Porcupine Wake Word Detection
Download custom wake word models from [Picovoice Console](https://console.picovoice.ai/ppn): [12](#0-11) 
- Place `asistente_es_linux_v3_0_0.ppn` in `./porcupine/`
- Place `cuelga_es_linux_v3_0_0.ppn` in `./porcupine/`
- Download `porcupine_params_es.pv` and `libpv_porcupine.so`

### 4. Configure API Tokens
Create `api_token.py` with: [13](#0-12) 
```python
porcupine_api_key = "your_porcupine_api_key"
ytmusic_oauth_client_id = "your_youtube_music_client_id"
ytmusic_oauth_client_secret = "your_youtube_music_client_secret"
```

### 5. Configure YouTube Music
- Set up OAuth credentials and save as `oauth.json` [14](#0-13) 

### 6. Configure Phone Integration (Optional)
- Place contacts in `contacts.vcf` format
- Ensure Ofono is running and Bluetooth phone is paired

### 7. Set Up Audio Files
Place audio feedback files in `./audio/`: [15](#0-14) 
- `mixkit-positive-interface-beep-221.wav`
- `error-8-206492.mp3`

### 8. Run the Assistant
```bash
python speech_recognition.py
```

The system runs continuously, listening for the wake word "asistente" followed by voice commands in Spanish. [16](#0-15) 

## Notes

The system is designed for Spanish voice commands and requires CUDA-compatible hardware for optimal Whisper performance. [17](#0-16)  WhatsApp integration uses browser automation which may be subject to WhatsApp's terms of service. Phone functionality requires a Bluetooth-connected phone with HFP support and the Ofono telephony stack.

Wiki pages you might want to explore:
- [Overview (yarete03/tux_voice_assistant)](/wiki/yarete03/tux_voice_assistant#1)
- [External Service Integrations (yarete03/tux_voice_assistant)](/wiki/yarete03/tux_voice_assistant#3)
