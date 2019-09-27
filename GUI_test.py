import time
import math
import globalvar
from tkinter import *


class node:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.nodetype = ''
        self.nodeip = ''
        self.nodepltform = ''
        self.nodeservice = ''
        self.defensetype = ''
        pass

class player:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.type = ''
        pass

class defender(player):
    def __init__(self):
        self.tau = '' 
        self.omega = ''
        self.mu = ''
        self.strategy = ''
        super().__init__()

    pass

class A:

    def __init__(self, master=None):
        self.root = master
        self.root.geometry('800x700')
        self.root.title('动态目标防御评估与优化仿真测试软件-界面测试')
        # self.root.bind("<Motion>", self.call_back)
        # 初始化时定义frame
        self.frm_topo = Frame(self.root)
        self.frm_node = Frame(self.root)
        self.frm_metric = Frame(self.root)
        self.frm_output = Frame(self.root)
        self.frm_option = Frame(self.root)
        # 初始化时定义其他界面元素
        self.canvas_topo = Canvas(self.frm_topo)
        self.list_demo = Listbox(self.frm_node)
        self.label_metric = Label(self.frm_metric)
        self.label_output = Label(self.frm_output)
        # 根据初始化元素，创建基本界面框架
        self.demoini()
        self.createpage()

    def call_back(self, event):
        print('现在的位置是：', event.x_root, event.y_root)

    def do_job(self):
        print("hello world")

    def run_simulation(self):

        simresults = StringVar()
        simresults.set('节点生成完毕!\n 拓扑生成完毕!\n 模拟环境参数设置完毕!\n\n 开始模拟!\n')
        self.label_output.config(textvariable=simresults)
        self.label_output.place(x=0, y=20)
        pass

    def demoini(self):
        nodenum = [2, 1, 1]
        global servernodelist,clientnodelist,attacknodelist,defenderlist
        servernodelist = []
        clientnodelist = []
        attacknodelist = []
        defenderlist = []
        for si in range(nodenum[0]):
            servernode = node()
            servernode.id = si
            servernode.name = 'Server_'+str(si)
            servernode.nodetype = 'Server'
            servernode.nodeip = '10.23.5.101==192.168.0.101'
            servernode.nodepltform = 'Ubuntu'
            servernode.nodeservice = 'Apache-web'
            servernode.defensetype = 'NMTD'
            servernodelist.append(servernode)
            nodedefender = defender()
            nodedefender.id = si
            nodedefender.name = servernode.defensetype+'@'+servernode.name
            nodedefender.type = servernode.defensetype
            nodedefender.tau = '50'
            nodedefender.omega = '200'
            nodedefender.mu = 'Pure-random'
            nodedefender.strategy = 'Time-fix'
            defenderlist.append(nodedefender)
            pass
        for ci in range(nodenum[1]):
            clientnode = node()
            clientnode.id = ci
            clientnode.name = 'Client_'+str(ci)
            clientnode.nodetype = 'Client'
            clientnode.nodeip = '192.168.0.105'
            clientnode.nodepltform = 'Windows'
            # servernode.nodeservice = 'Unknow'
            clientnodelist.append(clientnode)
            pass
        for ai in range(nodenum[2]):
            attacknode = node()
            attacknode.id = ai
            attacknode.name = "Attacker_"+str(ai)
            attacknode.nodetype = 'Attacker'
            attacknode.nodeip = '10.23.36.25'
            attacknode.nodepltform = 'Unknow'
            # servernode.nodeservice = 'Apache-web'
            attacknodelist.append(attacknode)
            pass
        # globalvar.set_value('servernodelist',servernodelist)
        pass

    def shownodemetric(self, event):
        w = event.widget
        print(w.curselection())
        print(self.list_demo.curselection())
        index = int(w.curselection()[0])
        value = w.get(index)
        nodetype = value.split('_', 1 )[0]
        nodeid = value.split('_', 1 )[1]
        if nodetype == 'Server':
            nodeselect = servernodelist[int(nodeid)]
            nodeipout = nodeselect.nodeip.split('==',1)[0]
            nodeipin = nodeselect.nodeip.split('==',1)[1]
            nodedefenderselect = defenderlist[int(nodeid)]
            node_metric = StringVar()
            node_metric.set('名称: ' + nodeselect.name + '\n'
                            + '内IP地址: '+ nodeipin + '\n'
                            + '外IP地址: '+ nodeipout + '\n'
                            + '运行平台: '+ nodeselect.nodepltform + '\n'
                            + '系统服务: '+ nodeselect.nodeservice + '\n'
                            + 'MTD部署: '+ nodeselect.defensetype + '\n'
                            + 'MTD周期: '+ nodedefenderselect.tau + '\n'
                            + 'MTD空间: '+ nodedefenderselect.omega + '\n'
                            + 'MTD方法: '+ nodedefenderselect.mu + '\n'
                            + 'MTD策略: '+ nodedefenderselect.strategy + '\n')
            pass
        elif nodetype == 'Client':
            node_metric = StringVar()
            node_metric.set('名称: ' + value + '\n'+ 'IP地址: '+'192.168.0.101')
            pass
        elif nodetype == 'Attacker':
            node_metric = StringVar()
            node_metric.set('Node name: ' + value + '\n'+ 'Node ip: '+'192.168.0.101')
            pass
        else:
            print('Error selection')
            node_metric = StringVar()
            node_metric.set('Node name: None' + '\n'+ 'Node ip: None')
            pass


        self.label_metric.config(textvariable=node_metric)
        self.label_metric.place(x=3, y=20)
        pass

    def drawtopo(self, nodelist):
        print(nodelist)
        titleFont = ('微软雅黑', 8, 'bold')
        servernode_op = (2, 'blue', 'blue', None)
        clientnode_op = (2, 'green', 'green', None)
        attacknode_op = (2, 'red', 'red', None)
        line_op = (1, 'black', None, None, None)

        for si in servernodelist:
            nodeimage_yplace = 50 + int(si.id * 150)
            nodetext_yplace = nodeimage_yplace - 10
            self.canvas_topo.create_oval(400, nodeimage_yplace, 420, nodeimage_yplace+20,
                width=servernode_op[0],  # 边框宽度
                fill=servernode_op[1],  # 填充颜色
                outline=servernode_op[2],  # 边框颜色
                stipple=servernode_op[3])  # 使用位图填充
            self.canvas_topo.create_text(390, nodetext_yplace, text = si.name,
                font = titleFont,
                fill='blue',
                anchor = W,
                justify = LEFT)
                
            pass


        self.canvas_topo.create_rectangle(40, 350, 60, 370,
                    width=clientnode_op[0],  # 边框宽度
                    fill=clientnode_op[1],  # 填充颜色
                    outline=clientnode_op[2],  # 边框颜色
                    stipple=clientnode_op[3])  # 使用位图填充
        self.canvas_topo.create_text(30, 340, text = 'Client_0',
                font = titleFont,
                fill='green',
                anchor = W,
                justify = LEFT)

        self.canvas_topo.create_polygon(40, 100, 50, 80, 60, 100,
                    width=attacknode_op[0],  # 边框宽度
                    fill=attacknode_op[1],  # 填充颜色
                    outline=attacknode_op[2],  # 边框颜色
                    stipple=attacknode_op[3])  # 使用位图填充
        self.canvas_topo.create_text(25,70, text = 'Attacker_0',
                font = titleFont,
                fill='red',
                anchor = W,
                justify = LEFT)
        
        
        self.canvas_topo.create_line(410, 210, 410, 60,
        width = line_op[0], # 边框宽度
        fill = line_op[1], # 填充颜色
        stipple = line_op[2], # 使用位图填充
        arrow = line_op[3], # 箭头风格
        arrowshape = line_op[4]) # 箭头形状
        
        self.canvas_topo.create_line(50, 90, 410, 60,
        width = line_op[0], # 边框宽度
        fill = line_op[1], # 填充颜色
        stipple = line_op[2], # 使用位图填充
        arrow = line_op[3], # 箭头风格
        arrowshape = line_op[4]) # 箭头形状



        self.canvas_topo.create_line(50, 360, 410, 60,
        width = line_op[0], # 边框宽度
        fill = line_op[1], # 填充颜色
        stipple = line_op[2], # 使用位图填充
        arrow = line_op[3], # 箭头风格
        arrowshape = line_op[4]) # 箭头形状
        
        pass

    def bindnodes(self):
        print("bind nodes to topo")
        var_nowtopo = StringVar()  # Label显示的文字要是会变化的话，只接受这种类型的变量
        var_nowtopo.set("默认模拟实验配置已加载！")
        label_nowtopo_frm_topo = Label(self.frm_topo, fg='black', textvariable=var_nowtopo,
                                       font='Verdana 10').place(x=50, y=0, height=30, width=500)
        self.canvas_topo.place(x=50, y=50, width=500, height=400)
        listi = 0
        node_list_get = []
        while self.list_demo.get(listi) != '':
            # print('{0} 和 {1}'.format(listi, self.list_demo.get(listi)))
            node_list_get.append(self.list_demo.get(listi))
            listi = listi + 1
            pass
        print("%s", node_list_get)
        self.drawtopo(node_list_get)

    def insert_demo(self):
        print("Insert demo!")
        var_demo = StringVar()  # 定义变量
        var_demo_nodenamelist = []
        for si in servernodelist:
            var_demo_nodenamelist.append(si.name)
            pass
        for ci in clientnodelist:
            var_demo_nodenamelist.append(ci.name)
            pass
        for ai in attacknodelist:
            var_demo_nodenamelist.append(ai.name)
            pass
        var_demo.set(var_demo_nodenamelist)
        # scrolly = Scrollbar(self.frm_node)
        # scrolly.pack(side=RIGHT, fill=Y)
        self.list_demo.config(selectmode=SINGLE, listvariable=var_demo)
        self.list_demo.place(x=3, y=30, width=140)
        # scrolly.config(command=node_list.yview)
        self.list_demo.bind('<Double-Button-1>', self.shownodemetric)
        self.bindnodes()

    def createpage(self):
        # 添加menu菜单项
        menu = Menu(self.root)
        self.root.config(menu=menu)
        # 文件菜单初始化
        filemenu = Menu(menu, tearoff=0)
        menu.add_cascade(label='文件', menu=filemenu)
        filemenu.add_command(label='新建', command=self.insert_demo)
        filemenu.add_command(label='打开', command=self.do_job)
        filemenu.add_command(label='保存', command=self.do_job)
        filemenu.add_separator()    # 添加一条分隔线
        # 用tkinter里面自带的quit()函数
        filemenu.add_command(label='退出', command=self.root.quit)    
       
        # 运行菜单初始化
        runmenu = Menu(menu, tearoff=0)
        menu.add_cascade(label='运行', menu=runmenu)
        runmenu.add_command(label='模拟运行', command=self.run_simulation)
        runmenu.add_command(label='结果分析', command=self.do_job)
        
        #分析菜单初始化
        runmenu = Menu(menu, tearoff=0)
        menu.add_cascade(label='分析', menu=runmenu)
        runmenu.add_command(label='结果分析', command=self.do_job)
        runmenu.add_command(label='结果展示', command=self.do_job)


        # 帮助菜单初始化
        helpmenu = Menu(menu, tearoff=0)
        menu.add_cascade(label='帮助',menu=helpmenu)
        helpmenu.add_command(label='查看帮助', command=self.do_job)
        
        # 生成对frame的配置（位置，大小，颜色等等）
        # self.frm_option.config(bg='grey', height=30, width=760)
        # Label(self.frm_option, text='Option').place(
        #     in_=self.frm_option, anchor=NW)
        # self.frm_option.place(x=20, y=0)

        self.frm_topo.config(height=500, width=600,bd=2,relief=GROOVE) # bg='blue', 
        Label(self.frm_topo, text='拓扑结构').place(in_=self.frm_topo, anchor=NW)
        self.frm_topo.place(x=180, y=0)

        self.frm_node.config( height=250, width=150,bd=2,relief=GROOVE) # bg='red',
        Label(self.frm_node, text='节点信息').place(anchor=NW)
        self.frm_node.place(x=20, y=0)

        self.frm_metric.config( height=250, width=150,bd=2,relief=GROOVE) # bg='yellow',
        Label(self.frm_metric, text='节点属性').place(
            in_=self.frm_metric, anchor=NW)
        self.frm_metric.place(x=20, y=250)

        self.frm_output.config(height=150, width=760,bd=2,relief=GROOVE) # bg='green', 
        Label(self.frm_output, text='模拟输出').place(
            in_=self.frm_output, anchor=NW)
        self.frm_output.place(x=20, y=510)

        # frm_node下listbox
        # scrolly = Scrollbar(self.frm_node)
        #  # scrolly.pack(side=RIGHT, fill=Y)
        # Listbox(self.frm_node,yscrollcommand=scrolly.set).place(x=5, y=30, width=140)
        # scrolly.config(command=node_list.yview)

        # frm_metric下的Label
        # Label(self.frm_metric, text='Metric Show:',
        #       fg='red', font='Verdana 10 bold').place(x=0, y=30)

        # Label(self.frm_output,text='Result Show',fg='red', font='Verdana 10 bold').place(x=0,y=20)
        # frm_option下的Button
        # Button(self.frm_option, text='Insert',
        #        command=self.insert_demo).place(x=50, y=0, width=50)
        # Button(self.frm_option, text='Bind',
        #        command=self.bindnodes).place(x=110, y=0, width=50)
        # Button(self.frm_option, text='Start').place(x=170, y=0, width=50)
        # Button(self.frm_option, text='Stop').place(x=230, y=0, width=50)
        # Button(self.frm_option, text='Clear ').place(x=290, y=0, width=50)

        # frm_topo下的控件
        # Label(self.frm_topo, text='拓扑结构展示',
        #       fg='red', font='Verdana 10 bold').place(x=100, y=50, height=80, width=400)


if __name__ == '__main__':
    root = Tk()
    A(root)
    mainloop()
