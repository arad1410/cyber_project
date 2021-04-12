class FileCmp(object):
    def __init__(self, my_file, other_file):
        self.my_file = my_file
        self.other_file = other_file
        self.diff_other_file = {}
        self.diff_my_file = {}
        self.diff_my_lines = []
        self.diff_other_lines = []
        self.chang_rate = 2 / 3
        self.other_index = 0
        self.my_index = 0
        self.deleted_lines = []
        self.other_deleted_lines = []

    def cmp_line(self, my_line, other_line):
        counter = 0
        answer = []
        diff_counter = 0
        for my_word in my_line:
            other_word = other_line[counter]
            if my_word != other_word:
                answer.append(counter)
                diff_counter += 1
            counter += 1
        if self.chang_rate * len(my_line) >= diff_counter:
            self.diff_other_file[self.other_index] = answer
            self.diff_my_file[self.my_index] = answer
            return True
        else:
            self.diff_other_file[self.other_index] = -1
            self.diff_my_file[self.my_index] = -1
            return False

    def main_cmp(self):
        self.deleted_lines = []
        self.other_deleted_lines = []
        same = False
        while self.my_index < len(self.my_file):
            my_line = self.my_file[self.my_index]
            other_line = self.other_file[self.other_index]
            if my_line != other_line:
                if self.check_other_deleted_lines(other_line) == self.check_my_deleted_lines(my_line) == False:
                    print(self.check_other_deleted_lines(other_line))
                    print(self.check_my_deleted_lines(my_line))
                    self.diff_other_lines.append(self.my_index - 1)
                    self.diff_my_lines.append(self.other_index - 1)
                    self.other_index = self.other_index - 1
                    self.my_index = self.my_index - 1
            else:
                self.diff_other_file[self.other_index] = -1
                self.diff_my_file[self.my_index] = -1
                self.my_index += 1
                self.other_index += 1
        print(self.deleted_lines)
        print(self.other_deleted_lines)
        print(self.diff_my_lines)
        print(self.diff_other_lines)

    def check_my_deleted_lines(self, my_line):
        deleted_lines = []
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
