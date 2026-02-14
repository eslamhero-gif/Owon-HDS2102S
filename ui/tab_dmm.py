from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QThread
import pyqtgraph as pg
import numpy as np
import pyttsx3
import threading

# --- محرك الصوت فائق السرعة ---
def speak_text(text):
    def run_speech():
        try:
            engine = pyttsx3.init()
            # زيادة السرعة ليكون النطق خاطفاً
            engine.setProperty('rate', 230) 
            engine.say(text)
            engine.runAndWait()
        except: pass
    threading.Thread(target=run_speech, daemon=True).start()

class DMMTab(QWidget):
    def __init__(self, hw):
        super().__init__()

        self.hw = hw
        self.mode_unit = "V"
        self.current_name = "V DC"
        
        # --- متغيرات الثبات الفائق ---
        self.stable_val = 0.0        
        self.ema_alpha = 0.25         # موازنة بين الثبات وسرعة القفز
        self.history_data = np.zeros(100)
        self.last_raw_input = 0.0
        self.stability_counter = 0    # العداد المسؤول عن توقيت الصوت
        self.last_spoken_val = ""

        self.offset_value = 0.0
        self.is_rel_active = False

        # --- الواجهة الرسومية ---
        layout = QVBoxLayout(self)

        # 1. شاشة العرض الرقمية
        self.display = QLabel("O.L")
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_display_style("#e95420") 
        layout.addWidget(self.display)

        # 2. الرسم البياني
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setFixedHeight(110)
        self.plot_widget.setBackground('black')
        self.plot_widget.hideAxis('bottom')
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color="#e95420", width=2))
        layout.addWidget(self.plot_widget)

        # 3. لوحة الأوضاع
        grid = QGridLayout()
        funcs = [
            ("V DC",  ":DMM:CONF:VOLT DC", "V"), ("V AC",  ":DMM:CONF:VOLT AC", "V"),
            ("Ω RES", ":DMM:CONF RES",     "Ω"), ("CAP",   ":DMM:CONF CAP",     "F"),
            ("DIODE", ":DMM:CONF DIOD",    "V"), ("CONT",  ":DMM:CONF CONT",    "Ω"),
            ("I DC",  ":DMM:CONF:CURR DC", "A"), ("I AC",  ":DMM:CONF:CURR AC", "A"),
        ]

        self.mode_buttons = []
        for i, (name, cmd, unit) in enumerate(funcs):
            b = QPushButton(name)
            b.setMinimumHeight(45)
            b.setStyleSheet("background-color: #222; color: #aaa; border: 1px solid #444;")
            b.clicked.connect(lambda _, c=cmd, u=unit, n=name, btn=b: self.set_function(c, u, n, btn))
            grid.addWidget(b, i // 4, i % 4)
            self.mode_buttons.append(b)
        layout.addLayout(grid)

        # 4. التحكم
        ctrl_layout = QHBoxLayout()
        self.btn_rel = QPushButton("ZERO")
        self.btn_hold = QPushButton("HOLD")
        self.btn_hold.setCheckable(True)
        self.btn_voice = QPushButton("VOICE OFF")
        self.btn_voice.setCheckable(True)

        for b in [self.btn_rel, self.btn_hold, self.btn_voice]:
            b.setMinimumHeight(45)
            b.setStyleSheet("background-color: #333; color: white; font-weight: bold;")
            ctrl_layout.addWidget(b)

        self.btn_rel.clicked.connect(self.toggle_relative)
        self.btn_voice.clicked.connect(self.sync_voice_ui)
        layout.addLayout(ctrl_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_logic)

    def set_display_style(self, color):
        self.display.setStyleSheet(f"""
            QLabel {{ background: black; border-radius: 12px; padding: 10px;
                     font-family: 'Consolas'; border: 3px solid {color}; color: {color};
                     font-size: 72pt; font-weight: bold; }}
        """)

    def set_function(self, cmd, unit, name, btn):
        for b in self.mode_buttons: b.setStyleSheet("background-color: #222; color: #aaa;")
        btn.setStyleSheet("background-color: #e95420; color: white; font-weight: bold; border: 2px solid white;")
        self.mode_unit, self.current_name = unit, name
        self.stable_val = 0.0
        self.stability_counter = 0
        self.last_spoken_val = ""
        self.hw.send(cmd)
        QThread.msleep(300)
        if not self.timer.isActive(): self.timer.start(70)

    def format_output(self, val):
        abs_v = abs(val)
        
        # 🛡️ منطق الـ O.L الموحد
        is_open = False
        if self.current_name == "DIODE":
            if abs_v > 2.0 or abs_v < 0.00001: is_open = True
        elif self.mode_unit == "Ω":
            if abs_v > 2e6 or abs_v < 0.000001: is_open = True
        elif abs_v > 1e10: is_open = True

        if is_open:
            self.set_display_style("#e95420")
            return "O.L"

        # 🚩 منطق الـ SHORT
        is_short = False
        if self.mode_unit == "Ω" and 0.0001 < abs_v < 2.5: is_short = True
        if self.current_name == "DIODE" and 0.0001 < abs_v < 0.04: is_short = True
        
        if is_short:
            self.set_display_style("#ff0000")
            return "SHORT"

        # 🟢 قراءة عادية
        self.set_display_style("#8ae234")
        u = self.mode_unit
        if abs_v >= 1e6: return f"{val/1e6:.3f} M{u}"
        if abs_v >= 1e3: return f"{val/1e3:.4f} k{u}"
        if abs_v >= 1:   return f"{val:.4f} {u}"
        return f"{val*1e3:.2f} m{u}" if abs_v >= 1e-3 else f"{val:.6f} {u}"

    def update_logic(self):
        if self.btn_hold.isChecked(): return
        
        try:
            raw_resp = self.hw.query(":DMM:MEAS?")
            if not raw_resp: return
            
            resp_str = raw_resp.decode().strip()
            
            if "OL" in resp_str.upper() or "9.9E37" in resp_str:
                formatted = "O.L"
                self.stability_counter += 1 # استقرار وهمي للـ OL للنطق السريع
            else:
                raw_val = float(resp_str) - self.offset_value
                
                # فلتر EMA
                diff = abs(raw_val - self.last_raw_input)
                if diff > 0.08: # قفزة (تغيير مكان المجس)
                    self.stable_val = raw_val
                    self.stability_counter = 0 # تصفير العداد عند الحركة
                else:
                    self.stable_val = (self.ema_alpha * raw_val) + (1 - self.ema_alpha) * self.stable_val
                    self.stability_counter += 1

                self.last_raw_input = raw_val
                formatted = self.format_output(self.stable_val)

            self.display.setText(formatted)

            # الرسم البياني
            if formatted not in ["O.L", "SHORT"]:
                self.history_data = np.roll(self.history_data, -1)
                self.history_data[-1] = self.stable_val
                self.curve.setData(self.history_data)

            # 🔊 النطق الفوري (بعد 5 قراءات مستقرة فقط)
            if self.btn_voice.isChecked() and self.stability_counter == 6:
                if formatted != self.last_spoken_val:
                    # تحويل الرموز لكلمات يفهمها المحرك
                    speech = formatted.replace("Ω", "Ohms").replace("V", "Volts").replace("SHORT", "Short")
                    speak_text(speech)
                    self.last_spoken_val = formatted

        except: pass

    def toggle_relative(self):
        self.is_rel_active = not self.is_rel_active
        self.offset_value = self.stable_val if self.is_rel_active else 0.0
        self.btn_rel.setStyleSheet(f"background-color: {'#ce5c00' if self.is_rel_active else '#333'}; color: white;")

    def sync_voice_ui(self):
        if self.btn_voice.isChecked():
            self.btn_voice.setText("🔊 VOICE ON")
            self.btn_voice.setStyleSheet("background-color: #ce5c00; color: white; font-weight: bold;")
        else:
            self.btn_voice.setText("VOICE OFF")
            self.btn_voice.setStyleSheet("background-color: #333; color: white;")

    def activate(self):
        self.hw.send(":MODE DMM"); QThread.msleep(200); self.timer.start(70)

    def deactivate(self):
        self.timer.stop()