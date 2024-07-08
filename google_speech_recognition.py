import speech_recognition as sr
from youtube_music_api_client import youtube_api_query
from gtts_speech_to_voice import text_to_speech
from pygame import mixer,init

recognizer = sr.Recognizer()
youtube_music_patterns = ['pon música de', 'pon la canción', 'pon']
tux_patters = ["hey tuxt", "hey tux", "itunes"]
init()
listening_sound = mixer.Sound("audio/mixkit-positive-interface-beep-221.wav")
error_sound = mixer.Sound("audio/error-8-206492.mp3")


def record_audio():
    with sr.Microphone() as source:
        while True:
            try:
                audio = recognizer.listen(source)
                query = recognizer.recognize_google(audio, language="es-ES")
                query = query.lower()
                if any(tux_patter in query for tux_patter in tux_patters):
                    listening_sound.play()
                    audio = recognizer.listen(source)
                    query = recognizer.recognize_google(audio, language="es-ES")
                    recognize_speech(query)
            except sr.UnknownValueError:
                pass


def recognize_speech(query):
    try:
        if any(youtube_music_pattern in query for youtube_music_pattern in youtube_music_patterns):
            query = next((query.replace(pattern, "") for pattern in youtube_music_patterns if pattern in query), query)
            text_to_speech(f"Vale, voy a intentar reproducir {query}")
            youtube_api_query(query)
        else:
            error_sound.play()

    except sr.UnknownValueError:
        text_to_speech("Lo siento, no te he entendido")
    except sr.RequestError:
        text_to_speech("Ha habido un problema mientras se procesaba la solicitud. Por favor, intentelo de nuevo")


if __name__ == "__main__":
    audio = record_audio()
