import usb.core
import threading
import time
import json
import numpy as np

try:
    import usb.core
    import usb.util
except ImportError:
    print("برجاء تثبيت مكتبة pyusb عبر الأمر: pip install pyusb")

class OwonDriver:
    """
    ✅ OWON HDS200 Driver (WinUSB + PyUSB)

    FIXED:
    - Dirty SCPI Bytes Decode
    - Safe Waveform Reading
    - Buffer Odd-Length Fix
    - Safe Measurements
    """

    def __init__(self, vid=0x5345, pid=0x1234):

        self.dev = usb.core.find(idVendor=vid, idProduct=pid)
        if self.dev is None:
            raise RuntimeError("❌ OWON Device Not Found!")

        self.lock = threading.Lock()
        self.dev.set_configuration()

        # Endpoints
        self.ep_out = 0x01
        self.ep_in = 0x81

        # Cached Header
        self.cached_header = None

        # ✅ Safe Init
        self.send(":SYSTem:REMote ON")
        time.sleep(0.2)
        self.send(":MODE OSC")

    # ==================================================
    # ✅ Safe Send Command
    # ==================================================
    def send(self, cmd):
        with self.lock:
            try:
                self.dev.write(self.ep_out, (cmd + "\n").encode())
                time.sleep(0.05)
            except:
                pass

    # ==================================================
    # ✅ Safe Query (Raw Bytes)
    # ==================================================
    def query(self, cmd, size=4096, timeout=3000):
        with self.lock:
            try:
                self.dev.write(self.ep_out, (cmd + "\n").encode())
                raw = self.dev.read(self.ep_in, size, timeout=timeout)
                return raw.tobytes()
            except:
                return None

    # ==================================================
    # ✅ Read Header (JSON)
    # ==================================================
    def get_header(self):

        if self.cached_header:
            return self.cached_header

        raw = self.query(":DATa:WAVe:SCReen:HEAD?", size=1024)

        if raw:
            txt = raw.decode("ascii", errors="ignore").strip()

            if txt.startswith("{"):
                try:
                    self.cached_header = json.loads(txt)
                    return self.cached_header
                except:
                    pass

        # ✅ Fallback default
        self.cached_header = {
            "VerticalScale": 0.01,
            "VerticalOffset": 0
        }
        return self.cached_header

    # ==================================================
    # ✅ SAFE Wave Voltage Reading
    # ==================================================
    def wave_voltage(self, ch="CH1"):

        h = self.get_header()

        scale = float(h.get("VerticalScale", 0.01))
        offset = float(h.get("VerticalOffset", 0))

        raw = self.query(f":DATa:WAVe:SCReen:{ch}?", size=8192)

        if raw is None or len(raw) < 30:
            return None

        # ✅ Remove SCPI Header Bytes (first 10 bytes)
        data = raw[10:]

        # ✅ FIX: OWON returns odd-length packets sometimes
        if len(data) % 2 != 0:
            data = data[:-1]

        # ✅ Too Small packet ignore
        if len(data) < 200:
            return None

        try:
            adc = np.frombuffer(data, dtype="<i2")

            # ✅ Convert ADC → Voltage
            volt = (adc - offset) * scale

            return volt.astype(np.float32)

        except:
            return None

    # ==================================================
    # ✅ SAFE Measurements (No Unicode Errors)
    # ==================================================
    def measure_scope(self, ch=1):

        def q(cmd):

            r = self.query(cmd)

            if not r:
                return "---"

            try:
                return r.decode("ascii", errors="ignore").strip()
            except:
                return "---"

        return (
            q(f":MEASurement:CH{ch}:PKPK?"),
            q(f":MEASurement:CH{ch}:FREQuency?"),
            q(f":MEASurement:CH{ch}:RMS?")
        )

    # ==================================================
    # ✅ Safe DMM Read
    # ==================================================
    def dmm_value(self):

        r = self.query(":DMM:MEAS?")

        if not r:
            return "---"

        return r.decode("ascii", errors="ignore").strip()
