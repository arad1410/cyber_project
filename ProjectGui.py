import wx
import ProjectClient
import os
import threading
import ProjectClientAndServer
import wx.lib.scrolledpanel as scrolled
import FileCmp


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
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)  # in charge of location of panel
        self.user = wx.TextCtrl(self, pos=(370, 25))  # text box of user name
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER,
                                    pos=(370, 75))  # text box of password
        self.btn = wx.Button(self, label="Login", pos=(350, 130))  # login button
        self.btn2 = wx.Button(self, label="Sign up", pos=(350, 180))  # sign up button
        wx.StaticText(self, label="Username:", pos=(300, 30))
        wx.StaticText(self, label="Password:", pos=(300, 80))


class HomePage(wx.Panel):

    # in charge to create the home page panel and to upload the file name or the file itself

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetSize((800, 600))
        self.clients = []  # holds all the usernames of the clients that are connected
        self.user = None  # holds the user name that was chosen
        self.target = wx.ComboBox(self, choices=self.clients, pos=(325, 100),
                                  style=wx.CB_READONLY)  # combobox of all the client available to work with
        self.connect = wx.Button(self, label="Start working", pos=(340, 130))  # button to start working together
        self.me = None  # holds my user name
        self.user_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.target.Bind(wx.EVT_COMBOBOX, self.target_handler)

    def print_name(self, name):
        self.me = name
        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        wx.StaticText(self, -1, "hello " + name + " enter user name to work with", (200, 10), ).SetFont(font)

    def target_handler(self, event):
        self.user = self.target.GetValue()


