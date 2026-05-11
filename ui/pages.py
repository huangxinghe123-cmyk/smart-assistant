"""
Pages - 统一设计系统
课表管理 · 工具箱 · 记事本
"""
import json, time, os
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit,
    QPlainTextEdit, QMessageBox, QFileDialog, QTabWidget,
    QHeaderView, QSpinBox, QScrollArea, QListWidget, QListWidgetItem,
    QSplitter
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QColor

from scraper.course_scraper import CourseScraper

# ── 统一样式工具 ──────────────────────────────────────────────

CARD = """
    QFrame {{
        background: rgba(18, 12, 38, 0.45);
        border: 1px solid rgba(167, 139, 250, 0.06);
        border-radius: 10px;
        padding: {padding};
    }}
"""

BTN_PRIMARY = """
    QPushButton {{
        padding: {padding};
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(124, 92, 250, 0.7), stop:1 rgba(200, 120, 180, 0.5));
        color: rgba(196, 176, 255, 0.85); border: none; border-radius: {radius};
        font-size: {font_size}; font-weight: 600; letter-spacing: 2px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(134, 102, 255, 0.8), stop:1 rgba(210, 130, 190, 0.6));
    }}
    QPushButton:disabled {{
        background: rgba(167, 139, 250, 0.1);
        color: rgba(167, 139, 250, 0.2);
    }}
"""

BTN_SECONDARY = """
    QPushButton {{
        padding: {padding};
        background: rgba(167, 139, 250, 0.06);
        border: 1px solid rgba(167, 139, 250, 0.1);
        border-radius: {radius};
        color: rgba(196, 176, 255, 0.6);
        font-size: {font_size};
    }}
    QPushButton:hover {{
        background: rgba(167, 139, 250, 0.12);
        border: 1px solid rgba(167, 139, 250, 0.2);
    }}
    QPushButton:disabled {{
        color: rgba(167, 139, 250, 0.15);
    }}
"""

INPUT_STYLE = """
    QLineEdit, QSpinBox, QPlainTextEdit {{
        padding: {padding};
        background: rgba(10, 6, 24, 0.4);
        border: 1px solid rgba(167, 139, 250, 0.08);
        border-radius: {radius};
        color: #c4b0ff;
        font-size: {font_size};
    }}
    QLineEdit:focus, QSpinBox:focus, QPlainTextEdit:focus {{
        border: 1px solid rgba(124, 92, 250, 0.25);
    }}
"""

TITLE_STYLE = 'font-size: 20px; font-weight: bold; color: #f0d060;'
SUBTITLE_STYLE = 'font-size: 12px; color: rgba(167, 139, 250, 0.4);'


def section_title(text):
    lb = QLabel(text)
    lb.setStyleSheet(TITLE_STYLE)
    return lb


def section_subtitle(text):
    lb = QLabel(text)
    lb.setStyleSheet(SUBTITLE_STYLE)
    return lb


def make_card(padding='16px'):
    card = QFrame()
    card.setStyleSheet(CARD.format(padding=padding))
    return card


def make_primary_btn(text, padding='10px 20px', radius='8px', font_size='14px'):
    btn = QPushButton(text)
    btn.setStyleSheet(BTN_PRIMARY.format(padding=padding, radius=radius, font_size=font_size))
    return btn


def make_secondary_btn(text, padding='8px 16px', radius='6px', font_size='12px'):
    btn = QPushButton(text)
    btn.setStyleSheet(BTN_SECONDARY.format(padding=padding, radius=radius, font_size=font_size))
    return btn


# ═══════════════════════════════════════════════════════════════
# Schedule Page
# ═══════════════════════════════════════════════════════════════

class SchedulePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scraper = CourseScraper()
        self.current_courses = []
        self.notes_dir = Path('user_data') / 'notes'
        self.notes_dir.mkdir(parents=True, exist_ok=True)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        header.addWidget(section_title('📚 课表管理'))
        header.addStretch()
        self.status_label = QLabel('就绪')
        self.status_label.setStyleSheet('font-size: 12px; color: rgba(167,139,250,0.25); padding-right: 4px;')
        header.addWidget(self.status_label)
        main_layout.addLayout(header)
        main_layout.addWidget(section_subtitle('一键获取教务系统课表，支持周次切换和导出'))
        main_layout.addSpacing(8)

        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame { background: rgba(18, 12, 38, 0.35); border: 1px solid rgba(167,139,250,0.05);
                border-radius: 10px; padding: 12px; }
        """)
        tb = QHBoxLayout(toolbar)
        tb.setSpacing(10)

        self.auto_btn = make_primary_btn('⟳ 一键获取课表', '10px 24px', '8px', '13px')
        self.auto_btn.clicked.connect(self._on_auto_login)
        tb.addWidget(self.auto_btn)

        tb.addSpacing(8)

        tb.addWidget(QLabel('周次'))
        self.week_spin = QSpinBox()
        self.week_spin.setRange(1, 20)
        self.week_spin.setValue(11)
        self.week_spin.valueChanged.connect(self._on_week_changed)
        self.week_spin.setStyleSheet(INPUT_STYLE.format(padding='4px 8px', radius='6px', font_size='13px'))
        self.week_spin.setFixedWidth(60)
        tb.addWidget(self.week_spin)
        self.week_status = QLabel('第11周')
        self.week_status.setStyleSheet('font-size: 12px; color: rgba(167,139,250,0.4);')
        tb.addWidget(self.week_status)

        tb.addStretch()

        self.export_btn = make_secondary_btn('📥 导出 Excel')
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self._export_excel)
        tb.addWidget(self.export_btn)

        adv_btn = make_secondary_btn('⚙️ 高级')
        adv_btn.clicked.connect(self._toggle_advanced)
        tb.addWidget(adv_btn)

        main_layout.addWidget(toolbar)

        # Debug log
        self.debug_log = QPlainTextEdit()
        self.debug_log.setMaximumHeight(90)
        self.debug_log.setReadOnly(True)
        self.debug_log.setStyleSheet("""
            QPlainTextEdit { background: rgba(0,0,0,0.2); color: rgba(100,200,100,0.5);
                border: 1px solid rgba(100,200,100,0.06); border-radius: 6px;
                font-size: 11px; padding: 8px; }
        """)
        debug_card = make_card('8px')
        dl = QVBoxLayout(debug_card)
        dl.setContentsMargins(0, 0, 0, 0)
        dl.addWidget(QLabel('日志'))
        dl.addWidget(self.debug_log)
        main_layout.addWidget(debug_card)

        # Course table
        self.table = QTableWidget(12, 7)
        self.table.setHorizontalHeaderLabels(['周一', '周二', '周三', '周四', '周五', '周六', '周日'])
        self.table.setVerticalHeaderLabels([
            '08:00\n1', '08:55\n2', '10:00\n3', '10:55\n4',
            '14:00\n5', '14:55\n6', '16:00\n7', '16:55\n8',
            '19:00\n9', '19:55\n10', '20:50\n11', '实践'
        ])
        self.table.setStyleSheet("""
            QTableWidget { background: rgba(18, 12, 38, 0.3); border: 1px solid rgba(167,139,250,0.05);
                border-radius: 8px; gridline-color: rgba(167,139,250,0.04); }
            QTableWidget::item { padding: 4px; }
            QHeaderView::section { background: rgba(10, 6, 24, 0.4); color: rgba(167,139,250,0.25);
                border: none; border-bottom: 1px solid rgba(167,139,250,0.04);
                font-size: 11px; padding: 4px; font-weight: normal; }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(58)
        self.table.setMinimumHeight(400)

        for r in range(12):
            for c in range(7):
                item = QTableWidgetItem('')
                item.setBackground(QColor(14, 10, 30, 180))
                item.setForeground(QColor(128, 144, 160, 100))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)

        table_card = make_card('4px')
        tcl = QVBoxLayout(table_card)
        tcl.setContentsMargins(0, 0, 0, 0)
        tcl.addWidget(self.table)
        main_layout.addWidget(table_card)

        # Advanced card
        self.adv_card = QFrame()
        self.adv_card.setVisible(False)
        self.adv_card.setStyleSheet("""
            QFrame { background: rgba(18, 12, 38, 0.35); border: 1px solid rgba(167,139,250,0.05);
                border-radius: 10px; padding: 16px; }
        """)
        al = QVBoxLayout(self.adv_card)
        al.addWidget(QLabel('Cookie 字符串'))
        self.cookie_input = QPlainTextEdit()
        self.cookie_input.setMaximumHeight(70)
        self.cookie_input.setStyleSheet(INPUT_STYLE.format(padding='6px 10px', radius='6px', font_size='11px'))
        al.addWidget(self.cookie_input)
        cookie_btn = make_secondary_btn('📋 设置 Cookie')
        cookie_btn.clicked.connect(self._set_cookie)
        al.addWidget(cookie_btn)
        main_layout.addWidget(self.adv_card)

        main_layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def log(self, msg):
        self.debug_log.appendPlainText(str(msg))

    def _toggle_advanced(self):
        self.adv_card.setVisible(not self.adv_card.isVisible())

    def _on_auto_login(self):
        self.auto_btn.setEnabled(False)
        self.auto_btn.setText('⏳ 正在获取...')
        QTimer.singleShot(100, self._do_auto_login)

    def _do_auto_login(self):
        try:
            from scraper.auto_login import run_auto_login
            result = run_auto_login('', '')

            if result['success']:
                cookie_str = result.get('cookies', '')
                self.log('✅ 登录成功')

                if cookie_str:
                    self.cookie_input.setPlainText(cookie_str)
                    xnm = result.get('xnm', '2025')
                    xqm = result.get('xqm', '12')
                    self.scraper.API_PARAMS['xnm'] = xnm
                    self.scraper.API_PARAMS['xqm'] = xqm

                    api_ok = self.scraper.set_cookies(cookie_str)
                    for line in self.scraper.get_debug_info():
                        self.log(f'  {line}')

                    if api_ok:
                        courses = self.scraper.fetch_semester()
                        self.log(f'📡 API: {len(courses)} 门')
                    else:
                        self.log('⚠️ API 不可用，使用页面数据')
                        default_data = result.get('data', {})
                        if default_data and default_data.get('kbList'):
                            self.scraper.import_from_json(json.dumps(default_data))
                            courses = self.scraper.fetch_schedule()
                            self.log(f'📄 页面: {len(courses)} 门')
                        else:
                            courses = []
                            self.log('❌ 无课表数据')
                else:
                    default_data = result.get('data', {})
                    courses = self.scraper.fetch_schedule() if default_data and default_data.get('kbList') and self.scraper.import_from_json(json.dumps(default_data)) else []

                self.current_courses = courses
                self._display_courses(courses)
                self.export_btn.setEnabled(bool(courses))
                self.week_spin.blockSignals(True)
                self.week_spin.setValue(11)
                self.week_spin.blockSignals(False)
                self.week_status.setText('第11周')
                self.status_label.setText(f'✓ {len(courses)} 门课程')
            else:
                err = result.get('message', '登录失败')
                self.log(f'❌ {err}')
                self.status_label.setText('⚠️ 登录失败')
                self.adv_card.setVisible(True)
        except Exception as e:
            self.log(f'❌ 错误: {str(e)[:80]}')
            self.status_label.setText('⚠️ 出错了')
        finally:
            self.auto_btn.setEnabled(True)
            self.auto_btn.setText('⟳ 一键获取课表')

    def _display_courses(self, courses):
        for r in range(12):
            for c in range(7):
                item = self.table.item(r, c)
                if item:
                    item.setText('')
                    item.setBackground(QColor(14, 10, 30, 180))

        if not courses:
            return

        grid = {}
        for course in courses:
            wd = course.get('weekday', 0)
            pr = course.get('period', 0)
            key = (wd, pr)
            if key not in grid:
                grid[key] = []
            grid[key].append(course)

        for (weekday, period), cls_list in grid.items():
            if not (1 <= weekday <= 7):
                continue
            row_idx = period - 1 if 1 <= period <= 11 else 11
            course = cls_list[0]
            parts = [course.get('name', '')[:14]]
            if course.get('teacher'):
                parts.append(f'👤 {course["teacher"][:8]}')
            if course.get('location'):
                parts.append(f'📍 {course["location"][:10]}')

            item = self.table.item(row_idx, weekday - 1)
            if item:
                text = '\n'.join(parts)
                if item.text():
                    item.setText(item.text() + '\n───\n' + text)
                else:
                    item.setText(text)
                item.setBackground(QColor(58, 123, 213, 30))
                item.setForeground(QColor(160, 140, 200))
                item.setTextAlignment(Qt.AlignCenter)

    def _on_week_changed(self, week):
        self.week_status.setText(f'第{week}周')
        courses = self.scraper.fetch_schedule(week=week)
        self._display_courses(courses)

    def _export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, '保存课表', 'schedule.xlsx', 'Excel (*.xlsx)')
        if path:
            try:
                self.scraper.export_to_excel(self.current_courses, path)
                QMessageBox.information(self, '完成', f'已保存到 {path}')
            except Exception as e:
                QMessageBox.warning(self, '错误', str(e))

    def _set_cookie(self):
        cookie_str = self.cookie_input.toPlainText().strip()
        if not cookie_str:
            return
        self.log('📋 设置 Cookie...')
        ok = self.scraper.set_cookies(cookie_str)
        for line in self.scraper.get_debug_info():
            self.log(f'  {line}')
        if ok:
            courses = self.scraper.fetch_semester()
            self.current_courses = courses
            self._display_courses(courses)
            self.log(f'✅ Cookie 有效: {len(courses)} 门')
        else:
            self.log('❌ Cookie 无效')


