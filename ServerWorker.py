import threading
import time
import subprocess

from logger_setup import LogType, set_logger

class Server():
    def __init__(self, args):
        set_logger(LogType.LT_INFO, "Init ServerWorker")
        try:
            self.comfy_path = args.ComfyUI_path
            self.server_address = args.server_address
            self.port = args.port

            self.app_close = False
            self.server_status = False

            self.process = None

            self.monitorThread = threading.Thread(target=self.monitor_comfyui_process)
            self.monitorThread.start()

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

    def set_app_status(self, status: bool):
        self.app_close = status

    def get_app_status(self):
        return self.app_close

    def set_server_status(self, status: bool):
        self.server_status = status

    def get_server_status(self):
        return self.server_status

    def run_comfyui(self):
        try:
            command = f'{self.comfy_path}\python_embeded\python.exe -s {self.comfy_path}\ComfyUI\main.py --port {self.port}'
            self.process = subprocess.Popen(command.split(), cwd=self.comfy_path, stdout=None,
                                            stderr=subprocess.DEVNULL)  # be aware of the pipe buffer
            self.set_server_status(True)
            set_logger(LogType.LT_INFO, f"Started ComfyUI with PID: {self.process.pid}")

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))


    def monitor_comfyui_process(self):
        while self.get_app_status() != True:
            if self.process==None or self.process.poll() is not None:
                self.set_server_status(False)
                set_logger(LogType.LT_WARNING, "ComfyUI process terminated, restarting...")
                self.run_comfyui()
                time.sleep(40)

            time.sleep(20)

    def close(self):
        try:
            self.set_app_status(True)

            if self.monitorThread !=None:
                self.monitorThread.join()
                self.monitorThread = None

            if self.process is not None:
                if self.process.poll() == None:
                    self.process.kill()

            set_logger(LogType.LT_INFO, 'Close ServerWorker')

        except Exception as e:
            set_logger(LogType.LT_EXCEPTION, str(e))

if __name__ == "__main__":
    from cmd_args import parse_args
    args = parse_args()
    server = Server(args)
    for i in range(40):
        print(i)
        time.sleep(1)
    server.close()