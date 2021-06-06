class FileCmp(object):
    # in charge of comparing thr files and show all the changes
    def __init__(self, my_file, other_file):
        self.my_file = my_file  # holds my file
        self.other_file = other_file  # holds the others file
        self.diff_my_lines = []  # holds all the different lines in my text
        self.diff_other_lines = []  # holds all the different lines in the other text
        self.other_index = 0  # other text line index
        self.my_index = 0  # my text line index
        self.deleted_lines = []  # all the lines i deleted
        self.other_deleted_lines = []  # all the other user deleted

    def main_cmp(self):
        # the main loop that compares a line from one file to the other
        self.deleted_lines = []
        self.other_deleted_lines = []
        while self.my_index < len(self.my_file):
            my_line = self.my_file[self.my_index]
            other_line = self.other_file[self.other_index]
            if my_line != other_line:
                if self.check_other_deleted_lines(other_line) == self.check_my_deleted_lines(my_line) == False:
                    self.check_other_deleted_lines(other_line)
                    self.check_my_deleted_lines(my_line)
                    self.diff_other_lines.append(self.my_index - 1)
                    self.diff_my_lines.append(self.other_index - 1)
                    self.other_index = self.other_index - 1
                    self.my_index = self.my_index - 1
            else:
                self.my_index += 1
                self.other_index += 1

    def check_my_deleted_lines(self, my_line):
        # checks if there any lines in my file that are messing from the others file
        deleted_lines = [self.my_index]
        counter = self.other_index
        self.other_index += 1
        deleted_lines.append(self.other_index)
        if my_line == "\n":
            my_line = self.my_file[self.other_index]
        for line in self.other_file[self.other_index:]:
            if my_line.strip(" ") == line.strip(" "):
                self.other_index += 1
                break
            self.other_index += 1
            deleted_lines.append(self.other_index)
        else:
            self.other_index = counter + 1
            return False
        self.deleted_lines.append(deleted_lines)
        return True

    def check_other_deleted_lines(self, other_line):
        # checks if there any lines in the others file that are messing from my file
        deleted_lines = []
        counter = self.my_index
        self.my_index += 1
        deleted_lines.append(self.my_index)
        if other_line == "\n":
            other_line = self.other_file[self.my_index]
        for line in self.my_file[self.my_index:]:
            if other_line == line:
                self.my_index += 1
                break
            self.my_index += 1
            deleted_lines.append(self.my_index)
        else:
            self.my_index = counter + 1
            return False
        self.other_deleted_lines.append(deleted_lines)
        return True


if __name__ == '__main__':
    with open("C:\\Users\\arad1\\PycharmProjects\\mortalcombat\\cyber_project\\gameserver.txt", "r") as f:
        f = f.read().split("\n")
    with open("C:\\Users\\arad1\\PycharmProjects\\mortalcombat\\cyber_project\\last_updated_gameserver.txt", "r") as f2:
        f2 = f2.read().split("\n")
    a = FileCmp(f, f2)
    a.main_cmp()
