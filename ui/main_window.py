from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QThread

# ===============================
# ✅ Core Driver
# ===============================
from core.driver import OwonDriver

# ===============================
# ✅ Tabs Imports
# ===============================
from ui.tab_scope_pro import ScopeTabPro
from ui.tab_dmm import DMMTab
from ui.tab_generator import GeneratorTab

from ui.tab_fft import FFTTab
from ui.tab_math import MathTab
from ui.tab_uart_pro import UARTTabPro
from ui.tab_i2c import I2CTab


# ===============================
# ✅ Ubuntu Dark Orange Pro Theme
# ===============================
UBUNTU_STYLE = """
QMainWindow { background: #0f111a; }

QTabWidget::pane { border: none; }

QTabBar::tab {
    background: #1a1c25;
    padding: 12px 20px;
    margin: 4px;
    border-radius: 10px;
    color: #dddddd;
    font-size: 11pt;
}

QTabBar::tab:selected {
    background: #e95420;
    color: white;
    font-weight: bold;
}

QPushButton {
    background: #232634;
    padding: 10px;
    border-radius: 10px;
    color: white;
    font-size: 11pt;
}

QPushButton:hover {
    background: #2f3347;
    border: 1px solid #e95420;
}

QGroupBox {
    border: 1px solid #333;
    border-radius: 10px;
    margin-top: 10px;
    color: #e95420;
    font-weight: bold;
}

QLabel { color: #dddddd; }
"""


# ==========================================
# ✅ MAIN WINDOW (ULTRA FULL SUITE)
# ==========================================
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # ✅ Apply Theme
        self.setStyleSheet(UBUNTU_STYLE)

        # ✅ Hardware Driver
        self.hw = OwonDriver()

        # ✅ Main Tabs
        self.tabs = QTabWidget()

        # ==================================================
        # ✅ MAIN SCOPE + SYSTEM TABS
        # ==================================================
        self.scope_tab = ScopeTabPro(self.hw)

        self.fft_tab = FFTTab(self.scope_tab)
        self.math_tab = MathTab(self.scope_tab)

        self.uart_tab = UARTTabPro(self.scope_tab)
        self.i2c_tab = I2CTab(self.scope_tab)

        # ==================================================
        # ✅ TOOL MODES
        # ==================================================
        self.dmm_tab = DMMTab(self.hw)
        self.gen_tab = GeneratorTab(self.hw)

        # ==================================================
        # ✅ Add Tabs
        # ==================================================
        self.tabs.addTab(self.scope_tab, "Oscilloscope")
        self.tabs.addTab(self.fft_tab, "FFT Spectrum")
        self.tabs.addTab(self.math_tab, "Math Channel")

        self.tabs.addTab(self.uart_tab, "UART Pro")
        self.tabs.addTab(self.i2c_tab, "I2C Pro")

        self.tabs.addTab(self.dmm_tab, "Multimeter")
        self.tabs.addTab(self.gen_tab, "Generator")

        self.setCentralWidget(self.tabs)

        # ✅ Tab Switching
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # ✅ Window Title
        self.setWindowTitle("OWON ULTRA FULL SUITE — Ubuntu Pro Edition")

        # ==================================================
        # ✅ FIXED SIZE AUTO (NO GEOMETRY WARNING)
        # ==================================================
        screen = QApplication.primaryScreen().availableGeometry()

        # Clamp maximum
        w = min(1600, screen.width())
        h = min(900, screen.height())

        self.setFixedSize(w, h)

        # ✅ Disable Maximize Button
        self.setWindowFlags(
            self.windowFlags() &
            ~Qt.WindowType.WindowMaximizeButtonHint
        )

        # ✅ Start Scope Mode
        self.scope_tab.activate()

    # ==================================================
    # ✅ TAB SWITCH HANDLER
    # ==================================================
    def on_tab_changed(self, index):

        # Stop loops
        self.scope_tab.deactivate()
        self.dmm_tab.deactivate()

        # ✅ Scope Tabs
        if index in [0, 1, 2, 3, 4]:
            self.scope_tab.activate()

            if index == 2:
                self.math_tab.refresh()

        # ✅ Multimeter
        elif index == 5:
            self.dmm_tab.activate()

        # ✅ Generator
        elif index == 6:
            self.hw.send(":MODE OSC")
            QThread.msleep(300)
            self.gen_tab.activate()
