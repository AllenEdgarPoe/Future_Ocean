import argparse
import json
import os

parser = argparse.ArgumentParser()

parser.add_argument('--output_path', default=r'C:\Users\chsjk\PycharmProjects\Future_Ocean\result')
parser.add_argument('--final_vid_output_path', default=r'C:\Users\chsjk\PycharmProjects\Future_Ocean\result\final')
parser.add_argument('--log_output_path', default=r'C:\Users\chsjk\PycharmProjects\Future_Ocean\log')

parser.add_argument('--server_address', default='127.0.0.1:8189')

parser.add_argument('--image_workflow', default=r'C:\Users\chsjk\PycharmProjects\Future_Ocean\workflow\sample_image_api.json')
parser.add_argument('--video_workflow', default=r'C:\Users\chsjk\PycharmProjects\Future_Ocean\workflow\sample_video_api.json')

parser.add_argument('--sample_text_path', default=r'C:\Users\chsjk\PycharmProjects\Future_Ocean\data\sample_prompt.txt')  #sample image when image execution is not done
parser.add_argument('--sample_image_path', default=r'C:\Users\chsjk\PycharmProjects\Future_Ocean\data\sample_image.png')  #sample image when image execution is not done
parser.add_argument('--sample_video_path', default=r'C:\Users\chsjk\PycharmProjects\Future_Ocean\data\sample_video.mp4')  #sample image when image execution is not done

