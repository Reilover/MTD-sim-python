# import sys files
import random
import itertools
import simpy
import numpy
import globalvar
import json

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
# read config.ini file 
with open('config.ini', 'r', encoding='utf-8') as f:
    configfilestr = f.read().strip()
    print(configfilestr)
    configlist = configfilestr.splitlines()
if f.closed:
    print('Config file config.ini read over!')
    pass
else:
    print('Config Error!')
    pass
config = {}
config['defaultset'] = configlist[0].split(' = ')[1]
config['defaultpath'] = configlist[1].split(' = ')[1]
config['userpath'] = configlist[2].split(' = ')[1]
config['simruntimes'] = configlist[3].split(' = ')[1]


#initailize the simulation
if config['defaultset'] == '1':
    print('Default setting is used!')
    systemini.simini('default',{})
    config_json = json.dumps(globalvar.get_value('simulationstate'))
    with open("./defaultconfig.json","w") as f:
        json.dump(config_json,f)
        print('Default Config file set!')
        pass
    pass
    if f.closed:
        print('Default Config file set!')
    pass
else:
    with open('./userconfig.json','r') as f:
        simulationsate = eval(json.load(f))
        pass
    if f.closed:
        print('User Config file read!')
    pass
    systemini.simini('user',simulationsate)
    print('User setting is used!')
    pass



# Setup and start the simulation
print('Simulaiton initialized!!')
usrview = globalvar.get_value('usrview')
fethreadpool = usrview['fecpunum']*usrview['perthreadsize']
beconnpool = usrview['beionum']*usrview['perconnectionsize']
# Create environment and start processes
print('MTD offense and defense process is going to START!')
env = simpy.Environment()
Threadpool = simpy.Container(env, fethreadpool, init=fethreadpool)
Connectionpool = simpy.Container(env, beconnpool, init=beconnpool)
Usrreqpool = simpy.Container(env,usrview['usrnummax'],init=usrview['usrnummax'])



# print(syslink)
defmove = defendmove.defendermove(env)
attmove = attackmove.attackermove(env)
usrmove = usermove.usermove(env,1,'Usr',50)
sermove = servicemove.servicemove(env)
interruptflag = interruptmove.interruptmove(env, defmove, attmove, usrmove)
datacollectandanalysis = dataanalysis.datacollectandanalysis(env, defmove, attmove, usrmove)
env.process(interruptflag.sysplayerinterrupt(env))
env.process(datacollectandanalysis.sysdatacollect(env,defmove,attmove,usrmove))
env.process(usrmove.generaterequest(env,Threadpool,Usrreqpool))
# env.process(sermove.webservice(env,Threadpool,Connectionpool,Usrreqpool,5,3,fecpunum,beionum))
interruptproc = globalvar.get_value('interruptproc')
ser_FEservice_proc_list = []
for i in range(usrview['fecpunum']):
    FEservice = service.service(env,i,'FE',usrview['FEinterval'],usrview['fecpunum'],usrview['beionum'])
    ser_FEservice_proc = env.process(FEservice.serviceaction(env, Threadpool, Connectionpool,Usrreqpool))
    ser_FEservice_proc_list.append(ser_FEservice_proc)
pass
interruptproc['ser_FEservice_proc_list'] = ser_FEservice_proc_list
ser_BEservice_proc_list = []
for i in range(usrview['beionum']):
    BEservice = service.service(env,i,'BE',usrview['BEinterval'],usrview['fecpunum'],usrview['beionum'])
    ser_BEservice_proc = env.process(BEservice.serviceaction(env, Threadpool, Connectionpool,Usrreqpool))
    ser_BEservice_proc_list.append(ser_BEservice_proc)
pass
interruptproc['ser_BEservice_proc_list'] = ser_BEservice_proc_list
globalvar.set_value('interruptproc',interruptproc)
reqtosave = []
globalvar.set_value('reqtosave',reqtosave)
env.run(until=None)
# for i in range(10):

#     print('Simulation runs in %d times',i)
#     pass

