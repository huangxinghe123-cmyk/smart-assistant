"""
小星助手 XiaoXing Assistant v1.0
极简美学 · 毛玻璃质感 · 专业级UI
"""
import sys, os
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor

sys.path.insert(0, str(Path(__file__).parent))

from ui.pages import SchedulePage, ToolboxPage, NotepadPage
from ui.fun_tools import FunToolsPage
from ui.games import GamesPage
from ui.settings_page import SettingsPage
from ui.help_page import HelpPage


# ═══════════════════════════════════════════════════════════════
# 全局样式 - 深空渐变 + 毛玻璃
# ═══════════════════════════════════════════════════════════════

GLOBAL_STYLE = """
QWidget {
    font-family: "Microsoft YaHei", "Segoe UI", "PingFang SC", sans-serif;
    color: #c4b0ff;
    background: transparent;
}

/* 主容器 - 深空蓝紫渐变，圆角边框 */
QFrame#mainContainer {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #100d24, stop:0.4 #151232, stop:0.8 #100d28, stop:1 #0c0a1c);
    border-radius: 16px;
    border: 1px solid rgba(167, 139, 250, 0.08);
}

/* 标题栏 - 半透明 */
QFrame#titleBar {
    background: transparent;
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
}

/* 侧边栏 - 深色半透明 */
QFrame#sidebar {
    background: rgba(12, 8, 28, 0.4);
    border-right: 1px solid rgba(167, 139, 250, 0.06);
    border-bottom-left-radius: 16px;
}

/* 侧边栏分隔线 */
QFrame#sidebarDivider {
    background: rgba(167, 139, 250, 0.06);
    max-height: 1px;
    margin: 6px 16px;
}

/* 导航按钮 - 磨砂玻璃效果 */
QPushButton#navBtn {
    text-align: left;
    padding: 10px 14px 10px 18px;
    margin: 1px 10px;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    color: rgba(167, 139, 250, 0.45);
    background: transparent;
}
QPushButton#navBtn:hover {
    background: rgba(120, 90, 240, 0.08);
    color: rgba(196, 176, 255, 0.75);
}
QPushButton#navBtn:checked {
    background: rgba(124, 92, 250, 0.14);
    color: #c4b0ff;
    font-weight: 600;
    border: none;
}
QPushButton#navBtn:pressed {
    background: rgba(124, 92, 250, 0.20);
}

/* 底部按钮（使用说明、设置）同导航，但小一号 */
QPushButton#navBtnBottom {
    text-align: left;
    padding: 8px 14px 8px 18px;
    margin: 0px 10px;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    color: rgba(167, 139, 250, 0.30);
    background: transparent;
}
QPushButton#navBtnBottom:hover {
    background: rgba(120, 90, 240, 0.06);
    color: rgba(167, 139, 250, 0.55);
}
QPushButton#navBtnBottom:checked {
    background: rgba(124, 92, 250, 0.10);
    color: rgba(196, 176, 255, 0.7);
}

/* 窗口按钮 */
QPushButton#winBtn {
    background: transparent;
    border: none;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    color: rgba(167, 139, 250, 0.25);
}
QPushButton#winBtn:hover {
    background: rgba(167, 139, 250, 0.08);
    color: rgba(167, 139, 250, 0.6);
}
QPushButton#winBtn.close:hover {
    background: rgba(255, 70, 70, 0.15);
    color: #ff6b6b;
}

/* 内容区 */
QFrame#contentArea {
    background: rgba(12, 8, 22, 0.6);
    border-bottom-right-radius: 16px;
}

/* 滚动条 */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(167, 139, 250, 0.12);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(167, 139, 250, 0.2);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('小星助手 XiaoXing Assistant')
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet(GLOBAL_STYLE)

        # 构建 UI
        container = QFrame()
        container.setObjectName('mainContainer')

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._build_titlebar(main_layout)
        self._build_content(main_layout)

        self.setCentralWidget(container)
        self._select_first_page()

    # ── 标题栏 ────────────────────────────────────────────────
    def _build_titlebar(self, parent):
        bar = QFrame()
        bar.setObjectName('titleBar')
        bar.setFixedHeight(40)

        h = QHBoxLayout(bar)
        h.setContentsMargins(16, 0, 10, 0)
        h.setSpacing(8)

        # 应用名
        name = QLabel('✦  小星助手')
        name.setStyleSheet('font-size: 13px; font-weight: 700; color: rgba(196,176,255,0.7); letter-spacing: 1px;')
        h.addWidget(name)

        ver = QLabel('v1.0')
        ver.setStyleSheet('font-size: 10px; color: rgba(167,139,250,0.2); padding-top: 2px;')
        h.addWidget(ver)

        h.addStretch()

        # 窗口按钮
        for label, action in [('─', self.showMinimized), ('□', self._toggle_max), ('✕', self.close)]:
            btn = QPushButton(label)
            btn.setObjectName('winBtn')
            btn.setFixedSize(38, 26)
            if label == '✕':
                btn.setProperty('class', 'close')
                btn.setStyleSheet("""
                    QPushButton { background: transparent; border: none; border-radius: 4px;
                        font-size: 12px; font-weight: 600; color: rgba(167,139,250,0.25); }
                    QPushButton:hover { background: rgba(255,70,70,0.15); color: #ff6b6b; }
                """)
            btn.clicked.connect(action)
            h.addWidget(btn)

        parent.addWidget(bar)

    def _toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # ── 主内容区 ──────────────────────────────────────────────
    def _build_content(self, parent):
        content = QWidget()
        h = QHBoxLayout(content)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        self._build_sidebar(h)
        self._build_pages(h)

        parent.addWidget(content, 1)

    def _build_sidebar(self, parent):
        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(200)

        v = QVBoxLayout(sidebar)
        v.setContentsMargins(0, 12, 0, 10)
        v.setSpacing(2)

        # Logo 区域
        logo_frame = QFrame()
        lf = QHBoxLayout(logo_frame)
        lf.setContentsMargins(20, 8, 20, 12)

        logo = QLabel('✦')
        logo.setStyleSheet('font-size: 26px; color: rgba(196,176,255,0.45);')
        lf.addWidget(logo)

        title = QLabel('小星助手')
        title.setStyleSheet('font-size: 15px; font-weight: 700; color: rgba(196,176,255,0.55); letter-spacing: 1px; margin-left: 4px;')
        lf.addWidget(title)
        lf.addStretch()
        v.addWidget(logo_frame)

        # 分隔线
        div = QFrame()
        div.setObjectName('sidebarDivider')
        v.addWidget(div)

        v.addSpacing(4)

        # 主导航
        self.nav_btns = []
        self.pages = {}

        nav_main = [
            ('📚', '课表管理', SchedulePage()),
            ('🎮', '趣味工具', FunToolsPage()),
            ('🎯', '小游戏', GamesPage()),
            ('🔧', '工具箱', ToolboxPage()),
            ('📝', '记事本', NotepadPage()),
        ]

        for icon, name, page in nav_main:
            btn = QPushButton(f'  {icon}  {name}')
            btn.setObjectName('navBtn')
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, n=name: self._switch_page(n))
            v.addWidget(btn)
            self.nav_btns.append(btn)
            self.pages[name] = page

        v.addStretch()

        # 分隔线
        div2 = QFrame()
        div2.setObjectName('sidebarDivider')
        v.addWidget(div2)
        v.addSpacing(2)

        # 底部导航
        nav_bottom = [
            ('📖', '使用说明', HelpPage()),
            ('⚙️', '设置', SettingsPage()),
        ]
        for icon, name, page in nav_bottom:
            btn = QPushButton(f'  {icon}  {name}')
            btn.setObjectName('navBtn')
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(34)
            btn.setStyleSheet("""
                QPushButton { text-align: left; padding: 8px 14px 8px 18px;
                    margin: 0px 10px; border: none; border-radius: 6px;
                    font-size: 12px; color: rgba(167,139,250,0.30);
                    background: transparent; }
                QPushButton:hover { background: rgba(120,90,240,0.06);
                    color: rgba(167,139,250,0.55); }
                QPushButton:checked { background: rgba(124,92,250,0.10);
                    color: rgba(196,176,255,0.7); }
            """)
            btn.clicked.connect(lambda checked, n=name: self._switch_page(n))
            v.addWidget(btn)
            self.nav_btns.append(btn)
            self.pages[name] = page

        parent.addWidget(sidebar)

    def _build_pages(self, parent):
        self.stack = QStackedWidget()
        self.stack.setObjectName('contentArea')
        for name in self.pages:
            self.stack.addWidget(self.pages[name])
        parent.addWidget(self.stack, 1)

    def _select_first_page(self):
        if self.nav_btns:
            self.nav_btns[0].setChecked(True)

    def _switch_page(self, name):
        if name not in self.pages:
            return
        idx = list(self.pages.keys()).index(name)
        self.stack.setCurrentIndex(idx)
        for btn in self.nav_btns:
            btn.setChecked(False)
        if idx < len(self.nav_btns):
            self.nav_btns[idx].setChecked(True)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('小星助手')

    font = QFont('Microsoft YaHei', 9)
    app.setFont(font)

    icon_path = Path(__file__).parent / 'assets' / 'app_icon.png'
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    Path('user_data/notes').mkdir(parents=True, exist_ok=True)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
