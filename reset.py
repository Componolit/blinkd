#!/usr/bin/env python3

import socket
import sys
import json

if __name__ == "__main__":
    led = 0
    if len(sys.argv) > 1:
        try:
            if int(sys.argv[1]) in [1,2]:
                led = int(sys.argv[1])
        except:
            pass

    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        s.connect("/tmp/blinkd.socket")
        s.sendall(json.dumps({'led':led, 'status':0}).encode('utf-8'))
        s.close()
    except FileNotFoundError:
        print("blinkd is not running")
