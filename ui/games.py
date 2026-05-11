"""
Mini Games - 小游戏
统一深空紫风格 · 井字棋 · 猜数字
"""
import random

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QTabWidget, QSpinBox, QTextEdit
)
from PySide6.QtCore import Qt, QTimer


# ── 样式 ──────────────────────────────────────────────────────

BTN_PRIMARY = """
    QPushButton {{
        padding: {p}; background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 rgba(124,92,250,0.6), stop:1 rgba(200,120,180,0.4));
        color: rgba(196, 176, 255, 0.85); border: none; border-radius: {r};
        font-size: {f}; font-weight: 600;
    }}
    QPushButton:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(134,102,255,0.7), stop:1 rgba(210,130,190,0.5)); }}
"""

BTN_SEC = """
    QPushButton {{
        padding: {p}; background: rgba(167,139,250,0.06);
        border: 1px solid rgba(167,139,250,0.1); border-radius: {r};
        color: rgba(196,176,255,0.5); font-size: {f};
    }}
    QPushButton:hover {{ background: rgba(167,139,250,0.12); color: #c4b0ff; }}
"""

CELL = """
    QPushButton {{
        background: rgba(18, 12, 38, 0.4);
        border: 1px solid rgba(167,139,250,0.06);
        border-radius: {r}; font-size: {f}; font-weight: bold;
    }}
    QPushButton:hover {{
        background: rgba(25, 16, 50, 0.6);
        border: 1px solid rgba(167,139,250,0.15);
    }}
    QPushButton:disabled {{
        background: rgba(18, 12, 38, 0.25);
        border: 1px solid rgba(167,139,250,0.03);
    }}
"""


def _prim(text, p='8px 20px', r='6px', f='13px'):
    btn = QPushButton(text)
    btn.setStyleSheet(BTN_PRIMARY.format(p=p, r=r, f=f))
    btn.setCursor(Qt.PointingHandCursor)
    return btn


def _sec(text, p='5px 14px', r='5px', f='11px'):
    btn = QPushButton(text)
    btn.setStyleSheet(BTN_SEC.format(p=p, r=r, f=f))
    btn.setCursor(Qt.PointingHandCursor)
    return btn


# ═══════════════════════════════════════════════════════════════
# 井字棋
# ═══════════════════════════════════════════════════════════════