class FileCmpPanel(scrolled.ScrolledPanel):

    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.my_file = wx.TextCtrl(self,
                                   style=wx.TE_LEFT | wx.TE_MULTILINE | wx.TE_RICH | wx.TE_READONLY | wx.TE_NO_VSCROLL,
                                   size=(-1, -1))  # holds my file
        self.other_file = wx.TextCtrl(self,
                                      style=wx.TE_LEFT | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_NO_VSCROLL,
                                      size=(-1, -1))  # holds other users file
        self.btn1 = wx.Button(self, label='write changes',
                              size=(700, 30))  # the button that is in charge to write the changes
        self.my_lbl = wx.StaticText(self, -1, style=wx.ALIGN_CENTER,
                                    label="Your File")  # the label that says what is my current file
        self.other_lbl = wx.StaticText(self, -1,
                                       style=wx.ALIGN_CENTER)
        # the other label holds either other users file or pld version of mu file
        self.boxes = wx.CheckListBox(self, size=(-1, -1))  # holds all the changes boxes
        self.organize_box = []  # in charge of organizing the boxes so thy will bi in order
        # the lines that were deleted or added so you will be able to write the lines at the correct position
        self.file_cmp = None  # holds the object of FileCmp
        self.my_file_text = None  # holds my files text
        self.other_file_text = None  # holds other files text
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)  # takes care of position of the panel
        self.all_texts_sizer = wx.BoxSizer(wx.HORIZONTAL)  # takes care of position of all the texts
        self.my_text_sizer = wx.BoxSizer(wx.VERTICAL)  # takes care of position of the my text
        self.changes_sizer = wx.BoxSizer(wx.VERTICAL)  # takes care of position of the changes column
        self.other_text_sizer = wx.BoxSizer(wx.VERTICAL)  # takes care of position of the other users text
        font = wx.Font(25, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.my_lbl.SetFont(font)
        self.other_lbl.SetFont(font)
        self.btn1.Bind(wx.EVT_BUTTON, self.make_changes, self.btn1)

    def write_file(self, my_file, other_file, lines, file_lbl):
        my_file = my_file.split("\n")
        other_file = other_file.split("\n")
        counter = 0
        self.other_file_text = other_file
        self.my_file_text = my_file
        self.file_cmp = FileCmp.FileCmp(my_file, other_file)
        self.file_cmp.main_cmp()
        self.write_my_file(my_file)
        self.write_other_file(other_file)
        self.check_diff_lines()
        self.make_window(lines, file_lbl)
        self.Refresh()

    def check_diff_lines(self):
        for i in range(len(self.file_cmp.diff_my_lines)):
            self.organize_box.append(
                "change line " + str(self.file_cmp.diff_other_lines[i]) + " with " + str(
                    self.file_cmp.diff_my_lines[i]))

    def write_my_file(self, my_file):
        other_deleted_lines = []
        for i in self.file_cmp.other_deleted_lines:
            self.organize_box.append("delete lines " + str(i[0]) + "-" + str(i[-1]))
            for j in i:
                other_deleted_lines.append(j)
        for i in range(1, len(my_file) + 1):
            if i not in other_deleted_lines and i not in self.file_cmp.diff_other_lines:
                self.my_line_number(wx.GREEN, i)
                self.my_file.AppendText(my_file[i - 1] + "\n")
            # elif i not in file_cmp.diff_my_lines:
            elif i not in other_deleted_lines:
                self.my_line_number(wx.RED, i)
                self.my_file.SetStyle(0, -1, wx.TextAttr(wx.RED))
                self.my_file.AppendText(my_file[i - 1] + "\n")
                self.my_file.SetStyle(0, -1, wx.TextAttr(wx.BLACK))
            else:
                self.my_line_number(wx.BLUE, i)
                self.my_file.SetStyle(0, -1, wx.TextAttr(wx.BLUE))
                self.my_file.AppendText(my_file[i - 1] + "\n")
                self.my_file.SetStyle(0, -1, wx.TextAttr(wx.BLACK))

    def write_other_file(self, my_file):
        my_deleted_lines = []
        for i in self.file_cmp.deleted_lines:
            self.organize_box.append("add lines " + str(i[1]) + "-" + str(i[-1]) + " at line " + str(i[0] - 1))
            for j in i:
                my_deleted_lines.append(j)
            del my_deleted_lines[0]
        for i in range(1, len(my_file) + 1):
            if i not in my_deleted_lines and i not in self.file_cmp.diff_my_lines:
                self.other_line_number(wx.GREEN, i)
                self.other_file.AppendText(my_file[i - 1] + "\n")
            # elif i not in file_cmp.diff_other_lines:
            elif i not in my_deleted_lines:
                self.other_line_number(wx.RED, i)
                self.other_file.SetStyle(0, -1, wx.TextAttr(wx.RED))
                self.other_file.AppendText(my_file[i - 1] + "\n")
                self.other_file.SetStyle(0, -1, wx.TextAttr(wx.BLACK))
            else:
                self.other_line_number(wx.BLUE, i)
                self.other_file.SetStyle(0, -1, wx.TextAttr(wx.BLUE))
                self.other_file.AppendText(my_file[i - 1] + "\n")
                self.other_file.SetStyle(0, -1, wx.TextAttr(wx.BLACK))

    def my_line_number(self, color, counter):
        self.my_file.SetStyle(0, -1, wx.TextAttr(color))
        self.my_file.AppendText(str(counter) + ").   ")
        self.my_file.SetStyle(0, -1, wx.TextAttr(wx.BLACK))

    def other_line_number(self, color, counter):
        self.other_file.SetStyle(0, -1, wx.TextAttr(color))
        self.other_file.AppendText(str(counter) + ").   ")
        self.other_file.SetStyle(0, -1, wx.TextAttr(wx.BLACK))

    def make_window(self, lines, file_lbl):
        self.other_lbl.SetLabel(file_lbl)
        self.my_file.SetMinSize((500, round(15.5 * lines)))
        self.other_file.SetMinSize((500, round(15.5 * lines)))
        self.my_text_sizer.Add(self.my_lbl, 1, wx.EXPAND)
        self.my_text_sizer.Add(self.my_file, 0, wx.EXPAND)
        self.other_text_sizer.Add(self.other_lbl, 1, wx.EXPAND)
        self.other_text_sizer.Add(self.other_file, 0, wx.EXPAND)
        self.organize_box_list()
        self.all_texts_sizer.Add(self.my_text_sizer, 1, wx.EXPAND)
        self.all_texts_sizer.Add(self.other_text_sizer, 1, wx.EXPAND)
        self.all_texts_sizer.Add(self.boxes, -1, wx.EXPAND)
        self.main_sizer.Add(self.all_texts_sizer, 1, wx.EXPAND)
        self.main_sizer.Add(self.btn1, flag=wx.CENTER)
        self.SetupScrolling()
        self.SetSizer(self.main_sizer)
        self.Refresh()

    def organize_box_list(self):
        self.organize_box.sort(key=self.sort_key)
        for box in self.organize_box:
            self.boxes.Append(box)

    def sort_key(self, e):
        action = e.split()
        if action[0] == "delete":
            lines = action[-1].split("-")
            return int(lines[0])
        elif action[0] == "change":
            return int(action[2])
        else:
            lines = action[-1].split("-")
            return int(lines[0])

    def make_changes(self, e):
        add_lines = 0
        for box in self.boxes.GetCheckedStrings():
            print(box)
            action = box.split()
            if action[0] == "delete":
                lines = action[-1].split("-")
                if add_lines != 0:
                    add_lines -= int(lines[-1]) - int(lines[0]) + 1
                    del self.my_file_text[int(lines[0]) + add_lines+1:int(lines[-1]) + add_lines + 2]
                else:
                    add_lines -= int(lines[-1]) - int(lines[0]) + 1
                    del self.my_file_text[int(lines[0]) - 1:int(lines[-1])]
                print([int(lines[0]) - 1 + add_lines, int(lines[-1])+add_lines])
            elif action[0] == "change":
                self.my_file_text[int(action[2]) + add_lines -1] = self.other_file_text[int(action[-1]) - 1]
            else:
                lines = action[2].split("-")
                where_to_add = action[-1]
                print(lines)
                print(where_to_add)
                for i in range(int(lines[-1]) - int(lines[0]) + 1):
                    self.my_file_text.insert(int(where_to_add) + add_lines + i,
                                             self.other_file_text[int(lines[0]) + i - 1])
                add_lines += int(lines[-1]) - int(lines[0]) + 1
        f = self.GetParent()
        f.Close()


class FileCmpFrame(wx.Frame):
    title = "new Window"

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'FileCmpFrame', size=(1300, 600))
        self.top_panel = FileCmpPanel(self)  # holds the object of FileCmpPanel

    def write(self, my_file, other_file, lines, file_lbl):
        self.top_panel.write_file(my_file, other_file, lines, file_lbl)
        self.Maximize(True)


