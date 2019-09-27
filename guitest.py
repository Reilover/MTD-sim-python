from tkinter import *
root = Tk()
root.title('试试文本框右键菜单')
root.resizable(False, False)
root.geometry("300x100+200+20")
Label(root, text='下面是一个刚刚被生成的文本框，试试操作吧').pack(side="top")
Label(root).pack(side="top")
show = StringVar()
Entry = Entry(root, textvariable=show, width="30")
Entry.pack()
class section:
    def onPaste(self):
        try:
            self.text = root.clipboard_get()
        except TclError:
            pass
        show.set(str(self.text))
    def onCopy(self):
        self.text = Entry.get()
        root.clipboard_append(self.text)
    def onCut(self):
        self.onCopy()
        try:
            Entry.delete('sel.first', 'sel.last')
        except TclError:
            pass
section = section()
menu = Menu(root, tearoff=0)
menu.add_command(label="复制", command=section.onCopy)
menu.add_separator()
menu.add_command(label="粘贴", command=section.onPaste)
menu.add_separator()
menu.add_command(label="剪切", command=section.onCut)
def popupmenu(event):
    menu.post(event.x_root, event.y_root)
Entry.bind("<Button-3>", popupmenu)
root.mainloop()