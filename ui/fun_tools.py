"""
Fun Tools - 趣味工具
统一设计系统 · 深空紫风格
"""
from datetime import datetime, date
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTabWidget, QLineEdit, QComboBox, QFormLayout,
    QSpinBox, QDateEdit, QScrollArea
)
from PySide6.QtCore import Qt, QDate


# ── 样式常量 ──────────────────────────────────────────────────

INPUT_STYLE = """
    QLineEdit, QSpinBox, QDateEdit, QComboBox {{
        padding: {p};
        background: rgba(10, 6, 24, 0.4);
        border: 1px solid rgba(167, 139, 250, 0.08);
        border-radius: {r};
        color: #c4b0ff;
        font-size: {f};
    }}
    QLineEdit:focus, QSpinBox:focus {{
        border: 1px solid rgba(124, 92, 250, 0.25);
    }}
"""

BTN_PRIMARY = """
    QPushButton {{
        padding: {p};
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(124, 92, 250, 0.65), stop:1 rgba(200, 120, 180, 0.5));
        color: rgba(196, 176, 255, 0.85); border: none; border-radius: {r};
        font-size: {f}; font-weight: 600; letter-spacing: 2px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(134, 102, 255, 0.75), stop:1 rgba(210, 130, 190, 0.6));
    }}
"""

CARD = """
    QFrame {{
        background: rgba(18, 12, 38, 0.3);
        border: 1px solid rgba(167, 139, 250, 0.04);
        border-radius: {r};
        padding: {p};
    }}
"""

TITLE_STYLE = 'font-size: 18px; font-weight: bold; color: #f0d060;'
SUBTITLE_STYLE = 'font-size: 11px; color: rgba(167, 139, 250, 0.35);'
VALUE_HIGHLIGHT = 'font-size: 36px; font-weight: bold; color: #f0d060;'
VALUE_SEC = 'font-size: 13px; color: rgba(196, 176, 255, 0.6);'


def _input_style(p='8px 12px', r='6px', f='13px'):
    return INPUT_STYLE.format(p=p, r=r, f=f)


def _primary_btn(text, p='10px 20px', r='8px', f='14px'):
    btn = QPushButton(text)
    btn.setStyleSheet(BTN_PRIMARY.format(p=p, r=r, f=f))
    btn.setCursor(Qt.PointingHandCursor)
    return btn


def _card(r='10px', p='16px'):
    card = QFrame()
    card.setStyleSheet(CARD.format(r=r, p=p))
    return card


def _info_row(label, widget):
    row = QHBoxLayout()
    lb = QLabel(label)
    lb.setStyleSheet('font-size: 12px; color: rgba(167,139,250,0.3); min-width: 60px;')
    row.addWidget(lb)
    row.addWidget(widget)
    row.addStretch()
    return row


# ═══════════════════════════════════════════════════════════════
# 亲戚称呼计算器
# ═══════════════════════════════════════════════════════════════

