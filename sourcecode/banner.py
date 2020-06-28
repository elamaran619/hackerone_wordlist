import pyfiglet
from termcolor import colored

print("{}\ngithub.com/xyele".format(pyfiglet.figlet_format("h1 wordlist"))) # print banner

def log(input):
    print(colored("[*] {}".format(str(input)),"blue"))
def successful(input):
    print(colored("[+] {}".format(str(input)),"green"))
def unsuccessful(input):
    print(colored("[-] {}".format(str(input)),"red"))