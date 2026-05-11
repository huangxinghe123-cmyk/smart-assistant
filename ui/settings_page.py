"""设置页面"""
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGroupBox, QFormLayout, QLineEdit, QMessageBox,
    QSpinBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 标题
        title = QLabel('⚙️ 设置')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #f0d060;')
        layout.addWidget(title)

        desc = QLabel('个性化配置')
        desc.setStyleSheet('font-size: 11px; color: rgba(167,139,250,0.25);')
        layout.addWidget(desc)
        layout.addSpacing(8)

        # ── 通用设置 ──
        general = self._make_group('通用设置', [
            ('默认周次', self._make_spin(1, 20, 11, '课表默认显示的周次')),
            ('启动时检查更新', self._make_checkbox(True, '每次启动时自动检查新版本')),
        ])
        layout.addWidget(general)

        # ── 关于 ──
        about = QGroupBox('关于')
        about.setStyleSheet("""
            QGroupBox { background: rgba(20,12,40,0.4); border: 1px solid rgba(167,139,250,0.08);
                border-radius: 10px; margin-top: 16px; padding: 16px; padding-top: 28px; font-size: 13px;
                color: rgba(167,139,250,0.3); font-weight: normal; }
        """)
        al = QVBoxLayout(about)
        al.setSpacing(6)

        info_items = [
            ('应用名称', '小星助手 XiaoXing Assistant'),
            ('版本', 'v1.0.0'),
            ('作者', '星星'),
            ('开源地址', 'github.com/huangxinglin/xiaoxing-assistant'),
            ('技术栈', 'PySide6 · Playwright · Python 3'),
        ]
        for k, v in info_items:
            row = QHBoxLayout()
            key_lb = QLabel(k)
            key_lb.setStyleSheet('color: rgba(167,139,250,0.3); font-size: 12px; min-width: 80px;')
            row.addWidget(key_lb)
            val_lb = QLabel(v)
            val_lb.setStyleSheet('color: #c4b0ff; font-size: 12px;')
            row.addWidget(val_lb)
            row.addStretch()
            al.addLayout(row)

        al.addSpacing(8)

        # 数据管理
        data_row = QHBoxLayout()
        clear_data_btn = QPushButton('🗑️ 清除本地数据')
        clear_data_btn.setStyleSheet("""
            QPushButton { padding: 6px 14px; background: rgba(231,76,60,0.1);
                border: 1px solid rgba(231,76,60,0.2); border-radius: 6px;
                color: #e74c3c; font-size: 11px; }
            QPushButton:hover { background: rgba(231,76,60,0.2); }
        """)
        clear_data_btn.clicked.connect(self._clear_data)
        data_row.addWidget(clear_data_btn)
        data_row.addStretch()
        al.addLayout(data_row)

        layout.addWidget(about)

        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _make_group(self, title, items):
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox { background: rgba(20,12,40,0.4); border: 1px solid rgba(167,139,250,0.08);
                border-radius: 10px; margin-top: 16px; padding: 16px; padding-top: 28px; font-size: 13px;
                color: rgba(167,139,250,0.3); font-weight: normal; }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        for label, widget in items:
            row = QHBoxLayout()
            lb = QLabel(label)
            lb.setStyleSheet('color: rgba(167,139,250,0.6); font-size: 12px; min-width: 80px;')
            row.addWidget(lb)
            row.addWidget(widget)
            row.addStretch()
            layout.addLayout(row)
        return group

    def _make_spin(self, min_v, max_v, default, desc):
        spin = QSpinBox()
        spin.setRange(min_v, max_v)
        spin.setValue(default)
        spin.setStyleSheet("""
            QSpinBox { padding: 4px 8px; background: rgba(15,10,30,0.4);
                border: 1px solid rgba(167,139,250,0.1); border-radius: 4px;
                color: #c4b0ff; font-size: 12px; min-width: 60px; }
        """)
        return spin

    def _make_checkbox(self, default, desc):
        cb = QCheckBox('')
        cb.setChecked(default)
        cb.setStyleSheet("""
            QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px;
                border: 1px solid rgba(167,139,250,0.2); background: rgba(15,10,30,0.4); }
            QCheckBox::indicator:checked { background: rgba(124,92,250,0.6);
                border: 1px solid rgba(124,92,250,0.3); }
        """)
        return cb

    def _clear_data(self):
        reply = QMessageBox.question(self, '确认', '确定要清除所有本地数据（笔记、缓存等）吗？\n此操作不可撤销。',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            import shutil
            data_dir = Path('user_data')
            if data_dir.exists():
                for item in data_dir.iterdir():
                    if item.is_dir() and item.name != 'notes':
                        shutil.rmtree(item, ignore_errors=True)
                    elif item.is_file():
                        item.unlink()
            QMessageBox.information(self, '完成', '本地数据已清理 ✅')
