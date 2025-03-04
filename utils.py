import os
import queue
import threading
from logger_setup import LogType, set_logger
import random
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


class TimeoutException(Exception):
    pass

def thread_execute(func, *args, timeout=20):
    que = queue.Queue()
    def wrapper_func():
        try:
            result = func(*args)
        except Exception as e:
            result = e
        que.put(result)

    thread = threading.Thread(target=wrapper_func)
    thread.daemon = True
    thread.start()

    try:
        result = que.get(block=True, timeout=timeout)
    except queue.Empty:
        raise TimeoutException(f"Function execution exceeded {timeout} seconds")
    if isinstance(result, Exception):
        raise result
    return result

def randomize_seed(prompt, node_id):
    prompt[node_id]['inputs']['seed'] = random.randint(1,4294967294)
    return prompt