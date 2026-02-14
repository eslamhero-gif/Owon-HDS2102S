import numpy as np


class UARTDecoderPro:
    """
    ✅ UART Professional Decoder Engine

    Features:
    - Auto Threshold Detection
    - Auto Baud Detection
    - Manual Baud Override
    - Mid-bit Sampling (Stable)
    - HEX + ASCII Output
    """

    def __init__(self, samplerate=1_000_000):
        # OWON does not provide metadata → default guess
        self.samplerate = samplerate

    # ======================================================
    # ✅ Auto Threshold
    # ======================================================
    def auto_threshold(self, wave):
        """
        Automatically pick threshold between HIGH and LOW
        Suitable for TTL 3.3V / 1.8V signals
        """
        return (float(np.max(wave)) + float(np.min(wave))) / 2.0

    # ======================================================
    # ✅ Auto Baud Detection
    # ======================================================
    def auto_baud(self, bits):
        """
        Try estimate baud rate from signal edge distances
        """
        edges = np.where(np.diff(bits) != 0)[0]

        if len(edges) < 10:
            return 115200  # fallback

        distances = np.diff(edges)

        bit_len = int(np.median(distances))

        if bit_len <= 0:
            return 115200

        baud = int(self.samplerate / bit_len)

        # Clamp common UART ranges
        if baud < 300:
            baud = 9600
        if baud > 2_000_000:
            baud = 115200

        return baud

    # ======================================================
    # ✅ UART Decode Core
    # ======================================================
    def decode(self, wave, manual_baud=None):
        """
        Decode UART frames into bytes.

        Parameters:
        - wave: waveform voltage array
        - manual_baud: if given → override baud

        Returns:
        - frames: list of decoded bytes
        - baud_used: baud used for decoding
        """

        if wave is None:
            return [], 115200

        # Auto threshold → bits
        thr = self.auto_threshold(wave)
        bits = (wave > thr).astype(int)

        # Baud Select
        if manual_baud:
            baud = int(manual_baud)
        else:
            baud = self.auto_baud(bits)

        # Samples per bit
        step = int(self.samplerate / baud)
        if step < 2:
            step = 2

        frames = []
        i = 1

        # Scan signal
        while i < len(bits) - step * 12:

            # ✅ Detect Start Bit (Falling Edge)
            if bits[i - 1] == 1 and bits[i] == 0:

                byte = 0

                # Sample in middle of each bit
                base = i + int(step * 1.5)

                for b in range(8):
                    idx = base + step * b
                    if idx < len(bits):
                        byte |= bits[idx] << b

                frames.append(byte)

                # Skip stop bit region
                i += step * 10

            else:
                i += 1

        return frames, baud

    # ======================================================
    # ✅ ASCII Helper
    # ======================================================
    def to_ascii(self, frames):
        """
        Convert decoded bytes into readable ASCII string
        """
        text = ""
        for b in frames:
            if 32 <= b < 127:
                text += chr(b)
            else:
                text += "."
        return text
