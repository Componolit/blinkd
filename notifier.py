
import logging
from time import sleep
import threading
from blink1.blink1 import Blink1, REPORT_ID
from usb.core import USBError

logger = logging.getLogger(__name__)

class Notifier:

    LED_BOTH = 0
    LED_UPPER = 1
    LED_LOWER = 2

    STATUS_OK = 0
    STATUS_WARN = 1
    STATUS_ERROR = 2

    def __init__(self):
        self.led = [0, self.STATUS_OK, self.STATUS_OK]
        try:
            blink = Blink1()
            led = threading.Thread(target=self.run_led, args=(blink,), daemon=True)
            led.start()
        except USBError as e:
            logger.fatal(str(e))
            raise RuntimeError(str(e))
            return

    
    def set_status(self, led, status):
        if led == 0:
            self.set_status(1, status)
            self.set_status(2, status)
            return
        self.led[led] = status
        self.led[0] = self.led[1] | self.led[2]

    def run_led(self, blink):
        while True:
            blink.write([REPORT_ID, ord('D'), 1, 400 >> 8, 400 & 0xff, 0, 0, 0])
            for led in [1,2]:
                if self.led[led] == self.STATUS_OK:
                    blink.fade_to_rgb_uncorrected(0, 0, 0, 0, led)
                elif self.led[led] == self.STATUS_WARN:
                    blink.fade_to_rgb_uncorrected(0, 255, 255, 0, led)
                elif self.led[led] == self.STATUS_ERROR:
                    blink.fade_to_rgb_uncorrected(0, 255, 0, 0, led)
            sleep(1)
