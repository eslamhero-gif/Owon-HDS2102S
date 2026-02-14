from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from core.uart_decoder_pro import UARTDecoderPro


class UARTTabPro(QWidget):
    """
    ✅ UART Pro Decoder Tab
    - Auto Baud Detect
    - Manual Baud Override
    - Custom Baud
    - CH1 / CH2 Select
    - HEX + ASCII Output
    """

    def __init__(self, scope_tab):
        super().__init__()

        self.scope = scope_tab

        layout = QVBoxLayout(self)

        # ==============================
        # ✅ Title
        # ==============================
        title = QLabel("UART PRO DECODER")
        title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
            color:#e95420;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # ==============================
        # ✅ Config Panel
        # ==============================
        form = QFormLayout()

        # Channel Select
        self.channel = QComboBox()
        self.channel.addItems(["CH1", "CH2"])
        form.addRow("Decode Channel:", self.channel)

        # Baud Mode
        self.baud_mode = QComboBox()
        self.baud_mode.addItems([
            "AUTO Detect",
            "9600",
            "19200",
            "38400",
            "57600",
            "115200",
            "Custom"
        ])
        form.addRow("Baud Mode:", self.baud_mode)

        # Custom Baud Input
        self.custom_baud = QSpinBox()
        self.custom_baud.setRange(300, 2_000_000)
        self.custom_baud.setValue(115200)
        self.custom_baud.setEnabled(False)
        form.addRow("Custom Baud:", self.custom_baud)

        self.baud_mode.currentTextChanged.connect(self.on_mode_changed)

        layout.addLayout(form)

        # ==============================
        # ✅ Decode Button
        # ==============================
        self.btn_decode = QPushButton("🚀 Decode UART Now")
        self.btn_decode.clicked.connect(self.run_decode)
        layout.addWidget(self.btn_decode)

        # ==============================
        # ✅ Output HEX + ASCII
        # ==============================
        self.hex_out = QTextEdit()
        self.hex_out.setReadOnly(True)

        self.ascii_out = QTextEdit()
        self.ascii_out.setReadOnly(True)

        layout.addWidget(QLabel("HEX Output:"))
        layout.addWidget(self.hex_out)

        layout.addWidget(QLabel("ASCII Output:"))
        layout.addWidget(self.ascii_out)

    # ======================================================
    # ✅ Mode Changed
    # ======================================================
    def on_mode_changed(self, text):
        self.custom_baud.setEnabled(text == "Custom")

    # ======================================================
    # ✅ Run Decode
    # ======================================================
    def run_decode(self):

        # Select waveform source
        wave = self.scope.last1 if self.channel.currentText() == "CH1" else self.scope.last2

        if wave is None:
            self.hex_out.setText("No waveform captured yet.")
            return

        dec = UARTDecoderPro()

        mode = self.baud_mode.currentText()

        # ✅ Baud Handling
        if mode == "AUTO Detect":
            frames, baud = dec.decode(wave)

        elif mode == "Custom":
            baud = self.custom_baud.value()
            frames, baud = dec.decode(wave, manual_baud=baud)

        else:
            baud = int(mode)
            frames, baud = dec.decode(wave, manual_baud=baud)

        # ✅ Output HEX
        hex_text = f"Baud Used: {baud}\n\n"
        hex_text += " ".join(hex(b) for b in frames[:200])

        self.hex_out.setText(hex_text)

        # ✅ Output ASCII
        self.ascii_out.setText(dec.to_ascii(frames[:400]))
