import os
import pandas as pd
import gradio as gr
from main import AIContentGenerator
from datetime import datetime
import cmd_args

args, _ = cmd_args.parser.parse_known_args()

class DataHandler:
    def __init__(self, output_path):
        self.output_path = output_path
        self.clip_df = self.get_clip_df()
        self.que_df = self.get_que_df()
        self.initial_clip_df = self.get_initial_clip_df()

    def get_textprompt(self, txtfile_path):
        if not os.path.exists(txtfile_path):
            return "None"
        else:
            with open(txtfile_path, 'r', encoding='utf-8') as f:
                return f.read().replace('\n', '')

    def get_initial_clip_df(self):
        # '''
        # {"que": "20240101-1300", "clip": 1, "prompt": "A site engineer monitoring different aspects of a construction project",
        #  "thumb": r"C:\Users\chsjk\PycharmProjects\MuseumX\DailyGeneration2\data\sample.png"}
        # '''
        que_list = os.listdir(self.output_path)
        result = []
        for que in que_list[:1]:
            imgfile_list = [file for file in os.listdir(os.path.join(self.output_path, que)) if file.endswith('.png')]
            for imgfile in imgfile_list:
                data_dict = {
                    'que': que,
                    'clip': os.path.splitext(imgfile)[0],
                    'prompt': self.get_textprompt(
                        os.path.join(self.output_path, que, f"{os.path.splitext(imgfile)[0]}.txt")),
                    'thumb': os.path.join(self.output_path, que, imgfile)
                }
                result.append(data_dict)
        return pd.DataFrame(result)

    def get_clip_df(self):
        # '''
        # {"que": "20240101-1300", "clip": 1, "prompt": "A site engineer monitoring different aspects of a construction project",
        #  "thumb": r"C:\Users\chsjk\PycharmProjects\MuseumX\DailyGeneration2\data\sample.png"}
        # '''
        que_list = os.listdir(self.output_path)
        result = []
        for que in que_list:
            imgfile_list = [file for file in os.listdir(os.path.join(self.output_path, que)) if file.endswith('.png')]
            for imgfile in imgfile_list:
                data_dict = {
                    'que': que,
                    'clip': os.path.splitext(imgfile)[0],
                    'prompt': self.get_textprompt(
                        os.path.join(self.output_path, que, f"{os.path.splitext(imgfile)[0]}.txt")),
                    'thumb': os.path.join(self.output_path, que, imgfile)
                }
                result.append(data_dict)
        return pd.DataFrame(result)


    def get_que_df(self):
        que_list = os.listdir(self.output_path)
        result = []
        for que in que_list:
            clip_list = [clip for clip in os.listdir(os.path.join(self.output_path, que)) if clip.endswith('.mp4')]
            data_dict = {
                'que' : que,
                'clip_nums' : len(clip_list)
            }
            result.append(data_dict)
        return pd.DataFrame(result)

class TableGenerator:
    def __init__(self):
        pass

    def generate_table(self, df, visible=False):
        # Return lists of components
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
                                    que_textbox = gr.Textbox(value=combined_text, interactive=False, show_label=False, visible=visible)
                                    que_textboxes.append(que_textbox)
                                with gr.Row():
                                    prompt_textbox = gr.Textbox(value=item['prompt'], lines=4, show_label=False, visible =visible)
                                    prompt_textboxes.append(prompt_textbox)
                            with gr.Column():
                                thumb = gr.Image(item['thumb'], show_download_button=False, show_fullscreen_button=True, visible =visible, key=item['thumb'])
                                thumbs.append(thumb)

        while len(que_textboxes) < 10:
            que_textboxes.append(gr.Textbox(visible=False))
            prompt_textboxes.append(gr.Textbox(visible=False))
            thumbs.append(gr.Image(visible=False))


        return que_textboxes, prompt_textboxes, thumbs


