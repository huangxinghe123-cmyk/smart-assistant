"""登录界面 - PBKDF2 安全密码 + 强制设置"""
import hashlib, os, base64
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from logger import log_info, log_error


def _hash_password(password: str, salt: bytes = None) -> tuple:
    """PBKDF2 加盐哈希"""
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt, dk


def _encode_hash(salt: bytes, dk: bytes) -> str:
    return base64.b64encode(salt + dk).decode()


def _decode_hash(stored: str) -> tuple:
    raw = base64.b64decode(stored.encode())
    return raw[:16], raw[16:]


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt, expected = _decode_hash(stored)
        _, actual = _hash_password(password, salt)
        return actual == expected
    except Exception:
        return False


class LoginScreen(QWidget):
    login_success = Signal()

    def __init__(self):
        super().__init__()
        self.objectName = 'loginWidget'
        self.config_file = Path('user_data') / 'login.hash'
        self._setup_ui()
        self._check_first_run()

    def _check_first_run(self):
        """首次运行强制设密码"""
        if not self.config_file.exists():
            self.pw_input.setPlaceholderText('设置你的登录密码（至少6位）')
            self.login_btn.setText('设 置 密 码')
            self.hint_label.setText('⚠️ 首次使用，请设置密码')
            self._first_run = True
        else:
            self.pw_input.setPlaceholderText('输入密码...')
            self.login_btn.setText('进 入')
            self.hint_label.setText('')
            self._first_run = False

    def _setup_ui(self):
        bg_paths = [
            Path(__file__).parent.parent / 'assets' / 'anime_bg_3.jpg',
            Path(__file__).parent.parent / 'assets' / 'bg_1.webp',
        ]
        bg_used = None
        for p in bg_paths:
            if p.exists():
                bg_used = str(p)
                break

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QFrame()
        if bg_used:
            container.setStyleSheet(f"""
                QFrame {{
                    background-image: url("{bg_used}");
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                }}
            """)
        else:
            container.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0a0620, stop:1 #1a1040);
                }
            """)

        cl = QHBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)

        overlay = QFrame()
        overlay.setStyleSheet("background: rgba(0,0,0,0.35);")
        ol = QHBoxLayout(overlay)
        ol.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName('loginCard')
        card.setFixedWidth(380)
        card.setStyleSheet("""
            QFrame#loginCard {
                background: rgba(10, 6, 25, 0.78);
                border: 1px solid rgba(167, 139, 250, 0.12);
                border-radius: 20px;
                padding: 30px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)

        logo = QLabel('✦')
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet('font-size: 48px; color: rgba(196, 176, 255, 0.8);')
        layout.addWidget(logo)

        title = QLabel('小星助手')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 28px; font-weight: 800; color: #c4b0ff;')
        layout.addWidget(title)

        subtitle = QLabel('XiaoXing Assistant')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet('font-size: 12px; color: rgba(167, 139, 250, 0.4); letter-spacing: 4px; margin-bottom: 16px;')
        layout.addWidget(subtitle)

        pw_label = QLabel('密码')
        pw_label.setStyleSheet('color: rgba(167, 139, 250, 0.6); font-size: 12px;')
        layout.addWidget(pw_label)

        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.returnPressed.connect(self._handle)
        self.pw_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 1px solid rgba(167, 139, 250, 0.1);
                border-radius: 12px;
                background: rgba(8, 4, 20, 0.5);
                color: #c4b0ff;
                font-size: 14px;
                min-height: 22px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(167, 139, 250, 0.3);
                background: rgba(12, 6, 30, 0.6);
            }
        """)
        layout.addWidget(self.pw_input)

        # 确认密码（首次设置时显示）
        self.confirm_label = QLabel('确认密码')
        self.confirm_label.setStyleSheet('color: rgba(167, 139, 250, 0.6); font-size: 12px;')
        self.confirm_label.setVisible(False)
        layout.addWidget(self.confirm_label)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setVisible(False)
        self.confirm_input.returnPressed.connect(self._handle)
        self.confirm_input.setStyleSheet(self.pw_input.styleSheet())
        layout.addWidget(self.confirm_input)

        self.hint_label = QLabel('')
        self.hint_label.setStyleSheet('color: rgba(255, 100, 120, 0.7); font-size: 12px;')
        self.hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.hint_label)

        layout.addSpacing(6)

        self.login_btn = QPushButton('进 入')
        self.login_btn.clicked.connect(self._handle)
        self.login_btn.setMinimumHeight(42)
        self.login_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(124, 92, 250, 0.8), stop:0.5 rgba(160, 112, 224, 0.7),
                    stop:1 rgba(200, 120, 180, 0.6));
                color: rgba(255,255,255,0.9);
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
                letter-spacing: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(134, 102, 255, 0.9), stop:0.5 rgba(170, 122, 234, 0.8),
                    stop:1 rgba(210, 130, 190, 0.7));
            }
        """)
        layout.addWidget(self.login_btn)

        layout.addSpacing(16)
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet('color: rgba(167, 139, 250, 0.3); font-size: 11px;')
        layout.addWidget(self.status_label)

        ol.addStretch()
        ol.addWidget(card)
        ol.addStretch()
        cl.addWidget(overlay)
        outer.addWidget(container)

    def _handle(self):
        if self._first_run:
            self._setup_password()
        else:
            self._check_password()

    def _setup_password(self):
        pw = self.pw_input.text()
        confirm = self.confirm_input.text()

        if not pw:
            self.hint_label.setText('请输入密码')
            return
        if len(pw) < 6:
            self.hint_label.setText('密码至少6位')
            return

        # 第一次点设置按钮时显示确认框
        if not self.confirm_input.isVisible():
            self.confirm_label.setVisible(True)
            self.confirm_input.setVisible(True)
            self.confirm_input.setFocus()
            self.hint_label.setText('请再次输入密码确认')
            return

        if pw != confirm:
            self.hint_label.setText('两次密码不一致')
            self.confirm_input.clear()
            self.confirm_input.setFocus()
            return

        # 保存
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        salt, dk = _hash_password(pw)
        self.config_file.write_text(_encode_hash(salt, dk), 'utf-8')
        log_info('密码已设置')
        self._first_run = False
        self._check_first_run()
        self.pw_input.clear()
        self.confirm_input.clear()
        self.confirm_label.setVisible(False)
        self.confirm_input.setVisible(False)
        self.hint_label.setText('✅ 密码设置成功，请登录')
        self.hint_label.setStyleSheet('color: rgba(46, 204, 113, 0.7); font-size: 12px;')

    def _check_password(self):
        pw = self.pw_input.text()
        if not self.config_file.exists():
            self.hint_label.setText('配置异常，请联系管理员')
            return

        stored = self.config_file.read_text('utf-8').strip()
        if _verify_password(pw, stored):
            log_info('登录成功')
            # 内存擦除尝试
            self.pw_input.clear()
            self.login_success.emit()
        else:
            self.hint_label.setText('密码错误')
            self.pw_input.clear()
            self.pw_input.setFocus()

    def change_password(self, old_pw: str, new_pw: str) -> bool:
        if not self.config_file.exists():
            return False
        stored = self.config_file.read_text('utf-8').strip()
        if not _verify_password(old_pw, stored):
            return False
        salt, dk = _hash_password(new_pw)
        self.config_file.write_text(_encode_hash(salt, dk), 'utf-8')
        log_info('密码已修改')
        return True
