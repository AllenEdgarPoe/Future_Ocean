import gradio as gr
import base64

def encode_image(file_path):
    with open(file_path, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode()
    return encoded_string

def return_css(encoded_string):
    css = f"""
    #custom-button {{
        background-image: url(data:image/png;base64,{encoded_string});
        width: 1000px;
        height: 1000px;
        border: none;
        cursor: pointer;
    }}
    """

    return css
from gradio.events import Dependency

class Button_foregrund_image(gr.Button):
    def __init__(self, img_file_path):
        super().__init__(img_file_path)
        self.img_file_path = img_file_path
        encoded_image = encode_image(self.img_file_path)
        self.css = return_css(encoded_image)
        self.elem_id = "custom-button",
        self.value = self.get_info(self.img_file_path)

    def get_info(self, img_file):
        return img_file
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer




