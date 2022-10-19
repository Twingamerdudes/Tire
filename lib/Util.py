import os
import sys
import subprocess

RESET = '\033[0m'
def get_color_escape(r, g, b, background=False):
    return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)
def print_color(text, r, g, b):
    print(get_color_escape(r, g, b) 
      + text
      + RESET)
def print_error(text):
    print_color(text, 194, 24, 8)
    os.system("pause")
    exit(1)
def clear():
    print("\033[H\033[J", end="")
    sys.stdout.flush()
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
def check_true_color():
    if sys.platform == 'win32':
        return True
    else:
        try:
            proc = subprocess.Popen(['tput', 'colors'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            if int(out) >= 256:
                return True
            else:
                return False
        except:
            return False