import sysutil
import globalvar
import random

global defview
global interruptflags
defview = globalvar.get_value('defview')
interruptflags = globalvar.get_value('interruptflags')

class defendermove(object):
    def __init__(self, env):
        self.env = env
        self.action = env.process(self.defaction(env))
        # self.process = env.process(self.defaction(env))
        # env.process(self.definterrupt(env,''))

    def defaction(self, env):
        defview = globalvar.get_value('defview')
        ipfreq = defview['defenders'].objective['ipfreq']
        portfreq = defview['defenders'].objective['portfreq']
        osfreq = defview['defenders'].objective['osfreq']
        serviceplatformfreq = defview['defenders'].objective['servicefreq']
        defstate = {}  # saving defense states
        # initializing need to act defense\
        defstate['needdoneact'] = {}
        defstate['needdoneact']['ipmutation'] = False
        defstate['needdoneact']['osmutation'] = False
        defstate['needdoneact']['portmutation'] = False
        defstate['needdoneact']['serviceplatformmutation'] = False
        # initializing action frequency or period, trigger point is offer in next version
        defstate['ipfreq'] = ipfreq[1]
        defstate['portfreq'] = portfreq[1]
        defstate['osfreq'] = osfreq[0]
        defstate['serviceplatformfreq'] = serviceplatformfreq[0]
        # initializing defense action holding time
        defstate['defholdingtime'] = {}
        while True:
            needdoneact = self.defactioncheck(env, defstate)
            if len(needdoneact) > 0:
                # print('++++++ defender need done action at time %d including: %s ++++++' %
                #       (env.now, repr(needdoneact)))
                yield env.process(self.defonce(env, needdoneact, defstate))
                pass


            defactiontime = 1
            yield env.timeout(defactiontime)
        pass

    # given the env time and defense states to set need done action flags and return need done action list
    def defactioncheck(self, env, defstate):
        if env.now % defstate['ipfreq'] == 0 and env.now != 0:
            defstate['needdoneact']['ipmutation'] = True
            pass
        if env.now % defstate['portfreq'] == 0 and env.now != 0:
            # defstate['needdoneact']['portmutation'] = True
            pass
        if env.now % defstate['osfreq'] == 0 and env.now != 0:
            defstate['needdoneact']['osmutation'] = True
            pass
        if env.now % defstate['serviceplatformfreq'] == 0 and env.now != 0:
            # defstate['needdoneact']['serviceplatformmutation'] = True
            pass
        needdoneact = sysutil.get_keys(defstate['needdoneact'], True)
        return needdoneact

    def defonce(self, env, deftype, defstate):
        deftypeset = set(deftype)
        ipportset = ['ipmutation', 'portmutation']
        ipportset = set(ipportset)
        iposset = ['ipmutation', 'osmutation']
        iposset = set(iposset)
        ipserviceplatform = ['ipmutation', 'serviceplatformmutation']
        ipserviceplatform = set(ipserviceplatform)
        osserviceplatform = ['osmutation', 'serviceplatformmutation']
        osserviceplatform = set(osserviceplatform)
        if 'ipmutation' in deftype and len(deftype) == 1:
            ipholdingtime = 3
            yield env.process(self.ipmutation(env, ipholdingtime, defstate))
            pass
        elif 'protmutation' in deftype and len(deftype) == 1:
            pass
        elif 'osmutation' in deftype and len(deftype) == 1:
            # print('----os type need move----')
            osholdingtime = 5
            yield env.process(self.osmutation(env, osholdingtime, defstate))
            pass
        elif 'serviceplatformmutation' in deftype and len(deftype) == 1:
            pass
        elif ipportset.issubset(deftypeset) and len(deftype) == 2:
            pass
        elif iposset.issubset(deftypeset) and len(deftype) == 2:
            ipholdingtime = 3
            osholdingtime = 5
            ipmutation = env.process(self.ipmutation(env, ipholdingtime, defstate))
            osmutation = env.process(self.osmutation(env, osholdingtime, defstate))
            yield ipmutation & osmutation
            pass
        elif ipserviceplatform.issubset(deftypeset) and len(deftype) == 2:
            ipholdingtime = 3
            serviceplatformholdingtime = 5
            ipmutation = env.process(self.ipmutation(env, ipholdingtime, defstate))
            serviceplatformmutation = env.process(self.serviceplatformmutation(env, serviceplatformholdingtime, defstate))
            yield ipmutation & serviceplatformmutation
            pass
        elif osserviceplatform.issubset(deftypeset) and len(deftype) == 2:
            osholdingtime = 5
            serviceplatformholdingtime = 5
            osmutation = env.process(self.osmutation(env, osholdingtime, defstate))
            serviceplatformmutation = env.process(self.serviceplatformmutation(env, serviceplatformholdingtime, defstate))
            yield osmutation & serviceplatformmutation
            pass
        else:
            print('++++++ Error defense type, please check! ++++++')
            pass
        pass

    def deftypesetinit(self):
        pass

    def ipmutation(self, env, ipholdingtime, defstate):  # ip muatation/hopping technique
        #
        defview = globalvar.get_value('defview')
        ippool = defview['defenders'].objective['ippool']
        # print(env.now % ipfreq[0])
        for nodeindex in range(len(defview['servernodes'])):
            if 'ipmutation' in defview['servernodes'][nodeindex].nodedeftype:
                ipbase = defview['servernodes'][nodeindex].ipbase
                ipold = defview['servernodes'][nodeindex].ip
                ipnew = ipbase + round(random.uniform(1, ippool[0]))
                if ipnew >= 256:
                    ipnew = ipnew - 256
                pass
                defview['servernodes'][nodeindex].ip = ipnew
                print("++++++ Defender Action! node: %s IP address in ip_base: %d at time: %d form ip_address_old: %d to ip_address_new: %d in ip_pool: %d ++++++" %
                      (defview['servernodes'][nodeindex].nodeid, ipbase, env.now, ipold, ipnew, ippool[0]))
                # yield env.timeout(ipholdingtime)
                defstate['needdoneact']['ipmutation'] = False
                # when ip mutation successed, cause an interruption which will catch by the attacker move and cause an expection as well.
                globalvar.set_value('defview',defview)
                yield env.process(self.definterrupt(env, ipholdingtime, 'ipmutation'))
                pass
            else:
                print('++++++ Node %s does not enable IP mutation defense! ++++++')
                yield env.timeout(1)
                pass
            pass

    # port muatation/hopping technique
    def portmutation(self, env, portholdingtime, defstate):
        pass

    def osmutation(self, env, osholdingtime, defstate):  # Os muatation technique
        defview = globalvar.get_value('defview')
        ospool = defview['defenders'].objective['ospool']
        # print('++++++ Os mutation pool is %s ++++++' % (repr(ospool)))
        for nodeindex in range(len(defview['servernodes'])):
            if 'osmutation' in defview['servernodes'][nodeindex].nodedeftype:
                osold = defview['servernodes'][nodeindex].os
                osnew = ospool[round(random.uniform(0, len(ospool) - 1))]
                defview['servernodes'][nodeindex].os = osnew
                if defview['servernodes'][nodeindex].os == 'Linux' or defview['servernodes'][nodeindex].os == 'Unix':
                    if defview['servernodes'][nodeindex].serviceplatform == 'IIS':
                        defview['servernodes'][nodeindex].serviceplatform = defview['defenders'].objective['servicepool']['Linux']['HTTP'][round(
                            random.uniform(0, len(defview['defenders'].objective['servicepool']['Linux']['HTTP'])-1))]
                        pass
                    pass
                # first we don't consider os transform time (os off-line time) and self-clearance
                # defview['servernodes'][nodeindex].nodeworkingstate = 'transforming'
                defview['servernodes'][nodeindex].nodebackdoor = False
                print('++++++ Defender Action! node: %s Os type at time: %d form Os_type_old: %s to Os_tyoe_new: %s in Os_pool: %s ++++++' %
                      (defview['servernodes'][nodeindex].nodeid, env.now, osold, osnew, repr(ospool)))
                # yield env.timeout(osholdingtime)
                defstate['needdoneact']['osmutation'] = False
                # defview['servernodes'][nodeindex].nodeworkingstate = 'up'
                globalvar.set_value('defview',defview)
                yield env.process(self.definterrupt(env, osholdingtime, 'osmutation'))
                pass
            pass
        pass

    # service platform muatation technique
    def serviceplatformmutation(self, env, serviceplatformholdingtime, defstate):
        pass

    def definterrupt(self, env, holdingtime, interrupttype):
        interruptflags = globalvar.get_value('interruptflags')
        if interrupttype == 'ipmutation':
            interruptflags['def-off']['ipmutation'] = True
            # print('Defense aciton %s interrupt! interrupt flag is %s'%(interrupttype,interruptflags['def-off']['ipmutation']))
            globalvar.set_value('interruptflags',interruptflags)
            yield env.timeout(0)
            pass
        elif interrupttype == 'portmutation':
            pass
        elif interrupttype == 'osmutation':
            interruptflags['def-off']['osmutation'] = True
            globalvar.set_value('interruptflags',interruptflags)
            yield env.timeout(0)
            pass
        elif interrupttype == 'serviceplatformmutation':
            interruptflags['def-off']['serviceplatformmutation'] = True
            globalvar.set_value('interruptflags',interruptflags)
            yield env.timeout(0)
            pass
        else:
            yield env.timeout(0)
            pass
        pass