
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from core.uart_decoder import UARTDecoder

class UARTTab(QWidget):
    def __init__(self, scope_tab):
        super().__init__()
        self.scope=scope_tab

        layout=QVBoxLayout(self)

        form=QFormLayout()
        self.baud=QSpinBox()
        self.baud.setRange(300,1000000)
        self.baud.setValue(115200)

        self.thr=QDoubleSpinBox()
        self.thr.setRange(-5,5)
        self.thr.setValue(0.0)

        form.addRow("Baud Rate:", self.baud)
        form.addRow("Threshold:", self.thr)
        layout.addLayout(form)

        self.output=QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        btn=QPushButton("Decode Now")
        btn.clicked.connect(self.run_decode)
        layout.addWidget(btn)

    def run_decode(self):
        wave=self.scope.last1
        if wave is None:
            return

        baud=self.baud.value()
        thr=self.thr.value()

        dec=UARTDecoder(baud,thr)

        # Samplerate manual guess (1MS/s default)
        samplerate=1_000_000

        frames=dec.decode(wave,samplerate)

        text="Decoded Bytes:\n"
        text+=" ".join([hex(x) for x in frames[:50]])
        self.output.setText(text)
