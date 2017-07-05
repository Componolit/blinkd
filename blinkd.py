#!/usr/bin/env python3

import socket
import stat
import os
import signal
import logging
import json
from notifier import Notifier

def handler(signum, frame):
    logger.info("Catched signal {}, stopping".format(signum))
    if os.path.exists("/tmp/blinkd.pid"):
        os.remove("/tmp/blinkd.pid")
    if os.path.exists("/tmp/blinkd.socket"):
        os.remove("/tmp/blinkd.socket")
    exit(0)

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s [%(name)s] %(levelname)s:%(message)s", level=logging.INFO)

if __name__ == "__main__":
    logger.info("Starting blinkd service")
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    pid = os.getpid()
    if os.path.exists("/tmp/blinkd.pid") or os.path.exists("/tmp/blinkd.socket"):
        logger.fatal("Failed to start, is there already an instance running? If not delete /tmp/blinkd.socket and /tmp/blinkd.pid")
        exit(2)
    pidfile = open("/tmp/blinkd.pid", "w")
    pidfile.write(str(os.getpid()))
    pidfile.close()
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as s:
        try:
            s.bind("/tmp/blinkd.socket")
            os.chmod("/tmp/blinkd.socket", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        except (PermissionError, OSError) as e:
            logger.fatal("Failed to bind socket: {}".format(str(e)))
            exit(1)
        try:
            n = Notifier()
        except RuntimeError:
            logger.fatal("Failed to start blinkd!")
            exit(1)
        logger.info("Started blinkd service successfully")
        while True:
            data = json.loads(s.recv(64).decode('utf-8'))
            n.set_status(data['led'], data['status'])
