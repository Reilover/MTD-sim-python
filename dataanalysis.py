import sysutil
import globalvar
import simpy

global attview
global defview
global usrview
global datatosave 

class datacollectandanalysis(object):
    def __init__(self, env, defmove, attmove, usrmove):
        self.env = env
        self.defmove = defmove
        self.attmove = attmove
        self.usrmove = usrmove
        pass

    def sysdatacollect(self, env, defmove, attmove, usrmove):
        while True:
            attview = globalvar.get_value('attview')
            attstateintime = []
            if 'attackerwinstate' in attview:
                # attwinstate = attview['attackerwinstate']
                # attstateintime.append(attwinstate)
                # f = open('E:/work/MTDsim/SASQF-EOMTD-Simpy/effresult.txt', 'a+')
                # f.write(str(attwinstate)+' '+str(env.now)+'\r\n')
                # f.close()
                yield env.timeout(1)
                pass
            else:
                yield env.timeout(1)
                pass

            pass
        pass


    pass
