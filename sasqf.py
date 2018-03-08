import random
import itertools
import simpy
import numpy
# define some global vers here
global attview
global defview
global usrview
global interruptflags
global interruptporc
attview = {}
defview = {}
usrview = {}
interruptflags = {}
interruptporc = {}


def get_keys(d, value):
    return [k for k, v in d.items() if v == value]


class simstate(object):
    #define simulation states
    def __init__(self, nodenum, servernum, usernum, attackernum, ipsegment, nodeostypes, nodeservicetypes, nodeserviceplatform, vulleveltypes, vulexpleveltypes, maxvulnum):
        self.nodenum = nodenum
        self.servernum = servernum
        self.usernum = usernum
        self.attackernum = attackernum
        self.ipsegment = ipsegment
        self.nodeostypes = nodeostypes
        self.nodeservicetypes = nodeservicetypes
        self.nodeserviceplatform = nodeserviceplatform
        self.vulleveltypes = vulleveltypes
        self.vulexpleveltypes = vulexpleveltypes
        #self.defippool = defippool #defippool is not defined in here
        self.maxvulnum = maxvulnum
        if self.nodenum != (self.servernum + self.usernum + self.attackernum):
            self.nodenum = self.servernum + self.usernum + self.attackernum


class node(object):
    #define node class to describe host (servers, users and attackers)
    def __init__(self, vulnum, vullevel, vulexplevel, vulexpaddress, ipbase, ippool, ip, port, os, servicetype, serviceplatform, nodeid, nodeworkingstate, nodebackdoor):
        self.vulnum = vulnum
        self.vullevel = vullevel
        self.vulexplevel = vulexplevel
        self.vulexpaddress = vulexpaddress
        self.ipbase = ipbase
        self.ippool = ippool
        self.ip = ip
        self.port = port
        self.os = os
        self.servicetype = servicetype
        self.serviceplatform = serviceplatform
        self.nodeid = nodeid
        self.nodeworkingstate = nodeworkingstate
        self.nodebackdoor = nodebackdoor


class topo(object):
    #define topology of simulation
    def __init__(self, servernum, usernum, attackernum, interlinkstate, exterlinkestate, linkmatrix):
        self.servernum = servernum
        self.usernum = usernum
        self.attackernum = attackernum
        self.interlinkstate = interlinkstate
        self.exterlinkestate = exterlinkestate
        self.linkmatrix = linkmatrix


class sysplayer(object):
    def __init__(self, strategy, objective, ability):
        self.strategy = strategy
        self.objective = objective
        self.ability = ability


def simini():
    #first, we initialize simulaiton states
    servernums = 1
    attacknums = 1
    usernums = 1
    nodenums = servernums + attacknums + usernums
    ipsegment = 'C'
    ostype = ['Windows', 'Linux']
    servicetype = ['FTP', 'HTTP', 'Media']
    serviceplatform = {}
    serviceplatform['FTP'] = ['FTP-MIT', 'FTP-IBM']
    serviceplatform['HTTP'] = ['IIS', 'Ngnix', 'Apache']
    serviceplatform['Media'] = ['Flash', 'Clint']
    vulleveltypes = ['C', 'S', 'V']
    vulexpleveltypes = ['E', 'C', 'H']
    maxvulnum = 3
    Simulationstate = simstate(nodenums, servernums, usernums, attacknums, ipsegment,
                               ostype, servicetype, serviceplatform, vulleveltypes, vulexpleveltypes, maxvulnum)
    #second, we initilize nodes including usernodes, servernodes, attackernodes
    attackernodes = nodesini('att', Simulationstate)
    servernodes = nodesini('server', Simulationstate)
    usernodes = nodesini('usr', Simulationstate)
    #finally, the topology is initialized and without this only point to point simulaiton can be done.
    simtopo = topoini('simple', Simulationstate)
    #add system players into simulation
    attackers = sysplayerini('att')
    defenders = sysplayerini('def')
    systemusers = sysplayerini('usr')
    #save nodes, topology and players to defview, usrview and attview
    attview['attnodes'] = attackernodes
    defview['servernodes'] = servernodes
    defview['usernodes'] = usernodes
    usrview = defview
    defview['topo'] = simtopo
    usrview['systemusers'] = systemusers
    defview['defenders'] = defenders
    attview['attackers'] = attackers
    # print(usrview['attnodes'][0].ip)
    # setup interrupt flags to save offense, defense and user operation interrupts
    interruptflags['def-off'] = interruptflagsinit('def-off')
    interruptflags['off-usr'] = interruptflagsinit('off-usr')
    interruptflags['def-usr'] = interruptflagsinit('def-usr')
    pass