class GradioInterface:
    def __init__(self, data_handler, table_generator, content_generator, args):
        self.block_css = """
            .scrollable-container{
          height: 800px;
          overflow-y: scroll;
          background-color: #888888;
        }
        """
        self.data_handler = data_handler
        self.table_generator = table_generator
        self.content_generator = content_generator
        self.args = args
        self.sample_textprompt = self.get_sample_textprompt(self.args.sample_text_path)
        self.demo = self.build_interface()

    def get_sample_textprompt(self, sample_path):
        with open(sample_path, mode='r', encoding='utf-8') as f:
            samples = [sample.replace('\n','') for sample in f.readlines()]
        return samples

    def change_dataframe(self, dataframe):
        new_que_df = self.data_handler.get_que_df()
        return new_que_df

    def run_clip_generator(self, text_prompts):
        results = []
        queue_number = self.generate_que_number()
        for idx, textprompt in enumerate(text_prompts):
            results.append(self.content_generator.run(queue_number, textprompt, idx))

        # update que lists
        # results = [r'C:\Users\chsjk\PycharmProjects\Future_Ocean\result\20250106-111749\0.png',r'C:\Users\chsjk\PycharmProjects\Future_Ocean\result\20250106-111749\0.png',r'C:\Users\chsjk\PycharmProjects\Future_Ocean\result\20250106-111749\0.png']
        new_que_df = self.data_handler.get_que_df()
        return results+[new_que_df]

    def generate_que_number(self):
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    def generate_merged_video(self, inputs):
        image_inputs = inputs[:len(inputs)//2]
        method_inputs = inputs[len(inputs)//2:]
        video_dirs = []
        for img_path in image_inputs:
            video_name = os.path.basename(img_path)+'.mp4'
        # self.content_generator.generate_merged_video(video_dirs, method_inputs)
        return

    def select_que_df(self, evt: gr.SelectData, que_table):
        selected_row = que_table.iloc[evt.index[0]]
        que = selected_row.que
        selected_df = self.data_handler.clip_df.loc[self.data_handler.clip_df['que']==que]

        new_que_textboxes, new_prompt_textboxes, new_thumbs = self.table_generator.generate_table(selected_df, visible=True)
        return [*new_que_textboxes, *new_prompt_textboxes, *new_thumbs]

    def select_merge_vid(self, evt: gr.SelectData, cur_filepaths, idx, prompt_num=3):
        # update idx
        filepath = evt.target.key
        cur_filepaths[idx] = filepath

        next_idx = (idx + 1) % prompt_num
        return *cur_filepaths, cur_filepaths, next_idx

    def build_interface(self, prompt_num=3):
        with gr.Blocks(css=self.block_css) as demo:
            with gr.Row():
                with gr.Column(scale=2):
                    with gr.Accordion("Que lists", open=False):
                        que_table = gr.DataFrame(value=self.data_handler.que_df, label="Que", max_height="500", show_label=False)
                    with gr.Row():
                        que_textboxes, prompt_textboxes, thumbs = self.table_generator.generate_table(self.data_handler.initial_clip_df)

                    que_table.select(self.select_que_df, inputs=que_table, outputs=que_textboxes + prompt_textboxes + thumbs)

                with gr.Column(scale=3):
                    with gr.Row():
                        with gr.Tab("Generate"):
                            with gr.Column():
                                gr.Markdown('# Make New Que')
                                clip_button = gr.Button("Generate Clips")
                                text_fields = []
                                image_fields = []

                                for i in range(prompt_num):
                                    with gr.Row():
                                        text_fields.append(
                                            gr.Textbox(
                                                label=f"Clip {i+1}",
                                                value=f"{self.sample_textprompt[i]}"
                                            )
                                        )
                                    with gr.Row():
                                        image_fields.append(gr.Image(show_label=False))

                                with gr.Row():
                                    clip_button.click(
                                        fn=lambda *args: self.run_clip_generator(args),
                                        inputs=text_fields,
                                        outputs=[*image_fields, que_table]
                                    )

                        with gr.Tab("Merge"):
                            with gr.Column():
                                gr.Markdown("# MERGE")
                                cur_filepaths = gr.State([None for _ in range(prompt_num)])
                                img_idx = gr.State(0)
                                img_inputs = []
                                inputs = []
                                for i in range(prompt_num):
                                    with gr.Row():
                                        with gr.Column():
                                            img_input = gr.Image(label=f'Thumbnail {i+1}')
                                            img_inputs.append(img_input)
                                            inputs.append(img_input)
                                    if i<prompt_num-1:
                                        with gr.Row(variant="panel"):
                                            method_input = gr.Dropdown(show_label=False, choices=["crossfade", "cut"], value="crossfade", interactive=True)
                                            inputs.append(method_input)

                                for image_widget in thumbs:
                                    image_widget.select(fn=self.select_merge_vid,
                                                        inputs=[cur_filepaths, img_idx],
                                                        outputs=img_inputs+[cur_filepaths, img_idx])


                                video_button = gr.Button("Generate Merged Video")
                                video_button.click(
                                    fn = self.generate_merged_video,
                                    inputs= inputs,
                                    outputs=None
                                )
        return demo

    def launch(self):
        self.demo.launch()


# 앱 실행
if __name__ == "__main__":
    data_handler = DataHandler(args.output_path)
    table_generator = TableGenerator()
    content_generator = AIContentGenerator()
    gradio_interface = GradioInterface(data_handler, table_generator, content_generator, args)
    gradio_interface.launch()

