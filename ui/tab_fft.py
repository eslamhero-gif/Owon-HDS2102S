from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import numpy as np
import pyqtgraph as pg


class FFTTab(QWidget):
    """
    ✅ Professional FFT Spectrum Tab
    - Real Time FFT
    - Peak Frequency Marker
    - Tektronix Style Analyzer
    """

    def __init__(self, scope_tab):
        super().__init__()

        self.scope = scope_tab

        layout = QVBoxLayout(self)

        # ==============================
        # ✅ Title
        # ==============================
        title = QLabel("FFT SPECTRUM ANALYZER")
        title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
            color:#e95420;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # ==============================
        # ✅ Spectrum Plot
        # ==============================
        self.plot = pg.PlotWidget(title="Frequency Domain")
        self.plot.setBackground("#111111")
        self.plot.showGrid(x=True, y=True, alpha=0.25)

        self.curve = self.plot.plot(pen=pg.mkPen("#8ae234", width=2))

        layout.addWidget(self.plot)

        # ==============================
        # ✅ Peak Display
        # ==============================
        self.peak_label = QLabel("Peak Frequency: --- Hz")
        self.peak_label.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
            color:#8ae234;
        """)
        self.peak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.peak_label)

        # ==============================
        # ✅ FFT Refresh Timer
        # ==============================
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_fft)
        self.timer.start(500)

    # ======================================================
    # ✅ FFT Update Loop
    # ======================================================
    def update_fft(self):

        # ✅ Get Last CH1 Waveform
        wave = self.scope.last1
        if wave is None:
            return

        # Convert to numpy float
        wave = np.array(wave, dtype=np.float32)

        # Remove DC offset
        wave -= np.mean(wave)

        # FFT Compute
        fft = np.abs(np.fft.rfft(wave))

        # Fake SampleRate (OWON does not provide metadata)
        samplerate = 1_000_000  # 1 MS/s assumption

        freqs = np.fft.rfftfreq(len(wave), d=1 / samplerate)

        # Ignore low bins
        if len(fft) < 10:
            return

        # Peak Detection
        peak_index = np.argmax(fft[5:]) + 5
        peak_freq = freqs[peak_index]

        # Update Plot
        self.curve.setData(freqs, fft)

        # Update Peak Label
        self.peak_label.setText(f"Peak Frequency: {peak_freq:,.1f} Hz")