def interruptflagsinit(types):
    interrupt = {}
    if types == 'off-def' or types == 'def-off':
        interrupt['ipmutation'] = False
        interrupt['osmuation'] = False
        interrupt['serviceplatformmuation'] = False
        return interrupt
    elif types == 'off-usr' or types == 'usr-off':
        interrupt['DoS'] = False
        return interrupt
    elif types == 'usr-def' or types == 'def-usr':
        interrupt['ipmutation'] = False
        interrupt['osmuation'] = False
        interrupt['serviceplatformmuation'] = False
        return interrupt
    else:
        print('Error types of interrupt, return none please check!')
        return interrupt


def topoini(type, simstate):  # for this version, we consider the simple topo with 3 connective nodes
    nodenum = simstate.servernum + simstate.usernum + simstate.attackernum
    internallink = 10
    externallink = 10
    linkstate = 10
    linkmatrix = [[0 for i in range(nodenum)] for i in range(nodenum)]
    for row in range(nodenum):
        for col in range(nodenum):
            linkmatrix[row][col] = linkstate
        pass
    simtopo = topo(simstate.servernum, simstate.usernum,
                   simstate.attackernum, internallink, externallink, linkmatrix)
    print('topology has been initialized!')
    return simtopo


def nodesini(type, simstate):
    if type == 'att':  # initialize attacker nodes
        attnodelist = []
        for attnum in range(0, simstate.attackernum):
            attnodeid = 'att' + str(attnum + 1)
            # the attacker node is set to '-1' since we can't know the attacker's state
            attnode = node(-1, -1, -1, -1, -1, -1, -1, -
                           1, -1, -1, -1, attnodeid, 'up', False)
            attnodelist.append(attnode)
            print('attnode No.%d of %d has been initialized! ' %
                  (attnum + 1, simstate.attackernum))
            pass
        return attnodelist  # return attacker nodes list

    elif type == 'server':
        servernodelist = []
        for servernum in range(0, simstate.servernum):
            servernodeid = 'server' + str(servernum + 1)
            if simstate.ipsegment == 'C':  # in this version, only class C is supported and other ip segment is under developed in the further
                ipbase = round(random.uniform(0, 255))
                pass
            else:
                print(
                    'error ip segment settings, only class C is supported please check! ')
                ipbase = -1
                pass
            iniip = ipbase
            # iniip = ipbase + round(random.uniform(1,simstate.defippool[0]))
            # if iniip >=256:
            #     iniip = 256 - iniip
            #     pass
            iniport = round(random.uniform(1000, 65535))
            servervulnum = round(random.uniform(1, simstate.maxvulnum))
            #print(servervulnum)
            servervullevel = []
            servervulexplevel = []
            servervulexpaddress = []
            for vul in range(servervulnum):
                # print('vul is %d and vuls is %d'%(vul,servervulnum))
                vullevel = simstate.vulleveltypes[round(
                    random.uniform(0, len(simstate.vulleveltypes) - 1))]
                servervullevel.append(vullevel)
                vulexplevel = simstate.vulexpleveltypes[round(
                    random.uniform(0, len(simstate.vulexpleveltypes) - 1))]
                servervulexplevel.append(vulexplevel)
                vulexpaddress = round(random.uniform(0, 65535))
                servervulexpaddress.append(vulexpaddress)
                pass
            # print(round(random.uniform(0,len(simstate.nodeostypes))))
            serveros = simstate.nodeostypes[round(
                random.uniform(0, len(simstate.nodeostypes) - 1))]
            # serverservicetype = simstate.nodeservicetypes[round(
            #     random.uniform(0, len(simstate.nodeservicetypes) - 1))]
            serverservicetype = 'HTTP'  # in this version, only web service is considered
            serverserviceplatform = []
            if serveros == 'Windows':
                serverserviceplatform = simstate.nodeserviceplatform['HTTP'][round(
                    random.uniform(0, len(simstate.nodeserviceplatform['HTTP']) - 1))]
                # for Windows, the web service can be IIS, Ngnix and Apache
                pass
            elif serveros == 'Linux':
                simstate.nodeserviceplatform['HTTP'].remove('IIS')
                serviceplatformlinux = simstate.nodeserviceplatform['HTTP']
                serverserviceplatform = serviceplatformlinux[round(
                    random.uniform(0, len(serviceplatformlinux) - 1))]
                pass
            else:
                print('Error Os type and service platform type, please check!')
                pass
            servernode = node(servervulnum, servervullevel, servervulexplevel, servervulexpaddress,
                              ipbase, -1, iniip, iniport, serveros, serverservicetype, serverserviceplatform, servernodeid, 'up', False)
            servernodelist.append(servernode)
            print('defnode No.%d of %d has been initialized! ' %
                  (servernum + 1, simstate.servernum))
            pass
        return servernodelist

    elif type == 'usr':
        usrnodelist = []
        for usernum in range(0, simstate.usernum):
            usernodeid = 'user' + str(usernum + 1)
            # the user node is set to '-1' since we don't care the users' state
            usernode = node(-1, -1, -1, -1, -1, -1, -1, -
                            1, -1, -1, -1, usernodeid, 'up', False)
            usrnodelist.append(usernode)
            print('usrnode No.%d of %d has been initialized! ' %
                  (usernum + 1, simstate.usernum))
            pass
        return usrnodelist
    else:
        print('no such type of node! please check! ')
        pass
    pass


