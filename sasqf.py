import random
import itertools
import simpy
import numpy
# define some global vers here
global attview
global defview
global usrview
attview = {}
defview = {}
usrview = {}


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
    def __init__(self, vulnum, vullevel, vulexplevel, vulexpaddress, ipbase, ippool, ip, port, os, servicetype, serviceplatform, nodeid, nodeworkingstate):
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
    serviceplatform['FTP'] = ['MIT', 'IBM']
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
    pass


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
                           1, -1, -1, -1, attnodeid, 'up')
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
                serviceplatformlinux = simstate.nodeserviceplatform['HTTP'].remove(
                    'IIS')
                serverserviceplatform = serviceplatformlinux[round(
                    random.uniform(0, len(serviceplatformlinux - 1)))]
                pass
            else:
                print('Error Os type and service platform type, please check!')
                pass
            servernode = node(servervulnum, servervullevel, servervulexplevel, servervulexpaddress,
                              ipbase, -1, iniip, iniport, serveros, serverservicetype, serverserviceplatform, servernodeid, 'up')
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
                            1, -1, -1, -1, usernodeid, 'up')
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
        attacker = sysplayer('CKC', 'CKC', 'low')
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
        # self.action = env.process(self.ipmutation(env))

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

    def portmutation(self, env):  # port muatation/hopping technique
        pass

    def osmutation(self, env):  # Os muatation technique
        pass

    def servicemutation(self, env):  # service muatation technique
        pass


class attackermove(object):
    def __init__(self, env):
        self.env = env

    def attaction(self, env):
        attobj = attview['attackers'].objective
        attabi = attview['attackers'].ability
        attwinstate = self.attwinstateini(attobj)
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
        for vulnodesnum in range(len(attstate['vulnodes'])):
            vulnodeid = 'target_' + str(vulnodesnum + 1)
            vulnode = node(-1, -1, -1, -1, -1, -1, -1, -
                           1, -1, -1, -1, vulnodeid, 'up')
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
    def attwinstateini(self, attobj):
        attwinstate = {}
        #set the win state according to the attack objective
        if attobj == 'CKC':
            attwinstate['reconnaissance'] = False
            attwinstate['weapon'] = False
            attwinstate['delivery'] = False
            attwinstate['exploition'] = False
            attwinstate['installation'] = False
            attwinstate['C&C'] = False
            attwinstate['AoO'] = False
            return attwinstate
        elif attobj == 'DoS':
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
            yield env.process(self.att_controlandcommand(env, attstate, attackholdingtimes))
            pass
        elif atttype == 'AoO':
            attackholdingtimes = 2
            yield env.process(self.att_attonobj(env, attstate, attackholdingtimes))
            pass
        else:
            print('Error attack type, please check!!')
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
                attview['targetnodes'][vulnodeindex] = node(attstate['vulnodes'][vulnodeindex].vulnum, attstate['vulnodes'][vulnodeindex].vullevel, attstate['vulnodes'][vulnodeindex].vulexplevel, attstate['vulnodes'][vulnodeindex].vulexpaddress, attstate['vulnodes'][vulnodeindex].ipbase, attstate['vulnodes'][vulnodeindex].ippool,
                                                            attstate['vulnodes'][vulnodeindex].ip, attstate['vulnodes'][vulnodeindex].port, attstate['vulnodes'][vulnodeindex].os, attstate['vulnodes'][vulnodeindex].servicetype, attstate['vulnodes'][vulnodeindex].serviceplatform, attstate['vulnodes'][vulnodeindex].nodeid, attstate['vulnodes'][vulnodeindex].nodeworkingstate)
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
        malwarecraftplatform = []
        for targetnode in attview['targetnodes']:
            weaponcrafttime = []
            print('target node %s has %d vuls and vellevel is %s velexplevel is %s' % (
                targetnode.nodeid, targetnode.vulnum, targetnode.vullevel, targetnode.vulexplevel))
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
                    pass
                elif attabi == 'medium':
                    crafttime = int(
                        (max(weaponcrafttime) + min(weaponcrafttime)) / 2)
                    pass
                elif attabi == 'high':
                    crafttime = min(weaponcrafttime)
                    pass
                else:
                    print('Error attacker ability, please check!')
                    pass
            malwarecrafttime.append(crafttime)

            malwarecraftplatform.append(targetnode.os)
            pass
        attview['malwarecrafttime'] = malwarecrafttime
        attview['malwarecraftplatform'] = malwarecraftplatform
        print('malware craft time is %s' % (repr(attview['malwarecrafttime'])))
        print('malware weapon craft start at time %d' % (env.now))
        # if have several assailable node, attack the most weak one(less malware craft time)
        attackholdingtimes = min(attview['malwarecrafttime'])
        yield env.timeout(attackholdingtimes)
        attview['attackerwinstate']['weapon'] = True
        malwaresave = {}
        malwaresave['malwarecrafttime'] = min(attview['malwarecrafttime'])
        malwaresave['malwareplatform'] = attview['malwarecraftplatform'][attview['malwarecrafttime'].index(
            min(attview['malwarecrafttime']))]
        malwaresave['malwaretarget'] = attview['targetnodes'][attview['malwarecrafttime'].index(
            min(attview['malwarecrafttime']))]
        attview['malwaresave'] = malwaresave
        print('malware weapon craft end at time %d' % (env.now))
        # print(attview['malwaresave']['malwareplatform'])
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

        attview['attackerwinstate']['exploition'] = True
        print('exploition successed at time %d' % (env.now))
        yield env.timeout(attackholdingtimes)
        pass

    def att_installation(self, env, attstate, attackholdingtimes):

        attview['attackerwinstate']['installation'] = True
        print('installation successed at time %d' % (env.now))
        yield env.timeout(attackholdingtimes)
        pass

    def att_controlandcommand(self, env, attstate, attackholdingtimes):

        attview['attackerwinstate']['C&C'] = True
        print('C&C successed at time %d' % (env.now))
        yield env.timeout(attackholdingtimes)
        pass

    def att_attonobj(self, env, attstate, attackholdingtimes):

        attview['attackerwinstate']['AoO'] = True
        print('AoO successed at time %d' % (env.now))
        yield env.timeout(attackholdingtimes)
        pass

# class usermove(object):
#     pass


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
env.process(defmove.defaction(env))
env.process(attmove.attaction(env))
env.run(until=None)
