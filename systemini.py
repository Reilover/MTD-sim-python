import sysutil
import globalvar
import random
import numpy
global attview
global defview
global usrview
global interruptflags
global interruptproc
global datatosave
attview = {}
defview = {}
usrview = {}
interruptflags = {}
interruptproc = {}
datatosave = {}
globalvar.set_value('attview',attview)
globalvar.set_value('defview',defview)
globalvar.set_value('usrview',usrview)
globalvar.set_value('interruptflags',interruptflags)
globalvar.set_value('interruptproc',interruptproc)
globalvar.set_value('datatosave',datatosave)


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
    def __init__(self, vulnum, vullevel, vulexplevel, vulexpaddress, ipbase, ippool, ip, port, os, servicetype, serviceplatform, nodeid, nodeworkingstate, nodebackdoor, nodedeftype):
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
        self.nodedeftype = nodedeftype


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

class malware(object):
    def __init__(self, malwareid, expos, expserviceplatform, exploitationaddress, version, crafttime, exploitationtime, targetnode):
        self.malwareid = malwareid
        self.expos = expos
        self.expserviceplatform = expserviceplatform 
        self.exploitationaddress = exploitationaddress
        self.version = version
        self.crafttime = crafttime
        self.exploitationtime = exploitationtime
        self.targetnode = targetnode

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
    serviceplatform['FTP'] = ['MIT', 'IBM', 'Stanford']
    serviceplatform['HTTP'] = ['IIS', 'Ngnix', 'Apache']
    serviceplatform['Media'] = ['Flash', 'Clint']
    vulleveltypes = ['C', 'S', 'V']
    vulexpleveltypes = ['E', 'C', 'H']
    maxvulnum = 3
    Simulationstate = simstate(nodenums, servernums, usernums, attacknums, ipsegment,
                               ostype, servicetype, serviceplatform, vulleveltypes, vulexpleveltypes, maxvulnum)
    # we initialize node's vuls state according to os type, service platform and service type, which is saved to defview for os and service mutation!
    vulstate = vulsini('random',Simulationstate)
    defview['vulstate'] = vulstate
    #second, we initialize nodes including usernodes, servernodes, attackernodes
    attackernodes = nodesini('att', Simulationstate)
    servernodes = nodesini('server', Simulationstate)
    usernodes = nodesini('usr', Simulationstate)
    #finally, the topology is initialized and without this only point to point simulaiton can be done.
    simtopo = topoini('simple', Simulationstate)
    #add system players into simulation
    attackers = sysplayerini('att', Simulationstate)
    defenders = sysplayerini('def', Simulationstate)
    systemusers = sysplayerini('usr', Simulationstate)
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
    globalvar.set_value('attview',attview)
    globalvar.set_value('defview',defview)
    globalvar.set_value('usrview',usrview)
    globalvar.set_value('interruptflags',interruptflags)
    pass


def interruptflagsinit(types):
    interrupt = {}
    if types == 'off-def' or types == 'def-off':
        interrupt['ipmutation'] = False
        interrupt['osmutation'] = False
        interrupt['serviceplatformmutation'] = False
        return interrupt
    elif types == 'off-usr' or types == 'usr-off':
        interrupt['DoS'] = False
        return interrupt
    elif types == 'usr-def' or types == 'def-usr':
        interrupt['ipmutation'] = False
        interrupt['osmutation'] = False
        interrupt['serviceplatformmutation'] = False
        return interrupt
    else:
        print('Error types of interrupt, return none please check!')
        return interrupt