class TicTacToe(QWidget):
    def __init__(self):
        super().__init__()
        self.board = [''] * 9
        self.current = 'X'
        self.over = False
        self.vs_ai = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        h = QHBoxLayout()
        title = QLabel('❌ 井字棋')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #f0d060;')
        h.addWidget(title)
        h.addStretch()

        self.mode_btn = _sec('🤖 AI 对战')
        self.mode_btn.setCheckable(True)
        self.mode_btn.setChecked(True)
        self.mode_btn.toggled.connect(lambda c: self._toggle_mode())
        h.addWidget(self.mode_btn)

        reset_btn = _sec('🔄 重开')
        reset_btn.clicked.connect(self._reset)
        h.addWidget(reset_btn)
        layout.addLayout(h)

        # Status
        self.status = QLabel('你的回合 (X)')
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet('font-size: 14px; color: rgba(196,176,255,0.5); padding: 6px;')
        layout.addWidget(self.status)

        # Board
        self.btns = []
        grid = QGridLayout()
        grid.setSpacing(6)
        for i in range(9):
            btn = QPushButton('')
            btn.setFixedSize(72, 72)
            btn.setStyleSheet(CELL.format(r='8px', f='28px'))
            btn.clicked.connect(lambda checked, pos=i: self._move(pos))
            grid.addWidget(btn, i // 3, i % 3)
            self.btns.append(btn)

        gw = QWidget()
        gw.setLayout(grid)
        gw.setFixedSize(240, 240)
        center = QHBoxLayout()
        center.addStretch()
        center.addWidget(gw)
        center.addStretch()
        layout.addLayout(center)

        # Score
        sc = QHBoxLayout()
        sc.setSpacing(16)
        self.sx = QLabel('你 X: 0')
        self.sx.setStyleSheet('color: rgba(46,204,113,0.5); font-size: 12px;')
        sc.addWidget(self.sx)
        self.so = QLabel('AI O: 0')
        self.so.setStyleSheet('color: rgba(231,76,60,0.5); font-size: 12px;')
        sc.addWidget(self.so)
        self.sd = QLabel('平局: 0')
        self.sd.setStyleSheet('color: rgba(167,139,250,0.25); font-size: 12px;')
        sc.addWidget(self.sd)
        sc.addStretch()
        layout.addLayout(sc)

        layout.addStretch()
        self.scores = {'X': 0, 'O': 0, 'draw': 0}

    def _toggle_mode(self):
        self.vs_ai = self.mode_btn.isChecked()
        self.mode_btn.setText('🤖 AI' if self.vs_ai else '👥 双人')
        self._reset()

    def _move(self, pos):
        if self.over or self.board[pos] != '':
            return
        if self.vs_ai and self.current == 'O':
            return

        self.board[pos] = self.current
        self.btns[pos].setText(self.current)

        color = '#2ecc71' if self.current == 'X' else '#e74c3c'
        self.btns[pos].setStyleSheet(f"""
            QPushButton {{ background: rgba({','.join(str(int(c)) for c in [(46,204,113)[::1 if self.current=='X' else -1]])},0.15);
                border: 1px solid {color}33; border-radius: 8px;
                font-size: 28px; font-weight: bold; color: {color}; }}
        """)

        winner = self._check()
        if winner:
            self._win(winner)
            return
        if '' not in self.board:
            self._draw()
            return

        self.current = 'O' if self.current == 'X' else 'X'
        self.status.setText(f'{"AI" if self.vs_ai else "P2"} 回合 (O)' if self.current == 'O' else '你的回合 (X)')

        if self.vs_ai and self.current == 'O':
            QTimer.singleShot(400, self._ai)

    def _ai(self):
        if self.over:
            return
        # Win > block > center > corner > side
        for i in range(9):
            if self.board[i] == '':
                self.board[i] = 'O'
                if self._check() == 'O':
                    self.board[i] = ''
                    return self._move(i)
                self.board[i] = ''
        for i in range(9):
            if self.board[i] == '':
                self.board[i] = 'X'
                if self._check() == 'X':
                    self.board[i] = ''
                    return self._move(i)
                self.board[i] = ''

        for p in [4] if self.board[4] == '' else []:
            self._move(p)
            return
        corners = [i for i in [0, 2, 6, 8] if self.board[i] == '']
        if corners:
            self._move(random.choice(corners))
            return
        sides = [i for i in [1, 3, 5, 7] if self.board[i] == '']
        if sides:
            self._move(random.choice(sides))

    def _check(self):
        for line in [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]:
            if self.board[line[0]] and self.board[line[0]] == self.board[line[1]] == self.board[line[2]]:
                return self.board[line[0]]
        return None

    def _win(self, p):
        self.over = True
        name = '你' if p == 'X' else 'AI'
        self.status.setText(f'{name} 赢了！ 🎉')
        self.scores[p] += 1
        self._update()

    def _draw(self):
        self.over = True
        self.status.setText('平局')
        self.scores['draw'] += 1
        self._update()

    def _update(self):
        self.sx.setText(f'你 X: {self.scores["X"]}')
        self.so.setText(f'AI O: {self.scores["O"]}')
        self.sd.setText(f'平局: {self.scores["draw"]}')

    def _reset(self):
        self.board = [''] * 9
        self.current = 'X'
        self.over = False
        self.status.setText('你的回合 (X)')
        for btn in self.btns:
            btn.setText('')
            btn.setStyleSheet(CELL.format(r='8px', f='28px'))
            btn.setEnabled(True)


# ═══════════════════════════════════════════════════════════════
# 猜数字
# ═══════════════════════════════════════════════════════════════

class GuessNumber(QWidget):
    def __init__(self):
        super().__init__()
        self.target = 0
        self.attempts = 0
        self.active = False
        self.min_v = 1
        self.max_v = 100

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        h = QHBoxLayout()
        title = QLabel('🔢 猜数字')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #f0d060;')
        h.addWidget(title)
        h.addStretch()
        layout.addLayout(h)

        desc = QLabel(f'猜一个 {self.min_v}-{self.max_v} 之间的数字，AI 给你提示')
        desc.setStyleSheet('font-size: 11px; color: rgba(167,139,250,0.25);')
        layout.addWidget(desc)
        layout.addSpacing(8)

        # Range
        range_card = QFrame()
        range_card.setStyleSheet("""
            QFrame { background: rgba(18,12,38,0.25); border: 1px solid rgba(167,139,250,0.04);
                border-radius: 8px; padding: 10px; }
        """)
        rr = QHBoxLayout(range_card)
        rr.addWidget(QLabel('范围'))
        self.min_spin = QSpinBox()
        self.min_spin.setValue(1)
        self.min_spin.setStyleSheet("padding:4px 8px;background:rgba(10,6,24,0.3);border:1px solid rgba(167,139,250,0.06);border-radius:4px;color:#c4b0ff;")
        rr.addWidget(self.min_spin)
        rr.addWidget(QLabel('~'))
        self.max_spin = QSpinBox()
        self.max_spin.setValue(100)
        self.max_spin.setStyleSheet(self.min_spin.styleSheet())
        rr.addWidget(self.max_spin)
        start = _prim('开始游戏', '6px 16px', '6px', '12px')
        start.clicked.connect(self._start)
        rr.addWidget(start)
        rr.addStretch()
        layout.addWidget(range_card)
        layout.addSpacing(8)

        # Hint
        self.hint = QLabel('点击「开始游戏」')
        self.hint.setAlignment(Qt.AlignCenter)
        self.hint.setMinimumHeight(40)
        self.hint.setStyleSheet("""
            font-size: 16px; color: rgba(167,139,250,0.3);
            background: rgba(18,12,38,0.2); border-radius: 8px;
            border: 1px solid rgba(167,139,250,0.03);
        """)
        layout.addWidget(self.hint)
        layout.addSpacing(8)

        # Guess input
        guess_row = QHBoxLayout()
        self.guess_input = QSpinBox()
        self.guess_input.setRange(self.min_v, self.max_v)
        self.guess_input.setEnabled(False)
        self.guess_input.setStyleSheet("""
            QSpinBox { padding: 8px 12px; background: rgba(10,6,24,0.4);
                border: 1px solid rgba(167,139,250,0.08); border-radius: 6px;
                color: #c4b0ff; font-size: 16px; min-width: 80px; }
        """)
        guess_row.addWidget(self.guess_input)

        guess_btn = _prim('🎯 猜', '8px 24px', '8px', '14px')
        guess_btn.clicked.connect(self._guess)
        guess_row.addWidget(guess_btn)
        layout.addLayout(guess_row)

        layout.addSpacing(6)

        # Stats
        self.attempt_label = QLabel('已猜: 0 次')
        self.attempt_label.setStyleSheet('font-size: 12px; color: rgba(167,139,250,0.3);')
        layout.addWidget(self.attempt_label)

        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.history.setMaximumHeight(100)
        self.history.setStyleSheet("""
            QTextEdit { background: rgba(0,0,0,0.15); color: rgba(100,200,100,0.4);
                border: 1px solid rgba(100,200,100,0.04); border-radius: 6px;
                font-size: 11px; padding: 6px; }
        """)
        layout.addWidget(self.history)

        layout.addStretch()

    def _start(self):
        self.min_v = self.min_spin.value()
        self.max_v = self.max_spin.value()
        if self.max_v <= self.min_v:
            self.max_v = self.min_v + 1
            self.max_spin.setValue(self.max_v)

        self.target = random.randint(self.min_v, self.max_v)
        self.attempts = 0
        self.active = True
        self.guess_input.setRange(self.min_v, self.max_v)
        self.guess_input.setEnabled(True)
        self.guess_input.setValue((self.min_v + self.max_v) // 2)
        self.hint.setText(f'猜 {self.min_v}~{self.max_v}')
        self.attempt_label.setText('已猜: 0 次')
        self.history.clear()

    def _guess(self):
        if not self.active:
            self.hint.setText('请先点开始')
            return

        guess = self.guess_input.value()
        self.attempts += 1

        if guess == self.target:
            self.hint.setText('🎉 猜对了！')
            self.history.append(f'第{self.attempts}次: {guess} ✅')
            self.active = False
        elif guess < self.target:
            d = self.target - guess
            h = '大很多' if d > 20 else ('大一些' if d > 10 else '大一点')
            self.hint.setText(f'⬆️ 小了！再{h}')
            self.history.append(f'第{self.attempts}次: {guess} ← 小了')
            self.guess_input.setMinimum(guess + 1)
        else:
            d = guess - self.target
            h = '小很多' if d > 20 else ('小一些' if d > 10 else '小一点')
            self.hint.setText(f'⬇️ 大了！再{h}')
            self.history.append(f'第{self.attempts}次: {guess} → 大了')
            self.guess_input.setMaximum(guess - 1)

        self.attempt_label.setText(f'已猜: {self.attempts} 次')


# ═══════════════════════════════════════════════════════════════
# 主页面
# ═══════════════════════════════════════════════════════════════

class GamesPage(QWidget):
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
        tabs.addTab(TicTacToe(), '❌ 井字棋')
        tabs.addTab(GuessNumber(), '🔢 猜数字')
        layout.addWidget(tabs)
