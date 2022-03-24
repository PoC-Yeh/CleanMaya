import os
import subprocess
from time import process_time


class MayaFiles:
    def __init__(self, path):
        self.path = path
        self.ma = path + r'\*.ma'
        self.mb = path + r'\*.mb'
        self.__ma_files = list()
        self.__mb_files = list()

    @staticmethod
    def get_file_list(search_name):
        # dir D:\ABC\BANANAS\*.ma /s /b
        command = "dir {} /s /b".format(search_name)
        out = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        file_list = list()
        try:
            file_str = stdout.decode("utf-8")
            file_list = file_str.split("\r\n")[:-1]
        except UnicodeDecodeError:
            file_str = stdout.decode("big5")
            print(file_str)
        return file_list

    @property
    def ma_files(self):
        self.__ma_files = self.get_file_list(self.ma)
        return self.__ma_files

    @property
    def mb_files(self):
        self.__mb_files = self.get_file_list(self.mb)
        return self.__mb_files


class MayaCheck:
    def __init__(self, ma):
        self.original_file = ma
        self.original_name = ma.split("\\")[-1].split("/")[-1].split(".")[0]
        self.file_type = ma.split("\\")[-1].split("/")[-1].split(".")[-1]  # ma or mb
        self.path = ma[:-1 * (len(self.original_name) + len(self.file_type) + 1)]
        self.new_name = self.original_name + "_NoVirus"
        self.new_file = self.path + self.new_name + "." + self.file_type

        # print(self.original_file)
        # print(self.new_file)
        # print(self.original_name)

    def check_ma_exist(self):
        if not os.path.isfile(self.original_file):
            print("file not found :　{}".format(self.original_file))
            return False
        return True

    def read_ma(self):
        for line in open(self.original_file, 'r'):
            yield line

    def replace_problem(self):
        if self.check_ma_exist():
            problem_chunk_list = list()
            line_gen = self.read_ma()
            problem_chunk = None
            problem_detected = False

            with open(self.new_file, 'w')as file:
                for line in line_gen:
                    if not problem_detected:
                        if line.startswith("createNode script") and "_gene" in line:
                            problem_chunk = line
                            problem_detected = True
                            # replace with ''
                            file.write('')
                        else:
                            file.write(line)
                    else:
                        # lines under the problem line
                        if line.startswith("\t"):
                            problem_chunk += line
                            # replace with ''
                            file.write('')

                        # new chunk
                        # update self.problem_chunk_list
                        # reset problem_chunk
                        else:
                            problem_chunk_list.append(problem_chunk)
                            problem_chunk = None
                            if line.startswith("createNode script") and "_gene" in line:
                                # problem_detected remains True
                                problem_chunk = line
                                # replace with ''
                                file.write('')
                            else:
                                problem_detected = False
                                file.write(line)
                file.close()

            # for i in problem_chunk_list:
            #     print(i)

    def delete_original(self):
        if os.path.isfile(self.original_file):
            os.remove(self.original_file)

    def rename_new_file(self):
        if os.path.isfile(self.new_file):
            os.rename(self.new_file, self.original_file)


def run_check(path):
    start = process_time()
    directory = MayaFiles(path)
    file_list = directory.ma_files

    if file_list:
        for file in file_list:
            check = MayaCheck(file)
            check.replace_problem()
            print(check.original_file, " complete!!")
    else:
        print("no files found")
    end = process_time()
    print("Elapsed time: {}".format(str(end - start)))
    print(len(file_list))


# run_check(r'D:\ABC\BANANAS\ORANGE\APPLE')

