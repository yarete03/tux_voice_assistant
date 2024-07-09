import speech_recognition as sr
from youtube_music_api_client import youtube_api_query
from gtts_speech_to_voice import text_to_speech
from pygame import mixer, init

youtube_music_patterns = ['pon música de', 'pon la canción', 'pon']
#tux_patters = ["hey tuxt", "itox", "hey tucson", "hey dux", "hey tux", "oye tux", "oye tuxt", "itunes", "hey tu", "oye tucson", "oye dux", "oye lux", "hey jux", "el tux", "oye tuc", "oye tú", "oye"]
voice_assistant_patters = ["alex", "alexa"]
init()
listening_sound = mixer.Sound("audio/mixkit-positive-interface-beep-221.wav")
error_sound = mixer.Sound("audio/error-8-206492.mp3")


for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{index} -> {name}")
    if "HyperX Cloud Flight S: USB Audio" in name:
        device_audio_index = index
        break

print(device_audio_index)


def record_audio():
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=device_audio_index)
    with mic as source:
        while True:
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=1)
                query = recognizer.recognize_google(audio, language="es-ES")
                query = query.lower()
                print(query)
                try:
                    if any(voice_assistant_patter in query for voice_assistant_patter in voice_assistant_patters):
                        listening_sound.play()
                        audio = recognizer.listen(source, phrase_time_limit=5, timeout=3)
                        query = recognizer.recognize_google(audio, language="es-ES")
                        print(query)
                        recognize_speech(query)
                except (sr.UnknownValueError, sr.exceptions.WaitTimeoutError):
                    error_sound.play()
            except (sr.UnknownValueError, sr.exceptions.WaitTimeoutError):
                pass


def recognize_speech(query):
    if any(youtube_music_pattern in query for youtube_music_pattern in youtube_music_patterns):
        query = next((query.replace(pattern, "") for pattern in youtube_music_patterns if pattern in query), query)
        text_to_speech(f"Vale, voy a intentar reproducir {query}")
        youtube_api_query(query)
    else:
        error_sound.play()


if __name__ == "__main__":
    audio = record_audio()
