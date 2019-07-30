# import *.py files
import simpy
import math
import random
import sysutil
# define and initialize parameters
requestgenlistsave = []
requestserlistsave = []
FEqueueset = {}
BEqueueset = {}
FE_cpu_queuelist = []
BE_io_queuelist = []
fecpunum = 2
beionum = 1
perthreadsize = 30
perconnectionsize = 40
FEinterval = 5
BEinterval = 2
usrnummax = 5
Poolset = {}
MAXsimtime = 2000

# defing class and functions
class request(object):
    def __init__(self, reqid, reqgentime, reqwaittime, reqsertime,reqfintime):
        self.reqid = reqid
        self.reqgentime = reqgentime
        self.reqwaittime = reqwaittime
        self.reqsertime = reqsertime
        self.reqfintime = reqfintime
        pass



class usr(object):
    def __init__(self, env, usrid, usrname, usrinterval):
        self.env = env
        self.usrid = usrid
        self.usrname = usrname
        self.usrinterval = usrinterval
    pass

    def generaterequest(self, env, Threadpool, Usrreqpool):
        # requestinterval = self.interval
        reqcount = 0
        while True:
            if Usrreqpool.level > 0:
                yield Usrreqpool.get(1)
                reqcount = reqcount + 1
                yield self.env.timeout(int(random.expovariate(1.0 / self.usrinterval)))
                reqid = self.usrname + '_' + str(self.usrid) + '-' + str(reqcount) + '@' + str(self.env.now)
                usrreq = request(reqid, {}, {}, {},-1)
                usrreq.reqgentime['usrgentime'] = self.env.now
                requestgenlistsave.append(usrreq)
                if Threadpool.level > 0: # if FE's thread pool is underfill, then put request in the service queue
                    yield Threadpool.get(1)
                    # print(usrreq)
                    if FEqueueset['waiting_queue'].isempty():
                        usrreq.reqwaittime['FEwaittime'] = self.env.now
                        FEqueueset['service_queue'].enqueue(usrreq)
                        # FEqueueset['service_queue'].showQueue()
                        print('FE\'s thread is underfill and FE waiting queue is empty, request %s is saved in FE service queue'%(usrreq.reqid))
                        pass
                    else:
                        reqwait = FEqueueset['waiting_queue'].dequeue()
                        FEqueueset['service_queue'].enqueue(reqwait)
                        print('FE\'s thread is underfill and FE waiting queue is not empty, request %s is saved in FE service queue'%(reqwait.reqid))
                        usrreq.reqwaittime['FEwaittime'] = self.env.now
                        FEqueueset['waiting_queue'].enqueue(usrreq)
                        print('request %s save in FE waiting queue'%(usrreq.reqid))
                        pass
                    pass
                else: # else put request in the waiting queue
                    usrreq.reqwaittime['FEwaittime'] = self.env.now
                    FEqueueset['waiting_queue'].enqueue(usrreq)
                    print('FE\'s thread is full, request %s save in FE waiting queue'%(usrreq.reqid))
                    pass
                pass
            else:
                yield self.env.timeout(1)
                pass
            pass    
        pass

