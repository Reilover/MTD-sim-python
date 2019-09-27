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
    
    def servicecontrol(self,sertype):
        FEqueueset = globalvar.get_value('FEqueueset')
        BEqueueset = globalvar.get_value('BEqueueset')
        FE_cpu_queuelist = globalvar.get_value('FE_cpu_queuelist')
        BE_io_queuelist = globalvar.get_value('BE_io_queuelist')
            
        if sertype == 'FE' and FEqueueset['service_queue'].isempty() == False:
            # print(FEqueueset['service_queue'].isempty())
            for i in range(FEqueueset['service_queue'].qlength()):
                # print(i)
                fereqdis = FEqueueset['service_queue'].dequeue()
                # FEqueueset['service_queue'].showQueue()
                # print(fereqdis)
                indexfereqdis = int(random.uniform(0,self.fecpunum))
                print('request %s distribute to FE-%d'%(fereqdis.reqid,indexfereqdis))
                FE_cpu_queuelist[indexfereqdis]['service_queue'].enqueue(fereqdis)
                
                pass
            globalvar.set_value('FEqueueset',FEqueueset)
            globalvar.set_value('FE_cpu_queuelist',FE_cpu_queuelist)
            print('FE-cpu distribute finish')
            pass
        if sertype == 'BE' and BEqueueset['service_queue'].isempty() == False:
            for i in range(BEqueueset['service_queue'].qlength()):
                bereqdis = BEqueueset['service_queue'].dequeue()
                indexbereqdis = int(random.uniform(0,self.beionum))
                print('request %s distribute to FE-%d'%(bereqdis.reqid,indexbereqdis))
                BE_io_queuelist[indexbereqdis]['service_queue'].enqueue(bereqdis)
                
                pass
            pass
            globalvar.set_value('BEqueueset',BEqueueset)
            globalvar.set_value('BE_io_queuelist',BE_io_queuelist)
            print('BE-io distribute finish')
        pass

    def serviceaction(self, env, Threadpool, Connectionpool,Usrreqpool):
        # print('+++ starting %s service at time %d +++'%(self.sername, env.now))
        
        while True:
            self.servicecontrol(self.sertype)
            FEqueueset = globalvar.get_value('FEqueueset')
            BEqueueset = globalvar.get_value('BEqueueset')
            FE_cpu_queuelist = globalvar.get_value('FE_cpu_queuelist')
            BE_io_queuelist = globalvar.get_value('BE_io_queuelist')
            if self.sertype == 'FE':
            # print(self.sername)
            # print(FE_cpu_queuelist[self.serid]['service_queue'])
                try:
                    if FE_cpu_queuelist[self.serid - 1]['service_queue'].isempty() == False:
                    # FE_cpu_queuelist[self.serid - 1]['service_queue'].showQueue()
                        reqfeser = FE_cpu_queuelist[self.serid - 1]['service_queue'].dequeue()
                        # print(reqfeser.reqwaittime)
                        reqfeser.reqwaittime['FEwaittime'] = env.now - reqfeser.reqwaittime['FEwaittime']
                        reqfeser.reqsertime['FEsertime'] = env.now
                        # yield env.timeout(self.serinterval)
                        servicetime = int(random.expovariate(1.0 / self.serinterval))
                        if servicetime == 0:
                            servicetime = 1
                            pass
                        yield env.timeout(servicetime)
                        reqfeser.reqsertime['FEsertime'] = env.now - reqfeser.reqsertime['FEsertime']
                        print('%s finish service request %s at time %d, using %d service time'%(self.sername,reqfeser.reqid,env.now,reqfeser.reqsertime['FEsertime']))
                        # requestserlistsave.append(reqserfinish)
                        globalvar.set_value('FE_cpu_queuelist',FE_cpu_queuelist)
                        if Connectionpool.level > 0: # if BE's connection's pool is underfill, then put request in the service queue
                            yield Connectionpool.get(1)

                            if BEqueueset['waiting_queue'].isempty():
                                reqfeser.reqwaittime['BEwaittime'] = env.now
                                BEqueueset['service_queue'].enqueue(reqfeser)
                                print('BE\'s connection is underfill and BE waiting queue is empty, request %s is saved in BE service queue'%(reqfeser.reqid))
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
                            reqfeser.reqwaittime['BEwaittime'] = env.now
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
                        mtdholdingtime = {}
                        mtdholdingtime['ipmutation'] = 30
                        mtdholdingtime['osmutation'] = 100
                        mtdholdingtime['serviceplatformmutation'] = 50
                        print('%s Service is interrupt at time %d'%(self.sertype,env.now))
                        interruptcause = globalvar.get_value('interruptcause')
                        if interruptcause[self.sertype]:
                            interruptlist = interruptcause['interruptlist']
                            if len(interruptlist) > 1:
                                holdingtimelist = []
                                for interrupt in interruptlist:
                                    holdingtimelist.append(mtdholdingtime[interrupt])
                                    pass 
                                holdingtimelist.sort(reverse=True)
                                maxholdingtime = holdingtimelist[0]
                                interrupttime = {}
                                interrupttime['start'] = env.now
                                interrupttime['hold'] = maxholdingtime
                                interrupttime['end'] = env.now + maxholdingtime
                                globalvar.set_value('interrupttime',interrupttime)
                                yield env.timeout(maxholdingtime)
                                pass
                            else:
                                interrupttime = {}
                                interrupttime['start'] = env.now
                                interrupttime['hold'] = mtdholdingtime[interruptlist[0]]
                                interrupttime['end'] = env.now + mtdholdingtime[interruptlist[0]]
                                globalvar.set_value('interrupttime',interrupttime)
                                yield env.timeout(mtdholdingtime[interruptlist[0]])
                                pass
                            pass
                        pass
                    except simpy.Interrupt:
                        interrupttime = globalvar.get_value('interrupttime')
                        intneedtime = interrupttime['end'] - env.now
                        print('%s Service is already interrupted at time %d and need another %d time to recover'%(self.sertype,env.now,intneedtime))
                        try:
                            yield env.timeout(intneedtime)
                            pass
                        except simpy.Interrupt:
                            print('%s Service is already interrupted at time %d and need another %d time to recover'%(self.sertype,env.now,intneedtime))
                            pass
                        pass
                    pass
                pass
            elif self.sertype == 'BE':
                # print('service BE')
                # BE_io_queuelist[self.serid - 1]['service_queue'].showQueue()
                try:
                    if BE_io_queuelist[self.serid - 1]['service_queue'].isempty() == False:
                        reqbeser = BE_io_queuelist[self.serid - 1]['service_queue'].dequeue()
                        reqbeser.reqwaittime['BEwaittime'] = env.now - reqbeser.reqwaittime['BEwaittime']
                        reqbeser.reqsertime['BEsertime'] = env.now
                        # yield env.timeout(self.serinterval)
                        servicetime = int(random.expovariate(1.0 / self.serinterval))
                        if servicetime == 0:
                            servicetime = 1
                            pass
                        yield env.timeout(servicetime)
                        reqbeser.reqsertime['BEsertime'] = env.now - reqbeser.reqsertime['BEsertime']
                        print('%s finish service request %s at time %d, using %d service time'%(self.sername,reqbeser.reqid,env.now,reqbeser.reqsertime['BEsertime']))
                        reqbeser.reqfintime = env.now
                        # requestserlistsave.append(reqbeser)
                        globalvar.set_value('BE_io_queuelist',BE_io_queuelist)
                        reqtosavelist = globalvar.get_value('reqtosave')
                        reqtosavelist.append(reqbeser)
                        globalvar.set_value('reqtosave',reqtosavelist)
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
                        yield env.timeout(1)
                        pass
                    except simpy.Interrupt:
                        print('%s Service is already interrupted at time %d'%(self.sertype,env.now))
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





