import argparse
import json
import os

def parse_args():
    base_dir = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser()

    # comfy server address
    parser.add_argument('--server_address', default='127.0.0.1')
    parser.add_argument('--port', default=8188)

    # save directory
    parser.add_argument('--output_path', default=os.path.join(base_dir, 'result'))
    parser.add_argument('--final_vid_output_path', default=os.path.join(base_dir, 'final_result'))
    parser.add_argument('--data_path', default=os.path.join(base_dir, 'data'))

    # comfyui directory
    parser.add_argument('--ComfyUI_path', default=r'C:\Users\chsjk\PycharmProjects\ComfyUI_windows_portable')

    # workflow path
    parser.add_argument('--image_workflow', default=os.path.join(base_dir, 'workflow', 'sample_image_api.json'))
    parser.add_argument('--video_workflow', default=os.path.join(base_dir, 'workflow', 'sample_video_api.json'))

    # samples
    parser.add_argument('--sample_text_path', default=os.path.join(base_dir, 'data', 'sample_prompt.txt'))
    parser.add_argument('--sample_image_path', default=os.path.join(base_dir, 'data', 'sample_image.png'))
    parser.add_argument('--sample_video_path', default=os.path.join(base_dir, 'data', 'sample_video.mp4'))

    # number of prompts to generate
    parser.add_argument('--prompt_num', default=3)

    args,_ = parser.parse_known_args()
    return args