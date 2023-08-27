import os
import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request
import requests
#from transcriber import Transcriber
from gtts import gTTS
from playsound import playsound
from characterai import PyCAI

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
client = PyCAI(os.getenv('CHARACTERAI_API_KEY'))



app = Flask(__name__)

@app.route("/")
def index():
    return render_template("recorder.html")

@app.route("/audio", methods=["POST"])
def audio():
    #Obtener audio grabado y transcribirlo
    audio = request.files.get("audio")
    audio.save("audio.mp3")
    audio_file = open("audio.mp3", "rb")
    #text = Transcriber().transcribe(audio)
    transcribed = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcribed.text)


    '''response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": "You are a foul-mouthed assistant."},
            {"role": "user", "content": transcribed.text}
        ],
    )
    result = ""
    for choice in response.choices:
        result += choice.message.content'''
    
    
    client.start()

    character_id = "oL2IzOD15_wBIP_o6NAWDwiVyAnzz_3aGLu9aU7i254"

    chat = client.chat.get_chat(character_id)

    participants = chat['participants']

    if not participants[0]['is_human']:
        tgt = participants[0]['user']['username']
    else:
        tgt = participants[1]['user']['username']


    message = transcribed.text
    data = client.chat.send_message(
        chat['external_id'], tgt, message
    )
    namec = data['src_char']['participant']['name']
    textoutput = data['replies'][0]['text']
    print(f"{namec}: {textoutput}")

    #tts = gTTS(result, lang='es', tld = 'com.mx')
    #tts.save("response.mp3")
    #playsound("response.mp3")

    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/oWAxZDx7w5VEj9dCyTzz"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_key
    }

    data = {
        "text": textoutput,
        "model_id": "eleven_multilingual_v1",
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.55
        }
    }
    response = requests.post(url, json=data, headers=headers, stream=True)

    with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    playsound("output.mp3")

    return {"result": "ok", "text": textoutput}
