#!/usr/bin/env python
# coding: utf-8
# github.com/xyele

from banner import *

import re,os,sys,csv,json,tldextract,argparse,html

from urllib.parse import unquote
from tldextract import extract as tldextract
from urllib.parse import urlparse
from urlextract import URLExtract as ue_object

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from io import BytesIO

class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()
    def send_error(self, code, message,temp=None):
        self.error_code = code
        self.error_message = message

parser = argparse.ArgumentParser()
parser.add_argument('--reports', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()

extractor = ue_object()
extractor.update()

def getItems(dictionary):
    for k, v in dictionary.items():
        if isinstance(v, dict):
            yield from getItems(v)
        elif isinstance(v,list):
            for i in v:
                if isinstance(i,dict):
                    yield from getItems(i)
        else:
            yield v
def getKeys(dictionary):
    for k, v in dictionary.items():
        yield k
        if isinstance(v, dict):
            yield from getKeys(v)   

def clearQuotes(raw):
    raw = html.unescape(str(raw))
    raw = raw.replace("\"","").replace("'","").replace("`","")
    return raw
def clearBrackets(raw):
    raw = re.sub(re.compile('\[.*?\]'), '', str(raw))
    return raw # input: email["test"], output: email
def clearMalformed(raw):
    raw = re.sub(re.compile("%ff", flags=re.IGNORECASE), '', str(raw))
    return raw

def extract(id,text):
    if type(text) == str:
        text = text.strip()
    if bool(text) == False:
        return

    """
    Extract RAW HTTP Requests
        e.g:
        ```
        POST /xyele/hackerone_wordlist HTTP/1.1
        Host: github.com

        star_repo=true
        ```
    """

    match = re.findall("(```\n.*?\n```)+",str(text), re.DOTALL)
    match += re.findall("(```http\n.*?\n```)+",str(text), re.DOTALL)
    for m in match:
        m = m.split("```")[1] if (m.startswith("```") and m.endswith("```")) else m
        m = str(m)[1:] if m.startswith("\n") else m
        request = HTTPRequest(m.encode())
        if (request.command != None):
            yield ["request",request]

    """
    Extract URLs
        e.g:
        https://github.com/xyele/hackerone_wordlist
        //github.com/xyele/hackerone_wordlist
        github.com/xyele/hackerone_wordlist
        ...
    """

    urls = extractor.find_urls(clearMalformed(text), only_unique=True)
    for u in urls:
        if ((u.startswith("http://") or u.startswith("https://")) == False):
            u = f"http://{u}"
        yield ["url",u]

    """
    Extract parameter names
        e.g:
        LFI throught the filename parameter --> filename
        SQL Injection on blabla domain via userid parameter --> userid

        e.g:
        ```
        <?php echo $_GET['makesense']; ?> --> makesense
        ```
    """
    phpParams = re.findall(re.compile("\$_(GET|POST)\[['|\"](.*?)['|\"]]"),str(text))
    for m in phpParams:
        if bool(m) and re.match(re.compile("^[A-Za-z0-9_.]+$"),clearBrackets(m)):
            yield ["justparameter",html.unescape(m)]

    textParams = re.findall(re.compile("(?i) (?:the|via|with|using by|that|this) (.*?) (?:param)"),clearQuotes(text))
    for m in textParams:
        if bool(m) and re.match(re.compile("^[A-Za-z0-9_.]+$"),clearBrackets(m)):
            yield ["justparameter",clearBrackets(m)] 

def get_parameters(method, query_string):
    """
    input --> "username=xyele&email=zeroxyele@wearehackerone.com"
    output --> "username,email"
    """
    if (method == "get") and ("?" in query_string):
        query_string = query_string.split("?")[1]
    if (method == "get") and ("#" in query_string):
        query_string = query_string.split("#")[0]
    parameters = []
    for qs in query_string.split("&"):
        (qs.split("=")[0] != "") and parameters.append(clearBrackets(unquote(qs.split("=")[0])))
    if bool(parameters):
        return parameters
    else:
        return ""
def get_multipart_parameters(query_string):
    """
    input:
        ```
        -----------------------------200821510612490
        Content-Disposition: form-data; name="username"

        xyele
        -----------------------------200821510612490
        Content-Disposition: form-data; name="email"

        zeroxyele@wearehackerone.com
        ```

    output:
        username,email
    """
    for content_disposition in re.findall("Content-Disposition: form-data; (.*)",str(query_string)):
        print(content_disposition)
        for name in re.findall(" name=\\\"(.*?)\\\"",str(content_disposition)):
            yield name

def isJson(myjson):
    try:
        json.loads(myjson)
        try:
            int(myjson)
            return False
        except Exception as efirst:
            return True
    except Exception as esecond:
        return False
    return True

reportsPath = args.reports # get 
outputDir = args.output

reports = [i for i in list(dict.fromkeys(os.listdir(reportsPath))) if (bool(i) and i.endswith(".json"))]
reports.sort(reverse = True)

results = []

blacklistedSubdomains = ["hackerone-us-west-2-production-attachments.s3.us-west-2"]
blacklistedDomains = ["hackerone-user-content.com"]

successful(f"Loaded {str(len(reports))} reports.")
log("Started to mine data...")

for report in reports:
    readReport = json.load(open("{}{}".format(reportsPath,report)))
    elements = getItems(readReport)
    reportid = report.replace(".json","")
    for element in elements:
        for a,b in extract(report,element):
            try:
                if a == "url":
                    url,raw_url = "",""
                    if ( (b.startswith("http://http%3A%2F%2F")) or ( b.startswith("http://https%3A%2F%2F") )):
                        if b.startswith("http://"):
                            raw_url = unquote(str(b)[7:])
                        else:
                            raw_url = unquote(str(b)[8:])
                    else:
                        raw_url = b
                    url = urlparse(str(raw_url))
                    domain = tldextract(raw_url)

                    get_params = [clearBrackets(unquote(i)) for i in get_parameters("get",url.query)]
                    get_params = [i for i in get_params if re.match(re.compile("^[A-Za-z0-9_\-.]+$"),clearBrackets(i))]
                    get_params = ",".join(get_params)

                    if ((f"{str(domain.domain)}.{str(domain.suffix)}".lower() in blacklistedDomains) == False) and ((str(domain.subdomain) in blacklistedSubdomains) == False):
                        results.append((reportid, b, "GET", domain.subdomain, domain.domain, domain.suffix, url.path, url.fragment, url.query, "", get_params, "", "", ""))
                elif a == "request":
                    if "Host" in b.headers:
                        if ((b.path.startswith("/")) == False):
                            b.path = f"/{b.path}"
                        raw_url = "http://{}{}".format(b.headers["Host"],b.path)
                        url = urlparse("http://{}{}".format(b.headers["Host"],b.path))
                        domain = tldextract(str(b.headers["Host"]))
                        post_data = b.rfile.read().decode()

                        post_parameters,json_parameters = "",""

                        if isJson(post_data): # if post data is valid json
                            json_parameters = getKeys(json.loads(post_data)) # then get all keynames and put it to json_parameters variable

                        if (("Content-Type" in b.headers) and (b.headers["Content-Type"] == "application/x-www-form-urlencoded")):
                            post_parameters = get_parameters("post",post_data)
                        elif (("Content-Type" in b.headers) and (b.headers["Content-Type"] == "multipart/form-data")):
                            post_parameters = get_multipart_parameters(post_data)

                        post_parameters = [clearBrackets(unquote(i)) for i in post_parameters]
                        post_parameters = [i for i in get_params if re.match(re.compile("^[A-Za-z0-9_\-.]+$"),clearBrackets(i))]
                        post_parameters = ",".join(post_parameters)

                        get_params = [clearBrackets(unquote(i)) for i in get_parameters("post",url.query)]
                        get_params = [i for i in get_params if re.match(re.compile("^[A-Za-z0-9_\-.]+$"),clearBrackets(i))]
                        get_params = ",".join(get_params)

                        json_parameters = [clearBrackets(unquote(i)) for i in json_parameters]
                        json_parameters = [i for i in json_parameters if re.match(re.compile("^[A-Za-z0-9_\-.]+$"),clearBrackets(i))]
                        json_parameters = ",".join(json_parameters)

                        headers = ""
                        try:
                            headers = ",".join(list(b.headers))
                        except Exception as identifier:
                            pass

                        if ((f"{str(domain.domain)}.{str(domain.suffix)}".lower() in blacklistedDomains) == False) and ((str(domain.subdomain) in blacklistedSubdomains) == False):
                            results.append( (reportid, raw_url, b.command, domain.subdomain, domain.domain, domain.suffix, url.path, url.fragment, url.query, post_data, get_params, post_parameters, json_parameters, ",".join(list(b.headers)) ) )
                elif a == "justparameter":
                    url,domain = urlparse(""),tldextract("")
                    raw_url = ""
                    if (bool(readReport)) and ("structured_scope" in readReport) and bool(readReport["structured_scope"]) and ("asset_type" in readReport["structured_scope"]) and ((" " in readReport["structured_scope"]["asset_identifier"]) == False):
                        asset_data = str(readReport["structured_scope"]["asset_identifier"]).replace("*","www")
                        asset_type = readReport["structured_scope"]["asset_type"]
                        if (bool(asset_data)) and ((asset_type == "Domain") or (asset_type == "URL")) and ((asset_data.startswith("http://") or asset_data.startswith("https://")) == False):
                            raw_url = f"http://{asset_data}/"
                        if asset_type == "Domain":
                            domain = tldextract(raw_url)
                        elif asset_type == "URL":
                            url = urlparse(raw_url)
                            domain = tldextract(url.netloc)
                    if re.match(re.compile("^[A-Za-z0-9_\-.]+$"),clearBrackets(b)):
                        results.append((reportid, raw_url, "GET", domain.subdomain, domain.domain, domain.suffix, url.path, url.fragment, url.query, "", b, "", "", ""))
            except Exception as e:
                unsuccessful(f"Got exception: \"{str(e)}\", Line: {sys.exc_info()[-1].tb_lineno}")
                pass

results = list(set(results)) # remove duplicates of results throught

successful("Got {} results.".format( format(len(results),",")) )

writer = csv.writer(open(args.output, 'w+', newline=''))
writer.writerow(["id", "url", "method", "subdomain","domain","tld","path","fragment","query_string","post_data","get_parameters","post_parameters","json_parameters","headers"])
for result in results:
    writer.writerow(result)

successful("Saved to {} all results.".format( args.output ) )
exit()