def sysplayerini(type):
    if type == 'att':
        # in this version, only cyber kill chain like attacke type is considered.
        # // DoS and other type of attack is under developed
        # for strategy CKC-C means need continuous C&C and CKC-D means need discrete C&C
        # for objective, there are three type: Data Exfiltration, Network Spreading, System Disruption
        # and in this version, only system disruption is under considerd.
        attacker = sysplayer('CKC-D', 'Sys-Dis', 'low')
        return attacker
    elif type == 'def':
        defstrategy = ['ip', 'platform']
        defobjective = {}
        defobjective['ippool'] = [20, 100, 200]
        defobjective['portpool'] = [200, 1000, 5000]
        defobjective['ospool'] = 2
        defobjective['servicepool'] = 3
        defobjective['ipfreq'] = [10, 100, 300]  # ip change frequency (s)
        defobjective['portfreq'] = [10, 120, 300]  # port chagne frequency (s)
        # service chagne frequency (s)
        defobjective['servicefreq'] = [60, 300, 1200]
        defobjective['osfreq'] = [120, 540, 1200]  # OS chagne frequency (s)
        defender = sysplayer(defstrategy, defobjective, -1)
        return defender
    elif type == 'usr':
        systemuser = sysplayer('http-web', 'http-web', -1)
        return systemuser
    else:
        print('no such type of system player! please check')
        pass

    pass


class defendermove(object):
    def __init__(self, env):
        self.env = env
        self.action = env.process(self.defaction(env))
        # self.process = env.process(self.defaction(env))
        # env.process(self.definterrupt(env,''))

    def defaction(self, env):
        ipfreq = defview['defenders'].objective['ipfreq']
        portfreq = defview['defenders'].objective['portfreq']
        osfreq = defview['defenders'].objective['osfreq']
        servicefreq = defview['defenders'].objective['servicefreq']
        while True:
            #we consider the muation with small pool and high frequency
            if env.now % ipfreq[1] == 0:
                ipholdingtime = 3
                yield env.process(self.ipmutation(env, ipholdingtime))
                # print(defview['topo'].linkmatrix[defview['topo'].servernum+defview['topo'].usernum+defview['topo'].attackernum-1])
            # elif env.now%osfreq[0] == 0: #
            #     pass
            # elif env.now%servicefreq[0] == 0:
            #     pass
            else:
                defactiontime = 1
                yield env.timeout(defactiontime)
        pass

    def ipmutation(self, env, ipholdingtime):  # ip muatation/hopping technique
        ippool = defview['defenders'].objective['ippool']
        # print(env.now % ipfreq[0])
        for nodeindex in range(len(defview['servernodes'])):
            ipbase = defview['servernodes'][nodeindex].ipbase
            ipold = defview['servernodes'][nodeindex].ip
            ipnew = ipbase + round(random.uniform(1, ippool[0]))
            if ipnew >= 256:
                ipnew = ipnew - 256
            pass
            defview['servernodes'][nodeindex].ip = ipnew
            print("Defender move node:%s ip address in ip_base: %d at %d(s) form ip_address_old: %d to ip_address_new: %d in ip_pool: %d" %
                  (defview['servernodes'][nodeindex].nodeid, ipbase, env.now, ipold, ipnew, ippool[0]))
        yield env.timeout(ipholdingtime)
        #
        yield env.process(self.definterrupt(env, 'ipmutation'))

    def portmutation(self, env):  # port muatation/hopping technique
        pass

    def osmutation(self, env):  # Os muatation technique
        pass

    def servicemutation(self, env):  # service muatation technique
        pass

    def definterrupt(self, env, interrupttype):

        if interrupttype == 'ipmutation':
            interruptflags['def-off']['ipmutation'] = True
            # print('Defense aciton %s interrupt! interrupt flag is %s'%(interrupttype,interruptflags['def-off']['ipmutation']))
            yield env.timeout(0)
            pass
        else:
            yield env.timeout(0)
            pass
        pass