class RelativeCalculator(QWidget):
    RELATION_MAP = {
        ('爸爸', '爸爸'): '爷爷', ('爸爸', '妈妈'): '奶奶',
        ('妈妈', '爸爸'): '外公', ('妈妈', '妈妈'): '外婆',
        ('爸爸', '哥哥'): '伯父', ('爸爸', '弟弟'): '叔叔',
        ('爸爸', '姐姐'): '姑妈', ('爸爸', '妹妹'): '姑姑',
        ('妈妈', '哥哥'): '舅舅', ('妈妈', '弟弟'): '舅舅',
        ('妈妈', '姐姐'): '姨妈', ('妈妈', '妹妹'): '小姨',
        ('爸爸', '兄弟的儿子'): '堂哥/堂弟', ('爸爸', '兄弟的女儿'): '堂姐/堂妹',
        ('妈妈', '兄弟的儿子'): '表哥/表弟', ('妈妈', '兄弟的女儿'): '表姐/表妹',
        ('爸爸', '姐妹的儿子'): '表哥/表弟', ('爸爸', '姐妹的女儿'): '表姐/表妹',
        ('妈妈', '姐妹的儿子'): '表哥/表弟', ('妈妈', '姐妹的女儿'): '表姐/表妹',
    }

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        layout.addWidget(self._title('👨‍👩‍👧‍👦 亲戚称呼计算器'))
        layout.addWidget(self._subtitle('输入关系链，自动推导正确称呼'))
        layout.addSpacing(12)

        # 输入区
        input_card = _card('10px', '16px')
        il = QVBoxLayout(input_card)

        # 快速按钮
        quick = QHBoxLayout()
        quick.setSpacing(6)
        for t in ['爸爸的哥哥', '妈妈的弟弟', '爸爸的姐姐', '妈妈的妹妹']:
            btn = QPushButton(t)
            btn.setStyleSheet("""
                QPushButton { padding: 5px 12px; background: rgba(124,92,250,0.08);
                    border: 1px solid rgba(124,92,250,0.1); border-radius: 5px;
                    color: rgba(196,176,255,0.45); font-size: 11px; }
                QPushButton:hover { background: rgba(124,92,250,0.15); color: #c4b0ff; }
            """)
            btn.clicked.connect(lambda checked, x=t: self._quick_fill(x))
            quick.addWidget(btn)
        quick.addStretch()
        il.addLayout(quick)

        il.addSpacing(8)

        # 关系输入
        input_row = QHBoxLayout()
        self.relation_input = QLineEdit()
        self.relation_input.setPlaceholderText('例: 爸爸的哥哥的儿子')
        self.relation_input.setStyleSheet(_input_style('10px 14px', '8px', '14px'))
        input_row.addWidget(self.relation_input, 1)

        calc_btn = _primary_btn('计算', '10px 20px', '8px', '13px')
        calc_btn.clicked.connect(self._calculate)
        input_row.addWidget(calc_btn)
        il.addLayout(input_row)

        layout.addWidget(input_card)
        layout.addSpacing(12)

        # 结果展示
        self.result_label = QLabel('等待输入...')
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setMinimumHeight(60)
        self.result_label.setStyleSheet("""
            font-size: 32px; font-weight: bold; color: rgba(167,139,250,0.25);
            background: rgba(18,12,38,0.25); border-radius: 10px;
            border: 1px solid rgba(167,139,250,0.04); padding: 12px;
        """)
        layout.addWidget(self.result_label)
        layout.addSpacing(8)

        # 参考表
        ref = _card('8px', '12px')
        rl = QVBoxLayout(ref)
        rl.setSpacing(2)
        rl.addWidget(self._subtitle('📋 常用关系参考'))
        ref_lines = [
            '爸爸的爸爸 = 爷爷    爸爸的妈妈 = 奶奶',
            '妈妈的爸爸 = 外公    妈妈的妈妈 = 外婆',
            '爸爸的哥哥 = 伯父    爸爸的弟弟 = 叔叔',
            '爸爸的姐妹 = 姑姑    妈妈的兄弟 = 舅舅',
            '妈妈的姐妹 = 姨妈    堂系 = 爸爸兄弟的孩子',
            '表系 = 爸爸姐妹/妈妈兄弟姐妹的孩子',
        ]
        for line in ref_lines:
            lb = QLabel(line)
            lb.setStyleSheet('font-size: 11px; color: rgba(167,139,250,0.2); padding: 1px 0;')
            rl.addWidget(lb)
        layout.addWidget(ref)
        layout.addStretch()

    def _title(self, text):
        lb = QLabel(text)
        lb.setStyleSheet('font-size: 18px; font-weight: bold; color: #f0d060;')
        return lb

    def _subtitle(self, text):
        lb = QLabel(text)
        lb.setStyleSheet('font-size: 11px; color: rgba(167,139,250,0.25);')
        return lb

    def _quick_fill(self, text):
        self.relation_input.setText(text)
        self._calculate()

    def _calculate(self):
        relation = self.relation_input.text().strip()
        if not relation:
            self.result_label.setText('请输入关系描述')
            self.result_label.setStyleSheet(
                self.result_label.styleSheet().replace('rgba(167,139,250,0.25)', '#e74c3c')
                .replace('32px', '18px'))
            return
        result = self._resolve(relation)
        self.result_label.setText(f'  ➜  {result}')
        self.result_label.setStyleSheet("""
            font-size: 36px; font-weight: bold; color: #f0d060;
            background: rgba(18,12,38,0.25); border-radius: 10px;
            border: 1px solid rgba(167,139,250,0.04); padding: 12px;
        """)

    def _resolve(self, text):
        text = text.replace('的', ' ').strip()
        parts = [p for p in text.split() if p]
        if not parts:
            return '无法识别'
        direct = {'爸爸': '爸爸', '妈妈': '妈妈', '爷爷': '爷爷', '奶奶': '奶奶',
                  '外公': '外公', '外婆': '外婆', '哥哥': '哥哥', '姐姐': '姐姐',
                  '弟弟': '弟弟', '妹妹': '妹妹', '儿子': '儿子', '女儿': '女儿'}
        if len(parts) == 1:
            return direct.get(parts[0], f'"{parts[0]}" 无法识别')
        if len(parts) == 2:
            key = (parts[0], parts[1])
            if key in self.RELATION_MAP:
                return self.RELATION_MAP[key]
            return f'暂时无法计算"{parts[0]}的{parts[1]}"'
        current = parts[0]
        for i in range(1, len(parts)):
            key = (current, parts[i])
            if key in self.RELATION_MAP:
                current = self.RELATION_MAP[key]
            else:
                return f'链式关系暂不支持'
        return current


