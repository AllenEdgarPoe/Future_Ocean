import sys
import signal
import threading
import time

import cmd_args
from utils import preparation
from logger_setup import LogType, set_logger, init_logger

from ServerWorker import Server
from WebSocketClientWorker import WebSocketClient
from AIContentWorker import AIContent
from GradioWorker import GradioInterface
from DataHandlerWorker import DataHandler
class MainWorker():
    def __init__(self):
        self.server = None
        self.wsclient = None
        self.aicontent = None
        self.gradio = None
        self.data_handler = None

        try:
            set_logger(LogType.LT_INFO, 'Init MainWorker')
            signal.signal(signal.SIGINT, self.signal_handler)

            self.args = cmd_args.parse_args()
            preparation(self.args)

            self.running = True

            # self.server = Server(self.args)
            # time.sleep(45)

            self.wsclient = WebSocketClient(self.args)

            self.aicontent = AIContent(self.args)
            self.register_content_callbacks()

            self.gradio = GradioInterface(self.args)
            self.register_gradio_callbacks()

            self.data_handler = DataHandler(self.args.output_path)

            self.gradio_launch()

            while self.running:
                time.sleep(0.001)

            if self.gradio != None:
                self.gradio.close()
                self.gradio = None

            if self.aicontent != None:
                self.aicontent.close()
                self.aicontent = None

            if self.wsclient != None:
                self.wsclient.close()
                self.wsclient = None

            if self.server != None:
                self.server.close()
                self.server = None

            set_logger(LogType.LT_INFO, 'Close MainWorker')


        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, f"Exception: {e}")

    def signal_handler(self, sig, frame):
        self.running = False

    def generate_event_callback(self, data: tuple):
        queue_number, textprompt, idx = data[0], data[1], data[2]
        return self.aicontent.run(queue_number, textprompt, idx)

    def merge_event_callback(self, data: tuple):
        cur_filepaths, method_inputs = data[0], data[1]
        return self.aicontent.generate_merged_video(cur_filepaths, method_inputs)

    def get_quedf_event_callback(self):
        return self.data_handler.get_que_df()

    def get_clipdf_event_callback(self):
        return self.data_handler.get_clip_df()

    def update_df_event_callback(self):
        self.data_handler.update_dataframe()
        return self.data_handler.que_df

    def que_and_rcv_data_callback(self, data):
        prompt, timeout = data[0], data[1]
        return self.wsclient.que_and_rcv_data(prompt, timeout)

    def register_gradio_callbacks(self):
       self.gradio.set_callbacks(
           self.generate_event_callback,
           self.merge_event_callback,
           self.get_quedf_event_callback,
           self.get_clipdf_event_callback,
           self.update_df_event_callback
       )

    def register_content_callbacks(self):
        self.aicontent.set_callbacks(
            self.que_and_rcv_data_callback
        )

    def gradio_launch(self):
        self.gradio.launch()

def main():
    init_logger()
    set_logger(LogType.LT_INFO, "+-----------------------------------+")
    set_logger(LogType.LT_INFO, "+      Start AI Video Generation    +")
    set_logger(LogType.LT_INFO, "+-----------------------------------+")
    try:
        mainworker = MainWorker()

    except:
        set_logger(LogType.LT_EXCEPTION, 'Exception')
    finally:
        set_logger(LogType.LT_INFO, "+-----------------------------------+")
        set_logger(LogType.LT_INFO, "+        End AI Video Generation     +")
        set_logger(LogType.LT_INFO, "+-----------------------------------+")

        sys.exit()

if __name__ == "__main__":
    main()