class attackermove(object):
    def __init__(self, env):
        self.env = env
        self.action = env.process(self.attaction(env))
        # self.att_controlandcommand_proc = env.process(self.att_controlandcommand(env, attstate, attackholdingtimes))

    def attaction(self, env):
        attstrategy = attview['attackers'].strategy
        attobj = attview['attackers'].objective
        attabi = attview['attackers'].ability
        attwinstate = self.attwinstateini(attstrategy)
        attzday = self.attabiini(attabi)
        attview['attackerwinstate'] = attwinstate
        attview['attackerzday'] = attzday
        attview['targetnodes'] = []
        attstate = {}
        attstate['iniip'] = 0
        attstate['endip'] = 255
        nodenum = defview['topo'].servernum + \
            defview['topo'].usernum + defview['topo'].attackernum
        attstate['vulnodes'] = []
        attstate['vulnodes'] = self.attchecktarnodes(nodenum)
        attstate['C&Ctype'] = attstrategy.split(
            '-')[len(attstrategy.split('-')) - 1]
        # for C&C time, 50 time step is a relative value.
        attstate['C&Ctime'] = 50
        for vulnodesnum in range(len(attstate['vulnodes'])):
            vulnodeid = 'target_' + str(vulnodesnum + 1)
            vulnode = node(-1, -1, -1, -1, -1, -1, -1, -
                           1, -1, -1, -1, vulnodeid, 'up', False)
            attview['targetnodes'].append(vulnode)
            pass

        while True:
            attstate['vulnodes'] = self.attchecktarnodes(nodenum)
            undonephase = self.attwinstatecheck(attview['attackerwinstate'])
            # print('the attacker win state is %s' % (repr(attview['attackerwinstate'])))
            # print('the target node is %s, vul node is %s'% (repr(attview['targetnodes']),repr(attstate['vulnodes'])))
            # print(attview['targetnodes'][0].nodeid)
            if len(undonephase) > 0:
                yield env.process(self.attackonce(env, undonephase[0], attstate))
            else:
                print('Attack successed at time %d, start data collecting!' % (env.now))
                exit()
                pass
            pass
        pass

    # initialize attacker's state，those states show when the attack can win the game
    def attwinstateini(self, attstrategy):
        attwinstate = {}
        #set the win state according to the attack objective
        if attstrategy == 'CKC-C' or attstrategy == 'CKC-D':
            attwinstate['reconnaissance'] = False
            attwinstate['weapon'] = False
            attwinstate['delivery'] = False
            attwinstate['exploition'] = False
            attwinstate['installation'] = False
            attwinstate['C&C'] = False
            attwinstate['AoO'] = False
            return attwinstate
        elif attstrategy == 'DoS':
            attwinstate['reconnaissance'] = False
            attwinstate['C&C'] = False
            attwinstate['AoO'] = False
            return attwinstate
        else:
            print(
                'Error type of attack objective! Please check and only \'CKC\' and \'DoS\' is supported')
            return attwinstate
        pass

    # initialize attacker's ability to use z-day vuls.
    def attabiini(self, attabi):
        if attabi == 'low':
            attzday = 0
            return attzday
        elif attabi == 'medium':
            attzday = 0.5
            return attzday
        elif attabi == 'high':
            attzday = 1
            return attzday
        else:
            return
        pass

    def attwinstatecheck(self, attackstates):  # check attack's unsuccess phase
        undonephase = get_keys(attackstates, False)
        return undonephase

    # using topo links to find ccc nodes, which have external link to attack nodes.s
    def attchecktarnodes(self, nodenum):
        vulnodes = []
        for exlinkstateindex in range(len(defview['topo'].linkmatrix[nodenum - 1])):
            if exlinkstateindex <= (defview['topo'].servernum - 1) and defview['topo'].linkmatrix[nodenum - 1][exlinkstateindex] >= 0:
                vulnodes.append(defview['servernodes'][exlinkstateindex])
                pass
            pass
        return vulnodes

    def attackonce(self, env, atttype, attstate):  # attack once based on CKC steps(phase)
        # print('Attack!')
        if atttype == 'reconnaissance':
            attackholdingtimes = 2
            yield env.process(self.att_reconnaissance(env, attstate, attackholdingtimes))
            pass
        elif atttype == 'weapon':
            attackholdingtimes = 2
            yield env.process(self.att_weapon(env, attstate, attackholdingtimes))
            pass
        elif atttype == 'delivery':
            attackholdingtimes = 2
            yield env.process(self.att_delivery(env, attstate, attackholdingtimes))
            pass
        elif atttype == 'exploition':
            attackholdingtimes = 2
            yield env.process(self.att_exploition(env, attstate, attackholdingtimes))
            pass
        elif atttype == 'installation':
            attackholdingtimes = 2
            yield env.process(self.att_installation(env, attstate, attackholdingtimes))
            pass
        elif atttype == 'C&C':
            attackholdingtimes = 2
            att_controlandcommand_proc = env.process(
                self.att_controlandcommand(env, attstate, attackholdingtimes))
            interruptporc['att_controlandcommand_proc'] = att_controlandcommand_proc
            yield att_controlandcommand_proc
            pass
        elif atttype == 'AoO':
            attackholdingtimes = 2
            yield env.process(self.att_attonobj(env, attstate, attackholdingtimes))
            pass
        else:
            print('Error attack type, please check!!')
            pass

        pass

    def attprocinterrupt(self, env, proc):
        if interruptflags['def-off']['ipmutation']:
            try:
                proc
            except NameError:
                proc_exists = False
            else:
                proc_exists = True
            print(
                '--------defense ip muation interrupt offense at time %d --------' % (env.now))
            # proc_exists = 'att_controlandcommand_proc' in locals() or 'att_controlandcommand_proc' in globals()
            if proc_exists and proc.is_alive:
                proc.interrupt('ipmutation')
                pass
            interruptflags['def-off']['ipmutation'] = False
            yield env.timeout(1)
            pass
        else:
            yield env.timeout(1)
            pass
        pass

    def att_reconnaissance(self, env, attstate, attackholdingtimes):
        # print('Reconnaissance Attack!')
        if attstate['iniip'] > attstate['endip']:
            attstate['iniip'] = 0
            pass
        for vulnodeindex in range(len(attstate['vulnodes'])):
            # print(attstate['vulnodes'][vulnodeindex].ip)
            if attstate['vulnodes'][vulnodeindex].ip == attstate['iniip'] or attstate['iniip'] == attview['targetnodes'][vulnodeindex].ip:
                yield env.timeout(attackholdingtimes)
                attview['targetnodes'][vulnodeindex] = node(attstate['vulnodes'][vulnodeindex].vulnum, attstate['vulnodes'][vulnodeindex].vullevel,
                                                            attstate['vulnodes'][vulnodeindex].vulexplevel, attstate[
                                                                'vulnodes'][vulnodeindex].vulexpaddress,
                                                            attstate['vulnodes'][vulnodeindex].ipbase, attstate['vulnodes'][vulnodeindex].ippool,
                                                            attstate['vulnodes'][vulnodeindex].ip, attstate['vulnodes'][
                                                                vulnodeindex].port, attstate['vulnodes'][vulnodeindex].os,
                                                            attstate['vulnodes'][vulnodeindex].servicetype, attstate[
                                                                'vulnodes'][vulnodeindex].serviceplatform,
                                                            attstate['vulnodes'][vulnodeindex].nodeid, attstate[
                                                                'vulnodes'][vulnodeindex].nodeworkingstate,
                                                            attstate['vulnodes'][vulnodeindex].nodebackdoor)
                # in python, the global vers with list type only point to the vers with assignment, so to keep the global vers not change with local vers we have to
                # 'new' a class and assignment to the global ver
                attview['attackerwinstate']['reconnaissance'] = True
                print('reconnaissance success at time %d! the target node:%s ip is %d' %
                      (env.now, attview['targetnodes'][vulnodeindex].nodeid, attview['targetnodes'][vulnodeindex].ip))

            else:
                # print('Reconnaissance ip is %d at time %d, target node ip is %d'%(attstate['iniip'], env.now,attstate['vulnodes'][vulnodeindex].ip))
                attstate['iniip'] = attstate['iniip'] + 1
                yield env.timeout(attackholdingtimes)
                pass
            pass

    def att_weapon(self, env, attstate, attackholdingtimes):
        malwarecrafttime = []
        malwarecraftos = []
        malwarecraftserviceplatform = []
        malwarecraftexpaddress = []
        for targetnode in attview['targetnodes']:
            weaponcrafttime = []
            print('target node %s has %d vuls and vullevel is %s vulexplevel is %s vulexpaddress is %s' % (
                targetnode.nodeid, targetnode.vulnum, targetnode.vullevel, targetnode.vulexplevel, repr(targetnode.vulexpaddress)))
            for targetvul in range(targetnode.vulnum):
                if targetnode.vulexplevel[targetvul] == 'E':
                    wct = 100
                    pass
                elif targetnode.vulexplevel[targetvul] == 'C':
                    wct = 300
                    pass
                elif targetnode.vulexplevel[targetvul] == 'H':
                    wct = 500
                    pass
                elif targetnode.vulexplevel[targetvul] == 'Zday':
                    wct = 100
                    pass
                else:
                    print("Error vuls' exploition level, please check")
                    pass
                pass
                weaponcrafttime.append(wct)
                attabi = attview['attackers'].ability
                if attabi == 'low':
                    crafttime = max(weaponcrafttime)
                    exploitaddress = targetnode.vulexpaddress[weaponcrafttime.index(
                        crafttime)]
                    pass
                # elif attabi == 'medium': # for medium attack ability, the exploition address is a problem so this part is not support in this version
                #     crafttime = int(
                #         (max(weaponcrafttime) + min(weaponcrafttime)) / 2)
                #     pass
                elif attabi == 'high':
                    crafttime = min(weaponcrafttime)
                    exploitaddress = targetnode.vulexpaddress[weaponcrafttime.index(
                        crafttime)]
                    pass
                else:
                    print('Error attacker ability, please check!')
                    pass
            malwarecrafttime.append(crafttime)
            malwarecraftos.append(targetnode.os)
            malwarecraftserviceplatform.append(targetnode.serviceplatform)
            malwarecraftexpaddress.append(exploitaddress)
            pass
        attview['malwarecrafttime'] = malwarecrafttime
        attview['malwarecraftos'] = malwarecraftos
        attview['malwarecraftserviceplatform'] = malwarecraftserviceplatform
        attview['malwarecraftexpaddress'] = malwarecraftexpaddress
        print('malware craft time is %s' % (repr(attview['malwarecrafttime'])))
        print('malware weapon craft start at time %d' % (env.now))
        # if have several assailable node, attack the most weak one(less malware craft time)
        attackholdingtimes = min(attview['malwarecrafttime'])
        yield env.timeout(attackholdingtimes)
        attview['attackerwinstate']['weapon'] = True
        malwaresave = {}
        malwaresave['malwarecrafttime'] = min(attview['malwarecrafttime'])
        malwaresave['malwarecraftserviceplatform'] = attview['malwarecraftserviceplatform'][attview['malwarecrafttime'].index(
            min(attview['malwarecrafttime']))]
        malwaresave['malwarecraftos'] = attview['malwarecraftos'][attview['malwarecrafttime'].index(
            min(attview['malwarecrafttime']))]
        malwaresave['malwarecraftexpaddress'] = attview['malwarecraftexpaddress'][attview['malwarecrafttime'].index(
            min(attview['malwarecrafttime']))]
        malwaresave['malwaretarget'] = attview['targetnodes'][attview['malwarecrafttime'].index(
            min(attview['malwarecrafttime']))]
        attview['malwaresave'] = malwaresave
        print('malware weapon craft end at time %d' % (env.now))
        print('malware weapon state for target node %s are: os-type: %s, service-platform: %s, exploition-address: %d' %
              (malwaresave['malwaretarget'].nodeid, malwaresave['malwarecraftos'], malwaresave['malwarecraftserviceplatform'], malwaresave['malwarecraftexpaddress']))
        # print(attview['malwaresave']['malwarecraftserviceplatform'])
        pass

    def att_delivery(self, env, attstate, attackholdingtimes):

        for vulnode in attstate['vulnodes']:
            if vulnode.nodeid == attview['malwaresave']['malwaretarget'].nodeid:
                for targetnode in attview['targetnodes']:
                    if targetnode.nodeid == attview['malwaresave']['malwaretarget'].nodeid:
                        if targetnode.ip == vulnode.ip:
                            if vulnode.nodeworkingstate == 'up':
                                print('delivery start at time %d, sending malware to %s with ip %d' % (
                                    env.now, targetnode.nodeid, targetnode.ip))
                                yield env.timeout(attackholdingtimes)
                                attview['attackerwinstate']['delivery'] = True
                                print('delivery successed at time %d' %
                                      (env.now))
                                pass
                            else:
                                print('target node %s is not online, delivery will try %d time step later!' % (
                                    vulnode.nodeid, attackholdingtimes))
                                yield env.timeout(attackholdingtimes)
                                pass
                            pass
                        else:
                            print('delivery can not start, error target ip address (attacker know ip is %d, target real ip is %d)' % (
                                targetnode.ip, vulnode.ip))
                            print(
                                'reconnaissance will restart to get the real ip for target node!')
                            attview['attackerwinstate']['reconnaissance'] = False
                            pass
                        pass
                    else:
                        print('target node is not match malware type!')
                        pass
                    pass
            else:
                print('vul node is not match malware type!')
                pass
            pass

        pass

    def att_exploition(self, env, attstate, attackholdingtimes):
        # print('target node vul exploition address is ')
        # print(attview['targetnodes'][0].vulexpaddress)
        for vulnode in attstate['vulnodes']:
            if vulnode.nodeid == attview['malwaresave']['malwaretarget'].nodeid:
                for targetnode in attview['targetnodes']:
                    if targetnode.nodeid == attview['malwaresave']['malwaretarget'].nodeid:
                        if targetnode.os == vulnode.os:
                            if targetnode.serviceplatform == vulnode.serviceplatform:
                                if attview['malwaresave']['malwarecraftexpaddress'] in vulnode.vulexpaddress:
                                    if vulnode.nodeworkingstate == 'up':
                                        print('malware exploition start at %d, target node id is %s, os is %s, service platform is %s, vuls address is %d' %
                                              (env.now, targetnode.nodeid, targetnode.os, targetnode.serviceplatform, attview['malwaresave']['malwarecraftexpaddress']))
                                        yield env.timeout(attackholdingtimes)
                                        attview['attackerwinstate']['exploition'] = True
                                        print(
                                            'exploition successed at time %d' % (env.now))
                                        pass
                                    else:
                                        print('target node %s is not online, exploition will try %d time step later!' % (
                                            vulnode.nodeid, attackholdingtimes))
                                        yield env.timeout(attackholdingtimes)
                                        pass
                                    pass
                                else:
                                    # this part will come soon!
                                    print(
                                        'target node using ASLR, exploition will try later!')
                                    yield env.timeout(attackholdingtimes)
                                    pass
                                pass
                            else:
                                print(
                                    'target node servie paltform is not match malware, reconnaissance and weapon craft will re-start soon')
                                attview['attackerwinstate']['weapon'] = False
                                attview['attackerwinstate']['reconnaissance'] = False
                                attview['attackerwinstate']['delivery'] = False
                                yield env.timeout(attackholdingtimes)
                                pass
                            pass
                        else:
                            print(
                                'target node servie os type is not match malware, reconnaissance, weapon craft and delivery will re-start soon')
                            attview['attackerwinstate']['weapon'] = False
                            attview['attackerwinstate']['reconnaissance'] = False
                            attview['attackerwinstate']['delivery'] = False
                            yield env.timeout(attackholdingtimes)
                            pass
                        pass
                    else:
                        print('target node is not match exploition type!')
                        pass
                    pass
            else:
                print('vul node is not match exploition type!')
                pass
            pass
        pass

    def att_installation(self, env, attstate, attackholdingtimes):
        for vulnode in attstate['vulnodes']:
            if vulnode.nodeid == attview['malwaresave']['malwaretarget'].nodeid:
                for targetnode in attview['targetnodes']:
                    if targetnode.nodeid == attview['malwaresave']['malwaretarget'].nodeid:
                        if vulnode.nodeworkingstate == 'up':
                            if targetnode.os == vulnode.os:
                                print('Other malware intstallation start at %d, target node id is %s, os is %s, service platform is %s, vuls address is %d' %
                                      (env.now, targetnode.nodeid, targetnode.os, targetnode.serviceplatform, attview['malwaresave']['malwarecraftexpaddress']))
                                yield env.timeout(attackholdingtimes)
                                attview['attackerwinstate']['installation'] = True
                                defview['servernodes'][defview['servernodes'].index(
                                    vulnode)].nodebackdoor = True
                                # print(defview['servernodes'].index(vulnode))
                                print('installation successed at time %d, target node %s backdoor state is %s' %
                                      (env.now, targetnode.nodeid, format(defview['servernodes'][defview['servernodes'].index(vulnode)].nodebackdoor, "")))
                                pass
                            else:
                                print(
                                    'target node servie os type is not match malware, reconnaissance, weapon craft, delivery and exploition will re-start soon')
                                attview['attackerwinstate']['weapon'] = False
                                attview['attackerwinstate']['reconnaissance'] = False
                                attview['attackerwinstate']['delivery'] = False
                                attview['attackerwinstate']['exploition'] = False
                                yield env.timeout(attackholdingtimes)
                                pass
                            pass
                        else:
                            print('target node %s is not online, installation will try %d time step later!' % (
                                vulnode.nodeid, attackholdingtimes))
                            yield env.timeout(attackholdingtimes)
                            pass
                        pass
                    else:
                        print('target node is not match malware installation type!')
                        pass
                    pass
            else:
                print('vul node is not match malware installation type!')
                pass
            pass
        pass
        pass

    def att_controlandcommand(self, env, attstate, attackholdingtimes):
        # for C&C, only two types are considered. one is continuous C&C for several time step, another is discrete C&C for several time step
        # print('C&C type is %s, need C&C %d time steps' %
        #       (attstate['C&Ctype'], attstate['C&Ctime']))
        for vulnode in attstate['vulnodes']:
            if vulnode.nodeid == attview['malwaresave']['malwaretarget'].nodeid:
                for targetnode in attview['targetnodes']:
                    if targetnode.nodeid == attview['malwaresave']['malwaretarget'].nodeid:
                        if vulnode.nodeworkingstate == 'up':
                            if vulnode.ip == targetnode.ip:
                                if vulnode.nodebackdoor:
                                    attstate['C&C-D'] = {}
                                    if attstate['C&Ctype'] == 'C':
                                        try:
                                            print('C&C type is %s. Start C&C on target node %s at time %d for continuous %d time steps' %
                                                  (attstate['C&Ctype'],targetnode.nodeid, env.now, attstate['C&Ctime']))
                                            yield env.timeout(attstate['C&Ctime'])
                                            attview['attackerwinstate']['C&C'] = True
                                            print(
                                                'C&C successfully end at time %d' % (env.now))
                                        except simpy.Interrupt:
                                            print(
                                                '!!!!!! C&C is interrupted at time %d !!!!!!!' % (env.now))
                                            yield env.timeout(1)
                                    elif attstate['C&Ctype'] == 'D':
                                        
                                        try:
                                            print('C&C type is %s. Start C&C on target node %s at time %d for continuous %d time steps' %
                                                  (attstate['C&Ctype'],targetnode.nodeid, env.now, attstate['C&Ctime']))
                                            attstate['C&C-D']['starttime'] = env.now
                                            yield env.timeout(attstate['C&Ctime'])
                                            attview['attackerwinstate']['C&C'] = True
                                            print(
                                                'C&C successfully end at time %d' % (env.now))
                                            pass
                                        except simpy.Interrupt:
                                            attstate['C&C-D']['interrrupttime'] = env.now
                                            attstate['C&C-D']['timeleft'] = attstate['C&Ctime'] - (attstate['C&C-D']['interrrupttime'] - attstate['C&C-D']['starttime'])
                                            attstate['C&Ctime'] = attstate['C&C-D']['timeleft']
                                            print(
                                                '!!!!!! C&C is interrupted at time %d and need %d time step left to C&C !!!!' % (env.now,attstate['C&Ctime']))
                                            yield env.timeout(1)
                                            pass
                                        pass
                                    else:
                                        print('Error C&C type, please check!')
                                        pass
                                    pass
                                else:
                                    print(
                                        'target node back door is not exist, reconnaissance, weapon craft, delivery, exploition and installation will re-start soon')
                                    attview['attackerwinstate']['weapon'] = False
                                    attview['attackerwinstate']['reconnaissance'] = False
                                    attview['attackerwinstate']['delivery'] = False
                                    attview['attackerwinstate']['exploition'] = False
                                    attview['attackerwinstate']['installation'] = False
                                    yield env.timeout(attackholdingtimes)
                                    pass
                                pass
                            else:
                                print('target node %s is not reachable at time %d in ip %d for real ip is %d, reconnaissance will re-start!' %
                                      (targetnode.nodeid, env.now, targetnode.ip, vulnode.ip))
                                attview['attackerwinstate']['reconnaissance'] = False
                                yield env.timeout(attackholdingtimes)
                                pass
                        else:
                            print('target node %s is not online, C&C will try %d time step later!' % (
                                vulnode.nodeid, attackholdingtimes))
                            yield env.timeout(attackholdingtimes)
                            pass
                        pass
                    else:
                        print('target node is not match C&C!')
                        pass
                    pass
            else:
                print('vul node is not match C&C!')
                pass
            pass
        pass
    pass

    def att_attonobj(self, env, attstate, attackholdingtimes):

        attview['attackerwinstate']['AoO'] = True
        print('AoO successed at time %d' % (env.now))
        yield env.timeout(attackholdingtimes)
        pass


