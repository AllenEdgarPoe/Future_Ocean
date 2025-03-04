import os
import pandas as pd
from logger_setup import LogType, set_logger

class DataHandler:
    def __init__(self, output_path):
        self.output_path = output_path
        self.clip_df = pd.DataFrame()
        self.que_df = pd.DataFrame()
        self.update_dataframe()

    def update_dataframe(self):
        try:
            self.clip_df = self.get_clip_df()
            self.que_df = self.get_que_df()
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def get_textprompt(self, txtfile_path):
        try:
            if not os.path.exists(txtfile_path):
                return "None"
            else:
                with open(txtfile_path, 'r', encoding='utf-8') as f:
                    return f.read().replace('\n', '')
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def get_clip_df(self):
        try:
            que_list = os.listdir(self.output_path)
            result = []
            for que in que_list:
                imgfile_list = [file for file in os.listdir(os.path.join(self.output_path, que)) if file.endswith('.png')]
                for imgfile in imgfile_list:
                    data_dict = {
                        'que': que,
                        'clip': os.path.splitext(imgfile)[0],
                        'prompt': self.get_textprompt(os.path.join(self.output_path, que, f"{os.path.splitext(imgfile)[0]}.txt")),
                        'thumb': os.path.join(self.output_path, que, imgfile)
                    }
                    result.append(data_dict)
            self.clip_df = pd.DataFrame(result)
            return self.clip_df

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def get_que_df(self):
        try:
            que_list = os.listdir(self.output_path)
            result = []
            for que in que_list:
                if que!='final':
                    clip_list = [clip for clip in os.listdir(os.path.join(self.output_path, que)) if clip.endswith('.mp4')]
                    data_dict = {
                        'que': que,
                        'clip_nums': len(clip_list)
                    }
                    result.append(data_dict)
            self.que_df = pd.DataFrame(result)
            return self.que_df
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))
