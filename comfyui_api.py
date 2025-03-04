import re
import random
import os
import cv2
from base64 import b64encode
import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import sys
import socket
import cmd_args
import threading
sys.path.append('.')
args = cmd_args.parse_args()
server_address = args.server_address
client_id = str(uuid.uuid4())

class TimeoutException(Exception):
    pass

def readImage(path):
    img = cv2.imread(path)
    retval, buffer = cv2.imencode('.png', img)
    b64img = b64encode(buffer).decode("utf-8")
    return b64img

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())


def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            continue #previews are binary data
    history = get_history(prompt_id)
    return history[prompt_id]


def check_file_exists(file_path):
    if os.path.exists(file_path):
        return True
    else:
        raise FileNotFoundError(f'The file {file_path} does not exists. ')

def randomize_seed(prompt, node_id):
    prompt[node_id]['inputs']['seed'] = random.randint(1,4294967294)
    return prompt


def generate_image(workflow_path, image_output_path, text_prompt):
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            prompt = json.load(f)

        # preprocess article
        text_prompt = re.sub(r'^\d+\s*\.', '', text_prompt)
        text_prompt = text_prompt.rstrip()

        # put input path
        prompt['6']['inputs']['text'] = text_prompt

        # save file
        prompt['98']['inputs']['path'] = image_output_path
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id), ping_interval=None)

        # ws_url = f'ws://{server_address}/ws?clientId={client_id}'
        # ws = websocket.create_connection(ws_url, timeout=timeout)
        history = get_images(ws, prompt)
        return

    except (websocket.WebSocketTimeoutException, socket.timeout) as e:
        raise TimeoutException()

    except Exception as e:
        raise e
def generate_sample_image(workflow_path, image_output_path, text_prompt):
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            prompt = json.load(f)

        # preprocess article
        text_prompt = re.sub(r'^\d+\s*\.', '', text_prompt)
        text_prompt = text_prompt.rstrip()

        randomize_seed(prompt, '3')
        # put input path
        prompt['6']['inputs']['text'] = text_prompt

        # save file
        prompt['14']['inputs']['path'] = image_output_path
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id), ping_interval=None)
        # ws_url = f'ws://{server_address}/ws?clientId={client_id}'
        # ws = websocket.create_connection(ws_url, timeout=timeout)
        history = get_images(ws, prompt)
        # file_name = history['outputs']['13']['images'][0]['filename']

        return image_output_path

    except (websocket.WebSocketTimeoutException, socket.timeout) as e:
        raise TimeoutException()

    except Exception as e:
        raise e

def generate_video(workflow_path, text_prompt, image_path, video_save_path):
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            prompt = json.load(f)

        prompt['22']['inputs']['positive_prompt'] = text_prompt
        # put image input path
        prompt['36']['inputs']['image'] = image_path

        # set video path
        prompt['14']['inputs']['filename_prefix'] = video_save_path

        # ws_url = f'ws://{server_address}/ws?clientId={client_id}'
        # ws = websocket.create_connection(ws_url, timeout=timeout)
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
        history = get_images(ws, prompt)
        return


    except (websocket.WebSocketTimeoutException, socket.timeout) as e:
        raise TimeoutException()

    except Exception as e:
        raise e

def generate_sample_video(workflow_path, text_prompt, image_path, video_save_path):
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            prompt = json.load(f)

        prompt['7']['inputs']['text'] = text_prompt
        # put image input path
        prompt['22']['inputs']['image'] = image_path

        # set video path
        prompt['21']['inputs']['filename_prefix'] = video_save_path

        # ws = websocket.WebSocket()
        ws_url = f'ws://{server_address}/ws?clientId={client_id}'
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
        history = get_images(ws, prompt)
        return

    except (websocket.WebSocketTimeoutException, socket.timeout) as e:
        raise TimeoutException()

    except Exception as e:
        raise e



if __name__ == '__main__':
    # generate_image('./workflow/image_api.json', 'Paris, beautiful sea, France', 1)
    # generate_video(r'C:\Users\xorbis\PycharmProjects\workflow\video_api.json', ['C:\\info\\1.png', 'C:\\info\\2.png', 'C:\\info\\2.png', 'C:\\info\\3.png', 'C:\\info\\4.png', 'C:\\info\\5.png'], '.')
    article_path = r'C:\info\prompt.txt'
    article_list = [line for line in open(article_path, 'r', encoding='utf-8').readlines()[1:] if len(line)>1]

    for idx, article in enumerate(article_list):
        generate_image(r'C:\Users\xorbis\PycharmProjects\workflow\image_api.json', article, idx)

