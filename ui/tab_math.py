from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import numpy as np
import pyqtgraph as pg


class MathTab(QWidget):
    """
    ✅ Math Channel Tab (Fixed Version)
    تم إصلاح خطأ اختلاف أطوال المصفوفات
    """

    def __init__(self, scope_tab):
        super().__init__()

        self.scope = scope_tab

        layout = QVBoxLayout(self)

        # ==============================
        # ✅ Title
        # ==============================
        title = QLabel("MATH FUNCTIONS")
        title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
            color:#e95420;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # ==============================
        # ✅ Math Mode Selector
        # ==============================
        self.mode = QComboBox()
        self.mode.addItems([
            "CH1 + CH2",
            "CH1 - CH2",
            "Invert CH1",
            "Absolute CH1"
        ])

        self.mode.setStyleSheet("font-size:12pt; padding:6px;")
        layout.addWidget(self.mode)

        # ==============================
        # ✅ Math Plot
        # ==============================
        self.plot = pg.PlotWidget(title="Math Waveform")
        self.plot.setBackground("#111111")
        self.plot.showGrid(x=True, y=True, alpha=0.25)

        self.curve = self.plot.plot(
            pen=pg.mkPen("#e95420", width=2)
        )

        layout.addWidget(self.plot)

        # ==============================
        # ✅ Refresh Timer
        # ==============================
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(100) # تم تقليل الوقت ليكون التحديث أسرع

    # ======================================================
    # ✅ Refresh Math Waveform (With Length Check)
    # ======================================================
    def refresh(self):
        ch1_raw = self.scope.last1
        ch2_raw = self.scope.last2

        if ch1_raw is None or len(ch1_raw) == 0:
            return

        # تحويل CH1 إلى مصفوفة نيمباي
        ch1 = np.array(ch1_raw, dtype=np.float32)
        mode = self.mode.currentText()
        result = ch1 # القيمة الافتراضية

        # ✅ العمليات التي تتطلب القناتين معاً
        if mode in ["CH1 + CH2", "CH1 - CH2"]:
            if ch2_raw is not None and len(ch2_raw) > 0:
                ch2 = np.array(ch2_raw, dtype=np.float32)
                
                # 🛠️ حل المشكلة: توحيد الأطوال (قص المصفوفة الأطول)
                min_len = min(len(ch1), len(ch2))
                ch1_clipped = ch1[:min_len]
                ch2_clipped = ch2[:min_len]

                if mode == "CH1 + CH2":
                    result = ch1_clipped + ch2_clipped
                else:
                    result = ch1_clipped - ch2_clipped
            else:
                result = ch1 # إذا كانت CH2 غير موجودة اعرض CH1 فقط

        # ✅ العمليات التي تتطلب القناة الأولى فقط
        elif mode == "Invert CH1":
            result = -ch1

        elif mode == "Absolute CH1":
            result = np.abs(ch1)

        # ✅ تحديث الرسم البياني
        self.curve.setData(result)