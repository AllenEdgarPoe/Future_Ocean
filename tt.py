import os
import gradio as gr
from datetime import datetime

import pandas as pd

from logger_setup import LogType, set_logger
from PythonDelegate.src.pythondelegate.funcs import Func1Arg as Delegate1
from PythonDelegate.src.pythondelegate.funcs import Func as Delegate

GLOBAL_STATE = {'status': 'idle',  #'idle' or 'processing'
                'status_text' : '준비 완료'
                }

class GradioInterfaceWorker:
    def __init__(self, args):
        set_logger(LogType.LT_INFO, "GradioInterfaceWorker Start")
        self.block_css = """
        width: 100vw;
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
            font-size: 20px;
            color: #2ecc71 !important;
            padding: 10px;
            border-radius: 5px;
            background-color: #f8f9fa;
        }
            .app-title textarea {
            font-size: 30px !important;
            color: #0285C5 !important;
            font-weight: bold;
        }
        .comp-title textarea {
            font-size: 14px !important; 
            font-weight: bold;
            color: #10B981 !important;
        }
        .title-active textarea {
            color: #10B981 !important;
        }
        .title-process textarea {
            color: #BB3320 !important;
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

    def set_status(self, new_status):
        GLOBAL_STATE['status'] = new_status

    def get_status(self):
        return GLOBAL_STATE['status']

    def set_status_text(self, status_text):
        GLOBAL_STATE['status_text'] = status_text
    def get_status_text(self):
        return GLOBAL_STATE['status_text']

    def reload_func(self):
        new_que_table =self.update_df_event_callback()
        status_bool = self.get_status()=='idle'
        if status_bool:
            self.set_status_text('준비 완료')

        return new_que_table, self.get_status_text(), gr.update(interactive=status_bool), gr.update(interactive=status_bool)

    def tick_func(self):
        status_bool = self.get_status()=='idle'
        return self.get_status_text(), gr.update(interactive=status_bool), gr.update(interactive=status_bool)

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
            self.set_status_text(f"에러가 발생했습니다: {str(e)}")


    def generate_clip_table(self, df, visible=False):
        try:
            prompt_textboxes = []
            thumbs = []
            with gr.Column() as table_row:
                for idx in range(10):
                    try:
                        item = df.iloc[idx, :]
                        with gr.Group():
                            with gr.Row():
                                thumb = gr.Image(item['thumb'], show_download_button=False,
                                                 show_fullscreen_button=True,
                                                 visible=visible, key=item['thumb'])
                                thumbs.append(thumb)
                            with gr.Row():
                                prompt_textbox = gr.Textbox(value=item['prompt'], lines=4, show_label=False,
                                                            visible=visible)
                                prompt_textboxes.append(prompt_textbox)

                    except IndexError:
                        with gr.Row():
                            prompt_textboxes.append(gr.Textbox(visible=False))
                        with gr.Row():
                            thumbs.append(gr.Image(visible=False))

            return prompt_textboxes, thumbs

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))
            self.set_status_text(f"에러가 발생했습니다: {str(e)}")


    def run_clip_generator(self, *text_prompts):
        set_logger(LogType.LT_INFO, "--Generate Clips Button Clicked")
        self.set_status('processing')
        self.set_status_text('영상 생성 중...')

        try:
            results = [None] * (len(text_prompts))
            queue_number = self.generate_que_number()

            # make que directory
            os.makedirs(os.path.join(self.args.output_path, queue_number))

            for i, text_prompt in enumerate(text_prompts):
                self.set_status_text(f'영상 생성 중 : {str(i+1)}/{len(text_prompts)}')

                result = self.generate_event_callback((queue_number, text_prompt, i))
                results[i] = result
                yield (*results, None)

            updated_que_df = self.get_quedf_event_callback()
            self.set_status_text('영상 생성이 완료 되었습니다.')
            yield (*results, updated_que_df)

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))
            self.set_status_text(f"에러가 발생했습니다: {str(e)}")


        finally:
            self.set_status('idle')


    def generate_que_number(self):
        try:
            return datetime.now().strftime("%Y%m%d-%H%M%S")
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def generate_merged_video(self, *args):
        set_logger(LogType.LT_INFO, "--Generate Merged Video Button Clicked")
        self.set_status('processing')
        self.set_status_text('비디오를 합치는 중입니다...')
        try:
            method_inputs = list(args[:-1])
            cur_filepaths = [f for f in args[-1] if f!=None]
            self.merge_event_callback((cur_filepaths, method_inputs))
            self.set_status_text(f"비디오가 만들어졌습니다. 폴더 저장 위치 : {os.path.join(self.args.final_vid_output_path, 'combined.mp4')}")

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))
            self.set_status_text(f"에러가 발생했습니다: {str(e)}")

        finally:
            self.set_status('idle')


    def select_que_df(self, evt: gr.SelectData, que_table):
        try:
            selected_row = que_table.iloc[evt.index[0]]
            que = selected_row.que
            new_clip_df = self.get_clipdf_event_callback()
            if new_clip_df.empty:
                set_logger(LogType.LT_WARNING, "Empty Dataframe")
                new_prompt_textboxes, new_thumbs = self.generate_clip_table(pd.DataFrame(), visible=False)
            else:
                selected_df = new_clip_df.loc[new_clip_df['que'] == que]
                new_prompt_textboxes, new_thumbs = self.generate_clip_table(selected_df, visible=True)

            return [*new_prompt_textboxes, *new_thumbs]

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))
            self.set_status_text(f"에러가 발생했습니다: {str(e)}")


    def select_merge_vid(self, evt: gr.SelectData, cur_filepaths, idx):
        try:
            filepath = evt.target.key
            if None in cur_filepaths:
                idx = cur_filepaths.index(None)
            cur_filepaths[idx] = filepath
            next_idx = (idx + 1) % self.prompt_num
            return [*cur_filepaths, cur_filepaths, next_idx]
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))
            self.set_status_text(f"에러가 발생했습니다: {str(e)}")


    def remove_thumb(self, cur_filepaths, idx):
        try:
            cur_filepaths[idx] = None
            return [*cur_filepaths, cur_filepaths]
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))
            self.set_status_text(f"에러가 발생했습니다: {str(e)}")



    def update_que_table(self):
        try:
            return self.update_df_event_callback()
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))
            self.set_status_text(f"에러가 발생했습니다: {str(e)}")


    def build_interface(self):
        try:
            with gr.Blocks(css=self.block_css, fill_width=True, theme=gr.themes.Ocean()) as demo:
                # 왼쪽 Queue List 영역
                with gr.Sidebar(width=600):
                    gr.Textbox(value="Que List", elem_classes=["comp-title","title-active"], show_label=False)
                    que_table = gr.DataFrame(label="Que List", value=self.get_quedf_event_callback(), max_height="500", show_label=False, interactive=False, show_row_numbers=True, headers=["QUE", "CLIPS"])
                    prompt_textboxes, thumbs = self.generate_clip_table(self.get_clipdf_event_callback())
                    que_table.select(self.select_que_df, inputs=que_table, outputs=prompt_textboxes + thumbs)

                with gr.Column():
                    gr.Textbox(label="for Future Ocean Museum v0.8.1 250213", value="XORBIS AI Video Generator",
                               elem_classes="app-title")
                    status_md = gr.Textbox(label="Status", show_label="False", value=f"현재 상태 : {self.get_status_text()}", elem_classes="comp-title")

                    with gr.Tabs():
                            # Generate 탭
                            with gr.Tab("Generate"):
                                with gr.Column():
                                    gr.Markdown("아래 텍스트 프롬프트를 입력한 후 **Generate Clips** 버튼을 눌러 새 클립을 생성하세요.")
                                    with gr.Column():
                                        generate_button = gr.Button("Generate Clips", variant="primary")
                                        text_fields = []
                                        image_fields = []
                                        for i in range(self.prompt_num):
                                            with gr.Row(equal_height=True):
                                                text_fields.append(gr.Textbox(label=f"Clip {i+1}", value=self.sample_textprompt[i], placeholder="Enter prompt here..."))
                                                image_fields.append(gr.Image(label=f"Output Clip {i+1}", show_label=False))
                                        generate_button.click(
                                            fn= self.run_clip_generator,
                                            inputs=text_fields,
                                            outputs=[*image_fields, que_table],
                                            queue=True
                                        )
                            # Merge 탭
                            with gr.Tab("Merge"):
                                with gr.Column():
                                    gr.Markdown("사이드바에서 10개의 썸네일을을 선택하고 **Generate Merged Video** 버튼을 눌러 병합 영상을 생성하세요.")
                                    merge_button = gr.Button("Generate Merged Video", variant="primary")
                                    cur_filepaths = gr.State([None for _ in range(self.prompt_num)])
                                    img_idx = gr.State(0)
                                    img_inputs = []
                                    method_inputs = []
                                    for i in range(self.prompt_num):
                                        with gr.Row(equal_height=True):
                                            with gr.Column(scale=8):
                                                img_inputs.append(gr.Image(label=f'Thumbnail {i+1}'))
                                            with gr.Column(scale=1):
                                                if i < self.prompt_num - 1:
                                                    with gr.Row(variant="panel"):
                                                        method_inputs.append(gr.Dropdown(choices=["crossfade", "cut"], value="crossfade", show_label=True, label=f"Transition {i+1}"))
                                                else:
                                                    gr.Markdown("END")
                                    for image_widget in thumbs:
                                        image_widget.select(
                                            fn=self.select_merge_vid,
                                            inputs=[cur_filepaths, img_idx],
                                            outputs=img_inputs +[cur_filepaths, img_idx]
                                        )

                                    for idx, image_widget in enumerate(img_inputs):
                                        image_widget.select(
                                            fn=self.remove_thumb,
                                            inputs=[cur_filepaths, gr.State(idx)],
                                            outputs=img_inputs +[cur_filepaths],
                                            queue=True
                                        )

                                    merge_button.click(
                                        fn=self.generate_merged_video,
                                        inputs=method_inputs + [cur_filepaths],
                                        queue=True
                                    )

                            timer = gr.Timer(1)
                            timer.tick(fn=self.tick_func, outputs=[status_md, generate_button, merge_button])

                demo.load(
                    fn=self.reload_func,
                    inputs=None,
                    outputs=[que_table, status_md, generate_button, merge_button]
                )
            return demo

        except Exception as e:
            set_logger(LogType.LT_ERROR, str(e))
    def launch(self):
        try:
            self.demo = self.build_interface()
            self.demo.queue().launch()
        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))


# if __name__ == "__main__":
#     import cmd_args
#     args, _ = cmd_args.parser.parse_known_args()
#     gradio = GradioInterfaceWorker(args)
#     demo = gradio.build_interface()
#     demo.launch()
