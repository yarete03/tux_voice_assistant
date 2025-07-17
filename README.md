


# Tux Voice Assistant

A Spanish language voice assistant for Linux that provides hands-free control of various system functions and media services through voice commands.

## What Does This App Do?

Tux Voice Assistant is a comprehensive voice-controlled system that offers the following capabilities:

### Core Features
- **Wake Word Detection**: Uses Porcupine AI for "asistente" and "cuelga" wake word detection [1](#0-0) 
- **Speech Recognition**: Implements Whisper AI for accurate Spanish speech transcription [2](#0-1) 
- **Text-to-Speech**: Converts responses to speech using Google TTS in Spanish [3](#0-2) 

### Media Control
- **Music Playback Control**: Next/previous track, play/pause via playerctl [4](#0-3) 
- **YouTube Music Integration**: Search and play songs directly from YouTube Music [5](#0-4) 
- **Song Information**: Get current artist and track information [6](#0-5) 

### Communication Features
- **WhatsApp Messaging**: Send messages via WhatsApp Web automation [7](#0-6) 
- **Phone Call Management**: Make, answer, and hang up calls via Bluetooth/HFP [8](#0-7) 

### System Control
- **Screen Lock**: Lock the screen using i3lock-fancy [9](#0-8) 
- **System Shutdown**: Power off the system [10](#0-9) 
- **Time Information**: Get current time via voice query [11](#0-10) 

## Voice Commands (Spanish)

The assistant recognizes various Spanish command patterns: [12](#0-11) 

## Dependencies

### Python Dependencies
Install from requirements.txt: [13](#0-12) 

```bash
pip install -r requirements.txt
```

Key Python packages include:
- `faster-whisper==1.1.1` - Speech recognition
- `gTTS==2.5.4` - Text-to-speech
- `pvporcupine==3.0.5` - Wake word detection
- `PyAudio==0.2.14` - Audio processing
- `playwright==1.50.0` - WhatsApp automation
- `ytmusicapi` - YouTube Music integration

### System Dependencies

**Audio System:**
- PulseAudio (`pactl` command) [14](#0-13) 

**Media Control:**
- `playerctl` - Media player control [15](#0-14) 

**System Control:**
- `i3lock-fancy` - Screen locking [16](#0-15) 
- `poweroff` utility [17](#0-16) 
- `notify-send` - Desktop notifications [18](#0-17) 

**Phone Integration:**
- oFono daemon for Bluetooth phone connectivity [19](#0-18) 
- D-Bus system bus access [20](#0-19) 

### Third-Party Services
# Tux Voice Assistant
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

**Porcupine AI (Picovoice):**
- API key required [21](#0-20) 
- Custom wake word models needed [22](#0-21) 

**YouTube Music:**
- OAuth credentials required [23](#0-22) 
- OAuth configuration file (`oauth.json`) [24](#0-23) 

## Installation and Configuration

### 1. System Packages Installation

```bash
# Ubuntu/Debian
sudo apt install pulseaudio-utils playerctl i3lock-fancy ofono

# Arch Linux
sudo pacman -S pulseaudio playerctl i3lock-fancy ofono
```

### 2. Python Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 3. Porcupine Configuration

1. **Get API Key**: Register at [Picovoice Console](https://console.picovoice.ai/)
2. **Download Wake Word Models**: 
   - Create custom wake words for "asistente" and "cuelga"
   - Download Spanish language model
   - Download platform-specific library
3. **Create Directory Structure**:
   ```
   ./porcupine/
   ├── asistente_es_linux_v3_0_0.ppn
   ├── cuelga_es_linux_v3_0_0.ppn
   ├── porcupine_params_es.pv
   └── libpv_porcupine.so
   ```

### 4. API Configuration

Create `api_token.py` file: [21](#0-20) 

```python
# Porcupine API key
porcupine_api_key = "YOUR_PORCUPINE_API_KEY"

# YouTube Music OAuth credentials
ytmusic_oauth_client_id = "YOUR_YOUTUBE_MUSIC_CLIENT_ID"
ytmusic_oauth_client_secret = "YOUR_YOUTUBE_MUSIC_CLIENT_SECRET"
```

### 5. YouTube Music Setup

1. **OAuth Setup**: Follow ytmusicapi documentation to create `oauth.json`
2. **Authentication**: Run the OAuth flow to authenticate with YouTube Music

### 6. Audio Files

Create `audio/` directory with sound files: [25](#0-24) 
```
./audio/
├── mixkit-positive-interface-beep-221.wav
└── error-8-206492.mp3
```

### 7. Contacts Configuration

Create `contacts.vcf` file with phone contacts in VCF format [26](#0-25) 

### 8. Phone Integration (Optional)

1. **Enable oFono**: 
   ```bash
   sudo systemctl enable ofono
   sudo systemctl start ofono
   ```
2. **Pair Bluetooth Phone**: Connect your phone via Bluetooth with HFP profile
3. **Test D-Bus Access**: Ensure your user has access to system D-Bus

## Usage

### Starting the Assistant

```bash
python speech_recognition.py
```

The assistant will:
1. Initialize audio systems
2. Start call management process
3. Listen for wake words
4. Process voice commands

### First-Time Setup

1. **WhatsApp Web**: On first WhatsApp command, the assistant will open a browser for QR code scanning [27](#0-26) 
2. **Phone Pairing**: Connect your Bluetooth phone before using call features
3. **Audio Permissions**: Ensure microphone access is granted

## Security Considerations

- **WhatsApp Cookies**: Stored locally in `.whatsapp_cookies` directory [28](#0-27) 
- **API Keys**: Keep `api_token.py` secure and never commit to version control
- **System Access**: The assistant requires system-level permissions for power control and D-Bus access

## Notes

- The assistant is designed specifically for Spanish language commands and responses
- CUDA support is enabled for Whisper AI for better performance [2](#0-1) 
- WhatsApp functionality may be limited due to automation detection [29](#0-28) 
- Phone integration requires a Bluetooth-connected phone with HFP profile support
- The system uses fuzzy string matching for command recognition [30](#0-29) 
