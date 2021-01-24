import wx
import ProjectClient
import os
import threading
import ProjectClientAndServer
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
        self.search = wx.Button(self, label="search files", pos=(600, 400))
        self.upload = wx.Button(self, label="upload files", pos=(100, 400))
        self.user = wx.TextCtrl(self, pos=(325, 100))
        self.connect = wx.Button(self, label="Start working", pos=(340, 130))
        self.file_name = wx.Button(self, label="upload file name", pos=(100, 450))
        self.path = None

    def print_name(self, name):
        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        wx.StaticText(self, -1, "hello " + name + " enter user name to work with", (200, 10), ).SetFont(font)

    def upload_file(self):  # opens the file explore and lets you choose a file to upload
        self.path = None
        dlg = wx.FileDialog(
            self, message="Choose a file",
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.path = dlg.GetPaths()
        dlg.Destroy()


class Template(wx.Panel):

    # in charge of the files page has all the files and file name for display for the user to choose the file he
    # wants to download
    def __init__(self, parent):
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

    def send_file(self, path):
        self.file = path
        self.client = ProjectClientAndServer.Server(path)

    def open_file(self, path):
        self.file = path
        if os.path.exists(path):
            with open(path) as fobj:
                for line in fobj:
                    self.my_text.AppendText(line)
            print(self.my_text.Value.split("\n"))
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
            f2 = f.read().split("\n")
        new_file = self.my_text.Value.split('\n')
        counter = 0
        d = difflib.Differ()
        diff = d.compare(new_file, f2)
        for line in diff:
            if line[0] == "+" and "#" not in line:
                print(counter)
                print(line)
                change = re.sub(r"^[+](\s+)", "", line)
                print(new_file[counter - 1])
                print(f2[counter - 1])
                print(counter - 1)
                new_file[counter - 1] += "#" + change
            counter += 1
        self.my_text.Clear()
        self.my_text.write("\n".join(new_file))

    def rcv_messages(self):
        while True:
            request = self.client.rcv().decode()
            if request:
                if request == "@sync":
                    dlg = wx.MessageBox('want to sync your file?', 'TestDialog',
                                        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                    if dlg == wx.YES:
                        print("yes")
                        self.client.send("@yes sync".encode())
                        self.client.rcv_file()
                        self.write_changes()
                        print("rcv")
                if request == "@yes sync":
                    print("send")
                    self.client.send_file(self.last_updated_file)

    def rcv_file(self):
        self.client = ProjectClientAndServer.Client()
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


class SearchPage(wx.Panel):

    # in charge of the files page has all the files and file name for display for the user to choose the file he
    # wants to download
    def __init__(self, parent, client):
        wx.Panel.__init__(self, parent)
        self.SetSize((800, 600))
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.go_back = wx.Button(self, label="go back to home page", pos=(10, 10))
        self.buttons = []
        self.client = client
        self.answer = ""
        self.button_name = None
        self.button_label = None
        self.name = None

    def make_buttons(self, files):
        x = 0
        print(files)
        for file in files:
            x = x + 50
            self.buttons.append(
                wx.Button(self, label=file, name=files[file]["ip"] + " " + files[file]["user_name"], pos=(300, x)))
            # creates all the buttons and sets there label to be the file name and directory and sets there name to
            # be or the pear to pear plus the clients name or 0 so for when i press a file i will know if im getting
            # the file from the server or a different client
        for button in self.buttons:
            self.build_buttons(button)

    def build_buttons(self, btn):
        btn.Bind(wx.EVT_BUTTON, self.on_button)

    def on_button(self, event):
        button = event.GetEventObject()
        self.button_label = button.GetLabel()
        self.button_name = button.GetName()
        if "0" in self.button_name:  # if 0 is in the button name so the clients gets the file from the server
            msg = {"action": "fs", "file_name": self.button_label}  # create the msg that tells the server to send
            # the file over
            self.client.send_message(msg)
            self.client.answer = None
            while not self.client.answer:  # waits until a message from the server has return
                pass
            print_answer("file received check your " + str(os.getcwd()) + "directory")
        else:
            msg = {"action": "sr", "file_name": self.button_label,
                   "user_name": self.button_name.split(" ")[-1]}  # creates the message to send to the server to tell
            # this client which fie i want to download to send me his file
            self.client.answer = None
            self.client.send_message(msg)
            while not self.client.answer:
                pass
            if self.client.answer == "asked the client":  # checks if the server has told the client to send me his
                # files
                ProjectClientAndServer.Client("127.0.0.1")  # starts the client for the pear to pear connection
                print_answer("file received check your " + str(os.getcwd()) + "directory")
            else:
                print_answer("user not found")


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
        self.search_page = SearchPage(self, self.client)
        self.search_page.Hide()
        self.sizer.Add(self.panel_one.main_sizer, 1, wx.EXPAND)
        self.panel_one.btn2.Bind(wx.EVT_BUTTON, self.show_panel_three)  # after creating the panels it check if the
        # buttons at the panel was pressed and if was it will go the the function to show the correct panel
        self.sizer.Add(self.panel_three.main_sizer, 1, wx.EXPAND)
        self.panel_one.btn.Bind(wx.EVT_BUTTON, self.show_panel_two)
        self.panel_three.btn.Bind(wx.EVT_BUTTON, self.show_home_page)
        self.sizer.Add(self.home_page.user_sizer, 1, wx.EXPAND)
        self.home_page.upload.Bind(wx.EVT_BUTTON, self.upload_file)

        self.home_page.file_name.Bind(wx.EVT_BUTTON, self.upload_file_name)
        self.home_page.connect.Bind(wx.EVT_BUTTON, self.show_template)
        self.home_page.search.Bind(wx.EVT_BUTTON, self.show_search_page)
        self.search_page.go_back.Bind(wx.EVT_BUTTON, self.create_home_page)
        self.sizer.Add(self.search_page.main_sizer, 1, wx.EXPAND)
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

    def start_to_work(self):
        self.home_page.Hide()
        self.template.Show()
        self.template.rcv_file()

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

    def show_search_page(self, event):
        # shows the files panel and sends a message to the server to so it will get back the a list of all the files
        self.home_page.Hide()
        msg = {"action": "s"}
        self.client.send_message(msg)
        self.search_page.Show()
        self.search_page.make_buttons(self.client.answer)  # creates a button for every file
        self.Layout()

    def create_home_page(self, event):
        self.threads()
        self.panel_three.Hide()
        self.search_page.Hide()
        self.panel_one.Hide()
        self.home_page.Show()
        self.Layout()

    def upload_file(self, event):
        # in charge of sending the server a message to upload the file with the file name and directory and then
        # sends the file
        self.home_page.upload_file()
        if self.home_page.path:
            file = "".join(self.home_page.path).replace(" ", "")
            msg = {"action": "u", "file_name": file,
                   "file_size": os.path.getsize(file), "ip": "0", "user_name": self.user_name}
            self.client.send_message(msg)
            self.client.send_file(file)
            print_answer("file uploaded was successful")

    def upload_file_name(self, event):
        # in charge of sending the server a message with a file name that im willing to send to a different client
        self.home_page.upload_file()
        if self.home_page.path:
            msg = {"action": "f", "user_name": self.user_name,
                   "user_password": self.panel_one.password.Value,
                   "file_name": "".join(self.home_page.path), "ip": "pear to pear"}
            self.client.send_message(msg)
            self.client.answer = None
            while not self.client.answer:
                pass
            if self.client.answer == "no":
                print_answer("file name taken change file name")
            else:
                print_answer("file name uploaded")

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
