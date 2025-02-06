import os
import pandas as pd
import gradio as gr
from AIcontentWorker import AIContentWorker
from datetime import datetime
from logger_setup import LogType, set_logger, init_logger


class GradioInterfaceWorker:
    def __init__(self, args):
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
        """
        self.args = args
        self.prompt_num = self.args.prompt_num
        self.sample_textprompt = self.get_sample_textprompt(self.args.sample_text_path)

        self.generate_event_callback = None
        self.merge_event_callback = None

        self.get_quedf_event_callback = None
        self.get_clipdf_event_callback = None
        self.update_df_event_callback = None

        # self.demo = self.build_interface()

    def get_sample_textprompt(self, sample_path):
        with open(sample_path, mode='r', encoding='utf-8') as f:
            samples = [line.strip() for line in f if line.strip()]
        return samples

    def generate_table(self, df, visible=False):
        que_textboxes = []
        prompt_textboxes = []
        thumbs = []
        with gr.Row() as table_row:
            with gr.Row():
                with gr.Column(variant="panel"):
                    for idx, item in enumerate(df.iterrows()):
                        if idx >= 10:
                            break
                        _, item = item
                        with gr.Row():
                            with gr.Column():
                                with gr.Row():
                                    combined_text = f'{item["que"]} // {item["clip"]}'
                                    que_textbox = gr.Textbox(value=combined_text, interactive=False, show_label=False,
                                                             visible=visible)
                                    que_textboxes.append(que_textbox)
                                with gr.Row():
                                    prompt_textbox = gr.Textbox(value=item['prompt'], lines=4, show_label=False,
                                                                visible=visible)
                                    prompt_textboxes.append(prompt_textbox)
                            with gr.Column():
                                thumb = gr.Image(item['thumb'], show_download_button=False, show_fullscreen_button=True,
                                                 visible=visible, key=item['thumb'])
                                thumbs.append(thumb)

        while len(que_textboxes) < 10:
            que_textboxes.append(gr.Textbox(visible=False))
            prompt_textboxes.append(gr.Textbox(visible=False))
            thumbs.append(gr.Image(visible=False))

        return que_textboxes, prompt_textboxes, thumbs

    def run_clip_generator(self, *text_prompts):
        results = []
        queue_number = self.generate_que_number()
        for idx, textprompt in enumerate(text_prompts):
            result = self.generate_event_callback((queue_number, textprompt, idx))
            results.append(result)
        new_que_df = self.get_quedf_event_callback()
        return results + [new_que_df]

    def generate_que_number(self):
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    def generate_merged_video(self, *args):
        method_inputs = list(args[:-2])
        cur_filepaths = args[-2]
        status = args[-1]
        self.merge_event_callback((cur_filepaths, method_inputs))
        return "Finished!"

    def select_que_df(self, evt: gr.SelectData, que_table):
        selected_row = que_table.iloc[evt.index[0]]
        que = selected_row.que
        new_clip_df = self.get_clipdf_event_callback()
        selected_df = new_clip_df.loc[new_clip_df['que'] == que]
        new_que_textboxes, new_prompt_textboxes, new_thumbs = self.generate_table(selected_df, visible=True)
        return [*new_que_textboxes, *new_prompt_textboxes, *new_thumbs]

    def select_merge_vid(self, evt: gr.SelectData, cur_filepaths, idx):
        filepath = evt.target.key
        cur_filepaths[idx] = filepath
        next_idx = (idx + 1) % self.prompt_num
        # img_inputs의 개수는 prompt_num과 같으므로 cur_filepaths를 그대로 반환
        return [*cur_filepaths, cur_filepaths, next_idx]

    def update_que_table(self):
        return self.update_df_event_callback()

    def build_interface(self):
        with gr.Blocks(css=self.block_css) as demo:
            # 왼쪽 Queue List 영역
            gr.Markdown("## 영상 리스트")
            with gr.Row():
                with gr.Column(scale=2):
                    with gr.Accordion("큐 리스트", open=True):
                        que_table = gr.DataFrame(value=self.get_quedf_event_callback(), label="Queue", max_height="500", show_label=False)
                    with gr.Column():
                        que_textboxes, prompt_textboxes, thumbs = self.generate_table(self.get_clipdf_event_callback())
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
                                    fn=lambda *args: self.run_clip_generator(*args),
                                    inputs=text_fields,
                                    outputs=[*image_fields, que_table]
                                )
                        # Merge 탭
                        with gr.Tab("Merge"):
                            gr.Markdown("### Merge Videos")
                            gr.Markdown("썸네일을 선택하여 병합 순서를 지정하고, 전환 방식을 선택한 후 **Generate Merged Video** 버튼을 눌러 병합 영상을 생성하세요.")
                            with gr.Column():
                                merge_button = gr.Button("Generate Merged Video", variant="primary")
                                # 진행 상태는 gr.Markdown을 사용하여 표시
                                status_md = gr.Markdown("**Status:** Ready", elem_classes="status-text")
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
                                    inputs=method_inputs + [cur_filepaths] + [status_md],
                                    outputs=status_md
                                )
            demo.load(
                fn=self.update_que_table,
                inputs=None,
                outputs=[que_table]
            )
        return demo


# if __name__ == "__main__":
#     init_logger()
#     data_handler = DataHandler(args.output_path)
#     table_generator = TableGenerator()
#     content_generator = AIContentWorker()
#     gradio_interface = GradioInterface(data_handler, table_generator, content_generator, args)
#     gradio_interface.launch()