class FilePanel(wx.Panel):
    """
    This is the main editing page
    """

    def __init__(self, parent, homepage):
        """
        in charge of the files page has all the files and file name for display for the user to choose the file he
        wants to download
        :param parent: string
        """
        wx.Panel.__init__(self, parent)
        self.SetSize((800, 600))
        self.all_version = []  # holds all the version of my file
        self.sync = wx.Button(self, wx.ID_CLEAR, "SYNC WORK", pos=(200, 540))  # in charge of syncing the files
        self.my_text = wx.TextCtrl(self, size=(785, 540), style=wx.TE_MULTILINE | wx.TE_RICH)
        # holds the text of my file
        self.exit = wx.Button(self, label='EXIT AND SAVE', pos=(300, 540))
        # in charge of exiting and saving the current version of thr file
        self.target = wx.ComboBox(self, choices=self.all_version, pos=(425, 540), style=wx.CB_READONLY,
                                  size=(300, -1))  # combo box that holds all the file versions
        self.text = None  # holds my text
        self.homepage = homepage  # holds the object of homepage
        self.line = self.my_text.PositionToXY(self.my_text.GetInsertionPoint())[2]  # holds the current InsertionPoint
        self.client = None  # holds the object of ProjectClientAndServer.ServerP2P or ProjectClientAndServer.ClientP2P
        self.file = None  # holds file name
        self.last_updated_file = None  # holds the last version of the file
        self.lines = None  # holds the number of lines
        self.other_lines = None  # folds the number of the other users lines
        self.version = 0  # golds the number version we are at
        self.path = None  # holds the file path
        self.frame = FileCmpFrame(None)  # holds the object of FileCmpFrame
        self.frame.Bind(wx.EVT_CLOSE, self.re_open, self.frame)
        self.my_text.Bind(wx.EVT_CHAR, self.change_color, self.my_text)
        self.sync.Bind(wx.EVT_BUTTON, self.sync_files)
        self.target.Bind(wx.EVT_COMBOBOX, self.version_handler)

    def re_open(self, e):
        print("hi")
        self.write_new_changes()
        self.frame.Destroy()
        self.frame = FileCmpFrame(None)
        self.frame.Bind(wx.EVT_CLOSE, self.re_open, self.frame)

    def write_new_changes(self):
        self.my_text.Clear()
        self.my_text.WriteText("\n".join(self.frame.top_panel.my_file_text))

    def send_file(self, path):
        self.file = path
        self.client = ProjectClientAndServer.ServerP2P(path)
        self.client.send_file(path)

    def open_file(self, path):
        print("arad " + path)
        self.path = path
        self.file = path
        self.all_version.append(path)
        self.target.SetItems(self.all_version)
        if os.path.exists(path):
            with open(path) as fobj:
                for line in fobj:
                    if line != "\n":
                        self.my_text.AppendText(line)
            self.lines = len(self.my_text.Value.split("\n"))
            threading.Thread(target=self.rcv_messages).start()

    def sync_files(self, e):
        file = self.file.split("\\")
        print(file)
        self.version += 1
        new_file = "version_" + str(self.version) + "_" + file[-1]
        file[-1] = new_file
        file = "\\".join(file)
        self.all_version.append(file)
        self.target.SetItems(self.all_version)
        self.last_updated_file = file
        with open(file, "w") as f:
            f.write(self.my_text.Value)
        self.client.send("@sync".encode())

    def save_version(self):
        self.version += 1
        file = self.file.split("\\")
        file[-1] = "version_" + str(self.version) + "_" + file[-1]
        file = "\\".join(file)
        self.all_version.append(file)
        self.target.SetItems(self.all_version)
        with open(file, "w") as f:
            f.write(self.my_text.Value)

    def write_changes(self, file, file_lbl):
        print(file)
        with open(file if file else self.client.file, "r")as f:
            f2 = f.read()
        self.frame.Show()
        other_lines = len(f2.split("\n"))
        self.frame.write(self.my_text.Value, f2, self.lines if self.lines > other_lines else other_lines, file_lbl)

    def version_handler(self, event):
        self.write_changes(self.target.GetValue(), "Old Version")

    def rcv_messages(self):
        while True:
            try:
                request = self.client.rcv().decode()
            except OSError:
                print_answer("connection stopped because your partner stopped")
                self.client.close()
                print(self.my_text.Value)
                with open("".join(self.path), "w") as f:
                    f.write(self.my_text.Value)
                self.my_text.Clear()
                self.Hide()
                self.homepage.Show()
                break
            if request:
                if request == "@sync":
                    dlg = wx.MessageBox('want to sync your file?', 'TestDialog',
                                        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                    if dlg == wx.YES:
                        self.save_version()
                        self.client.send("@yes sync".encode())
                        self.client.rcv_file()
                        self.write_changes(None, "Other File")
                if request == "@yes sync":
                    self.client.send_file(self.last_updated_file)
                if request == "exit":
                    self.client.close()

    def rcv_file(self):
        self.client = ProjectClientAndServer.ClientP2P()
        self.open_file(self.client.file)

    def change_color(self, e):
        if self.line == self.my_text.PositionToXY(self.my_text.GetInsertionPoint())[2]:
            self.text += chr(e.GetKeyCode())
        else:
            self.text = chr(e.GetKeyCode())
            self.line = self.my_text.PositionToXY(self.my_text.GetInsertionPoint())[2]
        self.my_text.SetStyle(0, -1, wx.TextAttr(wx.RED))
        e.Skip()


class SignUp(wx.Panel):
    # in charge of thr sing up page for new clients gets all their details to start there new client
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.SetSize((800, 600))
        self.name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_lbl = wx.StaticText(self, label="First name")
        self.name_sizer.Add(name_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.name = wx.TextCtrl(self)
        self.name_sizer.Add(self.name, 0, wx.ALL | wx.CENTER, 5)
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)
        user_lbl = wx.StaticText(self, label="Username:")
        user_sizer.Add(user_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.user = wx.TextCtrl(self)
        user_sizer.Add(self.user, 0, wx.ALL | wx.CENTER, 5)
        p_sizer = wx.BoxSizer(wx.HORIZONTAL)
        p_lbl = wx.StaticText(self, label="Password")
        p_sizer.Add(p_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        p_sizer.Add(self.password, 0, wx.ALL | wx.CENTER, 5)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.name_sizer, 0, wx.ALL | wx.CENTER, 10)
        self.main_sizer.Add(user_sizer, 0, wx.ALL | wx.CENTER, 10)
        self.main_sizer.Add(p_sizer, 0, wx.ALL | wx.CENTER, 10)
        self.btn = wx.Button(self, label="Sign Up")
        self.main_sizer.Add(self.btn, 0, wx.ALL | wx.CENTER, 10)

    def check_sign_up(self):
        if self.user.Value and self.name.Value and self.password.Value:
            if self.valid_username():
                return self.valid_password()
        else:
            print_answer("missing information")

    def valid_username(self):
        username = self.user.GetValue()
        if username.isdigit():
            print_answer("invalid username")
            return False
        return True

    def valid_password(self):
        password = self.password.GetValue()
        if len(password) < 8:
            print_answer("password too short")
            return False
        elif password.isdigit():
            print_answer("password can not be only numbers")
            return False
        elif password.isalpha():
            print_answer("password can not be only string")
            return False
        return True


class Program(wx.Frame):

    # the "main" of the gui has access to all the panels and is in charge of sending the server message and
    # switching the panels

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 'Program')

        self.client = ProjectClient.Client()  # holds the object of ProjectClient.Client
        self.client.start_connection()
        self.recvThread = None  # holds the object of threading.Thread with the target of rcv_message()
        self.sizer = wx.BoxSizer()  # sizer
        self.SetSizer(self.sizer)
        self.log_in_panel = LogIn(self)  # holds the object of the log in panel
        self.home_page = HomePage(self)  # holds the object of the home page panel
        self.file_panel = FilePanel(self, self.home_page)  # holds the object of the file panel
        self.sign_up_panel = SignUp(self)  # holds the object of the sign_up panel
        self.sizer.Add(self.log_in_panel.main_sizer, 1, wx.EXPAND)
        self.sign_up_panel.Hide()
        self.file_panel.Hide()
        self.home_page.Hide()
        self.log_in_panel.btn2.Bind(wx.EVT_BUTTON, self.show_sign_up_panel)  # after creating the panels it check if the
        # buttons at the panel was pressed and if was it will go the the function to show the correct panel
        self.sizer.Add(self.sign_up_panel.main_sizer, 1, wx.EXPAND)
        self.log_in_panel.btn.Bind(wx.EVT_BUTTON, self.check_log_in)
        self.file_panel.exit.Bind(wx.EVT_BUTTON, self.exit_and_save)
        self.sign_up_panel.btn.Bind(wx.EVT_BUTTON, self.check_sign_up)
        self.sizer.Add(self.home_page.user_sizer, 1, wx.EXPAND)
        self.home_page.connect.Bind(wx.EVT_BUTTON, self.show_FilePanel)
        self.SetSize((800, 600))
        self.Centre()

    def show_sign_up_panel(self, event):  # shows the sign up panel
        self.sign_up_panel.Show()
        self.log_in_panel.Hide()
        self.Layout()

    def show_FilePanel(self, event):
        wildcard = "TXT files (*.txt)|*.txt"
        dialog = wx.FileDialog(self, "Open Text Files", wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()
        msg = {"action": "wc", "user_name": self.home_page.user, "file_name": path,
               "my_user_name": self.home_page.me}
        self.client.answer = None
        self.client.send_message(msg)
        while not self.client.answer:
            pass
        if self.client.answer == "yes":
            print("answer")
            msg = {"action": "work", "user_name": self.home_page.user, "file_name": path}
            self.client.send_message(msg)
            self.home_page.Hide()
            self.file_panel.Show()
            self.file_panel.send_file(path)
            self.file_panel.open_file(path)
        else:
            print_answer(self.home_page.user + " dose not want to work with you try a different user")

    def start_to_work(self):
        self.home_page.Hide()
        self.file_panel.Show()
        self.file_panel.rcv_file()

    def check_log_in(self, event):  # checks if got a user name and password the sends to to the server to check if
        # it is a correct password or user name if it is it will call the function in charge of showing the home page
        if self.log_in_panel.user.Value and self.log_in_panel.password.Value:
            self.home_page.print_name(self.log_in_panel.user.Value)
            msg = {"action": "c", "user_name": self.log_in_panel.user.Value,
                   "user_password": self.log_in_panel.password.Value}
            self.client.send_message(msg)
            self.client.rcv_message()
            if self.client.answer == "no":
                print_answer("wrong username or password")
            else:
                self.create_home_page(None)
        else:
            print_answer("missing password or username")
            self.log_in_panel.Refresh()

    def check_sign_up(self, event):  # checks from the sign up page if all the fields are filled and send the server
        # a message to create this new client and checks if this client wanted user name already exists if it does
        # show error if not calls the function in charge of showing the home page
        if self.sign_up_panel.check_sign_up():
            msg = {"action": "w", "user_name": self.sign_up_panel.user.Value,
                   "user_password": self.sign_up_panel.password.Value}
            self.client.send_message(msg)
            self.client.rcv_message()
            if self.client.answer == "no":
                print_answer("username taken change username")
            else:
                self.home_page.print_name(self.sign_up_panel.user.Value)
                self.create_home_page(None)
        else:
            self.log_in_panel.Refresh()

    def exit_and_save(self, event):
        self.file_panel.my_text.Clear()
        self.file_panel.path = self.file_panel.path.split("\\")
        self.file_panel.path[-1] = "final_version_" + self.file_panel.path[-1]
        with open("".join(self.file_panel.path), "w") as f:
            f.write(self.file_panel.my_text.Value)
        self.file_panel.client.send("exit".encode())
        self.file_panel.Hide()
        self.home_page.Show()

    def create_home_page(self, event):
        self.threads()
        self.sign_up_panel.Hide()
        self.log_in_panel.Hide()
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
                dlg = wx.MessageBox(self.client.answer.split(" ")[-1] + ' wants to work with you', 'TestDialog',
                                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                if dlg == wx.YES:
                    msg = {"action": "yes", "user_name": self.client.answer.split(" ")[-1]}
                else:
                    msg = {"action": "no", "user_name": self.client.answer.split(" ")[-1]}
                self.client.send_message(msg)
            if "lets start" in self.client.answer:
                self.start_to_work()
                while not self.client.answer:
                    pass
            if self.client.answer == "close client":  # stops the connection
                self.client.my_socket.close()
                on = False
            if "&" in self.client.answer:
                clients = self.client.answer.split()[1:]
                if self.home_page.me in clients:
                    clients.remove(self.home_page.me)
                self.home_page.target.SetItems(clients)

if __name__ == "__main__":
    app = wx.App(False)
    frame = Program()
    frame.Show()
    app.MainLoop()
    frame.client.send_message("close connection")
