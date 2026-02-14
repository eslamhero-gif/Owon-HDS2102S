import numpy as np


class I2CDecoder:
    """
    ✅ Semi-Manual I2C Decoder
    SDA = CH1
    SCL = CH2
    """

    def __init__(self, samplerate=1_000_000, speed=100_000):
        self.samplerate = samplerate
        self.speed = speed

    def auto_threshold(self, wave):
        return (float(np.max(wave)) + float(np.min(wave))) / 2.0

    def decode(self, sda_wave, scl_wave):

        if sda_wave is None or scl_wave is None:
            return []

        # Auto Threshold → bits
        thr_sda = self.auto_threshold(sda_wave)
        thr_scl = self.auto_threshold(scl_wave)

        SDA = (sda_wave > thr_sda).astype(int)
        SCL = (scl_wave > thr_scl).astype(int)

        frames = []
        bits = []

        # Detect rising edges of SCL
        clk_edges = np.where((SCL[1:] == 1) & (SCL[:-1] == 0))[0]

        if len(clk_edges) < 20:
            return []

        # Start condition = SDA falling while SCL high
        for i in range(1, len(SDA)):
            if SDA[i - 1] == 1 and SDA[i] == 0 and SCL[i] == 1:
                frames.append("START")
                break

        # Sample SDA on each rising clock
        for edge in clk_edges[:200]:
            bits.append(SDA[edge])

            if len(bits) == 8:
                byte = 0
                for b in range(8):
                    byte = (byte << 1) | bits[b]

                frames.append(f"0x{byte:02X}")
                bits = []

        frames.append("STOP")

        return frames
