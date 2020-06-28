#!/usr/bin/env python
# coding: utf-8
# github.com/xyele

from banner import *

from urllib.parse import unquote

import csv,argparse,math,re

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--entropy', required=False)
args = parser.parse_args()

entropy_limit = 4.2 # default

def check_entropy(input,limit):
    prob = [float(input.count(c)) / len(input) for c in dict.fromkeys(list(input))]
    entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
    if entropy > limit:
        return False
    else:
        return True

def clearParam(raw):
    raw = unquote(raw) # url decode
    raw = re.sub(re.compile('\[.*?\]'), '', str(raw)) # 
    return raw
try:
    entropy_limit = float(args.entropy)
    log(f"Entropy limit is set to: {str(entropy_limit)}")
except Exception as e:
    unsuccessful("Missing or wrong entropy input")
    

if (args.output.endswith("/") == False):
    args.output = f"{args.output}/"

wordlist = {
    "subdomains":[],
    
    "paths":[],
    "paths_splitted":[],
    "paths_efficient":[],

    "parameters":[],
    "http_parameters":[],
    "json_parameters":[],

    "headers":[]
}

read_dataset = open(args.dataset) # reac csv file
read_dataset = csv.reader(read_dataset, delimiter=',')

blacklistedChars = ["`",")","(",",","&","]]","&gt","&amp",":",".","&am"]

log("Started to read dataset.")

for row in list(read_dataset)[1:]:
    report_id,url,request_method,subdomain,domain,tld,path,fragment,query_string,post_data,get_parameters,post_parameters,json_parameters,headers = row
    
    wordlist["subdomains"] += subdomain.split(".")

    path = path.replace("&quot","").replace("&lt","")

    ((path.startswith("/reports/")) == False) and wordlist["paths"].append(path)

    for i in str(path).split("/"):
        wordlist["paths_splitted"].append(i)

    if (("█" in path) == False) and (path.startswith("/reports/") == False) and check_entropy(path,entropy_limit):
        for char in blacklistedChars:
            if path.endswith(char):
                path = path[:-1]
        wordlist["paths_efficient"].append(path)

    wordlist["parameters"] += get_parameters.split(",")
    wordlist["parameters"] += post_parameters.split(",")
    wordlist["parameters"] += json_parameters.split(",")

    wordlist["http_parameters"] += get_parameters.split(",")
    wordlist["http_parameters"] += post_parameters.split(",")

    wordlist["json_parameters"] += json_parameters.split(",")

    wordlist["headers"] += headers.split(",")

for key,value in wordlist.items():
    value = list(dict.fromkeys(value))
    value = [i for i in value if ((i == "") == False)]
    value.sort()
    file_writer = open(f"{args.output}{key}.txt","w+")
    started_statement = False
    for n in value:
        if started_statement == True:
            file_writer.write(f"\n{n}")
        else:
            started_statement = True
            file_writer.write(f"{n}")
    successful(f"Wordlist created! {str(args.output+key)}.txt")
    file_writer.close()
log("Finished.")
exit()
