
import numpy as np

class DiskRecorder:
    def __init__(self):
        self.file=None
        self.csv=None
        self.recording=False

    def start(self,binfile,csvfile):
        self.file=open(binfile,"wb")
        self.csv=open(csvfile,"w")
        self.recording=True

    def stop(self):
        if self.file: self.file.close()
        if self.csv: self.csv.close()
        self.recording=False

    def push(self,ch1,ch2):
        if not self.recording: return
        np.save(self.file,ch1)
        np.save(self.file,ch2)
        # CSV simplified export
        self.csv.write(",".join(map(str,ch1[:200]))+"\n")

