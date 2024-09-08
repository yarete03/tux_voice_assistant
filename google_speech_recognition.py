import speech_recognition as sr
from youtube_music_api_client import youtube_api_query
from gtts_speech_to_voice import text_to_speech
from pygame import mixer, init
from subprocess import run
import logging
from whatsapp_sender import whatsapp_cookie_maker, whatsapp_sender
from webbrowser import open as webbroser_open


logging.basicConfig(filename="logfilename.log", level=logging.DEBUG)

next_song_patterns = ['salta la canción', 'pon la siguiente canción']
previous_song_patterns = ['pon la canción anterior', 'pon la canción de antes', 'pon la de antes', "pon la anterior canción"]
youtube_music_patterns = ['pon música de', 'pon la canción', 'ponme', 'pon']
who_made_song_patterns = ['de quién es', 'quién hizo', 'quién canta']
what_song_patterns = ['cómo se llama', 'cuál es el nombre de', 'qué canción es esta']
whatsapp_send_patterns = ['enviar un whatsapp a', 'envía un whatsapp a', 'envíale un whatsapp a', 'manda un whatsapp a', 'mandale un whatsapp a', 'escribele un whatsapp a', 'escribe un whatsapp a']


#tux_patters = ["hey tuxt", "itox", "hey tucson", "hey dux", "hey tux", "oye tux", "oye tuxt", "itunes", "hey tu", "oye tucson", "oye dux", "oye lux", "hey jux", "el tux", "oye tuc", "oye tú", "oye"]
voice_assistant_patters = ["alex", "alexa"]


init()
listening_sound = mixer.Sound("audio/mixkit-positive-interface-beep-221.wav")
error_sound = mixer.Sound("audio/error-8-206492.mp3")


def record_audio():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold=0.5
    mic = sr.Microphone()
    with mic as source:
        while True:
            try:
                audio = recognizer.listen(source)
                query = recognizer.recognize_google(audio, language="es-ES")
                query = query.lower()
                try:
                    if any(voice_assistant_patter in query for voice_assistant_patter in voice_assistant_patters):
                        listening_sound.play()
                        audio = recognizer.listen(source, timeout=3)
                        query = recognizer.recognize_google(audio, language="es-ES")
                        query = query.lower()
                        print(query)
                        recognize_speech(query, source, recognizer)
                except sr.UnknownValueError as e:
                    print(e, "Uknown vaule error", query)
                    error_sound.play()
                except sr.exceptions.WaitTimeoutError as e:
                    print(e, "Wait Timeout Error")
                    error_sound.play()
            except (sr.UnknownValueError, sr.exceptions.WaitTimeoutError):
                pass


def recognize_speech(query, source, recognizer):
    if any(next_song_pattern in query for next_song_pattern in next_song_patterns):
        run(['/usr/bin/playerctl', 'next'])
    elif any(previous_song_pattern in query for previous_song_pattern in previous_song_patterns):
        actual_song = run(['/home/yaret/polybar-scripts/polybar-scripts/player-mpris-simple/player-mpris-simple.sh'],  capture_output=True).stdout
        run(['/usr/bin/playerctl', 'previous'])
        next_song = run(['/home/yaret/polybar-scripts/polybar-scripts/player-mpris-simple/player-mpris-simple.sh'],  capture_output=True).stdout
        if actual_song == next_song:
            run(['/usr/bin/playerctl', 'previous'])
    elif any(youtube_music_pattern in query for youtube_music_pattern in youtube_music_patterns):
        query = next((query.replace(pattern, "") for pattern in youtube_music_patterns if pattern in query), query)
        text_to_speech(f"Vale, voy a intentar reproducir {query}")
        youtube_url = youtube_api_query(query)
        webbroser_open(youtube_url, new=0)
        #run(['/snap/bin/opera', youtube_url])
    elif any(who_made_song_pattern in query for who_made_song_pattern in who_made_song_patterns) or any(what_song_pattern in query for what_song_pattern in what_song_patterns):
        artist = run(['/usr/bin/playerctl', 'metadata', 'artist'], capture_output=True).stdout.decode()
        song = run(['/usr/bin/playerctl', 'metadata', 'title'], capture_output=True).stdout.decode()
        text_to_speech(f'Estás escuchando {song}, de {artist}')
    elif any(whatsapp_send_pattern in query for whatsapp_send_pattern in whatsapp_send_patterns):
        receiver = next((query.replace(whatsapp_send_pattern, "") for whatsapp_send_pattern in whatsapp_send_patterns if
                         whatsapp_send_pattern in query), query)
        text_to_speech(f'¿Qué le quieres decir a {receiver}?')
        listening_sound.play()
        audio = recognizer.listen(source)
        message = recognizer.recognize_google(audio, language="es-ES")
        text_to_speech(f'{message}. ¿Enviar o cancelar?')
        listening_sound.play()
        audio = recognizer.listen(source)
        confirmation = recognizer.recognize_google(audio, language="es-ES")
        if confirmation == "enviar":
            session = whatsapp_sender(receiver, message)
            if not session:
                text_to_speech(f"Parece que no has iniciado sesión en whatsapp.")
                whatsapp_cookie_maker()
                whatsapp_sender(receiver, message)
            text_to_speech("Enviado")
        else:
            text_to_speech("Cancelado")

    else:
        error_sound.play()


if __name__ == "__main__":
    record_audio()