class service(object):
    def __init__(self, env, serid, sertype, serinterval):
        self.env = env
        self.serid = serid
        self.sername = sertype + '-' + str(serid)
        self.sertype = sertype
        self.serinterval = serinterval
        pass
    
    def servicecontrol(self):
        if FEqueueset['service_queue'].isempty() == False:
            # print(FEqueueset['service_queue'].isempty())
            for i in range(FEqueueset['service_queue'].qlength()):
                # print(i)
                fereqdis = FEqueueset['service_queue'].dequeue()
                # FEqueueset['service_queue'].showQueue()
                # print(fereqdis)
                indexfereqdis = int(random.uniform(0,fecpunum))
                print('request %s distribute to FE-%d'%(fereqdis.reqid,indexfereqdis))
                FE_cpu_queuelist[indexfereqdis]['service_queue'].enqueue(fereqdis)
                print('FE-cpu distribute finish')
                pass
            pass
        if BEqueueset['service_queue'].isempty() == False:
            for i in range(BEqueueset['service_queue'].qlength()):
                bereqdis = BEqueueset['service_queue'].dequeue()
                indexbereqdis = int(random.uniform(0,beionum-1))
                print('request %s distribute to FE-%d'%(bereqdis.reqid,indexbereqdis))
                BE_io_queuelist[indexbereqdis]['service_queue'].enqueue(bereqdis)
                print('BE-io distribute finish')
                pass
            pass
            
        pass

    def serviceaction(self, env, Threadpool, Connectionpool,Usrreqpool):
        # print('+++ starting %s service at time %d +++'%(self.sername, env.now))
        while True:
            self.servicecontrol()
            if self.sertype == 'FE':
                # print(self.sername)
                # print(FE_cpu_queuelist[self.serid]['service_queue'])
                if FE_cpu_queuelist[self.serid - 1]['service_queue'].isempty() == False:
                    # FE_cpu_queuelist[self.serid - 1]['service_queue'].showQueue()
                    reqfeser = FE_cpu_queuelist[self.serid - 1]['service_queue'].dequeue()
                    # print(reqfeser.reqwaittime)
                    reqfeser.reqwaittime['FEwaittime'] = self.env.now - reqfeser.reqwaittime['FEwaittime']
                    reqfeser.reqsertime['FEsertime'] = self.env.now
                    yield env.timeout(self.serinterval)
                    reqfeser.reqsertime['FEsertime'] = self.env.now - reqfeser.reqsertime['FEsertime']
                    print('%s finish service request %s at time %d, using %d service time'%(self.sername,reqfeser.reqid,self.env.now,reqfeser.reqsertime['FEsertime']))
                    # requestserlistsave.append(reqserfinish)
                    if Connectionpool.level > 0: # if FE's thread pool is underfill, then put request in the service queue
                        yield Connectionpool.get(1)

                        if BEqueueset['waiting_queue'].isempty():
                            reqfeser.reqwaittime['BEwaittime'] = self.env.now
                            BEqueueset['service_queue'].enqueue(reqfeser)
                            print('BE\'s connection is underfill and BE waiting queue is empty, request %s is saved in FE service queue'%(reqfeser.reqid))
                            pass
                        else:
                            reqwait = BEqueueset['waiting_queue'].dequeue()
                            BEqueueset['service_queue'].enqueue(reqwait)
                            print('BE\'s connection is underfill and BE waiting queue is not empty, request %s is saved in BE service queue'%(reqwait.reqid))
                            BEqueueset['waiting_queue'].enqueue(reqfeser)
                            print('request %s save in BE waiting queue'%(reqfeser.reqid))
                            pass
                    else: # else put request in the waiting queue
                        reqfeser.reqwaittime['BEwaittime'] = self.env.now
                        BEqueueset['waiting_queue'].enqueue(reqfeser)
                        print('BE\'s connection is full, request %s save in BE waiting queue'%(reqfeser.reqid))
                        pass
                    pass
                else:
                    yield env.timeout(1)
                    pass
                pass
            elif self.sertype == 'BE':
                # print('service BE')
                # BE_io_queuelist[self.serid - 1]['service_queue'].showQueue()
                if BE_io_queuelist[self.serid - 1]['service_queue'].isempty() == False:
                    reqbeser = BE_io_queuelist[self.serid - 1]['service_queue'].dequeue()
                    reqbeser.reqwaittime['BEwaittime'] = self.env.now - reqbeser.reqwaittime['BEwaittime']
                    reqbeser.reqsertime['BEsertime'] = self.env.now
                    yield env.timeout(self.serinterval)
                    reqbeser.reqsertime['BEsertime'] = self.env.now - reqbeser.reqsertime['BEsertime']
                    print('%s finish service request %s at time %d, using %d service time'%(self.sername,reqbeser.reqid,self.env.now,reqbeser.reqsertime['BEsertime']))
                    reqbeser.reqfintime = self.env.now
                    requestserlistsave.append(reqbeser)
                    yield Threadpool.put(1)
                    yield Connectionpool.put(1)
                    yield Usrreqpool.put(1)
                    pass
                else:
                    yield env.timeout(1)
                    pass
                pass
            else:
                print('Error Service type')
                pass

            pass
                
                # yield servicepool.put(1)
        pass
    pass

def Queueini():
    # define and initialized queues 
    Queueset = {}
    Queueset['service_queue'] = sysutil.Queue()
    Queueset['waiting_queue'] = sysutil.Queue()
    return Queueset

def webservice(env,Threadpool,Connectionpool,Usrreqpool,FEinterval,BEinterval):
    for i in range(fecpunum):
        FEservice = service(env,i,'FE',FEinterval)
        env.process(FEservice.serviceaction(env, Threadpool, Connectionpool,Usrreqpool))
        pass
    
    for i in range(beionum):
        BEservice = service(env,i,'BE',BEinterval)
        env.process(BEservice.serviceaction(env, Threadpool, Connectionpool,Usrreqpool))
        pass
    
    pass

    

    
# Setup and start the simulation
print('Web service simulations')

# Create environment and start processes
FEqueueset = Queueini()
BEqueueset = Queueini()

for i in range(fecpunum):
    FE_cpu_queueset = Queueini()
    FE_cpu_queuelist.append(FE_cpu_queueset)
    pass
for i in range(beionum):
    BE_io_queueset = Queueini()
    BE_io_queuelist.append(BE_io_queueset)
    pass


env = simpy.Environment()
Threadpool = simpy.Container(env, fecpunum*perthreadsize, init=fecpunum*perthreadsize)
Connectionpool = simpy.Container(env, beionum*perconnectionsize, init=beionum*perconnectionsize)
Usrreqpool = simpy.Container(env,usrnummax,init=usrnummax)
Poolset['Threadpool'] = Threadpool
Poolset['Connectionpool'] = Connectionpool
Usr = usr(env,1,'Usr',1)
env.process(Usr.generaterequest(env,Threadpool,Usrreqpool))
webservice(env,Threadpool,Connectionpool,Usrreqpool,FEinterval,BEinterval)

# Execute!
env.run(until=MAXsimtime)

# print(requestserlistsave)
# print(requestgenlistsave)