# ═══════════════════════════════════════════════════════════════
# Toolbox Page
# ═══════════════════════════════════════════════════════════════

class ToolboxPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(section_title('🔧 工具箱'))
        layout.addWidget(section_subtitle('JSON 格式化、时间戳转换等开发辅助工具'))
        layout.addSpacing(12)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { background: rgba(18,12,38,0.35); border: 1px solid rgba(167,139,250,0.05);
                border-radius: 8px; border-top-left-radius: 0; padding: 12px; }
            QTabBar::tab { color: rgba(167,139,250,0.4); padding: 8px 24px;
                font-size: 12px; min-width: 80px; border: none; }
            QTabBar::tab:selected { color: #f0d060; border-bottom: 2px solid #f0d060; padding-bottom: 6px; }
            QTabBar::tab:hover { color: #c4b0ff; }
        """)

        # JSON
        json_tab = QWidget()
        jl = QVBoxLayout(json_tab)
        jl.addWidget(QLabel('输入 JSON'))
        self.json_input = QPlainTextEdit()
        self.json_input.setStyleSheet(INPUT_STYLE.format(padding='8px 12px', radius='6px', font_size='12px'))
        self.json_input.setMinimumHeight(120)
        jl.addWidget(self.json_input)
        jbtn = make_primary_btn('格式化 JSON', '8px 20px', '6px', '12px')
        jbtn.clicked.connect(self._format_json)
        jl.addWidget(jbtn)
        jl.addWidget(QLabel('输出'))
        self.json_output = QPlainTextEdit()
        self.json_output.setReadOnly(True)
        self.json_output.setStyleSheet(INPUT_STYLE.format(padding='8px 12px', radius='6px', font_size='12px'))
        jl.addWidget(self.json_output)
        tabs.addTab(json_tab, 'JSON')

        # Timestamp
        ts_tab = QWidget()
        tl = QVBoxLayout(ts_tab)
        tl.addWidget(QLabel('输入时间戳或日期 (YYYY-MM-DD)'))
        self.ts_input = QLineEdit()
        self.ts_input.setPlaceholderText('例如: 1746937200 或 2026-05-11')
        self.ts_input.setStyleSheet(INPUT_STYLE.format(padding='8px 12px', radius='6px', font_size='13px'))
        tl.addWidget(self.ts_input)
        tbtn = make_primary_btn('转换', '8px 20px', '6px', '12px')
        tbtn.clicked.connect(self._convert_ts)
        tl.addWidget(tbtn)
        tl.addWidget(QLabel('结果'))
        self.ts_output = QPlainTextEdit()
        self.ts_output.setReadOnly(True)
        self.ts_output.setMinimumHeight(100)
        self.ts_output.setStyleSheet("""
            QPlainTextEdit { background: rgba(10,6,24,0.3); color: #88cc88;
                border: 1px solid rgba(100,200,100,0.06); border-radius: 6px;
                font-size: 12px; padding: 10px; }
        """)
        tl.addWidget(self.ts_output)
        tabs.addTab(ts_tab, '时间戳')

        layout.addWidget(tabs)
        layout.addStretch()

    def _format_json(self):
        text = self.json_input.toPlainText().strip()
        if not text:
            return
        try:
            data = json.loads(text)
            self.json_output.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            self.json_output.setPlainText('❌ JSON 格式错误')

    def _convert_ts(self):
        text = self.ts_input.text().strip()
        if not text:
            return
        try:
            ts = int(text)
            if ts > 1e12:
                ts /= 1000
            dt = datetime.fromtimestamp(ts)
            self.ts_output.setPlainText(
                f'📍 本地时间: {dt.strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'🌐 UTC 时间: {dt.strftime("%Y-%m-%d %H:%M:%S")} UTC\n'
                f'🔢 时间戳:   {int(ts)}'
            )
        except ValueError:
            try:
                dt = datetime.strptime(text, '%Y-%m-%d')
                self.ts_output.setPlainText(f'🔢 时间戳: {int(dt.timestamp())}')
            except:
                self.ts_output.setPlainText('❌ 输入无效，请输入时间戳或 YYYY-MM-DD 格式日期')


# ═══════════════════════════════════════════════════════════════
# Notepad Page
# ═══════════════════════════════════════════════════════════════

class NotepadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notes_dir = Path('user_data') / 'notes'
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.current_file = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(section_title('📝 记事本'))
        layout.addWidget(section_subtitle('快速记录灵感随笔'))
        layout.addSpacing(12)

        # 主内容区
        splitter = QSplitter(Qt.Horizontal)

        # 左侧笔记列表
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame { background: rgba(18, 12, 38, 0.35); border: 1px solid rgba(167,139,250,0.05);
                border-radius: 8px; padding: 8px; }
        """)
        ll = QVBoxLayout(left_panel)
        ll.setContentsMargins(8, 8, 8, 8)
        ll.addWidget(QLabel('📂 笔记列表'))
        self.note_list = QListWidget()
        self.note_list.setStyleSheet("""
            QListWidget { background: transparent; border: none; color: rgba(196,176,255,0.5);
                font-size: 12px; outline: none; }
            QListWidget::item { padding: 8px 10px; border-radius: 4px; }
            QListWidget::item:selected { background: rgba(124,92,250,0.12); color: #c4b0ff; }
            QListWidget::item:hover { background: rgba(167,139,250,0.04); }
        """)
        self.note_list.itemClicked.connect(self._load_note)
        ll.addWidget(self.note_list)

        new_btn = make_secondary_btn('+ 新建笔记', '8px 16px', '6px', '12px')
        new_btn.clicked.connect(self._new_note)
        ll.addWidget(new_btn)

        del_btn = make_secondary_btn('🗑️ 删除', '8px 16px', '6px', '12px')
        del_btn.clicked.connect(self._delete_note)
        ll.addWidget(del_btn)

        splitter.addWidget(left_panel)

        # 右侧编辑器
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame { background: rgba(18, 12, 38, 0.2); border: 1px solid rgba(167,139,250,0.03);
                border-radius: 8px; padding: 12px; }
        """)
        rl = QVBoxLayout(right_panel)
        rl.setContentsMargins(12, 12, 12, 12)

        self.note_title = QLineEdit()
        self.note_title.setPlaceholderText('笔记标题...')
        self.note_title.setStyleSheet(INPUT_STYLE.format(padding='8px 12px', radius='6px', font_size='15px'))
        rl.addWidget(self.note_title)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText('写下你的想法…\n\nCtrl+S 保存')
        self.editor.setStyleSheet("""
            QPlainTextEdit { background: rgba(10,6,24,0.2); border: 1px solid rgba(167,139,250,0.04);
                border-radius: 6px; color: #c4b0ff; font-size: 13px; padding: 12px; }
        """)
        rl.addWidget(self.editor, 1)

        save_btn = make_primary_btn('💾 保存 (Ctrl+S)', '8px 20px', '6px', '12px')
        save_btn.clicked.connect(self._save_note)
        rl.addWidget(save_btn)

        splitter.addWidget(right_panel)
        splitter.setSizes([200, 500])

        layout.addWidget(splitter)

        self._refresh_list()
        self._new_note()

    def _refresh_list(self):
        self.note_list.clear()
        for f in sorted(self.notes_dir.glob('*.txt'), reverse=True):
            self.note_list.addItem(f.stem)

    def _new_note(self):
        self.current_file = None
        self.note_title.clear()
        self.editor.clear()
        self.note_title.setFocus()

    def _save_note(self):
        title = self.note_title.text().strip()
        content = self.editor.toPlainText()
        if not title:
            title = '未命名笔记'
            self.note_title.setText(title)
        path = self.notes_dir / f'{title}.txt'
        path.write_text(content, 'utf-8')
        self.current_file = path
        self._refresh_list()
        self.status_label.setText(f'✅ 已保存')

    def _load_note(self, item):
        title = item.text()
        path = self.notes_dir / f'{title}.txt'
        if path.exists():
            self.note_title.setText(title)
            self.editor.setPlainText(path.read_text('utf-8'))
            self.current_file = path

    def _delete_note(self):
        current = self.note_list.currentItem()
        if not current:
            return
        reply = QMessageBox.question(self, '确认', f'删除笔记「{current.text()}」？',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            path = self.notes_dir / f'{current.text()}.txt'
            if path.exists():
                path.unlink()
            self._refresh_list()
            self._new_note()
