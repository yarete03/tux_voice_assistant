from dbus import exceptions as dbus_exception
from time import sleep
from Levenshtein import distance
from youtube_music_api_client import youtube_api_query
from gtts_speech_to_voice import text_to_speech
from pygame import mixer, init
from subprocess import run, Popen
from whatsapp_sender import whatsapp_cookie_maker, whatsapp_sender
from webbrowser import open as webbroser_open
from multiprocessing import Process
from datetime import datetime
from api_token import porcupine_api_key
from os import remove
from fuzzywuzzy import fuzz
from faster_whisper import WhisperModel
import record_and_transcribe_whisper_custom_exceptions as custom_exceptions
import phone_call_manager
import pyaudio
import struct
import pvporcupine
import wave
import time
import numpy as np

command_patters = {
    "next_song_patterns": ['salta la canción', 'pon la siguiente canción'],
    "previous_song_patterns": ['pon la canción anterior', 'pon la canción de antes', 'pon la de antes',
                              "pon la anterior canción"],
    "pause_patterns": ['para la canción', 'para la música'],
    "play_patterns": ['dale al', 'pon la música', 'vuelve a poner la música'],
    "youtube_music_patterns": ['ponme música de', 'pon música de', 'pon la canción', 'ponme', 'pon'],
    "who_made_song_patterns": ['de quién es', 'quién hizo', 'quién canta'],
    "what_song_patterns": ['cómo se llama', 'cuál es el nombre de', 'qué canción es esta', 'cuál es esta canción'],
    "whatsapp_send_patterns": ['enviar un whatsapp a', 'envía un whatsapp a', 'envíale un whatsapp a', 'manda un whatsapp a',
                              'mandale un whatsapp a', 'escribele un whatsapp a', 'escribe un whatsapp a'],
    "block_screen_patterns": ['bloquea la', 'bloquea el'],
    "power_off_pattern": 'apaga el',
    "call_pattern": 'llama a',
    "hour_patterns": ['qué hora es', 'que hora es'],
    "hang_out_pattern": "cuelga",
}

init()
listening_sound = mixer.Sound("audio/mixkit-positive-interface-beep-221.wav")
error_sound = mixer.Sound("audio/error-8-206492.mp3")


def record_audio():
    model = WhisperModel("turbo", device="cuda", compute_type="float16")
    porcupine = pvporcupine.create(
        access_key=porcupine_api_key,
        keyword_paths=['./porcupine/asistente_es_linux_v3_0_0.ppn'],
        model_path='./porcupine/porcupine_params_es.pv',
        library_path='./porcupine/libpv_porcupine.so'
    )

    pa = pyaudio.PyAudio()

    # Open audio stream matching Porcupine's specs
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    print("Listening for the Porcupine wake word...")

    try:
        while True:
            # Read a frame of audio
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            # Convert to int16
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            # Process with Porcupine
            result = porcupine.process(pcm)
            if result >= 0:
                try:
                    # Wake word detected!
                    listening_sound.play()
                    print("Wake up word: HIT")
                    query = record_and_transcribe_whisper(model)
                    query = query.lower()
                    print(f"Query: {query}")
                    recognize_speech(query)
                except custom_exceptions.SilenceTimeoutExceeded:
                    error_sound.play()
    except KeyboardInterrupt:
        print("Porcupine listener stopped by user.")
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

    return True


