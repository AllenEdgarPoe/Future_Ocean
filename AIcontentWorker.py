import os
import time
import cv2
import shutil
import subprocess
from logger_setup import set_logger, LogType

import cmd_args
from comfyui_api import thread_execute, generate_sample_image, generate_sample_video


class AIContentWorker():
    def __init__(self):
        try:
            self.args, _ = cmd_args.parser.parse_known_args()
            set_logger(LogType.LT_INFO, 'Init AIContentWorker')
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def replace_with_sample(self, sample_path, save_path):
        shutil.copyfile(sample_path, save_path)
        return

    def make_image(self, textprompt, idx, timeout=5):
        """
        :param textprompt:
        :param filename: {que_idx} without extension. e.g. 20250113-085630_1
        :param idx:
        :param timeout:
        :return:
        """
        img_filename = str(idx) +'.png'
        save_file_path = os.path.join(self.output_path, img_filename)
        args = (self.args.image_workflow, save_file_path, textprompt)

        max_retries = 3
        attempt = 0

        while max_retries>attempt:
            try:
                thread_execute(generate_sample_image, *args, timeout=timeout)

                # save text prompt
                text_filename = str(idx)+'.txt'
                with open(os.path.join(self.output_path, text_filename), 'w', encoding='utf-8') as f:
                    f.write(textprompt)

                set_logger(LogType.LT_INFO, f"--Step 2 - {str(idx)}: Successfully generated image for prompt : '{textprompt}'")
                break
            except Exception as e:
                attempt+=1
                set_logger(LogType.LT_EXCEPTION, f'Step 2 - {str(idx)}: Error Occurred : {str(e)}')
                time.sleep(1)

        # If all retires fail, use the sample image
        if attempt >= max_retries:
            set_logger(LogType.LT_EXCEPTION, f'Step 2 - {str(idx)}: Failed to generate image after {max_retries} attempts.')
            try:
                self.replace_with_sample(self.args.sample_image_path, save_file_path)
                set_logger(LogType.LT_INFO, f'Sample image copied to {save_file_path} as a fallback')
            except Exception as e:
                set_logger(LogType.LT_EXCEPTION, f'Failed to copy sample image to {save_file_path}: {str(e)}')
                return None

        return save_file_path

    def make_video(self, idx, timeout=10):
        video_fname = str(idx)+'.mp4'
        image_fname = str(idx)+'.png'
        vid_file_path = os.path.join(self.output_path, video_fname)
        img_file_path = os.path.join(self.output_path, image_fname)

        # if base image does not exist -> sample video
        if not os.path.exists(img_file_path):
            self.replace_with_sample(self.args.sample_video_path, vid_file_path)
            return vid_file_path

        args = (self.args.video_workflow, img_file_path, vid_file_path)

        max_retries = 3
        attempt = 0
        while attempt < max_retries:
            try:
                thread_execute(generate_sample_video, *args, timeout=timeout)
                set_logger(LogType.LT_INFO, f'--Step 3 - {str(idx)}: Successfully generated video')
                break
            except Exception as e:
                attempt+=1
                set_logger(LogType.LT_EXCEPTION, f'--Step 3 - {str(idx)}: Error Occurred : {str(e)}')
                time.sleep(1)

        if attempt >= max_retries:
            set_logger(LogType.LT_EXCEPTION, f'Step 3 - {str(idx)}: Failed to generate video after {max_retries} attempts.')
            self.replace_with_sample(self.args.sample_video_path, vid_file_path)

        return vid_file_path


    # def dissolve_videos(self, video_dir, overlapped_time=1):
    #     video_paths = [os.path.join(video_dir, vid) for vid in os.listdir(video_dir) if vid.endswith('.mp4')]
    #
    #     if len(video_paths) < 2:
    #         set_logger(LogType.LT_EXCEPTION, 'At least two video files are required.')
    #         return
    #
    #     output_path = os.path.join(video_dir, os.path.join(video_dir, 'combined.mp4'))
    #     cap1 = cv2.VideoCapture(video_paths[0])
    #     if not cap1.isOpened():
    #         set_logger(LogType.LT_EXCEPTION, 'First video open failed')
    #         return
    #
    #     fps = cap1.get(cv2.CAP_PROP_FPS)
    #     w = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
    #     h = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #     effect_frame = int(fps * overlapped_time)  # 3 seconds of overlap
    #
    #     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #     out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    #
    #     for i, video_path in enumerate(video_paths[1:]):
    #         cap2 = cv2.VideoCapture(video_path)
    #         if not cap2.isOpened():
    #             set_logger(LogType.LT_EXCEPTION, f'Failed to open video: {video_path}')
    #             continue
    #
    #         frame_cnt1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
    #
    #         # Write all frames from the first video except the last 3 seconds
    #         if i == 0:
    #             for j in range(frame_cnt1 - effect_frame):
    #                 ret1, frame1 = cap1.read()
    #                 if not ret1:
    #                     set_logger(LogType.LT_EXCEPTION, 'Frame read error from cap1!')
    #                     break
    #                 out.write(frame1)
    #         else:
    #             for j in range(frame_cnt1 - effect_frame * 2):
    #                 ret1, frame1 = cap1.read()
    #                 if not ret1:
    #                     set_logger(LogType.LT_EXCEPTION, 'Frame read error from cap1!')
    #                     break
    #                 out.write(frame1)
    #
    #         # Proceed with transition between current cap1 and cap2
    #         for j in range(effect_frame):
    #             ret1, frame1 = cap1.read()
    #             ret2, frame2 = cap2.read()
    #
    #             if not ret1 or not ret2:
    #                 set_logger(LogType.LT_EXCEPTION, 'Frame read error during transition!')
    #                 break
    #
    #             alpha = j / effect_frame
    #             frame = cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)
    #             out.write(frame)
    #
    #         cap1.release()  # Release the old video capture
    #         cap1 = cap2  # Update cap1 to the current cap2, continue the loop
    #
    #     # After processing videos, capture remaining frames of the last video
    #     while True:
    #         ret1, frame1 = cap1.read()
    #         if not ret1:
    #             break
    #         out.write(frame1)
    #
    #     # Cleanup resources
    #     cap1.release()
    #     out.release()
    #     set_logger(LogType.LT_INFO, 'Video Combined Finished')
    #     return

    def get_vidpath_from_imgpath(self, img_path):
        base, ext = os.path.splitext(img_path)
        mp4_file_path = base + '.mp4'
        if os.path.isfile(mp4_file_path):
            return mp4_file_path
        else:
            return None


    def generate_merged_video(self, img_paths, merge_methods, transition_time=3):
        output_path = os.path.join(self.args.final_vid_output_path, 'combined.mp4')
        video_paths = [self.get_vidpath_from_imgpath(img_path) for img_path in img_paths]
        if len(video_paths)<2:
            set_logger(LogType.LT_EXCEPTION, 'At least 2 videos are needed')
            raise Exception('At least 2 videos are needed')

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


    def crossfade_merge(self, video_path, transition_time=1):
        output_path = os.path.join(video_path, 'combined.mp4')
        video_paths = [os.path.join(video_path, vid) for vid in os.listdir(video_path) if vid.endswith('.mp4')]
        video_time = 8 - transition_time

        ffmpeg_command = ['ffmpeg']
        filter_complex_command = ''

        for idx, video in enumerate(video_paths):
            ffmpeg_command.extend(['-i', video])
            time = (idx+1) * video_time
            if idx==0:
                filter_complex_command += f'[{idx}:v][{idx + 1}:v]xfade=transition=fade:duration={transition_time}:offset={time}[v{idx + 1}];'
            elif idx==len(video_paths)-2:
                filter_complex_command += f'[v{idx}][{idx + 1}:v]xfade=transition=fade:duration={transition_time}:offset={time}[v]'
            elif idx==len(video_paths)-1:
                pass
            else:
                filter_complex_command += f'[v{idx}][{idx + 1}:v]xfade=transition=fade:duration={transition_time}:offset={time}[v{idx + 1}];'

        ffmpeg_command.extend(['-filter_complex'])
        ffmpeg_command.append(filter_complex_command)
        ffmpeg_command.extend(['-map', '[v]', output_path])

        try:
            subprocess.run(ffmpeg_command, check=True)
            set_logger(LogType.LT_INFO, 'Video Combined Finished')

        except subprocess.CalledProcessError as e:
            set_logger(LogType.LT_EXCEPTION, f"Video Combined Failed : {e}")
        return

    def run_img_video(self, queue_number, text_prompt, idx):
        self.output_path = os.path.join(self.args.output_path, queue_number)
        image_paths = self.make_image(text_prompt, idx)
        # Make 10 videos
        video_paths = self.make_video(idx)
        # combine videos
        # self.dissolve_videos2(self.video_output_path)
        return image_paths


if __name__ == "__main__":
    dailygeneration = AIContentWorker()
    path = r'C:\Users\chsjk\PycharmProjects\Future_Ocean\result\20250203-084729'
    img_paths = [os.path.join(path,img) for img in os.listdir(path) if img.endswith('.png')]
    dailygeneration.generate_merged_video(img_paths, ['cut', 'cut'])
