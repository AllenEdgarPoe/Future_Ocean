import os
import gradio as gr
from datetime import datetime

import pandas as pd

from logger_setup import LogType, set_logger
from PythonDelegate.src.pythondelegate.funcs import Func1Arg as Delegate1
from PythonDelegate.src.pythondelegate.funcs import Func as Delegate

class GradioInterfaceWorker:
    def __init__(self, args):
        set_logger(LogType.LT_INFO, "GradioInterfaceWorker Start")
        self.block_css = """
        .scrollable-container {
            height: 800px;
            overflow-y: scroll;
            background-color: #f0f0f0;
        }
        .clip-info {
            font-weight: bold;
            color: #333;
        }
        .status-text {
            font-size: 50px;
            color: green;
            font-weight: bold;
        }
        .status-text {
            font-size: 20px !important;
            color: #2ecc71 !important;
            padding: 10px;
            border-radius: 5px;
            background-color: #f8f9fa;
        }
        .bold-status { font-weight: 800 !important; }
        #merge-status-indicator { margin: 15px 0; }
        """
        self.args = args
        self.prompt_num = self.args.prompt_num
        self.sample_textprompt = self.get_sample_textprompt()

        # callback function
        self.generate_event_callback = None
        self.merge_event_callback = None

        self.get_quedf_event_callback = None
        self.get_clipdf_event_callback = None
        self.update_df_event_callback = None

    def set_callbacks(self, generate_cb, merge_cb, get_quedf_cb, get_clipdf_cb, update_df_cb):
        try:
            self.generate_event_callback = Delegate1[object, object]([generate_cb])
            self.merge_event_callback = Delegate1[object, object]([merge_cb])
            self.get_quedf_event_callback = Delegate[object]([get_quedf_cb])
            self.get_clipdf_event_callback = Delegate[object]([get_clipdf_cb])
            self.update_df_event_callback = Delegate[object]([update_df_cb])
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))
    def get_sample_textprompt(self):
        try:
            sample_text_path = self.args.sample_text_path
            if os.path.exists(sample_text_path):
                with open(sample_text_path, mode='r', encoding='utf-8') as f:
                    samples = [line.strip() for line in f if line.strip()]
                return samples
            else:
                return [None]*self.prompt_num
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def generate_clip_table(self, df, visible=False):
        try:
            que_textboxes = []
            prompt_textboxes = []
            thumbs = []
            with gr.Row() as table_row:
                with gr.Row():
                    with gr.Column(variant="panel"):
                        for idx in range(100):
                            with gr.Row():
                                with gr.Column():
                                    try:
                                        item = df.iloc[idx, :]

                                        with gr.Row():
                                            combined_text = f'{item["que"]} // {item["clip"]}'
                                            que_textbox = gr.Textbox(value=combined_text, interactive=False,
                                                                     show_label=False,
                                                                     visible=visible)
                                            que_textboxes.append(que_textbox)
                                        with gr.Row():
                                            prompt_textbox = gr.Textbox(value=item['prompt'], lines=4, show_label=False,
                                                                        visible=visible)
                                            prompt_textboxes.append(prompt_textbox)
                                        with gr.Row():
                                            thumb = gr.Image(item['thumb'], show_download_button=False,
                                                             show_fullscreen_button=True,
                                                             visible=visible, key=f"thumbnail_{idx}")
                                            thumbs.append(thumb)
                                    except IndexError:
                                        with gr.Row():
                                            que_textboxes.append(gr.Textbox(visible=False))
                                        with gr.Row():
                                            prompt_textboxes.append(gr.Textbox(visible=False))
                                        with gr.Row():
                                            thumbs.append(gr.Image(visible=False))

            return que_textboxes, prompt_textboxes, thumbs

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def run_clip_generator(self, *text_prompts):
        set_logger(LogType.LT_INFO, "--Generate Clips Button Clicked")
        try:
            results = [None] * (len(text_prompts))
            queue_number = self.generate_que_number()

            # make que directory
            os.makedirs(os.path.join(self.args.output_path, queue_number))

            for i, text_prompt in enumerate(text_prompts):
                result = self.generate_event_callback((queue_number, text_prompt, i))
                results[i] = result
                yield (*results, None)

            updated_que_df = self.get_quedf_event_callback()
            yield (*results, updated_que_df)
            # results = []
            # queue_number = self.generate_que_number()
            # for idx, textprompt in enumerate(text_prompts):
            #     result = self.generate_event_callback((queue_number, textprompt, idx))
            #     results.append(result)
            # new_que_df = self.get_quedf_event_callback()
            # return results + [new_que_df]
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def generate_que_number(self):
        try:
            return datetime.now().strftime("%Y%m%d-%H%M%S")
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def generate_merged_video(self, *args):
        set_logger(LogType.LT_INFO, "--Generate Merged Video Button Clicked")
        try:
            method_inputs = list(args[:-1])
            cur_filepaths = [f for f in args[-1] if f!=None]
            self.merge_event_callback((cur_filepaths, method_inputs))
            return f"비디오가 만들어졌습니다. 폴더 저장 위치 : {os.path.join(self.args.final_vid_output_path, 'combined.mp4')}"
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def select_que_df(self, evt: gr.SelectData, que_table):
        try:
            selected_row = que_table.iloc[evt.index[0]]
            que = selected_row.que
            new_clip_df = self.get_clipdf_event_callback()
            if new_clip_df.empty:
                set_logger(LogType.LT_WARNING, "Empty Dataframe")
                new_que_textboxes, new_prompt_textboxes, new_thumbs = self.generate_clip_table(pd.DataFrame(), visible=False)
            else:
                selected_df = new_clip_df.loc[new_clip_df['que'] == que]
                new_que_textboxes, new_prompt_textboxes, new_thumbs = self.generate_clip_table(selected_df, visible=True)

            return [*new_que_textboxes, *new_prompt_textboxes, *new_thumbs]

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def select_merge_vid(self, evt: gr.SelectData, cur_filepaths, idx):
        set_logger(LogType.LT_INFO, f"--Thumbnail for Video #{idx} Selected")
        try:
            filepath = evt.target.key
            cur_filepaths[idx] = filepath
            next_idx = (idx + 1) % self.prompt_num
            # img_inputs의 개수는 prompt_num과 같으므로 cur_filepaths를 그대로 반환
            return [*cur_filepaths, cur_filepaths, next_idx]
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def update_que_table(self):
        try:
            return self.update_df_event_callback()
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def build_interface(self):
        try:
            with gr.Blocks(css=self.block_css) as demo:
                # 왼쪽 Queue List 영역
                gr.Markdown("## 영상 리스트")
                with gr.Row():
                    with gr.Column(scale=2):
                        with gr.Accordion("큐 리스트", open=True):
                            que_table = gr.DataFrame(value=self.get_quedf_event_callback(), label="Queue", max_height="500", show_label=False)
                        with gr.Column():
                            que_textboxes, prompt_textboxes, thumbs = self.generate_clip_table(self.get_clipdf_event_callback())
                        que_table.select(self.select_que_df, inputs=que_table, outputs=que_textboxes + prompt_textboxes + thumbs)
                    # 오른쪽 메인 탭 영역
                    with gr.Column(scale=3):
                        with gr.Tabs():
                            # Generate 탭
                            with gr.Tab("Generate"):
                                gr.Markdown("### Generate Clips")
                                gr.Markdown("아래 텍스트 프롬프트를 입력한 후 **Generate Clips** 버튼을 눌러 새 클립을 생성하세요.")
                                with gr.Column():
                                    generate_button = gr.Button("Generate Clips", variant="primary")
                                    text_fields = []
                                    image_fields = []
                                    for i in range(self.prompt_num):
                                        with gr.Group():
                                            with gr.Row():
                                                text_fields.append(gr.Textbox(label=f"Clip {i+1}", value=self.sample_textprompt[i], placeholder="Enter prompt here..."))
                                            with gr.Row():
                                                image_fields.append(gr.Image(label=f"Output Clip {i+1}", show_label=False))
                                    generate_button.click(
                                        fn= self.run_clip_generator,
                                        inputs=text_fields,
                                        outputs=[*image_fields, que_table],
                                        queue=True
                                    )
                            # Merge 탭6
                            with gr.Tab("Merge"):
                                gr.Markdown("### Merge Videos")
                                gr.Markdown("썸네일을 선택하여 병합 순서를 지정하고, 전환 방식을 선택한 후 **Generate Merged Video** 버튼을 눌러 병합 영상을 생성하세요.")
                                with gr.Column():
                                    merge_button = gr.Button("Generate Merged Video", variant="primary")
                                    # 진행 상태는 gr.Markdown을 사용하여 표시
                                    status_md = gr.Markdown("**Status:** Ready",
                                                            elem_classes=["status-text", "bold-status"],
                                                            elem_id="merge-status-indicator")
                                    cur_filepaths = gr.State([None for _ in range(self.prompt_num)])
                                    img_idx = gr.State(0)
                                    img_inputs = []
                                    method_inputs = []
                                    for i in range(self.prompt_num):
                                        with gr.Row():
                                            img_inputs.append(gr.Image(label=f'Thumbnail {i+1}'))
                                        if i < self.prompt_num - 1:
                                            with gr.Row(variant="panel"):
                                                method_inputs.append(gr.Dropdown(choices=["crossfade", "cut"], value="crossfade", show_label=True, label=f"Transition {i+1}"))
                                    for image_widget in thumbs:
                                        image_widget.select(
                                            fn=self.select_merge_vid,
                                            inputs=[cur_filepaths, img_idx],
                                            outputs=img_inputs + [cur_filepaths, img_idx]
                                        )
                                    merge_button.click(
                                        fn=self.generate_merged_video,
                                        inputs=method_inputs + [cur_filepaths],
                                        outputs=status_md
                                    )
                demo.load(
                    fn=self.update_que_table,
                    inputs=None,
                    outputs=[que_table]
                )
            return demo

        except Exception as e:
            set_logger(LogType.LT_ERROR, str(e))
    def launch(self):
        try:
            self.demo = self.build_interface()
            self.demo.launch()
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))


# if __name__ == "__main__":
#     import cmd_args
#     args, _ = cmd_args.parser.parse_known_args()
#     gradio = GradioInterfaceWorker(args)
#     demo = gradio.build_interface()
#     demo.launch()
