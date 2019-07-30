import sysutil
import globalvar
import numpy
import math
import simpy
import random

class service(object):
    def __init__(self, env, serid, sertype, serinterval, fecpunum, beionum):
        self.env = env
        self.serid = serid
        self.sername = sertype + '-' + str(serid)
        self.sertype = sertype
        self.serinterval = serinterval
        self.fecpunum = fecpunum
        self.beionum = beionum

        pass
    
    def servicecontrol(self):
        FEqueueset = globalvar.get_value('FEqueueset')
        BEqueueset = globalvar.get_value('BEqueueset')
        FE_cpu_queuelist = globalvar.get_value('FE_cpu_queuelist')
        BE_io_queuelist = globalvar.get_value('BE_io_queuelist')
        if FEqueueset['service_queue'].isempty() == False:
            # print(FEqueueset['service_queue'].isempty())
            for i in range(FEqueueset['service_queue'].qlength()):
                # print(i)
                fereqdis = FEqueueset['service_queue'].dequeue()
                # FEqueueset['service_queue'].showQueue()
                # print(fereqdis)
                indexfereqdis = int(random.uniform(0,self.fecpunum))
                print('request %s distribute to FE-%d'%(fereqdis.reqid,indexfereqdis))
                FE_cpu_queuelist[indexfereqdis]['service_queue'].enqueue(fereqdis)
                print('FE-cpu distribute finish')
                pass
            pass
        if BEqueueset['service_queue'].isempty() == False:
            for i in range(BEqueueset['service_queue'].qlength()):
                bereqdis = BEqueueset['service_queue'].dequeue()
                indexbereqdis = int(random.uniform(0,self.beionum-1))
                print('request %s distribute to FE-%d'%(bereqdis.reqid,indexbereqdis))
                BE_io_queuelist[indexbereqdis]['service_queue'].enqueue(bereqdis)
                print('BE-io distribute finish')
                pass
            pass
            
        pass

    def serviceaction(self, env, Threadpool, Connectionpool,Usrreqpool):
        # print('+++ starting %s service at time %d +++'%(self.sername, env.now))
        FEqueueset = globalvar.get_value('FEqueueset')
        BEqueueset = globalvar.get_value('BEqueueset')
        FE_cpu_queuelist = globalvar.get_value('FE_cpu_queuelist')
        BE_io_queuelist = globalvar.get_value('BE_io_queuelist')
        while True:
            self.servicecontrol()
            if self.sertype == 'FE':
            # print(self.sername)
            # print(FE_cpu_queuelist[self.serid]['service_queue'])
                try:
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
                        globalvar.set_value('FE_cpu_queuelist',FE_cpu_queuelist)
                        if Connectionpool.level > 0: # if FE's thread pool is underfill, then put request in the service queue
                            yield Connectionpool.get(1)

                            if BEqueueset['waiting_queue'].isempty():
                                reqfeser.reqwaittime['BEwaittime'] = self.env.now
                                BEqueueset['service_queue'].enqueue(reqfeser)
                                print('BE\'s connection is underfill and BE waiting queue is empty, request %s is saved in FE service queue'%(reqfeser.reqid))
                                globalvar.set_value('BEqueueset',BEqueueset)
                                pass
                            else:
                                reqwait = BEqueueset['waiting_queue'].dequeue()
                                BEqueueset['service_queue'].enqueue(reqwait)
                                print('BE\'s connection is underfill and BE waiting queue is not empty, request %s is saved in BE service queue'%(reqwait.reqid))
                                BEqueueset['waiting_queue'].enqueue(reqfeser)
                                print('request %s save in BE waiting queue'%(reqfeser.reqid))
                                globalvar.set_value('BEqueueset',BEqueueset)
                                pass
                        else: # else put request in the waiting queue
                            reqfeser.reqwaittime['BEwaittime'] = self.env.now
                            BEqueueset['waiting_queue'].enqueue(reqfeser)
                            print('BE\'s connection is full, request %s save in BE waiting queue'%(reqfeser.reqid))
                            globalvar.set_value('BEqueueset',BEqueueset)
                            pass
                        pass
                    else:
                        yield env.timeout(1)
                        pass
                    pass
                except simpy.Interrupt:
                    try:
                        print('%s Service is interrupt at time %d'%(self.sertype,env.now))
                        print('The interrupt is %s'%(env.active_process.value))
                        yield env.timeout(300)
                        pass
                    except simpy.Interrupt:
                        print('%s Service is already interrupted at time %d'%(self.sertype,env.now))
                        pass
                    pass
                pass
            elif self.sertype == 'BE':
                # print('service BE')
                # BE_io_queuelist[self.serid - 1]['service_queue'].showQueue()
                try:
                    if BE_io_queuelist[self.serid - 1]['service_queue'].isempty() == False:
                        reqbeser = BE_io_queuelist[self.serid - 1]['service_queue'].dequeue()
                        reqbeser.reqwaittime['BEwaittime'] = self.env.now - reqbeser.reqwaittime['BEwaittime']
                        reqbeser.reqsertime['BEsertime'] = self.env.now
                        yield env.timeout(self.serinterval)
                        reqbeser.reqsertime['BEsertime'] = self.env.now - reqbeser.reqsertime['BEsertime']
                        print('%s finish service request %s at time %d, using %d service time'%(self.sername,reqbeser.reqid,self.env.now,reqbeser.reqsertime['BEsertime']))
                        reqbeser.reqfintime = self.env.now
                        # requestserlistsave.append(reqbeser)
                        globalvar.set_value('BE_io_queuelist',BE_io_queuelist)
                        yield Threadpool.put(1)
                        yield Connectionpool.put(1)
                        yield Usrreqpool.put(1)
                        pass
                    else:
                        yield env.timeout(1)
                        pass
                    pass
                
                    pass
                except simpy.Interrupt:
                    try:
                        print('%s Service is interrupt at time %d'%(self.sertype,env.now))
                        yield env.timeout(0)
                        pass
                    except simpy.Interrupt:
                        print('%s Service is already interrupted at time %d'%(self.sertype,env.now))
                        pass

                    pass
            else:
                    print('Error Service type')
                    pass

            pass    
                # yield servicepool.put(1)
        pass
    pass