def record_and_transcribe_whisper(
        model,
        first_sound_timeout: float = 3.0,  # Tiempo máximo esperando la primera voz
        silence_timeout: float = 1,  # Se detiene tras 0.5s de silencio continuo (una vez detectada voz)
        sample_rate: int = 16000,
        chunk_size: int = 1024,
        silence_threshold: int = 200,  # Umbral RMS para detectar silencio/sonido
) -> str:
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk_size
    )

    frames = []
    start_time = time.time()
    spoken = False
    silent_frames_count = 0
    required_silent_frames = int(silence_timeout * sample_rate / chunk_size)

    while True:
        data = stream.read(chunk_size, exception_on_overflow=False)
        frames.append(data)
        # Calculate RMS using our NumPy approach
        rms = calculate_rms(data, sample_width=2)
        if not spoken:
            # Still waiting for first voice
            if rms > silence_threshold:
                spoken = True
                silent_frames_count = 0
                print("Voz detectada; grabando hasta 0.5s de silencio...")
            else:
                # Check if we've exceeded the 3s wait
                if time.time() - start_time >= first_sound_timeout:
                    print("Timeout: no se detectó voz en 3s.")
                    # Clean up
                    stream.stop_stream()
                    stream.close()
                    pa.terminate()
                    raise custom_exceptions.SilenceTimeoutExceeded("Timeout has been reached")
        else:
            # Once we've detected voice, record until 0.5s of silence
            if rms < silence_threshold:
                silent_frames_count += 1
            else:
                silent_frames_count = 0
            if silent_frames_count >= required_silent_frames:
                break

    # Clean up PyAudio
    stream.stop_stream()
    stream.close()
    pa.terminate()

    # 3) Write the recorded audio to a temporary WAV
    tmp_wav = "temp_whisper.wav"
    wf = wave.open(tmp_wav, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

     # 4) Transcribing audio with whisper
    segments, info = model.transcribe(
        tmp_wav,
        language="es",
        initial_prompt="Transcripción de comando de voz en español."
                       f"Posibles comandos: {', '.join(', '.join(single_array) if type(single_array) is list else '' for single_array in command_patters.values())}",
        temperature=0.2,  # More deterministic output
        compression_ratio_threshold=2.4,  # Filter noisy audio
    )
    for segment in segments:
        text = segment.text
    remove(tmp_wav)
    return text


def calculate_rms(data: bytes, sample_width=2) -> float:
    """
    Computes RMS for 16-bit mono PCM data using NumPy.

    Args:
        data: Raw audio bytes.
        sample_width: Number of bytes per sample (2 for 16-bit).
    Returns:
        A float representing the RMS amplitude.
    """
    # Number of 16-bit samples
    num_samples = len(data) // sample_width

    # Unpack bytes to Python integers: little-endian (<), signed short (h).
    # e.g.: "<{num_samples}h"
    format_str = "<{}h".format(num_samples)
    samples = struct.unpack(format_str, data)

    # Convert to NumPy array, then compute RMS
    samples_array = np.array(samples, dtype=np.int16)
    # Cast to float64 for numerical stability in mean of squares
    return float(np.sqrt(np.mean(samples_array.astype(np.float64) ** 2)))


def playerctl_management(query):
    if fuzzy_match(command_patters["next_song_patterns"], query):
        run(['/usr/bin/playerctl', 'next'])
        return True
    elif fuzzy_match(command_patters["previous_song_patterns"], query):
        actual_song = run(['/usr/bin/playerctl', 'metadata', 'title'], capture_output=True).stdout
        run(['/usr/bin/playerctl', 'previous'])
        next_song = run(['/usr/bin/playerctl', 'metadata', 'title'], capture_output=True).stdout
        if actual_song == next_song:
            run(['/usr/bin/playerctl', 'previous'])
        return True
    elif fuzzy_match(command_patters["pause_patterns"], query):
        run(['/usr/bin/playerctl', 'pause'])
        return True
    elif fuzzy_match(command_patters["play_patterns"], query):
        run(['/usr/bin/playerctl', 'play'])
        return True
    elif (fuzzy_match(command_patters["who_made_song_patterns"], query) or
          fuzzy_match(command_patters["what_song_patterns"], query)):
        artist = run(['/usr/bin/playerctl', 'metadata', 'artist'], capture_output=True).stdout.decode()
        song = run(['/usr/bin/playerctl', 'metadata', 'title'], capture_output=True).stdout.decode()
        text_to_speech(f'Estás escuchando {song}, de {artist}')
        return True

    return False


# TODO: Whatsapp ban you when you try to run a browser on headless mode
def whatsapp_management(query, source, recognizer):
    if fuzzy_match(command_patters["whatsapp_send_patterns"], query):
        receiver = next((query.replace(whatsapp_send_pattern, "") for whatsapp_send_pattern in command_patters["whatsapp_send_patterns"]
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
    if fuzzy_match(command_patters["youtube_music_patterns"], query):
        query = next((query.replace(pattern, "") for pattern in command_patters["youtube_music_patterns"] if pattern in query), query)
        text_to_speech(f"Vale, voy a intentar reproducir {query}")
        youtube_url = youtube_api_query(query)
        if youtube_url:
            run(['/usr/bin/playerctl', 'pause'])
            webbroser_open(youtube_url, new=0)
        else:
            text_to_speech(f"No se ha podido reproducir la canción solicitada. Pruebe en otro momento")
        return True

    return False


def call_maker_manager(query):
    if fuzzy_match(command_patters["call_pattern"], query):
        modem_path = phone_call_manager.get_modem_path()
        contact_name = query.replace(command_patters["call_pattern"], "").strip()
        contacts = phone_call_manager.read_vcf()
        closest_contact = min(contacts, key=lambda contact: distance(contact_name, contact.fn.value.lower()))
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


def display_management(query):
    if fuzzy_match(command_patters["block_screen_patterns"], query):
        Popen(['/usr/bin/i3lock-fancy'])
        return True
    elif fuzzy_match(command_patters["power_off_pattern"], query):
        run(['/usr/sbin/poweroff'])
        return True
    return False


def date_time_management(query):
    if fuzzy_match(command_patters["hour_patterns"], query):
        current_time = datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        text_to_speech(f'Son las {hour} y {minute}')
        return True


def hang_out_management(query):
    if fuzzy_match(command_patters["hang_out_pattern"], query):
        try:
            modem_path = phone_call_manager.get_modem_path()
            if modem_path is None:
                text_to_speech('No se detecta la llamada a colgar')
            else:
                if not phone_call_manager.hang_out_call(modem_path):
                    text_to_speech('No se detecta la llamada a colgar')
                else:
                    text_to_speech('Llamada colgada')
        except dbus_exception.DBusException:
            text_to_speech('No se detecta la llamada a colgar')
        return True

    
def recognize_speech(query):
    if playerctl_management(query):
        return
    if youtube_music_manager(query):
        return
    # whatsapp_management(query, source, recognizer)
    if call_maker_manager(query):
        return
    if display_management(query):
        return
    if date_time_management(query):
        return
    if hang_out_management(query):
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


def fuzzy_match(patterns, query, threshold=80):
    if isinstance(patterns, str):
        patterns = [patterns]
    return any(fuzz.partial_ratio(pattern, query) >= threshold for pattern in patterns)


def main():
    while True:
        if not run(["/usr/bin/pactl", "info"], text=False, capture_output=False).returncode:
            try:
                process_hang_up_call_manager = Process(target=call_manager)
                process_hang_up_call_manager.start()
                record_audio()
            except OSError:
                process_hang_up_call_manager.terminate()
                sleep(1)
        else:
            sleep(1)


if __name__ == "__main__":
    main()
