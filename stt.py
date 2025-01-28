import speech_recognition as sr
from pydub import AudioSegment
import os
import uuid

def speech_to_text_ogg(ogg_file_path):
    recognizer = sr.Recognizer()
    temp_wav = f"temp_{uuid.uuid4().hex}.wav"

    try:
        # Конвертация OGG в WAV с настройкой параметров
        audio = AudioSegment.from_ogg(ogg_file_path)
        if len(audio) < 500:
            print("Аудио слишком короткое")
            return None
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(temp_wav, format="wav")

        # Распознавание речи
        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            print(f"Распознано: {text}")
            return text

    except sr.UnknownValueError:
        print("Google не распознал речь")
        return None
    except sr.RequestError as e:
        print(f"Ошибка API: {e}")
        return None
    except Exception as e:
        print(f"Общая ошибка: {e}")
        return None
    finally:
        # Удаление временного файла
        if os.path.exists(temp_wav):
            os.remove(temp_wav)