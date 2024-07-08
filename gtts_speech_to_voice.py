from gtts import gTTS
from io import BytesIO
from pygame import mixer, time


def text_to_speech(text, language='es'):
    tts = gTTS(text=text, lang=language, slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    mixer.init()
    mixer.music.load(fp)
    mixer.music.play()
    while mixer.music.get_busy():
        time.Clock().tick(1)
