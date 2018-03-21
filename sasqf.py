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
import interruptmove
import dataanalysis

#initailize the simulation
systemini.simini()
# Setup and start the simulation
print('Simulaiton initialized!!')
# print(defview['defenders'].objective['ippool'])
# Create environment and start processes
print('MTD offense and defense is going to START!')
env = simpy.Environment()
defmove = defendmove.defendermove(env)
attmove = attackmove.attackermove(env)
usrmove = usermove.usermove(env)
interruptflag = interruptmove.interruptmove(env, defmove, attmove, usrmove)
# env.process(defmove.defaction(env))
# env.process(attmove.attaction(env))
datacollectandanalysis = dataanalysis.datacollectandanalysis(env, defmove, attmove, usrmove)
env.process(interruptflag.sysplayerinterrupt(env, defmove, attmove, usrmove))
# env.process(datacollectandanalysis.sysdatacollect(env,defmove,attmove,usrmove))
env.run(until=None)
