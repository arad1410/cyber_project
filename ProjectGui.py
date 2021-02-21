import wx
import ProjectClient
import os
import threading
import ProjectClientAndServer
import wx.lib.scrolledpanel as scrolled
import wx.richtext as rt
import re
import difflib


# new gui is in charge of all the user interface of the program from getting the users name and password to making all
# the different panels and creates the client and or client or server for the pear to pear connection and file sending
def print_answer(arg):  # prints a message box on the screen
    wx.MessageBox(arg, 'Dialog', wx.OK)


class LogIn(wx.Panel):
    # login is the  first panel and is in charge of getting the users name and password and showing on the screen if
    # there was a mistake
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.SetSize((800, 600))

        wx.StaticText(self, label="Username:", pos=(300, 30))
        self.user = wx.TextCtrl(self, pos=(370, 25))

        # pass info

        wx.StaticText(self, label="Password:", pos=(300, 80))
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER, pos=(370, 75))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn = wx.Button(self, label="Login", pos=(350, 130))
        self.btn2 = wx.Button(self, label="Sign up", pos=(350, 180))


class HomePage(wx.Panel):

    # in charge to create the home page panel and to upload the file name or the file itself

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetSize((800, 600))
        self.user_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.user = wx.TextCtrl(self, pos=(325, 100))
        self.connect = wx.Button(self, label="Start working", pos=(340, 130))
        self.path = None

    def print_name(self, name):
        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        wx.StaticText(self, -1, "hello " + name + " enter user name to work with", (200, 10), ).SetFont(font)


class TopPanel(scrolled.ScrolledPanel):

    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.line_sizer = wx.BoxSizer(wx.VERTICAL)
        self.my_file = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH | wx.TE_READONLY | wx.TE_NO_VSCROLL,
                                   size=(-1, -1))
        self.other_file = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_NO_VSCROLL,
                                      size=(-1, -1))
        self.btn1 = wx.Button(self, label='write changes', size=(700, 30))
        self.btn1.Bind(wx.EVT_BUTTON, self.make_changes, self.btn1)
        # self.boxes = []
        self.boxes = wx.CheckListBox(self, size=(-1, -1))
        # for i in range(100):
        #   self.boxes.append(wx.CheckBox(self))
        self.diff = []

    def write_file(self, my_file, other_file, lines):
        my_file = my_file.split("\n")
        other_file = other_file.split("\n")
        counter = 0
        for my_line, other_line in zip(my_file, other_file):
            counter += 1
            if my_line == other_line:
                self.line_number(wx.GREEN, counter)
                self.my_file.AppendText(my_line + "\n")
                self.other_file.AppendText(other_line + "\n")
            else:
                self.line_number(wx.BLUE, counter)
                self.other_file.SetStyle(0, -1, wx.TextAttr(wx.BLUE))
                self.my_file.AppendText(my_line + "\n")
                self.other_file.AppendText(other_line + "\n")
                self.other_file.SetStyle(0, -1, wx.TextAttr(wx.BLACK))
                self.diff.append(counter)
        self.make_window(lines)

    def line_number(self, color, counter):
        self.my_file.SetStyle(0, -1, wx.TextAttr(color))
        self.other_file.SetStyle(0, -1, wx.TextAttr(color))
        self.my_file.AppendText(str(counter) + ").   ")
        self.other_file.AppendText(str(counter) + ").   ")
        self.other_file.SetStyle(0, -1, wx.TextAttr(wx.BLACK))
        self.my_file.SetStyle(0, -1, wx.TextAttr(wx.BLACK))

    def make_window(self, lines):

        self.my_file.SetMinSize((-1, round(15.5 * lines)))
        self.other_file.SetMinSize((-1, round(15.5 * lines)))
        print(lines)
        # for i in range(lines):
        #   text = wx.StaticText(self, label=str(i))
        # self.line_sizer.Add(text, 1)
        # self.text_sizer.Add(line_sizer, 1)
        # box = wx.BoxSizer(wx.VERTICAL)
        print(self.diff)
        # if self.diff:
        #   box.AddSpacer(round(15.3 * self.diff[0] - 1))
        #  box.Add(self.boxes[self.diff[0]])
        # for i in range(len(self.diff) - 1):
        #    print(i)
        #   print(15.3 * (self.diff[i + 1] - self.diff[i]))
        #  box.AddSpacer(round(15.3 * (self.diff[i + 1] - self.diff[i])))
        # box.Add(self.boxes[i + 1])
        for i in self.diff:
            self.boxes.Append("line " + str(i))
        self.text_sizer.Add(self.my_file, 1, wx.EXPAND)
        # self.text_sizer.Add(box, -1, wx.EXPAND)
        self.text_sizer.Add(self.other_file, 1, wx.EXPAND)
        self.text_sizer.Add(self.boxes, -1, wx.EXPAND)
        self.main_sizer.Add(self.text_sizer, 1, wx.EXPAND)
        self.main_sizer.Add(self.btn1, flag=wx.CENTER)
        self.SetupScrolling()
        self.SetSizer(self.main_sizer)
        self.Layout()
        self.Refresh()

    def make_changes(self, e):
        pass


