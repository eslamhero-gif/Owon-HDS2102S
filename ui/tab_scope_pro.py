from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import pyqtgraph as pg

from core.disk_recorder_pro import DiskRecorderPro


class ScopeTabPro(QWidget):
    """
    ✅ Tektronix Professional Scope Tab
    - Live CH1/CH2
    - Trigger Sidebar
    - Channel ON/OFF + View Mode
    - Measurements Dock
    - Recorder Pro + Playback
    """

    def __init__(self, hw):
        super().__init__()

        self.hw = hw
        self.hw.get_header()

        # Wave Buffers
        self.last1 = None
        self.last2 = None
        self.toggle = False

        # Channel Enable Flags
        self.ch1_enabled = True
        self.ch2_enabled = True

        # Playback Mode
        self.play_mode = False
        self.play_frames = []
        self.play_index = 0

        # Recorder Engine
        self.recorder = DiskRecorderPro()

        # ================================
        # ✅ Main Split (Plot + Dock)
        # ================================
        main_split = QSplitter(Qt.Orientation.Vertical)

        # ================================
        # ✅ Top Split (Sidebar + Plot)
        # ================================
        top_split = QSplitter(Qt.Orientation.Horizontal)

        # --------------------------------------------------
        # ✅ LEFT SIDEBAR
        # --------------------------------------------------
        sidebar = QWidget()
        side = QVBoxLayout(sidebar)

        # ---------------- TRIGGER -----------------
        title = QLabel("TRIGGER CONTROL")
        title.setStyleSheet("font-size:14px;font-weight:bold;color:#e95420;")
        side.addWidget(title)

        self.trig_mode = QComboBox()
        self.trig_mode.addItems(["AUTo", "NORM", "SING"])
        self.trig_mode.currentTextChanged.connect(
            lambda v: self.hw.send(f":TRIGger:SWEep {v}")
        )
        side.addWidget(QLabel("Sweep Mode:"))
        side.addWidget(self.trig_mode)

        self.trig_src = QComboBox()
        self.trig_src.addItems(["CH1", "CH2"])
        self.trig_src.currentTextChanged.connect(
            lambda v: self.hw.send(f":TRIGger:SOURce {v}")
        )
        side.addWidget(QLabel("Trigger Source:"))
        side.addWidget(self.trig_src)

        self.trig_edge = QComboBox()
        self.trig_edge.addItems(["RISE", "FALL"])
        self.trig_edge.currentTextChanged.connect(
            lambda v: self.hw.send(f":TRIGger:SLOPe {v}")
        )
        side.addWidget(QLabel("Edge:"))
        side.addWidget(self.trig_edge)

        self.level = QSlider(Qt.Orientation.Horizontal)
        self.level.setRange(-200, 200)
        self.level.valueChanged.connect(
            lambda v: self.hw.send(f":TRIGger:LEVel {v}mV")
        )
        side.addWidget(QLabel("Trigger Level:"))
        side.addWidget(self.level)

        # ---------------- CHANNEL DISPLAY -----------------
        ch_title = QLabel("CHANNEL DISPLAY")
        ch_title.setStyleSheet("font-size:14px;font-weight:bold;color:#e95420;")
        side.addWidget(ch_title)

        # --- CH1 Toggle ---
        self.btn_ch1 = QPushButton("CH1: ON ✅")
        self.btn_ch1.setCheckable(True)
        self.btn_ch1.setChecked(True)

        def toggle_ch1(state):
            self.ch1_enabled = state
            self.hw.send(f":CH1:DISP {'ON' if state else 'OFF'}")
            self.btn_ch1.setText("CH1: ON ✅" if state else "CH1: OFF ❌")

        self.btn_ch1.toggled.connect(toggle_ch1)
        side.addWidget(self.btn_ch1)

        # --- CH2 Toggle ---
        self.btn_ch2 = QPushButton("CH2: ON ✅")
        self.btn_ch2.setCheckable(True)
        self.btn_ch2.setChecked(True)

        def toggle_ch2(state):
            self.ch2_enabled = state
            self.hw.send(f":CH2:DISP {'ON' if state else 'OFF'}")
            self.btn_ch2.setText("CH2: ON ✅" if state else "CH2: OFF ❌")

        self.btn_ch2.toggled.connect(toggle_ch2)
        side.addWidget(self.btn_ch2)

        # --- View Mode Selector ---
        self.view_mode = QComboBox()
        self.view_mode.addItems(["Both Channels", "CH1 Only", "CH2 Only"])

        def change_view(mode):
            if mode == "CH1 Only":
                self.btn_ch1.setChecked(True)
                self.btn_ch2.setChecked(False)

            elif mode == "CH2 Only":
                self.btn_ch1.setChecked(False)
                self.btn_ch2.setChecked(True)

            else:
                self.btn_ch1.setChecked(True)
                self.btn_ch2.setChecked(True)

        self.view_mode.currentTextChanged.connect(change_view)

        side.addWidget(QLabel("View Mode:"))
        side.addWidget(self.view_mode)

        side.addStretch()
        top_split.addWidget(sidebar)

        # --------------------------------------------------
        # ✅ Scope Display (Big Plot)
        # --------------------------------------------------
        self.plot = pg.PlotWidget(title="OWON Ultra Live Scope")
        self.plot.showGrid(x=True, y=True, alpha=0.25)
        self.plot.setBackground("#111111")

        self.curve1 = self.plot.plot(pen=pg.mkPen("#fbef00", width=2))
        self.curve2 = self.plot.plot(pen=pg.mkPen("#34e2e2", width=2))

        top_split.addWidget(self.plot)
        top_split.setSizes([350, 1500])
        main_split.addWidget(top_split)

        # ================================
        # ✅ Bottom Dock
        # ================================
        dock = QSplitter(Qt.Orientation.Horizontal)

        meas_box = QGroupBox("MEASUREMENTS")
        meas_layout = QGridLayout(meas_box)

        self.meas_labels = {}
        for i, name in enumerate(["Vpp", "Vrms", "Freq"]):
            lab = QLabel(name)
            val = QLabel("---")
            val.setStyleSheet("color:#8ae234;font-size:15px;font-weight:bold;")
            meas_layout.addWidget(lab, 0, i)
            meas_layout.addWidget(val, 1, i)
            self.meas_labels[name] = val

        dock.addWidget(meas_box)

        rec_box = QGroupBox("DISK RECORDER PRO")
        rec_layout = QHBoxLayout(rec_box)

        self.btn_rec = QPushButton("⏺ Record")
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_play = QPushButton("▶ Playback")

        self.btn_rec.clicked.connect(self.start_record)
        self.btn_stop.clicked.connect(self.stop_record)
        self.btn_play.clicked.connect(self.start_playback)

        rec_layout.addWidget(self.btn_rec)
        rec_layout.addWidget(self.btn_stop)
        rec_layout.addWidget(self.btn_play)

        dock.addWidget(rec_box)

        main_split.addWidget(dock)
        main_split.setSizes([750, 200])

        layout = QVBoxLayout(self)
        layout.addWidget(main_split)

        # Timer Live
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_loop)

    # ======================================================
    def activate(self):
        self.hw.send(":MODE OSC")
        QThread.msleep(400)
        self.timer.start(220)

    def deactivate(self):
        self.timer.stop()

    # ======================================================
    # ✅ Recorder Functions
    def start_record(self):
        base, _ = QFileDialog.getSaveFileName(self, "Save Recording", "", "*.owon")
        if base:
            self.recorder.start(base)

    def stop_record(self):
        self.recorder.stop()
        self.play_mode = False

    def start_playback(self):
        base, _ = QFileDialog.getOpenFileName(self, "Open Recording", "", "*.owon")
        if base:
            self.play_frames = self.recorder.load_frames(base, max_frames=500)
            self.play_mode = True
            self.play_index = 0

    # ======================================================
    # ✅ Update Loop
    def update_loop(self):

        # Playback Mode
        if self.play_mode and self.play_frames:
            ch1, ch2 = self.play_frames[self.play_index]
            self.play_index = (self.play_index + 1) % len(self.play_frames)

            self.curve1.setData(ch1)
            self.curve2.setData(ch2)
            return

        # Live Mode
        self.toggle = not self.toggle

        if self.toggle and self.ch1_enabled:
            w = self.hw.wave_voltage("CH1")
            if w is not None:
                self.last1 = w

        if not self.toggle and self.ch2_enabled:
            w = self.hw.wave_voltage("CH2")
            if w is not None:
                self.last2 = w

        # ✅ Draw Enabled Channels Only
        if self.ch1_enabled and self.last1 is not None:
            self.curve1.setData(self.last1)
        else:
            self.curve1.clear()

        if self.ch2_enabled and self.last2 is not None:
            self.curve2.setData(self.last2)
        else:
            self.curve2.clear()

        # ✅ Recording
        if self.recorder.recording and self.last1 is not None and self.last2 is not None:
            self.recorder.push(self.last1, self.last2)

        # ✅ Measurements
        pkpk, freq, vrms = self.hw.measure_scope(1)
        self.meas_labels["Vpp"].setText(pkpk)
        self.meas_labels["Freq"].setText(freq)
        self.meas_labels["Vrms"].setText(vrms)

# ✅ Backward Compatibility Alias
ScopeTab = ScopeTabPro
