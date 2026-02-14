
from PyQt6.QtWidgets import *
from core.disk_recorder_pro import DiskRecorderPro

class RecorderDock(QGroupBox):
    def __init__(self, scope_tab):
        super().__init__("DISK RECORDER")
        self.scope=scope_tab
        self.rec=DiskRecorderPro()

        lay=QHBoxLayout(self)

        self.btn_start=QPushButton("⏺ Record")
        self.btn_stop=QPushButton("⏹ Stop")
        self.btn_play=QPushButton("▶ Playback")

        self.btn_start.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_play.clicked.connect(self.play)

        lay.addWidget(self.btn_start)
        lay.addWidget(self.btn_stop)
        lay.addWidget(self.btn_play)

    def start(self):
        file,_=QFileDialog.getSaveFileName(self,"Save Recording Base","","*.owon")
        if file:
            self.rec.start(file)

    def stop(self):
        self.rec.stop()

    def play(self):
        file,_=QFileDialog.getOpenFileName(self,"Open Recording Base","","*.owon")
        if file:
            frames=self.rec.load_frames(file, max_frames=500)
            self.scope.play_frames=frames
            self.scope.play_mode=True
            self.scope.play_index=0
