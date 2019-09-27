import sysutil
import globalvar
import numpy
import math
import random
import request

class usermove(object):
    def __init__(self, env, usrid, usrname, usrinterval):
        self.env = env
        self.usrid = usrid
        self.usrname = usrname
        self.usrinterval = usrinterval
        # self.action = env.process(self.usraction(env,syslink))
    pass
    
    def usraction(self,env):

        pass

    
    def generaterequest(self, env, Threadpool, Usrreqpool):
        # requestinterval = self.interval
        reqcount = 0
        requestgenlistsave = []
        FEqueueset = globalvar.get_value('FEqueueset')
        while True:
            if Usrreqpool.level > 0:
                yield Usrreqpool.get(1)
                reqcount = reqcount + 1

                # randomexp = int(random.expovariate(1.0 / self.usrinterval))

                yield env.timeout(int(random.expovariate(1.0 / self.usrinterval)))
                reqid = self.usrname + '_' + str(self.usrid) + '-' + str(reqcount) + '@' + str(env.now)
                usrreq = request.request(reqid, {}, {}, {},-1)
                usrreq.reqgentime['usrgentime'] = env.now
                print("====Usr@%d generate req@%s at time %d===="%(self.usrid,reqid,env.now))
                requestgenlistsave.append(usrreq)
                if Threadpool.level > 0: # if FE's thread pool is underfill, then put request in the service queue
                    yield Threadpool.get(1)
                    # print(usrreq)
                    if FEqueueset['waiting_queue'].isempty():
                        usrreq.reqwaittime['FEwaittime'] = env.now
                        FEqueueset['service_queue'].enqueue(usrreq)
                        # FEqueueset['service_queue'].showQueue()
                        print('FE\'s thread is underfill and FE waiting queue is empty, request %s is saved in FE service queue'%(usrreq.reqid))
                        globalvar.set_value('FEqueueset',FEqueueset)
                        pass
                    else:
                        reqwait = FEqueueset['waiting_queue'].dequeue()
                        FEqueueset['service_queue'].enqueue(reqwait)
                        print('FE\'s thread is underfill and FE waiting queue is not empty, request %s is saved in FE service queue'%(reqwait.reqid))
                        usrreq.reqwaittime['FEwaittime'] = env.now
                        FEqueueset['waiting_queue'].enqueue(usrreq)
                        print('request %s save in FE waiting queue'%(usrreq.reqid))
                        globalvar.set_value('FEqueueset',FEqueueset)
                        pass
                    pass
                else: # else put request in the waiting queue
                    usrreq.reqwaittime['FEwaittime'] = env.now
                    FEqueueset['waiting_queue'].enqueue(usrreq)
                    print('FE\'s thread is full, request %s save in FE waiting queue'%(usrreq.reqid))
                    globalvar.set_value('FEqueueset',FEqueueset)
                    pass
                pass
            else:
                yield env.timeout(1)
                pass
            pass    
        pass


