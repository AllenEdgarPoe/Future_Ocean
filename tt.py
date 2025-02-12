import gradio as gr
import pandas as pd

def make_html_table_from_df(df: pd.DataFrame) -> str:
    """df의 row마다 썸네일(img 태그)과 텍스트를 포함한 HTML 테이블 생성"""
    if df.empty:
        return "<p><strong>데이터가 없습니다.</strong></p>"
    html = "<table border='1' style='border-collapse: collapse;'>"
    html += "<tr><th>Queue</th><th>Prompt</th><th>Thumbnail</th></tr>"
    for i, row in df.iterrows():
        que = row['que']
        prompt = row['prompt']
        thumb_url = row['thumb']  # 이미지 경로/URL
        html += (
            f"<tr>"
            f"<td>{que}</td>"
            f"<td>{prompt}</td>"
            f"<td><img src='{thumb_url}' width='150' /></td>"
            f"</tr>"
        )
    html += "</table>"
    return html

def load_df():
    """예시용 df 로드 혹은 동적으로 생성"""
    data = {
        "que": ["Q1", "Q2", "Q3"],
        "prompt": ["Prompt1", "Prompt2", "Prompt3"],
        "thumb": [
            r"C:\Users\chsjk\PycharmProjects\Future_Ocean\result\20250204-132314\0.png",
            r"C:\Users\chsjk\PycharmProjects\Future_Ocean\result\20250204-132314\2.png",
            r"C:\Users\chsjk\PycharmProjects\Future_Ocean\result\20250204-132314\1.png",
        ],
    }
    return pd.DataFrame(data)

def refresh_table():
    df = load_df()
    return make_html_table_from_df(df)

with gr.Blocks() as demo:
    table_html = gr.HTML()
    refresh_btn = gr.Button("Refresh")

    # 처음 페이지 로드 시 df를 HTML로 생성
    demo.load(fn=refresh_table, inputs=None, outputs=table_html)
    # 필요할 때 강제로 다시 불러오기
    refresh_btn.click(fn=refresh_table, inputs=None, outputs=table_html)

demo.launch()
