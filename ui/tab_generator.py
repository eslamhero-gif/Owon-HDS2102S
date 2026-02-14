from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class GeneratorTab(QWidget):
    """
    ✅ Professional Signal Generator Tab
    - Waveform Select
    - Frequency Control
    - Amplitude + Offset
    - Output Enable
    """

    def __init__(self, hw):
        super().__init__()

        self.hw = hw

        layout = QVBoxLayout(self)

        # ============================
        # ✅ Title
        # ============================
        title = QLabel("SIGNAL GENERATOR")
        title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
            color:#e95420;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # ============================
        # ✅ Main Control Box
        # ============================
        box = QGroupBox("GENERATOR CONTROL")
        form = QFormLayout(box)

        # ------------------------------------------------
        # ✅ Waveform
        # ------------------------------------------------
        self.wave = QComboBox()
        self.wave.addItems(["SINE", "SQUARE", "RAMP", "PULSE"])

        self.wave.currentTextChanged.connect(
            lambda v: self.hw.send(f":FUNCtion {v}")
        )

        form.addRow("Waveform:", self.wave)

        # ------------------------------------------------
        # ✅ Frequency
        # ------------------------------------------------
        self.freq = QDoubleSpinBox()
        self.freq.setRange(0.1, 50_000_000)
        self.freq.setValue(1000)
        self.freq.setSuffix(" Hz")
        self.freq.setDecimals(2)

        self.freq.valueChanged.connect(
            lambda v: self.hw.send(f":FUNCtion:FREQuency {v}")
        )

        form.addRow("Frequency:", self.freq)

        # ------------------------------------------------
        # ✅ Amplitude
        # ------------------------------------------------
        self.amp = QDoubleSpinBox()
        self.amp.setRange(0.01, 20.0)
        self.amp.setValue(1.0)
        self.amp.setSuffix(" Vpp")
        self.amp.setDecimals(3)

        self.amp.valueChanged.connect(
            lambda v: self.hw.send(f":FUNCtion:AMPLitude {v}")
        )

        form.addRow("Amplitude:", self.amp)

        # ------------------------------------------------
        # ✅ Offset
        # ------------------------------------------------
        self.offset = QDoubleSpinBox()
        self.offset.setRange(-10.0, 10.0)
        self.offset.setValue(0.0)
        self.offset.setSuffix(" V")
        self.offset.setDecimals(3)

        self.offset.valueChanged.connect(
            lambda v: self.hw.send(f":FUNCtion:OFFSet {v}")
        )

        form.addRow("Offset:", self.offset)

        layout.addWidget(box)

        # ============================
        # ✅ Output Control
        # ============================
        out_box = QGroupBox("OUTPUT")
        out_layout = QHBoxLayout(out_box)

        self.btn_output = QPushButton("OUTPUT OFF")
        self.btn_output.setCheckable(True)

        self.btn_output.toggled.connect(self.toggle_output)

        out_layout.addWidget(self.btn_output)
        layout.addWidget(out_box)

        layout.addStretch()

    # ======================================================
    # ✅ Activate Generator (OSC Mode)
    # ======================================================
    def activate(self):
        self.hw.send(":MODE OSC")
        QThread.msleep(300)

    # ======================================================
    # ✅ Toggle Output
    # ======================================================
    def toggle_output(self, state):

        if state:
            self.hw.send(":OUTPut ON")
            self.btn_output.setText("OUTPUT ON ✅")
            self.btn_output.setStyleSheet(
                "background:#e95420;font-weight:bold;"
            )
        else:
            self.hw.send(":OUTPut OFF")
            self.btn_output.setText("OUTPUT OFF")
            self.btn_output.setStyleSheet("")
