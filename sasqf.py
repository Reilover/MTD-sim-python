# import sys files
import random
import itertools
import simpy
import numpy
import globalvar

globalvar._init() # define global vars
# import self-defined files
import sysutil
import systemini
import attackmove
import defendmove
import usermove
import servicemove
import interruptmove
import dataanalysis
import service
#initailize the simulation
systemini.simini()
# Setup and start the simulation
print('Simulaiton initialized!!')
fecpunum = 1
perthreadsize = 30
beionum = 1
perconnectionsize = 40
usrnummax = 500
Poolset = {}
FEinterval = 5
BEinterval = 3
# Create environment and start processes
print('MTD offense and defense process is going to START!')
env = simpy.Environment()
Threadpool = simpy.Container(env, fecpunum*perthreadsize, init=fecpunum*perthreadsize)
Connectionpool = simpy.Container(env, beionum*perconnectionsize, init=beionum*perconnectionsize)
Usrreqpool = simpy.Container(env,usrnummax,init=usrnummax)
Poolset['Threadpool'] = Threadpool
Poolset['Connectionpool'] = Connectionpool
# print(syslink)
defmove = defendmove.defendermove(env)
attmove = attackmove.attackermove(env)
usrmove = usermove.usermove(env,1,'Usr',10)
sermove = servicemove.servicemove(env)
interruptflag = interruptmove.interruptmove(env, defmove, attmove, usrmove)
datacollectandanalysis = dataanalysis.datacollectandanalysis(env, defmove, attmove, usrmove)
env.process(interruptflag.sysplayerinterrupt(env))
env.process(datacollectandanalysis.sysdatacollect(env,defmove,attmove,usrmove))
env.process(usrmove.generaterequest(env,Threadpool,Usrreqpool))
# env.process(sermove.webservice(env,Threadpool,Connectionpool,Usrreqpool,5,3,fecpunum,beionum))
interruptproc = globalvar.get_value('interruptproc')
ser_FEservice_proc_list = []
for i in range(fecpunum):
    FEservice = service.service(env,i,'FE',FEinterval,fecpunum,beionum)
    ser_FEservice_proc = env.process(FEservice.serviceaction(env, Threadpool, Connectionpool,Usrreqpool))
    ser_FEservice_proc_list.append(ser_FEservice_proc)
pass
interruptproc['ser_FEservice_proc_list'] = ser_FEservice_proc_list
ser_BEservice_proc_list = []
for i in range(beionum):
    BEservice = service.service(env,i,'BE',BEinterval,fecpunum,beionum)
    ser_BEservice_proc = env.process(BEservice.serviceaction(env, Threadpool, Connectionpool,Usrreqpool))
    ser_BEservice_proc_list.append(ser_BEservice_proc)
pass
interruptproc['ser_BEservice_proc_list'] = ser_BEservice_proc_list
globalvar.set_value('interruptproc',interruptproc)
env.run(until=3000)
