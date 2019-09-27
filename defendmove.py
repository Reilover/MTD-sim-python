import sysutil
import globalvar
import random

global defview
global interruptflags
# defview = globalvar.get_value('defview')
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
        # defstate['ipfreq'] = ipfreq[1]
        # defstate['portfreq'] = portfreq[1]
        # defstate['osfreq'] = osfreq[0]
        # defstate['serviceplatformfreq'] = serviceplatformfreq[0]
        nomtd = 1000000000000000000
        # defstate['ipfreq'] = nomtd
        # defstate['portfreq'] = nomtd
        # defstate['osfreq'] = nomtd
        # defstate['serviceplatformfreq'] = nomtd
        ipfreqlist = [50,100,200]
        ipfreqlistrandom = [100,100,50,50,50,50,100,100,100,100,100,100,100,50,100,100,200,200,100,100,100,50,100,50,50,100,200]
        ipfreqlistql = [100,50,50,50,50,50,100,50,50,50,50,100,50,50,50,50,50,50,50,50,50,50,50,50,50,50,100,50]
        ipfreqlistsarsa = [50,100,100,100,100,100,100,100,100,50,100,100,100,100,200,50,50,100,100,100,100,100,100,100,50,100,100,100,200,100,100,50,100,100,100,100,100,50,50,100,100,100,100,100,100,200,50,100,100,100,100,100,100,100,50,100,100,200,100,50,100,100,100,100,100,100,100,100,50,100,100,100,200,100,100,100,100,100,50,100,100,50,200,200,100,200,50,200]
        osfreqlist = [200,400,600]
        osfreqlistrandom = [500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,800,800,800,800,800,800,800,800,800,800]
        osfreqlistql = [800,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500]
        osfreqlistsarsa = [500,500,500,500,500,500,500,500,500,500,500,500,500,500,1000,500,500,500,500,500,500,500,500,500,500,500,500,500,1000,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,1000,500,500,500,500,500,500,500,500,500,500,500,1000,500,500,500,500,500,500,500,500,500,500,500,500,500,500,1000,500,500,500,500,500,500,500,500,500,500,500,500,500,500,1000]
        serviceplatformfreqlist = [500,800,1000]
        serviceplatformfreqlistrandom = [200,200,600,600,600,600,600,600,600,600,200,200,600,600,600,600,600,600,600,400,400,400,400,400,400,600,600]
        serviceplatformfreqlistql = [400,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600,600]
        serviceplatformfreqlistsarsa = [200,200,200,600,200,200,200,200,200,200,200,200,200,200,600,200,200,200,200,200,200,200,200,200,200,200,200,200,600,200,200,200,200,200,200,200,200,200,200,200,200,200,200,200,200,600,200,200,200,200,200,200,200,200,200,200,200,600,200,200,200,200,200,200,200,200,200,200,200,200,200,200,600,200,200,200,200,200,200,200,200,200,200,200,200,600,200,600]
        # defstate['ipfreq'] = 200
        defstate['portfreq'] = nomtd
        # defstate['osfreq'] = 1000
        # defstate['serviceplatformfreq'] = 600
        defstate['ipfreq'] = ipfreqlistrandom
        defstate['osfreq'] = osfreqlistrandom
        defstate['serviceplatformfreq'] = serviceplatformfreqlistrandom

        defstate['ippool'] = defview['defenders'].objective['ippool']
        ippoollist = [50,100,200]
        ippoollistrandom = [50,50,100,100,100,50,100,200,50,50,200,100,50,200,50,200,100,100,200,200,200,100,200,100,100,200,100]
        ippoollistql = [50,50,50,50,50,50,100,50,50,50,50,200,50,50,50,50,50,50,200,50,50,50,50,50,50,50,100,50]
        ippoollistsarsa = [50,50,50,50,50,50,100,50,100,50,50,50,50,50,200,50,50,50,50,50,50,50,50,50,50,50,50,50,200,50,50,50,50,50,50,50,50,200,50,50,50,50,50,50,50,200,50,50,50,200,50,50,50,50,50,50,50,200,50,50,50,50,50,50,50,50,50,50,50,50,50,50,200,50,50,50,50,50,50,50,50,50,100,100,50,100,50,200]
        ospoollistrandom = []
        ospoollistql = []
        ospoollistsarsa = []
        serviceplatformpoollistrandom = []
        serviceplatformpoollistql = []
        serviceplatformpoollistsarsa = []
        
        defstate['ippool'] = ippoollistsarsa
        defstate['ospool'] = ippoollistsarsa
        defstate['serviceplatformpool'] = ippoollistsarsa

        defstate['ipfreqtime'] = []
        defstate['ipfreqtime'].append(defstate['ipfreq'][0])
        defstate['ipfreqnext'] = []
        defstate['ipfreqnext'].append(1)
        defstate['osfreqtime'] = []
        defstate['osfreqtime'].append(defstate['osfreq'][0])
        defstate['osfreqnext'] = []
        defstate['osfreqnext'].append(1)
        defstate['serviceplatformfreqtime'] = []
        defstate['serviceplatformfreqtime'].append(defstate['serviceplatformfreq'][0])
        defstate['serviceplatformfreqnext'] = []
        defstate['serviceplatformfreqnext'].append(1)

        defstate['ippoolnow'] = []
        defstate['ippoolnow'].append(0)
        defstate['ospoolnow'] = []
        defstate['ospoolnow'].append(0)
        defstate['serviceplatformpoolnow'] = []
        defstate['serviceplatformpoolnow'].append(0)
        # initializing defense action holding time
        defstate['defholdingtime'] = {}
        while True:
            defstate = self.defactioncheck(env, defstate)
            needdoneact = sysutil.get_keys(defstate['needdoneact'], True)
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
        if isinstance(defstate['ipfreq'],int):
            if env.now % defstate['ipfreq'] == 0 and env.now != 0:
                defstate['needdoneact']['ipmutation'] = True
                pass
            pass
        elif isinstance(defstate['ipfreq'],list):
            # print(len(defstate['ipfreqtime']))
            if len(defstate['ipfreqtime']) == 1:
                if env.now == defstate['ipfreqtime'][-1]:
                    defstate['needdoneact']['ipmutation'] = True
                    nextchangetime = defstate['ipfreqtime'][-1]+defstate['ipfreq'][defstate['ipfreqnext'][-1]]
                    defstate['ipfreqtime'].append(nextchangetime)
                    defstate['ipfreqnext'].append(defstate['ipfreqnext'][-1]+1)
                    
                    pass
                pass
            else:
                if env.now == defstate['ipfreqtime'][-1]:
                    defstate['needdoneact']['ipmutation'] = True
                    nextchangetime = defstate['ipfreqtime'][-1]+defstate['ipfreq'][defstate['ipfreqnext'][-1]]
                    defstate['ipfreqtime'].append(nextchangetime)
                    
                    if (defstate['ipfreqnext'][-1]+1) == len(defstate['ipfreq']):
                        defstate['ippoolnow'].append(defstate['ipfreqnext'][-2])
                        defstate['ipfreqnext'].append(0)
                        # defstate['ippoolnow'].append(0)
                        pass
                    else:
                        defstate['ippoolnow'].append(defstate['ipfreqnext'][-2])
                        defstate['ipfreqnext'].append(defstate['ipfreqnext'][-1]+1)
                        pass
                    
                    pass
                pass
            pass
        else:
            print('MTD reconfigured Error!')
            pass


        if env.now % defstate['portfreq'] == 0 and env.now != 0:
            # defstate['needdoneact']['portmutation'] = True
            pass

        if isinstance(defstate['osfreq'],int):
            if env.now % defstate['osfreq'] == 0 and env.now != 0:
                defstate['needdoneact']['osmutation'] = True
                pass
        elif isinstance(defstate['osfreq'],list):
            # print(len(defstate['ipfreqtime']))
            if len(defstate['osfreqtime']) == 1:
                if env.now == defstate['osfreqtime'][-1]:
                    defstate['needdoneact']['osmutation'] = True
                    nextchangetime = defstate['osfreqtime'][-1]+defstate['osfreq'][defstate['osfreqnext'][-1]]
                    defstate['osfreqtime'].append(nextchangetime)
                    defstate['osfreqnext'].append(defstate['osfreqnext'][-1]+1)
                    pass
                pass
            else:
                if env.now == defstate['osfreqtime'][-1]:
                    defstate['needdoneact']['osmutation'] = True
                    nextchangetime = defstate['osfreqtime'][-1]+defstate['osfreq'][defstate['osfreqnext'][-1]]
                    defstate['osfreqtime'].append(nextchangetime)
                    if (defstate['osfreqnext'][-1]+1) == len(defstate['osfreq']):
                        defstate['ospoolnow'].append(defstate['osfreqnext'][-2])
                        defstate['osfreqnext'].append(0)
                        pass
                    else:
                        defstate['ospoolnow'].append(defstate['osfreqnext'][-2])
                        defstate['osfreqnext'].append(defstate['osfreqnext'][-1]+1)
                        pass
                    
                    pass
                pass
            pass
        else:
            print('MTD reconfigured Error!')
            pass

        if isinstance(defstate['serviceplatformfreq'],int):
            if env.now % defstate['serviceplatformfreq'] == 0 and env.now != 0:
                defstate['needdoneact']['serviceplatformmutation'] = True
                pass
        elif isinstance(defstate['serviceplatformfreq'],list):
            # print(len(defstate['ipfreqtime']))
            if len(defstate['serviceplatformfreqtime']) == 1:
                if env.now == defstate['serviceplatformfreqtime'][-1]:
                    defstate['needdoneact']['serviceplatformmutation'] = True
                    nextchangetime = defstate['serviceplatformfreqtime'][-1]+defstate['serviceplatformfreq'][defstate['serviceplatformfreqnext'][-1]]
                    defstate['serviceplatformfreqtime'].append(nextchangetime)
                    defstate['serviceplatformfreqnext'].append(defstate['serviceplatformfreqnext'][-1]+1)
                    pass
                pass
            else:
                if env.now == defstate['serviceplatformfreqtime'][-1]:
                    defstate['needdoneact']['serviceplatformmutation'] = True
                    nextchangetime = defstate['serviceplatformfreqtime'][-1]+defstate['serviceplatformfreq'][defstate['serviceplatformfreqnext'][-1]]
                    defstate['serviceplatformfreqtime'].append(nextchangetime)
                    if (defstate['serviceplatformfreqnext'][-1]+1) == len(defstate['serviceplatformfreq']):
                        defstate['serviceplatformpoolnow'].append(defstate['serviceplatformfreqnext'][-2])
                        defstate['serviceplatformfreqnext'].append(0)
                        pass
                    else:
                        defstate['serviceplatformpoolnow'].append(defstate['serviceplatformfreqnext'][-2])
                        defstate['serviceplatformfreqnext'].append(defstate['serviceplatformfreqnext'][-1]+1)
                        pass
                    
                    pass
                pass
            pass
        else:
            print('MTD reconfigured Error!')
            pass
        
        return defstate

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
        iposserviceplatform = ['ipmutation', 'osmutation', 'serviceplatformmutation']
        iposserviceplatform = set(iposserviceplatform)
        if 'ipmutation' in deftype and len(deftype) == 1:
            ipholdingtime = 3
            ipmutation = env.process(self.ipmutation(env, ipholdingtime, defstate))
            yield ipmutation
            pass
        elif 'protmutation' in deftype and len(deftype) == 1:
            pass
        elif 'osmutation' in deftype and len(deftype) == 1:
            # print('----os type need move----')
            osholdingtime = 5
            osmutation = env.process(self.osmutation(env, osholdingtime, defstate))
            yield osmutation
            pass
        elif 'serviceplatformmutation' in deftype and len(deftype) == 1:
            serviceplatformholdingtime = 5
            serviceplatformmutation = env.process(self.serviceplatformmutation(env, serviceplatformholdingtime, defstate))
            yield serviceplatformmutation
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
        elif iposserviceplatform.issubset(deftypeset) and len(deftype) == 3:
            ipholdingtime =3
            osholdingtime = 5
            serviceplatformholdingtime = 5
            ipmutation = env.process(self.ipmutation(env, ipholdingtime, defstate))
            osmutation = env.process(self.osmutation(env, osholdingtime, defstate))
            serviceplatformmutation = env.process(self.serviceplatformmutation(env, serviceplatformholdingtime, defstate))
            yield ipmutation & osmutation & serviceplatformmutation
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
        if isinstance(defstate['ippool'],int):
            ippool = defstate['ippool']
            pass
        elif isinstance(defstate['ippool'],list):
            ippool = defstate['ippool'][defstate['ippoolnow'][-1]]
            pass
        # ippool = defview['defenders'].objective['ippool']
        
        # print(env.now % ipfreq[0])
        for nodeindex in range(len(defview['servernodes'])):
            if 'ipmutation' in defview['servernodes'][nodeindex].nodedeftype:
                ipbase = defview['servernodes'][nodeindex].ipbase
                ipold = defview['servernodes'][nodeindex].ip
                ipnew = ipbase + round(random.uniform(1, ippool))
                if ipnew >= 256:
                    ipnew = ipnew - 256
                pass
                defview['servernodes'][nodeindex].ip = ipnew
                print("++++++ Defender Action! node: %s IP address in ip_base: %d at time: %d form ip_address_old: %d to ip_address_new: %d in ip_pool: %d ++++++" %
                      (defview['servernodes'][nodeindex].nodeid, ipbase, env.now, ipold, ipnew, ippool))
                # yield env.timeout(ipholdingtime)
                defstate['needdoneact']['ipmutation'] = False
                # when ip mutation successed, cause an interruption which will catch by the attacker move and cause an expection as well.
                globalvar.set_value('defview',defview)
                yield env.process(self.definterrupt(env, defview['servernodes'][nodeindex], ipholdingtime, 'ipmutation'))
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
        if isinstance(defstate['ospool'],int):
            ospool = defstate['ospool']
            pass
        elif isinstance(defstate['ospool'],list):
            ospool = defstate['ospool'][defstate['ospoolnow'][-1]]
            pass
        ospool = defview['defenders'].objective['ospool']
        # print(defview['vulstate'])
        # print(defview['vulstate']['vulnums']['Windows']['HTTP']['IIS'])
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
                defview['servernodes'][nodeindex].vulnum = defview['vulstate']['vulnums'][defview['servernodes'][nodeindex].os][defview['servernodes'][nodeindex].servicetype][defview['servernodes'][nodeindex].serviceplatform]
                defview['servernodes'][nodeindex].vullevel = defview['vulstate']['vullevels'][defview['servernodes'][nodeindex].os][defview['servernodes'][nodeindex].servicetype][defview['servernodes'][nodeindex].serviceplatform]
                defview['servernodes'][nodeindex].vulexplevel = defview['vulstate']['vulexplevels'][defview['servernodes'][nodeindex].os][defview['servernodes'][nodeindex].servicetype][defview['servernodes'][nodeindex].serviceplatform]
                defview['servernodes'][nodeindex].vulexpaddress = defview['vulstate']['vulexpaddresses'][defview['servernodes'][nodeindex].os][defview['servernodes'][nodeindex].servicetype][defview['servernodes'][nodeindex].serviceplatform]
                # first we don't consider os transform time (os off-line time) and self-clearance
                # defview['servernodes'][nodeindex].nodeworkingstate = 'transforming'
                defview['servernodes'][nodeindex].nodebackdoor = False
                print('++++++ Defender Action! node: %s Os type at time: %d form Os_type_old: %s to Os_tyoe_new: %s in Os_pool: %s ++++++' %
                      (defview['servernodes'][nodeindex].nodeid, env.now, osold, osnew, repr(ospool)))
                # yield env.timeout(osholdingtime)
                defstate['needdoneact']['osmutation'] = False
                # defview['servernodes'][nodeindex].nodeworkingstate = 'up'
                globalvar.set_value('defview',defview)
                yield env.process(self.definterrupt(env, defview['servernodes'][nodeindex], osholdingtime, 'osmutation'))
                pass
            pass
        pass

    # service platform muatation technique
    def serviceplatformmutation(self, env, serviceplatformholdingtime, defstate):
        defview = globalvar.get_value('defview')
        if isinstance(defstate['serviceplatformpool'],int):
            serviceplatformpool = defstate['serviceplatformpool']
            pass
        elif isinstance(defstate['serviceplatformpool'],list):
            serviceplatformpool = defstate['serviceplatformpool'][defstate['serviceplatformpoolnow'][-1]]
            pass
        serviceplatformpool = defview['defenders'].objective['servicepool']
        # print('++++++ Service Platform pool mutation pool is %s ++++++' % (repr(serviceplatformpool)))
        for nodeindex in range(len(defview['servernodes'])):
            serviceplatformpool = defview['defenders'].objective['servicepool'][defview['servernodes'][nodeindex].os][defview['servernodes'][nodeindex].servicetype]
            print('++++++ Service Platform pool mutation pool is %s in os type %s ++++++' % (repr(serviceplatformpool),defview['servernodes'][nodeindex].os))
            if 'serviceplatformmutation' in defview['servernodes'][nodeindex].nodedeftype:
                serviceplatformold = defview['servernodes'][nodeindex].serviceplatform
                serviceplatformnew = serviceplatformpool[round(random.uniform(0, len(serviceplatformpool) - 1))]
                defview['servernodes'][nodeindex].serviceplatform = serviceplatformnew
                defview['servernodes'][nodeindex].vulnum = defview['vulstate']['vulnums'][defview['servernodes'][nodeindex].os][defview['servernodes'][nodeindex].servicetype][defview['servernodes'][nodeindex].serviceplatform]
                defview['servernodes'][nodeindex].vullevel = defview['vulstate']['vullevels'][defview['servernodes'][nodeindex].os][defview['servernodes'][nodeindex].servicetype][defview['servernodes'][nodeindex].serviceplatform]
                defview['servernodes'][nodeindex].vulexplevel = defview['vulstate']['vulexplevels'][defview['servernodes'][nodeindex].os][defview['servernodes'][nodeindex].servicetype][defview['servernodes'][nodeindex].serviceplatform]
                defview['servernodes'][nodeindex].vulexpaddress = defview['vulstate']['vulexpaddresses'][defview['servernodes'][nodeindex].os][defview['servernodes'][nodeindex].servicetype][defview['servernodes'][nodeindex].serviceplatform]
                # first we don't consider os transform time (os off-line time) and self-clearance
                # defview['servernodes'][nodeindex].nodeworkingstate = 'transforming'
                defview['servernodes'][nodeindex].nodebackdoor = False
                print('++++++ Defender Action! node: %s Service Platform type at time: %d form Service_Platform_old: %s to Service_Platform_new: %s in Service_Platform_pool: %s ++++++' %
                      (defview['servernodes'][nodeindex].nodeid, env.now, serviceplatformold, serviceplatformnew, repr(serviceplatformpool)))
                # yield env.timeout(osholdingtime)
                defstate['needdoneact']['serviceplatformmutation'] = False
                # defview['servernodes'][nodeindex].nodeworkingstate = 'up'
                globalvar.set_value('defview',defview)
                yield env.process(self.definterrupt(env, defview['servernodes'][nodeindex], serviceplatformholdingtime, 'serviceplatformmutation'))
                pass
            pass
        pass

    def ASLR(self,env,aslrholdingtime,defstate):# addrsss space layout randomization technique
        # this method is not yield a process and only be activitied by service changing or crash
        defview = globalvar.get_value('defview')

        pass

    def definterrupt(self, env, node, holdingtime, interrupttype):
        interruptflags = globalvar.get_value('interruptflags')
        if interrupttype == 'ipmutation':
            interruptflags[node.nodeid]['def-off']['ipmutation'] = True
            interruptflags[node.nodeid]['def-usr']['ipmutation'] = True
            # print('Defense aciton %s interrupt! interrupt flag is %s'%(interrupttype,interruptflags['def-off']['ipmutation']))
            globalvar.set_value('interruptflags',interruptflags)
            yield env.timeout(0)
            pass
        elif interrupttype == 'portmutation':
            pass
        elif interrupttype == 'osmutation':
            interruptflags[node.nodeid]['def-off']['osmutation'] = True
            interruptflags[node.nodeid]['def-usr']['osmutation'] = True
            globalvar.set_value('interruptflags',interruptflags)
            yield env.timeout(0)
            pass
        elif interrupttype == 'serviceplatformmutation':
            interruptflags[node.nodeid]['def-off']['serviceplatformmutation'] = True
            interruptflags[node.nodeid]['def-usr']['serviceplatformmutation'] = True
            globalvar.set_value('interruptflags',interruptflags)
            yield env.timeout(0)
            pass
        else:
            yield env.timeout(0)
            pass
        pass