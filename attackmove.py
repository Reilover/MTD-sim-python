import random
import itertools
import simpy
import numpy
import sysutil
import globalvar
import systemini
global attview
global defview
global usrview
global interruptproc
global datatosave

attview = globalvar.get_value('attview')
defview = globalvar.get_value('defview')
usrview = globalvar.get_value('usrview')
interruptproc = globalvar.get_value('interruptproc')
datatosave = globalvar.get_value('datatosave')


class attackermove(object):
    def __init__(self, env):
        self.env = env
        self.action = env.process(self.attaction(env))
        # self.att_controlandcommand_proc = env.process(self.att_controlandcommand(env, attstate, attackholdingtimes))

    def attaction(self, env):
        attview = globalvar.get_value('attview')
        defview = globalvar.get_value('defview')
        attstrategy = attview['attackers'].strategy
        attobj = attview['attackers'].objective
        attabi = attview['attackers'].ability
        attwinstate = self.attwinstateini(attstrategy)
        attzday = self.attabiini(attabi)
        attview['attackerwinstate'] = attwinstate
        attview['attackerzday'] = attzday
        attview['targetnodes'] = []
        attview['malwaresave'] = []
        attview['malwaresend'] = []
        attview['malwareinstall'] = []
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
        attstate['C&Ctime'] = 100
        for vulnodesnum in range(len(attstate['vulnodes'])):
            vulnodeid = 'target_' + str(vulnodesnum + 1)
            vulnode = systemini.node(-1, -1, -1, -1, -1, -1, -1, -
                           1, -1, -1, -1, vulnodeid, 'up', False, [])
            attview['targetnodes'].append(vulnode)
            pass
        globalvar.set_value('attview',attview)
        while True:
            attview = globalvar.get_value('attview')
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
                '------ Error type of attack objective! Please check and only \'CKC\' and \'DoS\' is supported ------')
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
        undonephase = sysutil.get_keys(attackstates, False)
        return undonephase

    # using topo links to find target nodes, which have external link to attack nodes. 
    def attchecktarnodes(self, nodenum):
        defview = globalvar.get_value('defview')
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
            interruptproc['att_controlandcommand_proc'] = att_controlandcommand_proc
            globalvar.set_value('interruptproc',interruptproc)
            yield att_controlandcommand_proc
            pass
        elif atttype == 'AoO':
            attackholdingtimes = 2
            yield env.process(self.att_attonobj(env, attstate, attackholdingtimes))
            pass
        else:
            print('------ Error attack type, please check! ------')
            pass

        pass

    def att_reconnaissance(self, env, attstate, attackholdingtimes):
        # print('Reconnaissance Attack!')
        
        if attstate['iniip'] > attstate['endip']:
            attstate['iniip'] = 0
            pass
        for vulnodeindex in range(len(attstate['vulnodes'])):
            # print('------ the attacker reconnaissance node is : %s, ip is: %d, Real ip is: %d,at time: %d ------' % 
            #         (attstate['vulnodes'][vulnodeindex].nodeid,attstate['iniip'],attstate['vulnodes'][vulnodeindex].ip,env.now))
            # print(attstate['vulnodes'][vulnodeindex].ip)
            attview = globalvar.get_value('attview')
            if attstate['vulnodes'][vulnodeindex].ip == attstate['iniip'] or attstate['iniip'] == attview['targetnodes'][vulnodeindex].ip or attstate['vulnodes'][vulnodeindex].ip == attview['targetnodes'][vulnodeindex].ip:
                yield env.timeout(attackholdingtimes)
                attview['targetnodes'][vulnodeindex] = systemini.node(attstate['vulnodes'][vulnodeindex].vulnum, attstate['vulnodes'][vulnodeindex].vullevel,
                                                            attstate['vulnodes'][vulnodeindex].vulexplevel, attstate[
                                                                'vulnodes'][vulnodeindex].vulexpaddress,
                                                            attstate['vulnodes'][vulnodeindex].ipbase, attstate['vulnodes'][vulnodeindex].ippool,
                                                            attstate['vulnodes'][vulnodeindex].ip, attstate['vulnodes'][
                                                                vulnodeindex].port, attstate['vulnodes'][vulnodeindex].os,
                                                            attstate['vulnodes'][vulnodeindex].servicetype, attstate[
                                                                'vulnodes'][vulnodeindex].serviceplatform,
                                                            attstate['vulnodes'][vulnodeindex].nodeid, attstate[
                                                                'vulnodes'][vulnodeindex].nodeworkingstate,
                                                            attstate['vulnodes'][vulnodeindex].nodebackdoor, attstate['vulnodes'][vulnodeindex].nodedeftype)
                # in python, the global vers with list type only point to the vers with assignment, so to keep the global vers not change with local vers we have to
                # 'new' a class and assignment to the global ver
                attview['attackerwinstate']['reconnaissance'] = True
                print('------ reconnaissance success at time: %d! the target node: %s ip is: %d ------' %
                      (env.now, attview['targetnodes'][vulnodeindex].nodeid, attview['targetnodes'][vulnodeindex].ip))
                globalvar.set_value('attview',attview)
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
        malwarecraftexptime = []
        attview = globalvar.get_value('attview')
        # defview = globalvar.get_value('defview')
        for targetnode in attview['targetnodes']:
            weaponcrafttime = []
            print('------ target node: %s (os type: %s and service platform: %s) has: %d vuls and vullevel is: %s vulexplevel is: %s vulexpaddress is: %s ------' % (
                targetnode.nodeid, targetnode.os, targetnode.serviceplatform, targetnode.vulnum, targetnode.vullevel, targetnode.vulexplevel, repr(targetnode.vulexpaddress)))
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
                    print("------ Error vuls' exploition level, please check ------")
                    pass
                pass
                weaponcrafttime.append(wct)
                attabi = attview['attackers'].ability
                if attabi == 'low':
                    crafttime = max(weaponcrafttime)
                    exploitaddress = targetnode.vulexpaddress[weaponcrafttime.index(
                        crafttime)]
                    exploitationtime = 30
                    pass
                # elif attabi == 'medium': # for medium attack ability, the exploition address is a problem so this part is not support in this version
                #     crafttime = int(
                #         (max(weaponcrafttime) + min(weaponcrafttime)) / 2)
                #     pass
                elif attabi == 'high':
                    crafttime = min(weaponcrafttime)
                    exploitaddress = targetnode.vulexpaddress[weaponcrafttime.index(
                        crafttime)]
                    exploitationtime = 10
                    pass
                else:
                    print('------ Error attacker ability, please check! ------')
                    pass
            malwarecrafttime.append(crafttime)
            malwarecraftos.append(targetnode.os)
            malwarecraftserviceplatform.append(targetnode.serviceplatform)
            malwarecraftexpaddress.append(exploitaddress)
            malwarecraftexptime.append(exploitationtime)
            pass

        
        # if have several assailable node, attack the most weak one(less malware craft time)
        
        malwareworkingos = malwarecraftos[malwarecrafttime.index(min(malwarecrafttime))]
        malwarewokingtime = min(malwarecrafttime)
        malwareworkingplatform = malwarecraftserviceplatform[malwarecrafttime.index(min(malwarecrafttime))]
        malwareworkingexpaddress = malwarecraftexpaddress[malwarecrafttime.index(min(malwarecrafttime))]
        malwareworkingtarget = attview['targetnodes'][malwarecrafttime.index(min(malwarecrafttime))]
        malwareid = 'malware-'+ malwareworkingtarget.nodeid+'-'+malwareworkingos+'-'+malwareworkingplatform
        malwarewokingexptime = malwarecraftexptime[malwarecrafttime.index(min(malwarecrafttime))]
        malwarewokingversion = 'att'
        malwaresave = systemini.malware(malwareid,malwareworkingos,malwareworkingplatform,malwareworkingexpaddress,malwarewokingversion,malwarewokingtime,malwarewokingexptime,malwareworkingtarget)
        
        malwarecrafted = []
        for malwares in attview['malwaresave']:
            malwarecrafted.append(malwares.malwareid)
            pass
        if malwaresave.malwareid in malwarecrafted:
            print('------ malware: %s is already crafted! ------' % (malwaresave.malwareid))
            attview['attackerwinstate']['weapon'] = True
            globalvar.set_value('attview',attview)
            attackholdingtimes = 2
            yield env.timeout(attackholdingtimes)
            pass
        else:
            print('------ malware craft time is: %s ------' %
                        (malwarecrafttime))
            print('------ malware weapon craft start at time: %d ------' % (env.now))
            attview['malwaresave'].append(malwaresave)
            attackholdingtimes = min(malwarecrafttime)
            yield env.timeout(attackholdingtimes)
            attview['attackerwinstate']['weapon'] = True
            globalvar.set_value('attview',attview)
            print('------ malware weapon craft end at time %d ------' % (env.now))
            print('------ malware weapon state for target node %s are: os-type: %s, service-platform: %s, exploition-address: %d, exploition-time: %d ------' %
                (malwaresave.targetnode.nodeid, malwaresave.expos, malwaresave.expserviceplatform, malwaresave.exploitationaddress,malwaresave.exploitationtime))
            pass

        # print(attview['malwaresave']['malwarecraftserviceplatform'])
        pass

    def att_delivery(self, env, attstate, attackholdingtimes):
        malwaresend = []
        attview = globalvar.get_value('attview')
        for vulnode in attstate['vulnodes']:
            for targetnode in attview['targetnodes']:
                if targetnode.nodeid == vulnode.nodeid:
                    if targetnode.ip == vulnode.ip:
                        if vulnode.nodeworkingstate == 'up':
                            for malware in attview['malwaresave']:
                                if malware.targetnode.nodeid == targetnode.nodeid and malware.targetnode.nodeid == vulnode.nodeid:
                                    malwaresend.append(malware)
                                else:
                                    print('------ malware target does not match target node and vul node, Weapon will restart! ------')
                                    attview['attackerwinstate']['weapon'] = False
                                    globalvar.set_value('attview',attview)
                                    yield env.timeout(attackholdingtimes) 
                                    pass
                                pass
                            pass
                            if len(malwaresend) > 0:
                                print('------ delivery start at time: %d, sending malware to: %s with ip: %d ------' % (
                                    env.now, targetnode.nodeid, targetnode.ip))
                                yield env.timeout(attackholdingtimes)
                                attview['attackerwinstate']['delivery'] = True
                                attview['malwaresend'] = []
                                attview['malwaresend'] = (malwaresend)
                                globalvar.set_value('attview',attview)
                                print('------ delivery successed at time: %d ------' % (env.now))
                                pass
                            else:
                                print('------ No malware can be sent to target node: %s, reconnaissance and weapon will restart!　------' % (targetnode.nodeid))
                                attview['attackerwinstate']['reconnaissance'] = False
                                attview['attackerwinstate']['weapon'] = False
                                attstate['iniip'] = 0
                                globalvar.set_value('attview',attview)
                                pass     
                        else:
                            print('------ target node: %s is not online, delivery will try: %d time step later! ------' % (
                                    vulnode.nodeid, attackholdingtimes))
                            yield env.timeout(attackholdingtimes)
                            pass
                        pass
                    else:
                        print('------ delivery can not start at time: %d, error target ip address (attacker know ip is: %d, target real ip is: %d) ------' % (
                                env.now, targetnode.ip, vulnode.ip))
                        print(
                            '------ reconnaissance will restart to get the real ip for target node: %s at time: %d! ------' % 
                                    (targetnode.nodeid, (env.now+attackholdingtimes)))
                        attview['attackerwinstate']['reconnaissance'] = False
                        attstate['iniip'] = 0
                        globalvar.set_value('attview',attview)
                        yield env.timeout(attackholdingtimes) 
                    pass
                else:
                    print('------ target node is not in vul nodes, Reconnaissance will restart! ------')
                    attview['attackerwinstate']['reconnaissance'] = False
                    attstate['iniip'] = 0
                    globalvar.set_value('attview',attview)
                    yield env.timeout(attackholdingtimes) 
                    pass
                pass
            pass
        pass
    def att_exploition(self, env, attstate, attackholdingtimes):
        # print('target node vul exploition address is ')
        # print(repr(attview['malwaresend']))
        attview = globalvar.get_value('attview')
        for malwareindex in range(len(attview['malwaresend'])):
            # print(malwareindex)
            for vulnode in attstate['vulnodes']:
                if vulnode.nodeid == attview['malwaresend'][malwareindex].targetnode.nodeid:
                    for targetnode in attview['targetnodes']:
                        if targetnode.nodeid == attview['malwaresend'][malwareindex].targetnode.nodeid:
                            if targetnode.os == vulnode.os and attview['malwaresend'][malwareindex].expos == vulnode.os:
                                if targetnode.serviceplatform == vulnode.serviceplatform and attview['malwaresend'][malwareindex].expserviceplatform == vulnode.serviceplatform:
                                    if attview['malwaresend'][malwareindex].exploitationaddress in vulnode.vulexpaddress:
                                        if vulnode.nodeworkingstate == 'up':
                                            print('------ malware exploition start at: %d, target node id is: %s, os is: %s, service platform is: %s, vuls address is: %d ------' %
                                                (env.now, targetnode.nodeid, targetnode.os, targetnode.serviceplatform, attview['malwaresend'][malwareindex].exploitationaddress))
                                            yield env.timeout(attackholdingtimes)
                                            attview['attackerwinstate']['exploition'] = True
                                            globalvar.set_value('attview',attview)
                                            print(
                                                '------ exploition successed at time: %d ------' % (env.now))
                                            return
                                        else:
                                            print('------ target node: %s is not online, exploition will try %d time step later! ------' % (
                                                vulnode.nodeid, attackholdingtimes))
                                            yield env.timeout(attackholdingtimes)
                                            pass
                                        pass
                                    else:
                                        # this part will come soon!
                                        print(
                                            '------ target node using ASLR, exploition will try later! ------')
                                        yield env.timeout(attackholdingtimes)
                                        pass
                                    pass
                                else:
                                    if malwareindex == len(attview['malwaresend']) - 1:
                                        print(
                                        '------ target node servie paltform is not match malware: %s, reconnaissance and weapon craft will re-start soon ------' %(attview['malwaresend'][malwareindex].malwareid))
                                        attview['attackerwinstate']['weapon'] = False
                                        attview['attackerwinstate']['reconnaissance'] = False
                                        attview['attackerwinstate']['delivery'] = False
                                        attstate['iniip'] = 0
                                        globalvar.set_value('attview',attview)
                                        yield env.timeout(attackholdingtimes)
                                        pass
                                    else:
                                        continue
                                    pass
                                pass
                            else:
                                if malwareindex == len(attview['malwaresend']) - 1:
                                        print(
                                        '------ target node servie paltform is not match malware: %s, reconnaissance and weapon craft will re-start soon ------' %(attview['malwaresend'][malwareindex].malwareid))
                                        attview['attackerwinstate']['weapon'] = False
                                        attview['attackerwinstate']['reconnaissance'] = False
                                        attview['attackerwinstate']['delivery'] = False
                                        attstate['iniip'] = 0
                                        globalvar.set_value('attview',attview)
                                        yield env.timeout(attackholdingtimes)
                                        pass
                                else:
                                    continue
                                pass
                            pass
                        else:
                            print(
                                '------ target node is not match exploition type! ------')
                            pass
                        pass
                else:
                    print('------ vul node is not match exploition type! ------')
                    pass
                pass
            pass
        pass

    def att_installation(self, env, attstate, attackholdingtimes):
        attview = globalvar.get_value('attview')
        for vulnode in attstate['vulnodes']:
            for targetnode in attview['targetnodes']:
                if vulnode.nodeid == targetnode.nodeid:
                    if vulnode.nodeworkingstate == 'up':
                        if targetnode.os == vulnode.os:
                            print('------ Other malware intstallation start at: %d, target node id is: %s, os is: %s ------' %
                                    (env.now, targetnode.nodeid, targetnode.os))
                            yield env.timeout(attackholdingtimes)
                            attview['attackerwinstate']['installation'] = True
                            defview['servernodes'][defview['servernodes'].index(
                                vulnode)].nodebackdoor = True
                            globalvar.set_value('attview',attview)
                            globalvar.set_value('defview',defview)
                            # print(defview['servernodes'].index(vulnode))
                            print('------ installation successed at time: %d, target node: %s backdoor state is: %s ------' %
                                    (env.now, targetnode.nodeid, format(defview['servernodes'][defview['servernodes'].index(vulnode)].nodebackdoor, "")))
                            pass
                        else:
                            print(
                                '------ target node servie os type is not match installing other backdoor, reconnaissance, weapon craft, delivery and exploition will re-start soon ------')
                            attview['attackerwinstate']['weapon'] = False
                            attview['attackerwinstate']['reconnaissance'] = False
                            attview['attackerwinstate']['delivery'] = False
                            attview['attackerwinstate']['exploition'] = False
                            attstate['iniip'] = 0
                            globalvar.set_value('attview',attview)
                            yield env.timeout(attackholdingtimes)
                            pass
                        pass
                    else:
                        print('------ target node: %s is not online, installation will try: %d time step later! ------' % (
                            vulnode.nodeid, attackholdingtimes))
                        yield env.timeout(attackholdingtimes)
                        pass 
                    pass
                else:
                    print('target node: %s is not in Vul node set: %s' % (targetnode.nodeid, repr(attstate['vulnodes'])))
                    pass
            pass
        pass

    def att_controlandcommand(self, env, attstate, attackholdingtimes):
        # for C&C, only two types are considered. one is continuous C&C for several time step, another is discrete C&C for several time step
        # print('C&C type is %s, need C&C %d time steps' %
        #       (attstate['C&Ctype'], attstate['C&Ctime']))
        attview = globalvar.get_value('attview')
        for vulnode in attstate['vulnodes']:
            for targetnode in attview['targetnodes']:
                if vulnode.nodeworkingstate == 'up':
                    if vulnode.ip == targetnode.ip:
                        if vulnode.nodebackdoor:
                            attstate['C&C-D'] = {}
                            if attstate['C&Ctype'] == 'C':
                                try:
                                    print('------ C&C type is %s. Start C&C on target node %s at time %d for continuous %d time steps ------' %
                                            (attstate['C&Ctype'], targetnode.nodeid, env.now, attstate['C&Ctime']))
                                    yield env.timeout(attstate['C&Ctime'])
                                    attview['attackerwinstate']['C&C'] = True
                                    globalvar.set_value('attview',attview)
                                    print(
                                        '------ C&C successfully end at time %d ------' % (env.now))
                                except simpy.Interrupt:
                                    print(
                                        '------ C&C is interrupted at time %d and C&C has to re-restart! ------' % (env.now))
                                    yield env.timeout(0)
                                    return
                            elif attstate['C&Ctype'] == 'D':
                                try:
                                    print('------ C&C type is %s. Start C&C on target node %s at time %d for continuous %d time steps ------' %
                                            (attstate['C&Ctype'], targetnode.nodeid, env.now, attstate['C&Ctime']))
                                    attstate['C&C-D']['starttime'] = env.now
                                    yield env.timeout(attstate['C&Ctime'])
                                    attview['attackerwinstate']['C&C'] = True
                                    globalvar.set_value('attview',attview)
                                    print(
                                        '------ C&C successfully end at time %d ------' % (env.now))
                                    pass
                                except simpy.Interrupt:
                                    attstate['C&C-D']['interrrupttime'] = env.now
                                    attstate['C&C-D']['timeleft'] = attstate['C&Ctime'] - (
                                        attstate['C&C-D']['interrrupttime'] - attstate['C&C-D']['starttime'])
                                    attstate['C&Ctime'] = attstate['C&C-D']['timeleft']
                                    print(
                                        '------ C&C is interrupted at time %d and need another %d time step to finish C&C! ------' % (env.now, attstate['C&Ctime']))
                                    yield env.timeout(0)
                                    return
                                pass
                            else:
                                print(
                                    '------ Error C&C type, please check! ------')
                                pass
                            pass
                        else:
                            print(
                                '------ target node back door is not exist, reconnaissance, weapon craft, delivery, exploition and installation will re-start at time %d------' %
                                (attackholdingtimes + env.now))
                            attview['attackerwinstate']['weapon'] = False
                            attview['attackerwinstate']['reconnaissance'] = False
                            attview['attackerwinstate']['delivery'] = False
                            attview['attackerwinstate']['exploition'] = False
                            attview['attackerwinstate']['installation'] = False
                            attstate['iniip'] = 0
                            globalvar.set_value('attview',attview)
                            yield env.timeout(attackholdingtimes)
                            pass
                        pass
                    else:
                        try:
                            print('------ target node: %s is not reachable at time: %d in ip: %d for real ip: is %d, reconnaissance will re-start! ------' %
                                (targetnode.nodeid, env.now, targetnode.ip, vulnode.ip))
                            attview['attackerwinstate']['reconnaissance'] = False
                            attstate['iniip'] = 0
                            globalvar.set_value('attview',attview)
                            yield env.timeout(attackholdingtimes)
                            pass
                        except simpy.Interrupt:
                            print('------ CKC is interrupted at time %d! ------' % (env.now))
                            pass

                        
                        pass
                else:
                    print('------ target node: %s is not online, C&C will try %d time step later! ------' % (
                        vulnode.nodeid, attackholdingtimes))
                    yield env.timeout(attackholdingtimes)
                    pass
                pass
            pass
        pass
    pass

    def att_attonobj(self, env, attstate, attackholdingtimes):
        attview = globalvar.get_value('attview')
        yield env.timeout(attackholdingtimes)
        attview['attackerwinstate']['AoO'] = True
        globalvar.set_value('attview',attview)
        print('------ AoO successed at time %d ------' % (env.now))
        pass
