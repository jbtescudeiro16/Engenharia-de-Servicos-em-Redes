import queue

class Stream():
    def __init__(self, name):
        self.name = name
        self.clientList = []
        self.queue = queue.Queue(maxsize=1)

    def recievePacket(self, packet):
        return 