class usermove(object):
    def __init__(self, env):
        self.env = env
        pass
    pass


class interruptmove(object):
    def __init__(self, env, defmove, attmove, usrmove):
        self.env = env
        self.defmove = defmove
        self.attmove = attmove
        self.usrmove = usrmove
        pass

    def sysplayerinterrupt(self, env, defmove, attmove, usrmove):
        while True:
            # print(repr(interruptflags))
            if interruptflags['def-off']['ipmutation']:
                print(
                    '+++++++defense ip muation interrupt offense at time %d +++++++++' % (env.now))
                if 'att_controlandcommand_proc' in interruptporc:
                    proc = interruptporc['att_controlandcommand_proc']
                    if proc.is_alive:
                        interruptflags['def-off']['ipmutation'] = False
                        proc.interrupt('ipmutation')
                        pass
                    else:
                        yield env.timeout(1)
                        pass
                    pass
                else:
                    yield env.timeout(1)
                    pass
                interruptflags['def-off']['ipmutation'] = False
                yield env.timeout(1)
                pass
            else:
                yield env.timeout(1)
                pass
            pass
        pass
    pass


#initailize the simulation
simini()
# Setup and start the simulation
print('Simulaiton initialized!!')
# print(defview['defenders'].objective['ippool'])
# Create environment and start processes
print('MTD offense and defense is going to START!')
env = simpy.Environment()
defmove = defendermove(env)
attmove = attackermove(env)
usrmove = usermove(env)
interruptflag = interruptmove(env, defmove, attmove, usrmove)
# env.process(defmove.defaction(env))
# env.process(attmove.attaction(env))
env.process(interruptflag.sysplayerinterrupt(env, defmove, attmove, usrmove))
env.run(until=None)
