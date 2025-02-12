import sys
import cmd_args
from utils import preparation
from logger_setup import LogType, set_logger, init_logger
from AIcontentWorker import AIContentWorker
from GradioWorker import GradioInterfaceWorker
from DataHandlerWorker import DataHandlerWorker
class MainWorker():
    def __init__(self):
        try:
            self.args = cmd_args.parse_args()
            preparation(self.args)
            self.aicontent = AIContentWorker(self.args)
            self.gradio = GradioInterfaceWorker(self.args)
            self.data_handler = DataHandlerWorker(self.args.output_path)

            self.register_gradio_callbacks()
            self.gradio_launch()

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, f"Exception: {e}")

    def generate_event_callback(self, data: tuple):
        try:
            queue_number, textprompt, idx = data[0], data[1], data[2]
            return self.aicontent.run(queue_number, textprompt, idx)

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def merge_event_callback(self, data: tuple):
        try:
            cur_filepaths, method_inputs = data[0], data[1]
            return self.aicontent.generate_merged_video(cur_filepaths, method_inputs)
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def get_quedf_event_callback(self):
        try:
            return self.data_handler.get_que_df()
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def get_clipdf_event_callback(self):
        try:
            return self.data_handler.get_clip_df()
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def update_df_event_callback(self):
        try:
            self.data_handler.update_dataframe()
            return self.data_handler.que_df
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def register_gradio_callbacks(self):
        try:
           self.gradio.set_callbacks(
               self.generate_event_callback,
               self.merge_event_callback,
               self.get_quedf_event_callback,
               self.get_clipdf_event_callback,
               self.update_df_event_callback
           )
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))
    def gradio_launch(self):
        try:
            self.gradio.launch()
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

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



