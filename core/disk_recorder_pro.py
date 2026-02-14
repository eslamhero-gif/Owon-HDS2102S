
import numpy as np
import struct, os

class DiskRecorderPro:
    '''
    Professional streaming recorder:
    - Binary frames
    - Index file for fast seeking
    '''
    def __init__(self):
        self.fbin=None
        self.fidx=None
        self.recording=False
        self.frame_count=0

    def start(self, basefile):
        self.fbin=open(basefile+".bin","wb")
        self.fidx=open(basefile+".idx","w")
        self.recording=True
        self.frame_count=0

    def stop(self):
        if self.fbin: self.fbin.close()
        if self.fidx: self.fidx.close()
        self.recording=False

    def push(self,ch1,ch2):
        if not self.recording: return

        # Save offset in index
        pos=self.fbin.tell()
        self.fidx.write(str(pos)+"\n")

        np.save(self.fbin,ch1)
        np.save(self.fbin,ch2)

        self.frame_count+=1

    def load_frames(self, basefile, max_frames=200):
        frames=[]
        binfile=basefile+".bin"
        idxfile=basefile+".idx"

        if not os.path.exists(binfile): return frames

        with open(binfile,"rb") as f:
            while len(frames)<max_frames:
                try:
                    ch1=np.load(f,allow_pickle=True)
                    ch2=np.load(f,allow_pickle=True)
                    frames.append((ch1,ch2))
                except:
                    break
        return frames
