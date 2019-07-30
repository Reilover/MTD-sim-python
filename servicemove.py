import sysutil
import globalvar
import numpy
import math
import random
import service

class servicemove(object):
    def __init__(self, env):
        self.env = env
        # self.syslink = syslink
        # self.action = env.process(self.webservice(env, syslink))
    pass

    def webservice(self,env,Threadpool,Connectionpool,Usrreqpool,FEinterval,BEinterval,fecpunum,beionum):
        # fecpunum = globalvar.get_value('fecpunum')
        # beionum = globalvar.get_value('beionum')
        for i in range(fecpunum):
            FEservice = service.service(env,i,'FE',FEinterval,fecpunum,beionum)
            env.process(FEservice.serviceaction(env, Threadpool, Connectionpool,Usrreqpool))
        pass
    
        for i in range(beionum):
            BEservice = service.service(env,i,'BE',BEinterval,fecpunum,beionum)
            env.process(BEservice.serviceaction(env, Threadpool, Connectionpool,Usrreqpool))
            pass
        pass
    
        


