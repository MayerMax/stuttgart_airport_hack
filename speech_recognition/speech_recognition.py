import os
import wave
from pydub import AudioSegment
from gtts import gTTS
import json

# google api
from google.cloud import speech
from google.cloud import storage
from google.cloud.speech import enums
from google.cloud import texttospeech
from google.protobuf.json_format import MessageToJson

bucket_name = "hack-stuttgart-bucket"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key_to_cloud.json"

stt_client = speech.SpeechClient().from_service_account_json("key_to_cloud.json")
tts_client = texttospeech.TextToSpeechClient()


def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate,channels


def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")


def mp3_to_wav(audio_file_name):
    if audio_file_name.split('.')[1] == 'mp3':
        sound = AudioSegment.from_mp3(audio_file_name)
        audio_file_name = audio_file_name.split('.')[0] + '.wav'
        sound.export(audio_file_name, format="wav")


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


def delete_blob(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()


def audio_to_text(path_to_file):
    frame_rate, channels = frame_rate_channel(path_to_file)
    if channels > 1:
        stereo_to_mono(path_to_file)

    filename = os.path.basename(path_to_file)
    upload_blob(bucket_name, path_to_file, filename)
    gcs_uri = 'gs://' + bucket_name + '/' + filename
    config = {'encoding': enums.RecognitionConfig.AudioEncoding.LINEAR16,
              'sample_rate_hertz': frame_rate,
              'language_code': "en-US"}
    audio_file = {'uri': gcs_uri}
    text = stt_client.recognize(config, audio_file)
    delete_blob(bucket_name, filename)

    json_text = MessageToJson(text)

    result_text = json.loads(json_text)["results"][0]["alternatives"][0]["transcript"]

    return result_text


def text_to_audio(text_data, path_to_file):
    text_to_speech = gTTS(text_data)
    text_to_speech.save(path_to_file)


if __name__ == '__main__':
    text_from_audio = audio_to_text("resources/test.wav")
    text_to_audio(text_from_audio, "awesome_audio.mp3")
