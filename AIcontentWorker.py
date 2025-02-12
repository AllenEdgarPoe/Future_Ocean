import os
import time
import cv2
import shutil
import subprocess
from logger_setup import set_logger, LogType

import cmd_args
from comfyui_api import generate_sample_image, generate_sample_video, TimeoutException, thread_execute


class AIContentWorker():
    def __init__(self, args):
        try:
            self.args = args
            set_logger(LogType.LT_INFO, 'Init AIContentWorker')
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def replace_with_sample(self, sample_path, save_path):
        shutil.copyfile(sample_path, save_path)
        return


    def make_image(self, textprompt, idx, timeout=1):
        try:
            img_filename = str(idx) +'.png'
            save_file_path = os.path.join(self.output_path, img_filename)

            max_retries = 3
            attempt = 0

            while max_retries>attempt:
                try:
                    args = (self.args.image_workflow, save_file_path, textprompt)
                    thread_execute(generate_sample_image, *args, timeout=timeout)

                    # save text prompt
                    text_filename = str(idx)+'.txt'
                    with open(os.path.join(self.output_path, text_filename), 'w', encoding='utf-8') as f:
                        f.write(textprompt)

                    set_logger(LogType.LT_INFO, f"[Image] #{str(idx+1)}: Successfully generated image for prompt : '{textprompt}'")
                    break

                except Exception as e:
                    attempt+=1
                    set_logger(LogType.LT_WARNING, f'[Image] #{str(idx+1)}: {str(e)}')
                    time.sleep(1)

            # If all retires fail, use the sample image
            if attempt >= max_retries:
                set_logger(LogType.LT_EXCEPTION, f'[Image] #{str(idx+1)}: Failed to generate image after {max_retries} attempts.')
                try:
                    self.replace_with_sample(self.args.sample_image_path, save_file_path)
                    set_logger(LogType.LT_INFO, f'[Image] #{str(idx+1)}: Sample image copied to {save_file_path} as a fallback')
                except Exception as e:
                    set_logger(LogType.LT_ERROR, f'[Image] #{str(idx+1)}: Failed to copy sample image to {save_file_path}: {str(e)}')
                    return None

            return save_file_path

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def make_video(self, idx, timeout=1):
        try:
            video_fname = str(idx)+'.mp4'
            image_fname = str(idx)+'.png'
            vid_file_path = os.path.join(self.output_path, video_fname)
            img_file_path = os.path.join(self.output_path, image_fname)

            max_retries = 3
            attempt = 0
            while attempt < max_retries:
                try:
                    args = (self.args.video_workflow, img_file_path, vid_file_path)
                    thread_execute(generate_sample_video, *args, timeout=timeout)
                    set_logger(LogType.LT_INFO, f'[Video] #{str(idx+1)}: Successfully generated video')
                    break

                except Exception as e:
                    attempt+=1
                    set_logger(LogType.LT_WARNING, f'[Video] #{str(idx+1)}: Error Occurred : {str(e)}')
                    time.sleep(1)

            if attempt >= max_retries:
                set_logger(LogType.LT_EXCEPTION, f'[Video] #{str(idx+1)}: Failed to generate video after {max_retries} attempts.')
                try:
                    self.replace_with_sample(self.args.sample_image_path, vid_file_path)
                    set_logger(LogType.LT_INFO,
                               f'[Video] #{str(idx + 1)}: Sample image copied to {vid_file_path} as a fallback')
                except Exception as e:
                    set_logger(LogType.LT_ERROR,
                               f'[Video] #{str(idx + 1)}: Failed to copy sample image to {vid_file_path}: {str(e)}')
                    return None

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, f'[Video] #{str(idx+1)}: str(e)')


    def get_vidpath_from_imgpath(self, img_path):
        try:
            base, ext = os.path.splitext(img_path)
            mp4_file_path = base + '.mp4'
            if os.path.isfile(mp4_file_path):
                return mp4_file_path
            else:
                return None
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))


    def generate_merged_video(self, img_paths, merge_methods, transition_time=3):
        try:
            output_path = os.path.join(self.args.final_vid_output_path, 'combined.mp4')
            video_paths = [self.get_vidpath_from_imgpath(img_path) for img_path in img_paths]
            if len(video_paths)<2:
                set_logger(LogType.LT_EXCEPTION, 'At least 2 videos are needed')

            video_time = 8 - transition_time

            ffmpeg_command = ['ffmpeg', '-y']
            filter_complex_command = ''

            for idx, video in enumerate(video_paths):
                ffmpeg_command.extend(['-i', video])
                time = (idx+1) * video_time
                if idx < len(video_paths)-1:
                    method = merge_methods[idx]
                else:
                    method = None

                if idx == 0:
                    if method == 'crossfade':
                        filter_complex_command += f'[{idx}:v][{idx + 1}:v]xfade=transition=fade:duration={transition_time}:offset={time}[v{idx + 1}];'
                    elif method == 'cut':
                        filter_complex_command += f'[{idx}:v][{idx + 1}:v]concat=n=2:v=1:a=0[v{idx + 1}];'

                elif idx == len(video_paths)-2:
                    if method == 'crossfade':
                        filter_complex_command += f'[v{idx}][{idx + 1}:v]xfade=transition=fade:duration={transition_time}:offset={time}[v]'
                    elif method == 'cut':
                        filter_complex_command += f'[v{idx}][{idx + 1}:v]concat=n=2:v=1:a=0[v]'
                elif idx == len(video_paths)-1:
                    pass
                else:
                    if method == 'crossfade':
                        filter_complex_command += f'[v{idx}][{idx + 1}:v]xfade=transition=fade:duration={transition_time}:offset={time}[v{idx + 1}];'
                    elif method == 'cut':
                        filter_complex_command += f'[v{idx}][{idx + 1}:v]concat=n=2:v=1:a=0[v{idx + 1}];'

            ffmpeg_command.extend(['-filter_complex'])
            ffmpeg_command.append(filter_complex_command)
            ffmpeg_command.extend(['-map', '[v]', output_path])

            try:
                subprocess.run(ffmpeg_command, check=True)
                set_logger(LogType.LT_INFO, 'Video Combined Finished')

            except subprocess.CalledProcessError as e:
                set_logger(LogType.LT_EXCEPTION, f"Video Combined Failed : {e}")
            return
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def run(self, queue_number, text_prompt, idx):
        try:
            self.output_path = os.path.join(self.args.output_path, queue_number)
            image_paths = self.make_image(text_prompt, idx)
            # Make 10 videos
            self.make_video(idx)
            return image_paths
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))



if __name__ == "__main__":
    dailygeneration = AIContentWorker()
    path = r'C:\Users\chsjk\PycharmProjects\Future_Ocean\result\20250203-084729'
    img_paths = [os.path.join(path,img) for img in os.listdir(path) if img.endswith('.png')]
    dailygeneration.generate_merged_video(img_paths, ['cut', 'cut'])