class Window2(wx.Frame):
    title = "new Window"

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Window2', size=(1300, 600))
        self.top_panel = TopPanel(self)

    def write(self, my_file, other_file, lines):
        self.top_panel.write_file(my_file, other_file, lines)

class Template(wx.Panel):
    """
    This is the main editing page
    """

    def __init__(self, parent):
        """
        in charge of the files page has all the files and file name for display for the user to choose the file he
        wants to download
        :param parent: string
        """
        wx.Panel.__init__(self, parent)
        self.SetSize((800, 600))
        self.sync = wx.Button(self, wx.ID_CLEAR, "SYNC WORK", pos=(300, 540))
        self.my_text = wx.TextCtrl(self, size=(785, 540), style=wx.TE_MULTILINE | wx.TE_RICH)
        self.point = self.my_text.GetInsertionPoint()
        self.text = None
        self.line = self.my_text.PositionToXY(self.my_text.GetInsertionPoint())[2]
        self.client = None
        self.my_text.Bind(wx.EVT_CHAR, self.change_color, self.my_text)
        self.sync.Bind(wx.EVT_BUTTON, self.sync_files)
        self.file = None
        self.last_updated_file = None
        self.dlg = False
        self.lines = None
        self.frame = Window2(None)
        self.frame.Bind(wx.EVT_CLOSE, self.re_open, self.frame)

    def re_open(self, e):
        print("aaaa")
        self.frame.Destroy()
        self.frame = Window2(None)

    def send_file(self, path):
        self.file = path
        self.client = ProjectClientAndServer.ServerP2P(path)
        self.client.send_file(path)

    def open_file(self, path):
        self.file = path
        if os.path.exists(path):
            with open(path) as fobj:
                for line in fobj:
                    self.my_text.AppendText(line)
            self.lines = len(self.my_text.Value.split("\n"))
            threading.Thread(target=self.rcv_messages).start()

    def sync_files(self, e):
        file = self.file.split("\\")
        new_file = "last_updated_" + file[-1]
        file[-1] = new_file
        file = "\\".join(file)
        self.last_updated_file = file
        with open(file, "w") as f:
            f.write(self.my_text.Value)
        self.client.send("@sync".encode())

    def write_changes(self):
        with open(self.client.file, "r")as f:
            f2 = f.read()
        self.frame.Show()
        self.frame.write(self.my_text.Value, f2, self.lines)
        print("hi")

    def rcv_messages(self):
        while True:
            request = self.client.rcv().decode()
            if request:
                if request == "@sync":
                    self.dlg = wx.MessageBox('want to sync your file?', 'TestDialog',
                                             wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                    if self.dlg == wx.YES:
                        print("yes")
                        self.client.send("@yes sync".encode())
                        self.client.rcv_file()
                        self.write_changes()
                if request == "@yes sync":
                    with open(self.last_updated_file,"r") as f:
                        print(f.read())
                    self.client.send_file(self.last_updated_file)
        print("arad")

    def rcv_file(self):
        self.client = ProjectClientAndServer.ClientP2P()
        self.open_file(self.client.file)

    def change_color(self, e):
        if self.line == self.my_text.PositionToXY(self.my_text.GetInsertionPoint())[2]:
            self.text += chr(e.GetKeyCode())
        else:
            if self.text:
                print(self.text)
            self.text = chr(e.GetKeyCode())
            self.line = self.my_text.PositionToXY(self.my_text.GetInsertionPoint())[2]
        self.my_text.SetStyle(0, -1, wx.TextAttr(wx.RED))
        e.Skip()


class SignUp(wx.Panel):
    # in charge of thr sing up page for new clients gets all their details to start there new client
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.SetSize((800, 600))
        name_sizer = wx.BoxSizer(wx.HORIZONTAL)

        name_lbl = wx.StaticText(self, label="First and last name")
        name_sizer.Add(name_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.name = wx.TextCtrl(self)
        name_sizer.Add(self.name, 0, wx.ALL | wx.CENTER, 5)

        user_sizer = wx.BoxSizer(wx.HORIZONTAL)

        user_lbl = wx.StaticText(self, label="Username:")
        user_sizer.Add(user_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.user = wx.TextCtrl(self)
        user_sizer.Add(self.user, 0, wx.ALL | wx.CENTER, 5)

        # pass info
        p_sizer = wx.BoxSizer(wx.HORIZONTAL)

        p_lbl = wx.StaticText(self, label="Password")
        p_sizer.Add(p_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        p_sizer.Add(self.password, 0, wx.ALL | wx.CENTER, 5)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(name_sizer, 0, wx.ALL | wx.CENTER, 10)
        self.main_sizer.Add(user_sizer, 0, wx.ALL | wx.CENTER, 10)
        self.main_sizer.Add(p_sizer, 0, wx.ALL | wx.CENTER, 10)
        self.btn = wx.Button(self, label="Login")
        self.main_sizer.Add(self.btn, 0, wx.ALL | wx.CENTER, 10)


class Program(wx.Frame):

    # the "main" of the gui has access to all the panels and is in charge of sending the server message and
    # switching the panels

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 'Program')

        self.client = ProjectClient.Client()
        self.user_name = None
        self.client.start_connection()
        self.p2p_client = None
        self.p2p_client = None
        self.recvThread = None
        self.sizer = wx.BoxSizer()
        self.SetSizer(self.sizer)
        self.panel_one = LogIn(self)
        self.home_page = HomePage(self)
        self.home_page.Hide()
        self.template = Template(self)
        self.template.Hide()
        self.panel_three = SignUp(self)
        self.panel_three.Hide()
        self.sizer.Add(self.panel_one.main_sizer, 1, wx.EXPAND)
        self.panel_one.btn2.Bind(wx.EVT_BUTTON, self.show_panel_three)  # after creating the panels it check if the
        # buttons at the panel was pressed and if was it will go the the function to show the correct panel
        self.sizer.Add(self.panel_three.main_sizer, 1, wx.EXPAND)
        self.panel_one.btn.Bind(wx.EVT_BUTTON, self.show_panel_two)
        self.panel_three.btn.Bind(wx.EVT_BUTTON, self.show_home_page)
        self.sizer.Add(self.home_page.user_sizer, 1, wx.EXPAND)
        self.home_page.connect.Bind(wx.EVT_BUTTON, self.show_template)
        self.SetSize((800, 600))
        self.Centre()

    def show_panel_one(self, event):  # shows the log in panel
        self.panel_one.Show()
        self.home_page.Hide()
        self.Layout()

    def show_panel_three(self, event):  # shows the sign up panel
        self.panel_three.Show()
        self.panel_one.Hide()
        self.Layout()

    def show_template(self, event):
        print(self.home_page.user.Value)
        wildcard = "TXT files (*.txt)|*.txt"
        dialog = wx.FileDialog(self, "Open Text Files", wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()
        msg = {"action": "wc", "user_name": self.home_page.user.Value, "file_name": path}
        self.client.answer = None
        self.client.send_message(msg)
        while not self.client.answer:
            pass
        if self.client.answer == "asked the client":
            print("here")
            self.home_page.Hide()
            self.template.Show()
            self.template.send_file(path)
            self.template.open_file(path)
            print("back")

    def start_to_work(self):
        self.home_page.Hide()
        self.template.Show()
        self.template.rcv_file()
        print("back")

    def show_panel_two(self, event):  # checks if got a user name and password the sends to to the server to check if
        # it is a correct password or user name if it is it will call the function in charge of showing the home page
        if self.panel_one.user.Value and self.panel_one.password.Value:
            self.user_name = self.panel_one.user.Value
            self.home_page.print_name(self.panel_one.user.Value)
            msg = {"action": "c", "user_name": self.panel_one.user.Value,
                   "user_password": self.panel_one.password.Value}
            self.client.send_message(msg)
            self.client.rcv_message()
            if self.client.answer == "no":
                print_answer("wrong username or password")
            else:
                self.create_home_page(None)
        else:
            print_answer("missing password or username")
            self.panel_one.Refresh()

    def show_home_page(self, event):  # checks from the sign up page if all the fields are filled and send the server
        # a message to create this new client and checks if this client wanted user name already exists if it does
        # show error if not calls the function in charge of showing the home page
        if self.panel_three.user.Value and self.panel_three.name.Value and self.panel_three.password.Value:
            self.user_name = self.panel_three.user.Value
            self.home_page.print_name(self.panel_three.user.Value)
            msg = {"action": "w", "user_name": self.panel_three.user.Value,
                   "user_password": self.panel_three.password.Value}
            self.client.send_message(msg)
            self.client.rcv_message()
            if self.client.answer == "no":
                print_answer("username taken change username")
            else:
                self.create_home_page(None)
        else:
            print_answer("missing password or username or name")
            self.panel_one.Refresh()

    def create_home_page(self, event):
        self.threads()
        self.panel_three.Hide()
        self.panel_one.Hide()
        self.home_page.Show()
        self.Layout()

    def threads(self):
        self.recvThread = threading.Thread(target=self.rcv_message)
        self.recvThread.start()

    def rcv_message(self):
        on = True
        while on:
            self.client.rcv_message()
            if "@" in self.client.answer:  # means some one wants me to send hi a file
                self.start_to_work()
                while not self.client.answer:
                    pass
                print("here")
            if self.client.answer == "close client":  # stops the connection
                self.client.my_socket.close()
                on = False


if __name__ == "__main__":
    app = wx.App(False)
    frame = Program()
    frame.Show()
    app.MainLoop()
    frame.client.send_message("close connection")
