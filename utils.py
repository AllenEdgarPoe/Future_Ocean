import os
from logger_setup import LogType, set_logger

def preparation(args):
    try:
        # make directories for program
        dir_list = [
            args.output_path,
            args.final_vid_output_path,
            args.data_path
        ]
        for d in dir_list:
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
                set_logger(LogType.LT_WARNING, f"Directory '{d}' not found. Created new one.")

        # check if there are sample files
        sample_list = [
            args.sample_text_path,
            args.sample_image_path,
            args.sample_video_path
        ]
        for f in sample_list:
            if not os.path.exists(f):
                with open(f, 'wb') as fp:
                    pass
                set_logger(LogType.LT_WARNING, f"Sample file '{d}' not found. Created new one.")

    except Exception as e:
        set_logger(LogType.LT_EXCEPTION, str(e))