import pandas as pd
import os
import cmd_args

# '''
# {"que": "20240101-1300", "clip": 1, "prompt": "A site engineer monitoring different aspects of a construction project",
#  "thumb": r"C:\Users\chsjk\PycharmProjects\MuseumX\DailyGeneration2\data\sample.png"}
# '''

def parse_to_df(file_path):
    que_list = os.listdir(file_path)
    result = []
    for que in que_list:
        # thumbnail img 를 기준으로 찾기
        imgfile_list = [file for file in os.listdir(os.path.join(file_path, que)) if file.endswith('.png')]

        for imgfile in imgfile_list:
            data_dict = dict()

            data_dict['que'] = que

            clipname = os.path.splitext(imgfile)[0]
            data_dict['clip'] = clipname

            data_dict['prompt'] = get_textprompt(os.path.join(file_path, que, clipname+'.txt'))
            data_dict['thumb'] = os.path.join(file_path, que, imgfile)

            result.append(data_dict)
    return pd.DataFrame(result)


def get_textprompt(txtfile_path):
    with open(txtfile_path, mode='r', encoding='utf-8') as f:
        textprompt = f.read()

    return textprompt.replace('\n','')
