import os
from datetime import  datetime
import json
import re
import shutil
import subprocess

from PythonDelegate.src.pythondelegate.funcs import Func1Arg as Delegate
from logger_setup import set_logger, LogType

class AIContent():
    def __init__(self, args):
        try:
            self.args = args
            self.que_and_rcv_data_callback = None
            set_logger(LogType.LT_INFO, 'Init AIContentWorker')
        except Exception as e:
            # set_logger(LogType.LT_EXCEPTION, str(e))
            raise Exception(str(e))

    def set_callbacks(self, que_and_rcv_data_cb):
        self.que_and_rcv_data_callback = Delegate[object, object]([que_and_rcv_data_cb])

    def get_image_prompt(self, workflow_path, image_output_path, text_prompt):
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

            return prompt

        except Exception as e:
            raise e


    def get_sample_image_prompt(self, workflow_path, image_output_path, text_prompt):
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                prompt = json.load(f)

            # preprocess article
            text_prompt = re.sub(r'^\d+\s*\.', '', text_prompt)
            text_prompt = text_prompt.rstrip()

            # put input path
            prompt['6']['inputs']['text'] = text_prompt

            # save file
            prompt['14']['inputs']['path'] = image_output_path

            return prompt

        except Exception as e:
            raise e

    def get_video_prompt(self, workflow_path, text_prompt, image_path, video_save_path):
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                prompt = json.load(f)

            prompt['22']['inputs']['positive_prompt'] = text_prompt
            prompt['36']['inputs']['image'] = image_path
            prompt['14']['inputs']['filename_prefix'] = video_save_path

            return prompt

        except Exception as e:
            raise e

    def get_sample_video_prompt(self, workflow_path, text_prompt, image_path, video_save_path):
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                prompt = json.load(f)

            prompt['7']['inputs']['text'] = text_prompt
            prompt['22']['inputs']['image'] = image_path
            prompt['21']['inputs']['filename_prefix'] = video_save_path

            return prompt

        except Exception as e:
            raise e

    def replace_with_sample(self, sample_path, save_path):
        shutil.copyfile(sample_path, save_path)
        return

    def make_image(self, text_prompt, idx, timeout=1):
        try:
            img_filename = str(idx) +'.png'
            save_file_path = os.path.join(self.output_path, img_filename)

            args = (self.args.image_workflow, save_file_path, text_prompt)
            # thread_execute(generate_sample_image, *args, timeout=timeout)
            prompt = self.get_sample_image_prompt(*args)
            self.que_and_rcv_data_callback((prompt, timeout))

            # save text prompt
            text_filename = str(idx) + '.txt'
            with open(os.path.join(self.output_path, text_filename), 'w', encoding='utf-8') as f:
                f.write(text_prompt)

            set_logger(LogType.LT_INFO, f"[Image] #{str(idx+1)}: Successfully generated image for prompt : '{text_prompt}'")
            return save_file_path


            # If all retires fail, use the sample image
            # if attempt >= max_retries:
            #     set_logger(LogType.LT_EXCEPTION, f'[Image] #{str(idx+1)}: Failed to generate image after {max_retries} attempts.')
            #     raise Exception(f'[Image] #{str(idx+1)}: Failed to generate image after {max_retries} attempts.)
                # try:
                #     self.replace_with_sample(self.args.sample_image_path, save_file_path)
                #     set_logger(LogType.LT_INFO, f'[Image] #{str(idx+1)}: Sample image copied to {save_file_path} as a fallback')
                # except Exception as e:
                #     set_logger(LogType.LT_ERROR, f'[Image] #{str(idx+1)}: Failed to copy sample image to {save_file_path}: {str(e)}')
                #     return None
                # finally:
                #     # save text prompt
                #     text_filename = str(idx) + '.txt'
                #     with open(os.path.join(self.output_path, text_filename), 'w', encoding='utf-8') as f:
                #         f.write(text_prompt)


        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))
            raise Exception(str(e))

    def make_video(self, text_prompt, idx, timeout=1):
        try:
            video_fname = str(idx)+'.mp4'
            image_fname = str(idx)+'.png'
            vid_file_path = os.path.join(self.output_path, video_fname)
            img_file_path = os.path.join(self.output_path, image_fname)

            args = (self.args.video_workflow, text_prompt, img_file_path, vid_file_path)
            prompt = self.get_sample_video_prompt(*args)
            self.que_and_rcv_data_callback((prompt, timeout))
            # thread_execute(generate_sample_video, *args, timeout=timeout)
            set_logger(LogType.LT_INFO, f'[Video] #{str(idx+1)}: Successfully generated video')
            return
            # if attempt >= max_retries:
            #     set_logger(LogType.LT_EXCEPTION, f'[Video] #{str(idx+1)}: Failed to generate video after {max_retries} attempts.')
            #     try:
            #         self.replace_with_sample(self.args.sample_image_path, vid_file_path)
            #         set_logger(LogType.LT_INFO,
            #                    f'[Image] #{str(idx + 1)}: Sample video copied to {vid_file_path} as a fallback')
            #     except Exception as e:
            #         set_logger(LogType.LT_ERROR,
            #                    f'[Image] #{str(idx + 1)}: Failed to copy sample video to {vid_file_path}: {str(e)}')
            #         return None

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, f'[Video] #{str(idx+1)}: str(e)')
            raise Exception(str(e))


    def get_vidpath_from_imgpath(self, img_path):
        try:
            base, ext = os.path.splitext(img_path)
            mp4_file_path = base + '.mp4'
            if os.path.isfile(mp4_file_path):
                return mp4_file_path
            else:
                return None
        except Exception as e:
            # set_logger(LogType.LT_EXCEPTION, str(e))
            raise Exception(str(e))

    def get_video_length(self, path):
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "format=duration",
                "-of", "json",
                path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            return float(info["format"]["duration"])
        except Exception:
            return None

    def merge_two_clips(self, clip1, clip2, method, output_path, transition_time=3):
        length1 = self.get_video_length(clip1)
        if length1 is None:
            raise Exception(f"첫 번째 클립 길이를 알 수 없음: {clip1}")

        if method == "cut":
            filter_complex = "[0:v][1:v]concat=n=2:v=1:a=0[v]"
            cmd = [
                "ffmpeg", "-y",
                "-i", clip1,
                "-i", clip2,
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-an",
                output_path
            ]
        else:  # crossfade
            offset = max(0, int(length1) - transition_time)
            filter_complex = (
                f"[0:v][1:v]xfade=transition=fade:"
                f"duration={transition_time}:offset={offset}[v]"
            )
            cmd = [
                "ffmpeg", "-y",
                "-i", clip1,
                "-i", clip2,
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-an",
                output_path
            ]

        # ffmpeg 실행
        subprocess.run(cmd, check=True)
        set_logger(LogType.LT_INFO, f'--[Merge] #{idx} <{clip1}> / <{clip2}> / {method} ')

    def generate_merged_video(self, img_paths, merge_methods, transition_time=3):
        try:
            output_path = os.path.join(self.args.final_vid_output_path, f'{datetime.now().strftime("%Y%m%d-%H%M%S")}.mp4')
            video_paths = [self.get_vidpath_from_imgpath(img_path) for img_path in img_paths]
            if len(video_paths)<2:
                # set_logger(LogType.LT_WARNING, 'At least 2 videos are needed')
                raise Exception('최소 2개 이상의 동영상이 필요합니다.')

            current_output = video_paths[0]

            temp_dir = os.path.join(self.args.final_vid_output_path, 'temp_merge')
            os.makedirs(temp_dir, exist_ok=True)

            for i in range(1, len(video_paths)):
                method = merge_methods[i - 1]  # i-1번째 방식 (ex. cut, crossfade)
                next_clip = video_paths[i]

                temp_out = os.path.join(temp_dir, f"merge_{i}.mp4")

                self.merge_two_clips(
                    clip1=current_output,
                    clip2=next_clip,
                    method=method,
                    output_path=temp_out,
                    transition_time=transition_time
                )

                current_output = temp_out

            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(current_output, output_path)

            shutil.rmtree(temp_dir, ignore_errors=True)

            set_logger(LogType.LT_INFO, 'Video Combined Finished')

        except Exception as e:
            # set_logger(LogType.LT_EXCEPTION, str(e))
            raise Exception(str(e))

    # def generate_merged_video(self, img_paths, merge_methods, transition_time=3):
    #     try:
    #         output_path = os.path.join(self.args.final_vid_output_path, 'combined.mp4')
    #         video_paths = [self.get_vidpath_from_imgpath(img_path) for img_path in img_paths]
    #         if len(video_paths)<2:
    #             # set_logger(LogType.LT_WARNING, 'At least 2 videos are needed')
    #             raise Exception('At least 2 videos are needed')
    #
    #         video_time = 8 - transition_time
    #
    #         ffmpeg_command = ['ffmpeg', '-y']
    #         filter_complex_command = ''
    #
    #         for idx, video in enumerate(video_paths):
    #             ffmpeg_command.extend(['-i', video])
    #             time = (idx+1) * video_time
    #             if idx < len(video_paths)-1:
    #                 method = merge_methods[idx]
    #             else:
    #                 method = None
    #
    #             if idx == 0:
    #                 if method == 'crossfade':
    #                     filter_complex_command += f'[{idx}:v][{idx + 1}:v]xfade=transition=fade:duration={transition_time}:offset={time}[v{idx + 1}];'
    #                 elif method == 'cut':
    #                     filter_complex_command += f'[{idx}:v][{idx + 1}:v]concat=n=2:v=1:a=0[v{idx + 1}];'
    #
    #             elif idx == len(video_paths)-2:
    #                 if method == 'crossfade':
    #                     filter_complex_command += f'[v{idx}][{idx + 1}:v]xfade=transition=fade:duration={transition_time}:offset={time}[v]'
    #                 elif method == 'cut':
    #                     filter_complex_command += f'[v{idx}][{idx + 1}:v]concat=n=2:v=1:a=0[v]'
    #             elif idx == len(video_paths)-1:
    #                 pass
    #             else:
    #                 if method == 'crossfade':
    #                     filter_complex_command += f'[v{idx}][{idx + 1}:v]xfade=transition=fade:duration={transition_time}:offset={time}[v{idx + 1}];'
    #                 elif method == 'cut':
    #                     filter_complex_command += f'[v{idx}][{idx + 1}:v]concat=n=2:v=1:a=0[v{idx + 1}];'
    #
    #         ffmpeg_command.extend(['-filter_complex'])
    #         ffmpeg_command.append(filter_complex_command)
    #         ffmpeg_command.extend(['-map', '[v]', output_path])
    #
    #         subprocess.run(ffmpeg_command, check=True)
    #         set_logger(LogType.LT_INFO, 'Video Combined Finished')
    #
    #     except Exception as e:
    #         # set_logger(LogType.LT_EXCEPTION, str(e))
    #         raise Exception(str(e))

    def run(self, queue_number, text_prompt, idx):
        try:
            self.output_path = os.path.join(self.args.output_path, queue_number)
            image_paths = self.make_image(text_prompt, idx)
            self.make_video(text_prompt, idx)
            return image_paths
        except Exception as e:
            raise Exception(str(e))

    def close(self):
        set_logger(LogType.LT_INFO, 'Close AIContentWorker')



if __name__ == "__main__":
    from cmd_args import parse_args
    args = parse_args()
    aicontent = AIContent(args)
    text_prompt = 'a pig'
    idx = 0

    from WebSocketClientWorker import WebSocketClient
    ws = WebSocketClient(args)



    aicontent.make_image(text_prompt, idx)

