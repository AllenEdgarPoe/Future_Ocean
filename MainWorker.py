import cmd_args
from logger_setup import LogType, set_logger, init_logger
from PythonDelegate.src.pythondelegate.funcs import Func1Arg as Delegate1
from PythonDelegate.src.pythondelegate.funcs import Func as Delegate


from AIcontentWorker import AIContentWorker
from GradioWorker import GradioInterfaceWorker
from DataHanlderWorker import DataHandlerWorker

class MainWorker():
    def __init__(self):
        try:
            self.args, _ = cmd_args.parser.parse_known_args()
            init_logger()
            self.aicontent = AIContentWorker()
            self.gradio = GradioInterfaceWorker(self.args)
            self.data_handler = DataHandlerWorker(self.args.output_path)
            self.gradio_delegate()
            self.gradio_launch()

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, f"Exception: {e}")

    def generate_event_callback(self, data: tuple):
        queue_number, textprompt, idx = data[0], data[1], data[2]
        return self.aicontent.run_img_video(queue_number, textprompt, idx)

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

    def gradio_delegate(self):
        self.gradio.generate_event_callback = Delegate1[object, object]([self.generate_event_callback])
        self.gradio.merge_event_callback = Delegate1[object, object]([self.merge_event_callback])

        self.gradio.get_quedf_event_callback = Delegate[object]([self.get_quedf_event_callback])
        self.gradio.get_clipdf_event_callback = Delegate[object]([self.get_clipdf_event_callback])
        self.gradio.update_df_event_callback = Delegate[object]([self.update_df_event_callback])

    def gradio_launch(self):
        self.gradio.demo = self.gradio.build_interface()
        self.gradio.demo.launch()


if __name__ == "__main__":
    mainworker = MainWorker()


