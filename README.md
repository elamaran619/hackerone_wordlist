
<h1 align="center">
  <br>
  <a href="https://www.hackerone.com/"><img src="https://res-1.cloudinary.com/crunchbase-production/image/upload/c_lpad,f_auto,q_auto:eco/dgsrzgjf4paklpbom6uj" alt="hackerone_logo"></a>
  <br>
  HackerOne Wordlist
  <br>
</h1>
<h4 align="center">The wordlists that have been compiled using disclosed reports at HackerOne bug bounty platform.</h4>
<p align="center">
  <a href="https://github.com/xyele/hackerone_wordlist/stargazers">
    <img src="https://img.shields.io/github/stars/xyele/hackerone_wordlist">
  </a>
  <a href="https://github.com/xyele/hackerone_wordlist/releases">
      <img src="https://img.shields.io/github/release/xyele/hackerone_wordlist">
  </a>
</p>

## Match Cases
Here is the match cases how it extracts all these data.
#### URLs
I've used [urlextract](https://github.com/lipoja/URLExtract) library for extracting URLs based on TLDs. Eventhough it works awesome, there might be false matches rarely. 
#### Raw HTTP Requests
It extracts the raw http requests which is in three backticks (\`\`\`). Her are the example:
````
Hey team! I've found an SQL Injection issue with your website.

## Request
```
POST /xyele/hackerone_wordlist HTTP/1.1
Host: github.com

star_repo=true'
```
````
So it extracts the request and parsing it.
```
POST /xyele/hackerone_wordlist HTTP/1.1
Host: github.com

star_repo=true'
```

#### Parameter names
Besides the getting parameters from requests and URLs, it gets parameter names with regex again. Here are the examples:
```
LFI throught the filename parameter                 --> filename
SQL Injection on blabla domain via userid parameter --> userid
<?php echo $_GET['makesense']; ?>                   --> makesense
```

## To Do
- Extract json and parse parameters from markdown code block.
- Extract json and parse parameters from raw http response.

## Known Issues
- Nothing for yet =)

## Support Me
Reach out to me at one of the following places!
- https://github.com/xyele
- https://hackerone.com/zeroxyele
- https://twitter.com/zeroxyele
