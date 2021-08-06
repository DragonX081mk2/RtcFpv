import re

import subprocess

cmd = ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']

device_list = []
process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8",
                           text=True)
record = False
num_line = 0;
for line in process.stdout:
    # print(',,,,,', num_line)
    # print(line)
    if record:
        if line.startswith("[dshow"):
            _line = line[index + 2:]
            if _line.startswith("DirectShow audio"):
                record = False
            if record and num_line % 2 == 0:
                device_list.append(_line[2:len(_line) - 2])
            num_line += 1

    if line.startswith("[dshow"):
        index = line.find("]");
        if index > 0:
            _line = line[index + 2:]
            if _line.startswith("DirectShow audio"):
                # print('>>>>>>>', _line)
                num_line = 0
                record = True

for index in range(len(device_list)):
    print('--->', device_list[index])