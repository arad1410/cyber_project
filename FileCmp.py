class FileCmp(object):
    def __init__(self):
        self.my_file = open("C:\\Users\\arad1\\PycharmProjects\\mortalcombat\\cyber_project\\gameserver.txt",
                            "r").readlines()
        self.other_file = open(
            "C:\\Users\\arad1\\PycharmProjects\\mortalcombat\\cyber_project\\last_updated_gameserver.txt",
            "r").readlines()
        self.diff_other_file = {}
        self.diff_my_file = {}
        self.chang_rate = 2 / 3
        self.line = 0
        self.deleted_lines = []

    def cmp_line(self, my_line, other_line, line):
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
            self.diff_other_file[line] = answer
            self.diff_my_file[line] = answer
            return True
        else:
            self.diff_other_file[line] = -1
            self.diff_my_file[line] = -1
            return False

    def main_cmp(self):
        deleted_lines = 0
        same = False
        for my_line in self.my_file:
            other_line = self.other_file[self.line]
            if my_line != other_line:
                if same and not self.cmp_line(my_line.split(" "), other_line.split(" "), self.line):
                    self.check_deleted_lines(my_line)
            else:
                self.diff_other_file[self.line] = 1
                self.diff_my_file[self.line] = 1
                self.line += 1
                same = True

    def check_deleted_lines(self, my_line):
        deleted_lines = []
        for line in self.other_file[self.line:]:
            deleted_lines.append(self.line)
            if self.cmp_line(my_line, line, self.line):
                break
            self.line += 1
        else:
            return
        self.deleted_lines.append(deleted_lines)


if __name__ == '__main__':
    a = FileCmp()
    a.main_cmp()
