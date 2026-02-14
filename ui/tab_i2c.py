from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from core.i2c_decoder import I2CDecoder


class I2CTab(QWidget):

    def __init__(self, scope_tab):
        super().__init__()
        self.scope = scope_tab

        layout = QVBoxLayout(self)

        title = QLabel("I2C PRO DECODER (SDA=CH1 / SCL=CH2)")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:18px;font-weight:bold;color:#e95420;")
        layout.addWidget(title)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        btn = QPushButton("🚀 Decode I2C Now")
        btn.clicked.connect(self.run_decode)
        layout.addWidget(btn)

    def run_decode(self):

        sda = self.scope.last1
        scl = self.scope.last2

        if sda is None or scl is None:
            self.output.setText("No waveform captured yet.")
            return

        dec = I2CDecoder()
        frames = dec.decode(sda, scl)

        self.output.setText("I2C Frames:\n\n" + "  ".join(frames))
