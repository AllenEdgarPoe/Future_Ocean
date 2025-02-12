import threading
import socket
import time
from queue import Queue

from logger_setup import LogType, set_logger

class TcpClient():
    def __init__(self, args):
        self.port = args.port