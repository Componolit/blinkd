
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
    STATUS_FATAL = 3

    def __init__(self):
        self.led = [0, self.STATUS_OK, self.STATUS_OK]
        try:
            blink = Blink1()
            led1 = threading.Thread(target=self.run_led, args=(blink, 1), daemon=True)
            led2 = threading.Thread(target=self.run_led, args=(blink, 2), daemon=True)
            led1.start()
            led2.start()
        except USBError as e:
            logger.fatal(str(e))
            raise RuntimeError(str(e))
            return

    
    def set_status(self, led, status):
        if led == 0:
            self.set_status(1, status)
            self.set_status(2, status)

    def run_led(self, blink, led):
        while True:
            if self.led[led] == self.STATUS_OK:
                blink.fade_to_rgb_uncorrected(0, 0, 0, 0, led)
                blink.write([REPORT_ID, ord('D'), 1, 200 >> 8, 200 & 0xff, 0, 0, 0])
                sleep(0.5)
            elif self.led[led] == self.STATUS_WARN:
                blink.fade_to_rgb_uncorrected(0, 255, 255, 0, led)
                sleep(0.5)
            elif self.led[led] == self.STATUS_ERROR:
                blink.fade_to_rgb_uncorrected(0, 255, 0, 0, led)
                sleep(0.5)
            elif self.led[led] == self.STATUS_FATAL:
                while not self.led_changed[led].is_set():
                    blink.fade_to_rgb_uncorrected(0, 255, 0, 0, led)
                    sleep(0.25)
                    blink.fade_to_rgb_uncorrected(0, 0, 0, 0, led)
                    sleep(0.25)