def vulsini(types,simstate):
    # initialize nodes vul state! tow types are support, 'random' for random initialize and 'emulation' for CVE files.
    vulstate = {}
    servervulnum = {}
    servervullevel = {}
    servervulexplevel = {}
    servervulexpaddress = {}

    if types == 'random':
        servervulnum_ostype_list = []
        servervullevel_ostype_list = []
        servervulexplevel_ostype_list = []
        servervulexpaddress_ostype_list = []
        for ostype in simstate.nodeostypes:
            # print(ostype)
            servervulnum_servicetype_list = []
            servervullevel_servicetype_list = []
            servervulexplevel_servicetype_list = []
            servervulexpaddress_servicetype_list = []
            for servicetype in simstate.nodeservicetypes:
                # print(ostype+'-'+servicetype)
                servervulnum_serviceplatform_list = []
                servervullevel_serviceplatform_list = []
                servervulexplevel_serviceplatform_list = []
                servervulexpaddress_serviceplatform_list = []
                for serviceplatformtype in simstate.nodeserviceplatform[servicetype]:
                    # print(ostype+'-'+servicetype+'-'+serviceplatformtype)
                    vulnum= round(random.uniform(1, simstate.maxvulnum))
                    vullevellist = []
                    vulexplevellist = []
                    vulexpaddresslist = []
                    for vul in range(vulnum):
                        # print('vul is %d and vuls is %d'%(vul,servervulnum))
                        vullevel = simstate.vulleveltypes[round(
                            random.uniform(0, len(simstate.vulleveltypes) - 1))]
                        vullevellist.append(vullevel)
                        vulexplevel = simstate.vulexpleveltypes[round(
                        random.uniform(0, len(simstate.vulexpleveltypes) - 1))]
                        vulexplevellist.append(vulexplevel)
                        vulexpaddress = round(random.uniform(0, 65535))
                        vulexpaddresslist.append(vulexpaddress)
                        pass
                    # servervulnum[ostype][servicetype][serviceplatformtype]
                    servervulnum_serviceplatform_list.append((serviceplatformtype,vulnum))
                    servervullevel_serviceplatform_list.append((serviceplatformtype,vullevellist))
                    servervulexplevel_serviceplatform_list.append((serviceplatformtype,vulexplevellist))
                    servervulexpaddress_serviceplatform_list.append((serviceplatformtype,vulexpaddresslist))
                    pass
                servervulnum_serviceplatform_dict = dict(servervulnum_serviceplatform_list)
                servervullevel_serviceplatform_dict = dict(servervullevel_serviceplatform_list)
                servervulexplevel_serviceplatform_dict = dict(servervulexplevel_serviceplatform_list)
                servervulexpaddress_serviceplatform_dict = dict(servervulexpaddress_serviceplatform_list)
                    # print(servervulnum_serviceplatform_dict)
                servervulnum_servicetype_list.append((servicetype,servervulnum_serviceplatform_dict))
                servervullevel_servicetype_list.append((servicetype,servervullevel_serviceplatform_dict))
                servervulexplevel_servicetype_list.append((servicetype,servervulexplevel_serviceplatform_dict))
                servervulexpaddress_servicetype_list.append((servicetype,servervulexpaddress_serviceplatform_dict))
                pass
            servervulnum_servicetype_dict = dict(servervulnum_servicetype_list)
            servervullevel_servicetype_dict = dict(servervullevel_servicetype_list)
            servervulexplevel_servicetype_dict = dict(servervulexplevel_servicetype_list)
            servervulexpaddress_servicetype_dict = dict(servervulexpaddress_servicetype_list)
            # print(servervulnum_servicetype_dict)
            servervulnum_ostype_list.append((ostype,servervulnum_servicetype_dict))
            servervullevel_ostype_list.append((ostype,servervullevel_servicetype_dict))
            servervulexplevel_ostype_list.append((ostype,servervulexplevel_servicetype_dict))
            servervulexpaddress_ostype_list.append((ostype,servervulexpaddress_servicetype_dict))
            pass
        servervulnum = dict(servervulnum_ostype_list)
        servervullevel = dict(servervullevel_ostype_list)
        servervulexplevel = dict(servervulexplevel_ostype_list)
        servervulexpaddress = dict(servervulexpaddress_ostype_list)
        pass
    elif types == 'emulation':
        # to do!
        # finish in the future
        pass
    else:
        print('Error vul types, please check!')
        pass
    vulstate['vulnums'] = servervulnum
    vulstate['vullevels'] = servervullevel
    vulstate['vulexplevels'] = servervulexplevel
    vulstate['vulexpaddresses'] = servervulexpaddress
    # print(vulstate)
    return vulstate


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
    defview = globalvar.get_value('defview')
    if type == 'att':  # initialize attacker nodes
        attnodelist = []
        for attnum in range(0, simstate.attackernum):
            attnodeid = 'att' + str(attnum + 1)
            # the attacker node is set to '-1' since we can't know the attacker's state
            attnode = node(-1, -1, -1, -1, -1, -1, -1, -
                           1, -1, -1, -1, attnodeid, 'up', False, [])
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
                serviceplatformlinux = simstate.nodeserviceplatform['HTTP']
                serviceplatformlinux.remove('IIS')
                # print(serviceplatformlinux)
                serverserviceplatform = serviceplatformlinux[round(
                    random.uniform(0, len(serviceplatformlinux) - 1))]
                pass
            else:
                print('Error Os type and service platform type, please check!')
                pass
            nodeworkingstate = 'up'
            nodebackdoor = False
            nodedeftype = ['ipmutation', 'osmutation',
                           'serviceplatformmutation', 'ASLR']
            servervulnum = defview['vulstate']['vulnums'][serveros][serverservicetype][serverserviceplatform]
            servervullevel = defview['vulstate']['vullevels'][serveros][serverservicetype][serverserviceplatform]
            servervulexplevel = defview['vulstate']['vulexplevels'][serveros][serverservicetype][serverserviceplatform]
            servervulexpaddress = defview['vulstate']['vulexpaddresses'][serveros][serverservicetype][serverserviceplatform]
            servernode = node(servervulnum, servervullevel, servervulexplevel, servervulexpaddress,
                              ipbase, -1, iniip, iniport, serveros, serverservicetype, serverserviceplatform, servernodeid, nodeworkingstate, nodebackdoor, nodedeftype)
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
                            1, -1, -1, -1, usernodeid, 'up', False, [])
            usrnodelist.append(usernode)
            print('usrnode No.%d of %d has been initialized! ' %
                  (usernum + 1, simstate.usernum))
            pass
        return usrnodelist
    else:
        print('no such type of node! please check! ')
        pass
    pass