# ═══════════════════════════════════════════════════════════════
# 年龄计算器
# ═══════════════════════════════════════════════════════════════

class AgeCalculator(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        layout.addWidget(self._title('🎂 年龄计算器'))
        layout.addWidget(self._subtitle('输入出生日期，精确到天'))
        layout.addSpacing(12)

        # 输入
        input_card = _card('10px', '16px')
        fl = QVBoxLayout(input_card)

        date_row = QHBoxLayout()
        self.birth_date = QDateEdit()
        self.birth_date.setDate(QDate(2006, 1, 1))
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setStyleSheet(_input_style('8px 12px', '6px', '14px'))
        self.birth_date.setFixedWidth(160)
        date_row.addWidget(QLabel('出生日期'))
        date_row.addWidget(self.birth_date)
        date_row.addStretch()

        calc_btn = _primary_btn('计算年龄', '8px 24px', '8px', '13px')
        calc_btn.clicked.connect(self._calculate)
        date_row.addWidget(calc_btn)
        fl.addLayout(date_row)
        layout.addWidget(input_card)
        layout.addSpacing(12)

        # 结果
        self.age_result = QLabel('点击"计算年龄"查看结果')
        self.age_result.setAlignment(Qt.AlignCenter)
        self.age_result.setMinimumHeight(70)
        self.age_result.setStyleSheet("""
            font-size: 18px; color: rgba(167,139,250,0.25);
            background: rgba(18,12,38,0.25); border-radius: 10px;
            border: 1px solid rgba(167,139,250,0.04); padding: 12px;
        """)
        layout.addWidget(self.age_result)
        layout.addSpacing(8)

        # 详细信息
        detail_card = _card('10px', '16px')
        self.detail_labels = []
        dl = QVBoxLayout(detail_card)
        dl.setSpacing(4)
        for text in ['年龄', '已活天数', '已活小时', '已活分钟', '下次生日', '生肖', '星座']:
            lb = QLabel(f'{text}: --')
            lb.setStyleSheet('font-size: 12px; color: rgba(167,139,250,0.4); padding: 2px 0;')
            dl.addWidget(lb)
            self.detail_labels.append(lb)
        layout.addWidget(detail_card)
        layout.addStretch()

    def _title(self, text):
        lb = QLabel(text)
        lb.setStyleSheet('font-size: 18px; font-weight: bold; color: #f0d060;')
        return lb

    def _subtitle(self, text):
        lb = QLabel(text)
        lb.setStyleSheet('font-size: 11px; color: rgba(167,139,250,0.25);')
        return lb

    def _calculate(self):
        birth = self.birth_date.date().toPython()
        ref = date.today()

        if birth > ref:
            self.age_result.setText('⚠️ 出生日期不能晚于今天')
            return

        years = ref.year - birth.year
        months = ref.month - birth.month
        days = ref.day - birth.day
        if days < 0:
            months -= 1
            import calendar
            days += calendar.monthrange(ref.year, ref.month - 1 if ref.month > 1 else 12)[0]
        if months < 0:
            years -= 1
            months += 12

        delta = ref - birth
        total_days = delta.days
        total_hours = total_days * 24
        total_minutes = total_hours * 60

        try:
            next_bday = date(ref.year, birth.month, birth.day)
            if next_bday < ref:
                next_bday = date(ref.year + 1, birth.month, birth.day)
            days_to_bday = (next_bday - ref).days
        except:
            days_to_bday = '--'

        self.age_result.setText(
            f'<span style="font-size:42px;font-weight:bold;color:#f0d060;">{years}</span>'
            f'<span style="font-size:16px;color:rgba(167,139,250,0.4);"> 岁 </span>'
            f'<span style="font-size:24px;color:#c4b0ff;">{months}</span>'
            f'<span style="font-size:13px;color:rgba(167,139,250,0.4);"> 个月 </span>'
            f'<span style="font-size:20px;color:#c4b0ff;">{days}</span>'
            f'<span style="font-size:13px;color:rgba(167,139,250,0.4);"> 天</span>'
        )

        zodiac = self._get_zodiac(birth.month, birth.day)
        animal = self._get_animal(birth.year)
        items = [
            f'{years} 岁 {months} 个月 {days} 天',
            f'{total_days:,} 天',
            f'{total_hours:,} 小时',
            f'{total_minutes:,} 分钟',
            f'{days_to_bday} 天后' if isinstance(days_to_bday, int) else '--',
            f'{animal}年',
            f'{zodiac}',
        ]
        for lb, val in zip(self.detail_labels, items):
            lb.setText(val)
            # Highlight values
            parts = lb.text().split(':')
            if len(parts) == 2:
                lb.setText(f'{parts[0]}:  {val}')

    def _get_zodiac(self, m, d):
        for month, day, sign in [(1,20,'摩羯'),(2,19,'水瓶'),(3,21,'双鱼'),
            (4,20,'白羊'),(5,21,'金牛'),(6,22,'双子'),(7,23,'巨蟹'),
            (8,23,'狮子'),(9,23,'处女'),(10,24,'天秤'),(11,23,'天蝎'),(12,22,'射手')]:
            if (m == month and d >= day) or m > month:
                continue
            return sign
        return '摩羯'

    def _get_animal(self, year):
        return ['猴','鸡','狗','猪','鼠','牛','虎','兔','龙','蛇','马','羊'][year % 12]


# ═══════════════════════════════════════════════════════════════
# 主页面
# ═══════════════════════════════════════════════════════════════

class FunToolsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { background: transparent; border: none; }
            QTabBar::tab { color: rgba(167,139,250,0.25); padding: 8px 24px;
                font-size: 12px; min-width: 100px; }
            QTabBar::tab:selected { color: #f0d060; border-bottom: 2px solid #f0d060; }
            QTabBar::tab:hover { color: #c4b0ff; }
        """)
        tabs.addTab(RelativeCalculator(), '👨‍👩‍👧‍👦 亲戚称呼')
        tabs.addTab(AgeCalculator(), '🎂 年龄计算')
        layout.addWidget(tabs)
