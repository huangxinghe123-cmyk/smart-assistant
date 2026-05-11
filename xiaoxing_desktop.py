"""小星桌面端 v1.0 - 独立个体
连接本地 OpenClaw 网关，提供原生桌面交互体验
安全性：仅连接 127.0.0.1，不发送任何数据到外网
"""
import sys, os, json, subprocess
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSystemTrayIcon, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QIcon, QFont, QAction, QPixmap, QPainter, QColor, QFontDatabase


class TitleBar(QWidget):
    """自定义标题栏 - 小星风格"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(48)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0620, stop:1 #1a1040);
                border-bottom: 1px solid rgba(167, 139, 250, 0.15);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(8)

        # 小星标志
        logo = QLabel('✨')
        logo.setStyleSheet('font-size: 20px;')
        layout.addWidget(logo)

        # 标题
        title = QLabel('小星')
        title.setStyleSheet('''
            font-size: 15px; font-weight: 700;
            color: #c4b0ff; letter-spacing: 2px;
        ''')
        layout.addWidget(title)

        subtitle = QLabel('XiaoXing Assistant')
        subtitle.setStyleSheet('font-size: 10px; color: rgba(167,139,250,0.35);')
        layout.addWidget(subtitle)

        layout.addStretch()

        # 状态指示
        self.status_dot = QLabel('●')
        self.status_dot.setStyleSheet('color: #2ecc71; font-size: 10px;')
        layout.addWidget(self.status_dot)

        self.status_label = QLabel('Online')
        self.status_label.setStyleSheet('color: rgba(46,204,113,0.5); font-size: 10px;')
        layout.addWidget(self.status_label)

        # 窗口按钮
        for btn_text, btn_action, btn_color in [
            ('─', self.parent.showMinimized, '#8899aa'),
            ('□', self._toggle_maximize, '#8899aa'),
            ('✕', self.parent.close, '#e74c3c'),
        ]:
            btn = QPushButton(btn_text)
            btn.setFixedSize(36, 28)
            btn.setStyleSheet(f'''
                QPushButton {{
                    background: transparent; color: {btn_color};
                    border: none; border-radius: 4px;
                    font-size: 13px; font-weight: 600;
                }}
                QPushButton:hover {{
                    background: rgba(167,139,250,0.1);
                    color: {btn_color if btn_text != '✕' else '#ff6b6b'};
                }}
            ''')
            btn.clicked.connect(btn_action)
            layout.addWidget(btn)

    def _toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent._drag_pos = event.globalPosition().toPoint()
            self.parent._dragging = True

    def mouseMoveEvent(self, event):
        if hasattr(self.parent, '_dragging') and self.parent._dragging:
            self.parent.move(self.parent.pos() + event.globalPosition().toPoint() - self.parent._drag_pos)
            self.parent._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.parent._dragging = False


class XiaoxingDesktop(QMainWindow):
    """小星桌面主窗口"""
    def __init__(self):
        super().__init__()
        self._dragging = False
        self._drag_pos = None
        self.gateway_token = 'd2ba50f202d11efd4306bb18368ddede4b12c71c8d9a0d5e'
        self.gateway_url = f'http://127.0.0.1:18789/?token={self.gateway_token}'

        # 窗口设置
        self.setWindowTitle('小星')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(900, 680)
        self.setMinimumSize(600, 400)

        # 居中
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - 900) // 2, (screen.height() - 680) // 2)

        # 主容器
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d0828, stop:1 #181040);
                border: 1px solid rgba(167, 139, 250, 0.12);
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        # 标题栏
        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        # 内容区 - 嵌入式 WebView
        self._setup_webview(layout)

        # 底部状态栏
        status_bar = QWidget()
        status_bar.setFixedHeight(28)
        status_bar.setStyleSheet("background: rgba(0,0,0,0.2); border-radius: 0 0 11px 11px;")
        sl = QHBoxLayout(status_bar)
        sl.setContentsMargins(16, 0, 16, 0)

        ver = QLabel('v1.0 | 主人：星星')
        ver.setStyleSheet('color: rgba(167,139,250,0.25); font-size: 10px;')
        sl.addWidget(ver)
        sl.addStretch()

        self.conn_label = QLabel('● 已连接')
        self.conn_label.setStyleSheet('color: rgba(46,204,113,0.4); font-size: 10px;')
        sl.addWidget(self.conn_label)
        layout.addWidget(status_bar)

        self.setCentralWidget(container)

        # 系统托盘
        self._setup_tray()

        # 连接检查定时器
        self._check_timer = QTimer()
        self._check_timer.timeout.connect(self._check_connection)
        self._check_timer.start(30000)
        self._check_connection()

    def _setup_webview(self, layout):
        """设置嵌入式 WebView（加载本地 OpenClaw 网关）"""
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtWebEngineCore import QWebEngineSettings

            self.webview = QWebEngineView()
            self.webview.setStyleSheet("background: transparent;")

            # 安全设置 - 仅允许本地连接
            settings = self.webview.settings()
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, False)
            settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)

            # 设置透明背景
            self.webview.page().setBackgroundColor(Qt.transparent)

            # 加载本地网关
            self.webview.load(QUrl(self.gateway_url))

            layout.addWidget(self.webview)

        except ImportError:
            # 如果没有 QtWebEngine，显示信息提示
            info = QLabel(
                '小星桌面端\n\n'
                '✨ 连接到本地 AI 服务中...\n\n'
                f'网关地址: {self.gateway_url}\n'
                '请打开浏览器访问该地址与 小星 对话\n\n'
                '提示：安装 PySide6.QtWebEngine 可获得原生桌面体验'
            )
            info.setAlignment(Qt.AlignCenter)
            info.setStyleSheet('''
                font-size: 16px; color: rgba(167,139,250,0.4);
                padding: 40px; line-height: 1.8;
            ''')
            layout.addWidget(info)

    def _setup_tray(self):
        """系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)

        # 生成一个简单的图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor(196, 176, 255))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(8, 8, 48, 48, 12, 12)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Arial', 24, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, '⭐')
        painter.end()

        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip('小星 XiaoXing Assistant')

        tray_menu = QMenu()
        show_action = QAction('显示窗口', self)
        show_action.triggered.connect(self.show_and_raise)
        tray_menu.addAction(show_action)

        hide_action = QAction('隐藏到托盘', self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)

        tray_menu.addSeparator()

        about_action = QAction('关于 小星', self)
        about_action.triggered.connect(self._show_about)
        tray_menu.addAction(about_action)

        quit_action = QAction('退出', self)
        quit_action.triggered.connect(self._do_quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._tray_activated)
        self.tray_icon.show()

    def show_and_raise(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_and_raise()

    def _check_connection(self):
        """检查网关连接状态"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex(('127.0.0.1', 18789))
            s.close()
            if result == 0:
                self.conn_label.setText('● 已连接')
                self.conn_label.setStyleSheet('color: rgba(46,204,113,0.4); font-size: 10px;')
                self.title_bar.status_dot.setStyleSheet('color: #2ecc71; font-size: 10px;')
                self.title_bar.status_label.setText('Online')
            else:
                raise ConnectionError()
        except:
            self.conn_label.setText('○ 未连接')
            self.conn_label.setStyleSheet('color: rgba(231,76,60,0.4); font-size: 10px;')
            self.title_bar.status_dot.setStyleSheet('color: #e74c3c; font-size: 10px;')
            self.title_bar.status_label.setText('Offline')

    def _show_about(self):
        QMessageBox.about(self, '关于 小星',
            '✨ 小星 XiaoXing Assistant v1.0\n\n'
            '主人：星星\n'
            '安全：仅连接 127.0.0.1\n'
            '永不向外部泄露数据\n\n'
            'Powered by OpenClaw')

    def _do_quit(self):
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        """关闭窗口时隐藏到托盘而不是退出"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage('小星', '我还在后台运行，双击托盘图标回来找我 ✨',
                                    QSystemTrayIcon.Information, 2000)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('小星')
    app.setOrganizationName('Xiaoxing')

    # 确保字体
    QFontDatabase.addApplicationFont('C:/Windows/Fonts/msyh.ttc')  # 微软雅黑
    app.setFont(QFont('Microsoft YaHei', 9))

    window = XiaoxingDesktop()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
