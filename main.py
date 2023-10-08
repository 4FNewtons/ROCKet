from flask import Flask, request, render_template, send_file, Response, jsonify
import os
import requests
import json
import base64
import flask
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def asticaAPI(endpoint, payload, timeout):
  response = requests.post(endpoint,
                           data=json.dumps(payload),
                           timeout=timeout,
                           headers={
                               'Content-Type': 'application/json',
                           })
  if response.status_code == 200:
    return response.json()
  else:
    return {'status': 'error', 'error': 'Failed to connect to the API.'}


def img_to_text(asticaAPI_input):
  asticaAPI_key = '886F8EC6-60A6-4FEB-8068-62EF9F7BE7C619E1B15B-B3B6-4C6F-9CFA-B34C1D41B477'
  asticaAPI_visionParams = 'gpt, describe, describe_all, objects, faces'
  asticaAPI_modelVersion = '2.1_full'
  asticaAPI_gpt_prompt = ''
  asticaAPI_prompt_length = 95
  asticaAPI_timeout = 60
  asticaAPI_endpoint = 'https://vision.astica.ai/describe'
  asticaAPI_payload = {
      'tkn': asticaAPI_key,
      'modelVersion': asticaAPI_modelVersion,
      'input': asticaAPI_input,
      'visionParams': asticaAPI_visionParams,
      'gpt_prompt': asticaAPI_gpt_prompt,
      'prompt_length': asticaAPI_prompt_length
  }
  response = requests.post(asticaAPI_endpoint,
                           data=json.dumps(asticaAPI_payload),
                           timeout=asticaAPI_timeout,
                           headers={
                               'Content-Type': 'application/json',
                           })
  if response.status_code == 200:
    return response.json()['caption_GPTS']
    print(response.json()['caption_GPTS'])
  else:
    print('Failed to connect to the API.')


def text_to_speech(text, text_name):
  asticaAPI_key = '886F8EC6-60A6-4FEB-8068-62EF9F7BE7C619E1B15B-B3B6-4C6F-9CFA-B34C1D41B477'
  asticaAPI_timeout = 10 # in seconds.
  asticaAPI_endpoint = 'https://voice.astica.ai/speak'
  asticaAPI_modelVersion = '1.0_full'
  
  asticaAPI_voiceid = 5;
  asticaAPI_input = text
  asticaAPI_lang = 'en-US'
  
  asticaAPI_outputFile = f'outputs/{text_name}.wav'
  asticaAPI_outputPlayback = False
  asticaAPI_payload = {
      'tkn': asticaAPI_key,
      'modelVersion': asticaAPI_modelVersion,
      'input': asticaAPI_input,
      'voice': asticaAPI_voiceid,
      'lang': asticaAPI_lang,
  }
  asticaAPI_result = asticaAPI(asticaAPI_endpoint, asticaAPI_payload, asticaAPI_timeout)
  # print(asticaAPI_result)
  # print('\nastica API Output:')
  # print(json.dumps(asticaAPI_result, indent=4))
  # print('=================')
  # Handle asticaAPI response
  if 'status' in asticaAPI_result:
      # Output Error if exists
      if asticaAPI_result['status'] == 'error':
          print('Output:\n', asticaAPI_result['error'])
      # Output Success if exists
      if asticaAPI_result['status'] == 'success':
          print("Success")
  
          #handle wav buffer
          wavData = bytes(asticaAPI_result['wavBuffer']['data'])
  
          #save wav file
          with open(asticaAPI_outputFile, 'wb') as f:
              f.write(wavData)
  
          if asticaAPI_outputPlayback:
              wav_array = np.frombuffer(wavData, dtype=np.int16)
              fs = 16000
              sd.play(wav_array, fs)
              sd.wait()
  
  else:
      print('Invalid response')

if not os.path.exists(UPLOAD_FOLDER):
  os.makedirs(UPLOAD_FOLDER)


def get_image_base64_encoding(image_path: str) -> str:
  with open(image_path, 'rb') as file:
    image_data = file.read()
  image_extension = os.path.splitext(image_path)[1]
  base64_encoded = base64.b64encode(image_data).decode('utf-8')
  return f"data:image/{image_extension[1:]};base64,{base64_encoded}"


@app.route('/speech', methods=['POST'])
def speech():
  image64 = None
  image = request.files['image']
  filename = os.path.join(UPLOAD_FOLDER, image.filename)
  image.save(filename)
  image64 = get_image_base64_encoding('uploads/' + image.filename)
  convert_to_text = img_to_text(image64)
  # convert_to_audio = text_to_speech(convert_to_text, image.filename)
  # music_file_path = open(f'outputs/{image.filename}.mp3', 'rb')
  print(convert_to_text)
  return jsonify({'message': convert_to_text})

@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

@app.route('/sound', methods=['GET'])
def sound():
  return render_template('sound.html')
    
app.run(host='0.0.0.0', port=81)