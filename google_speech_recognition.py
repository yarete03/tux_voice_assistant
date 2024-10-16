import speech_recognition as sr
import phone_call_manager
from dbus import exceptions as dbus_exception
from time import sleep
from Levenshtein import distance
from youtube_music_api_client import youtube_api_query
from gtts_speech_to_voice import text_to_speech
from pygame import mixer, init
from subprocess import run
from whatsapp_sender import whatsapp_cookie_maker, whatsapp_sender
from webbrowser import open as webbroser_open
from multiprocessing import Process


next_song_patterns = ['salta la canción', 'pon la siguiente canción']
previous_song_patterns = ['pon la canción anterior', 'pon la canción de antes', 'pon la de antes',
                          "pon la anterior canción"]
pause_patterns = ['para la canción', 'para la música']
play_patterns = ['dale al', 'pon la música', 'vuelve a poner la música']
youtube_music_patterns = ['pon música de', 'pon la canción', 'ponme', 'pon']
who_made_song_patterns = ['de quién es', 'quién hizo', 'quién canta']
what_song_patterns = ['cómo se llama', 'cuál es el nombre de', 'qué canción es esta']
whatsapp_send_patterns = ['enviar un whatsapp a', 'envía un whatsapp a', 'envíale un whatsapp a', 'manda un whatsapp a',
                          'mandale un whatsapp a', 'escribele un whatsapp a', 'escribe un whatsapp a']
call_pattern = 'llama a'


# tux_patters = ["hey tuxt", "itox", "hey tucson", "hey dux", "hey tux", "oye tux", "oye tuxt", "itunes", "hey tu",
# "oye tucson", "oye dux", "oye lux", "hey jux", "el tux", "oye tuc", "oye tú", "oye"]
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
                audio = recognizer.listen(source, timeout=1)
                query = recognizer.recognize_google(audio, language="es-ES")
                query = query.lower()
                try:
                    if any(voice_assistant_patter in query for voice_assistant_patter in voice_assistant_patters):
                        listening_sound.play()
                        audio = recognizer.listen(source, timeout=3)
                        query = recognizer.recognize_google(audio, language="es-ES")
                        query = query.lower()
                        print(query)
                        recognize_speech(query)
                except sr.UnknownValueError as e:
                    print(e, "Uknown vaule error", query)
                    error_sound.play()
                except sr.exceptions.WaitTimeoutError as e:
                    print(e, "Wait Timeout Error")
                    error_sound.play()
            except (sr.UnknownValueError, sr.exceptions.WaitTimeoutError):
                pass


# 'pass' statement used in each 'if' statement to not perform further checks for that query
def playerctl_management(query):
    if any(next_song_pattern in query for next_song_pattern in next_song_patterns):
        run(['/usr/bin/playerctl', 'next'])
        return True
    elif any(previous_song_pattern in query for previous_song_pattern in previous_song_patterns):
        actual_song = run(['/home/yaret/polybar-scripts/polybar-scripts/player-mpris-simple/player-mpris-simple.sh'],
                          capture_output=True).stdout
        run(['/usr/bin/playerctl', 'previous'])
        next_song = run(['/home/yaret/polybar-scripts/polybar-scripts/player-mpris-simple/player-mpris-simple.sh'],
                        capture_output=True).stdout
        if actual_song == next_song:
            run(['/usr/bin/playerctl', 'previous'])
        return True
    elif any(pause_pattern in query for pause_pattern in pause_patterns):
        run(['/usr/bin/playerctl', 'pause'])
        return True
    elif any(play_pattern in query for play_pattern in play_patterns):
        run(['/usr/bin/playerctl', 'play'])
        return True
    elif (any(who_made_song_pattern in query for who_made_song_pattern in who_made_song_patterns) or
          any(what_song_pattern in query for what_song_pattern in what_song_patterns)):
        artist = run(['/usr/bin/playerctl', 'metadata', 'artist'], capture_output=True).stdout.decode()
        song = run(['/usr/bin/playerctl', 'metadata', 'title'], capture_output=True).stdout.decode()
        text_to_speech(f'Estás escuchando {song}, de {artist}')
        return True

    return False


# TODO: Whatsapp ban you when you try to run a browser on headless mode
def whatsapp_management(query, source, recognizer):
    if any(whatsapp_send_pattern in query for whatsapp_send_pattern in whatsapp_send_patterns):
        receiver = next((query.replace(whatsapp_send_pattern, "") for whatsapp_send_pattern in whatsapp_send_patterns
                         if whatsapp_send_pattern in query), query)
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
        return True

    return False


def youtube_music_manager(query):
    if any(youtube_music_pattern in query for youtube_music_pattern in youtube_music_patterns):
        query = next((query.replace(pattern, "") for pattern in youtube_music_patterns if pattern in query), query)
        text_to_speech(f"Vale, voy a intentar reproducir {query}")
        youtube_url = youtube_api_query(query)
        webbroser_open(youtube_url, new=0)
        return True

    return False


def call_maker_manager(query):
    if call_pattern in query:
        modem_path = phone_call_manager.get_modem_path()
        contact_name = query.replace(call_pattern, "")
        contact_name = contact_name.replace(' ', '')
        contacts = phone_call_manager.read_vcf()
        closest_contact = min(contacts, key=lambda contact: distance(contact_name,
                                                                  contact.fn.value.lower()))
        closest_name = closest_contact.fn.value.lower()
        closest_phone_number = closest_contact.tel.value.replace(' ', '')
        text_to_speech(f'Llamando a {closest_name}')
        try:
            phone_call_manager.caller(modem_path, closest_phone_number)
        except dbus_exception.DBusException:
            error_sound.play()
            text_to_speech('Parece que no tienes el teléfono conectado. Prueba de nuevo tras conectarlo.')
        return True

    return False


def recognize_speech(query):
    if playerctl_management(query):
        return
    if youtube_music_manager(query):
        return 
    # whatsapp_management(query, source, recognizer)
    if call_maker_manager(query):
        return
    error_sound.play()


def call_manager():
    modem_path = get_modem_path()
    while True:
        try:
            sleep(1)
            phone_call_manager.call_management(modem_path)
        except dbus_exception.DBusException:
            modem_path = get_modem_path()
            sleep(30)


def get_modem_path():
    modem_path = phone_call_manager.get_modem_path()
    while modem_path is None:
        modem_path = phone_call_manager.get_modem_path()
        sleep(30)
    return modem_path


def main():
    process_hang_up_call_manager = Process(target=call_manager)
    process_hang_up_call_manager.start()
    record_audio()


if __name__ == "__main__":
    main()
