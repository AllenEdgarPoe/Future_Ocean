import os
path = r'C:\Users\chsjk\PycharmProjects\LiveAI\LIVEAI_DEMO\prompt'
paths = [pp for pp in os.listdir(path) if pp.endswith('.dat')]

for idx, pp in enumerate(paths):
    os.rename(os.path.join(path, pp), os.path.join(path, str(idx)+'.dat'))
