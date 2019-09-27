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

def class_to_dict(obj):
    '''把对象(支持单个对象、list、set)转换成字典'''
    is_list = obj.__class__ == [].__class__
    is_set = obj.__class__ == set().__class__
     
    if is_list or is_set:
        obj_arr = []
        for o in obj:
            #把Object对象转换成Dict对象
            dict = {}
            dict.update(o.__dict__)
            obj_arr.append(dict)
        return obj_arr
    else:
        dict = {}
        dict.update(obj.__dict__)
        return dict

def props_with_(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value):
            pr[name] = value
    return pr
