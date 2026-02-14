
import numpy as np

class UARTDecoder:
    def __init__(self, baud=115200, threshold=0.0):
        self.baud=baud
        self.threshold=threshold

    def decode(self, wave, samplerate):
        if wave is None: return []
        bit_time = 1.0/self.baud
        step = int(samplerate * bit_time)

        bits=(wave>self.threshold).astype(int)

        frames=[]
        i=0
        while i < len(bits)-step*10:
            if bits[i]==0 and bits[i-1]==1:  # start edge
                byte=0
                for b in range(8):
                    byte |= bits[i+step*(b+1)]<<b
                frames.append(byte)
                i += step*10
            else:
                i+=1
        return frames
