import sysutil
import globalvar
global interruptflags
global interruptproc
interruptflags = globalvar.get_value('interruptflags')
interruptproc = globalvar.get_value('interruptproc')
class interruptmove(object):
    def __init__(self, env, defmove, attmove, usrmove):
        self.env = env
        self.defmove = defmove
        self.attmove = attmove
        self.usrmove = usrmove
        pass

    def interruptcheck(self):
        interruptflags = globalvar.get_value('interruptflags')
        interruptlist_def_off = sysutil.get_keys(interruptflags['def-off'],True)
        interruptlist_off_usr = sysutil.get_keys(interruptflags['off-usr'],True)
        interruptlist_def_usr = sysutil.get_keys(interruptflags['def-usr'],True)
        interruptlist = {}
        interruptlist['def-off'] = interruptlist_def_off
        interruptlist['off-usr'] = interruptlist_off_usr
        interruptlist['def-usr'] = interruptlist_def_usr
        return interruptlist
    
    def proccheck(self):
        interruptproc = globalvar.get_value('interruptproc')
        if 'att_controlandcommand_proc' in interruptproc:
            proc_cc = interruptproc['att_controlandcommand_proc']
        else:
            proc_cc = None
        procdict = {}
        procdict['proc_cc'] = proc_cc

        return procdict
        
    
    def interruptonce(self,env,interrupttype,interruptlist,procs):
        interruptflags = globalvar.get_value('interruptflags')
        for proc in procs:
            if procs[proc] != None and procs[proc].is_alive and procs[proc].target != None:
                print('++++++ Interrupt type: %s using: %s interrupt process: %s at time %d ++++++' % (interrupttype,interruptlist,proc,env.now))
                procs[proc].interrupt(str(interruptlist))
                for interrupt in interruptlist:
                    interruptflags[interrupttype][interrupt] = False
                    pass
                globalvar.set_value('interruptflags',interruptflags)
                yield env.timeout(0)
                pass
            else:
                for interrupt in interruptlist:
                    interruptflags[interrupttype][interrupt] = False
                    pass
                pass
                globalvar.set_value('interruptflags',interruptflags)
        pass

    def sysplayerinterrupt(self, env, defmove, attmove, usrmove):
        while True:
            # print(repr(interruptflags))
            interruptlist = self.interruptcheck()
            procs = self.proccheck()
            for interrupttype in interruptlist:
                if len(interruptlist[interrupttype]) > 0:
                    # print('interrupt type is: %s, interrupts are %s' % (interrupttype,interruptlist[interrupttype]))
                    yield env.process(self.interruptonce(env,interrupttype,interruptlist[interrupttype],procs))
                    pass
                else:
                    continue
                pass
            yield env.timeout(1)   
        pass
    pass