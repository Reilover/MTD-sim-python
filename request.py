class request(object):
    def __init__(self, reqid, reqgentime, reqwaittime, reqsertime,reqfintime):
        self.reqid = reqid
        self.reqgentime = reqgentime
        self.reqwaittime = reqwaittime
        self.reqsertime = reqsertime
        self.reqfintime = reqfintime
        pass