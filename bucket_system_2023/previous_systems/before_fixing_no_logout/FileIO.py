import glob

class FileIO:
    def read_file(filename):
        file_lines = []
        with open(filename) as file:
            while file:
                line = file.readline()
                if line == "":
                    break
                file_lines.append(line.lower())
                #file_lines.append(line)
        return file_lines