def sysplayerini(type, simstate):
    if type == 'att':
        # in this version, only cyber kill chain like attacke type is considered.
        # // DoS and other type of attack is under developed
        # for strategy CKC-C means need continuous C&C and CKC-D means need discrete C&C
        # for objective, there are three type: Data Exfiltration, Network Spreading, System Disruption
        # and in this version, only system disruption is under considerd.
        attacker = sysplayer('CKC-D', 'Sys-Dis', 'low')
        return attacker
    elif type == 'def':
        defstrategy = ['ipmutation', 'osmutation', 'serviceplatformmutation']
        defobjective = {}
        defobjective['ippool'] = [20, 100, 200]
        defobjective['portpool'] = [200, 1000, 5000]
        defobjective['ospool'] = simstate.nodeostypes  # Windows and Linux
        defobjective['servicepool'] = {}
        for ostype in simstate.nodeostypes:
            if ostype == 'Windows':
                defobjective['servicepool']['Windows'] = {}
                # print(simstate.nodeserviceplatform['HTTP'])
                defobjective['servicepool']['Windows']['HTTP'] = (
                    simstate.nodeserviceplatform['HTTP'])
                defobjective['servicepool']['Windows']['FTP'] = (
                    simstate.nodeserviceplatform['FTP'])
                defobjective['servicepool']['Windows']['Media'] = (
                    simstate.nodeserviceplatform['Media'])
                pass
            elif ostype == 'Linux':
                defobjective['servicepool']['Linux'] = {}
                # print(simstate.nodeserviceplatform['HTTP'])
                defobjective['servicepool']['Linux']['HTTP'] = (
                    simstate.nodeserviceplatform['HTTP'])
                defobjective['servicepool']['Linux']['FTP'] = (
                    simstate.nodeserviceplatform['FTP'])
                defobjective['servicepool']['Linux']['Media'] = (
                    simstate.nodeserviceplatform['Media'])
                pass
            # elif ostype == 'Unix':
            else:
                print('os type error, pleast check!')
                pass
            pass
        # print(defobjective['servicepool']['Linux']['HTTP'])

        defobjective['ipfreq'] = [30, 100, 300]  # ip change frequency (s)
        defobjective['portfreq'] = [50, 150, 300]  # port chagne frequency (s)
        # service chagne frequency (s)
        defobjective['servicefreq'] = [100, 300, 1200]
        defobjective['osfreq'] = [200, 600, 1200]  # OS chagne frequency (s)
        defender = sysplayer(defstrategy, defobjective, -1)
        return defender
    elif type == 'usr':
        systemuser = sysplayer('http-web', 'http-web', -1)
        return systemuser
    else:
        print('no such type of system player! please check')
        pass

    pass