def get_keys(d, value):
    return [k for k, v in d.items() if v == value]


class Queue():

    def __init__(self):
        self.front = -1
        self.rear = -1
        self.queue = []

    def enqueue(self, ele):
        self.queue.append(ele)
        self.rear = self.rear + 1
        # if len(self.queue) == 1:
        #     self.front = self.front + 1
        #     pass

    def dequeue(self):
        if len(self.queue) == 0:
            print('queue is empty')
            pass
        else:
            self.rear = self.rear - 1
            return self.queue.pop(0)

    def isempty(self):
        return self.front == self.rear

    def qlength(self):
        return len(self.queue)

    def showQueue(self):
        print(self.queue)

def queueini():
    Queueset = {}
    Queueset['service_queue'] = Queue()
    Queueset['waiting_queue'] = Queue()
    return Queueset
