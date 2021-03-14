import difflib
first_file = "C:\\Users\\arad1\\PycharmProjects\\mortalcombat\\cyber_project\\gameserver.txt"
second_file = "C:\\Users\\arad1\\PycharmProjects\\mortalcombat\\cyber_project\\last_updated_gameserver.txt"
first_file_lines = open(first_file).readlines()
second_file_lines = open(second_file).readlines()
difflib.
diff = difflib.HtmlDiff().make_file(first_file_lines,second_file_lines,first_file,second_file)
diff_report = open("C:\\Users\\arad1\\PycharmProjects\\mortalcombat\\cyber_project\\diff_report","w")
diff_report.write(diff)
diff_report.close()