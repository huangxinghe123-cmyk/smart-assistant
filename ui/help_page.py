"""使用说明页面"""
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt


class HelpPage(QWidget):
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
        title = QLabel('📖 使用说明')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #f0d060;')
        layout.addWidget(title)
        layout.addSpacing(8)

        # 功能卡片
        sections = [
            ('📚 课表管理', '核心功能',
             [
                 ('一键获取', '点击「一键获取课表」，浏览器会自动打开教务系统登录页。登录完成后返回本软件，课表自动加载。'),
                 ('周次切换', '使用周次选择器可查看任意一周的课程安排。'),
                 ('导出 Excel', '点击「导出 Excel」将当前课表保存为表格文件。'),
                 ('高级选项', '如自动登录失败，可手动粘贴 Cookie 或 JSON 数据。'),
             ]),
            ('🎮 趣味工具', '实用小工具',
             [
                 ('亲戚称呼计算器', '输入关系链（如"爸爸的哥哥"），自动推导应该怎么称呼。'),
                 ('年龄计算器', '输入出生日期，精确计算年龄（年/月/天），同时显示生肖、星座、已活天数。'),
             ]),
            ('🎯 小游戏', '轻松一刻',
             [
                 ('井字棋', '经典三连棋，支持对战 AI 和双人对战模式。'),
                 ('猜数字', 'AI 随机选数，你在范围内猜，系统提示大小。'),
             ]),
            ('🔧 工具箱', '开发辅助',
             [
                 ('JSON 格式化', '粘贴 JSON 文本，一键格式化和校验。'),
                 ('时间戳转换', '时间戳 ↔ 日期互相转换。'),
             ]),
            ('📝 记事本', '快速记录',
             [
                 ('写笔记', '支持标题 + 正文，Ctrl+S 保存。'),
                 ('管理笔记', '左侧列表管理所有笔记，支持删除。'),
             ]),
        ]

        for emoji_title, subtitle, steps in sections:
            card = QFrame()
            card.setStyleSheet("""
                QFrame { background: rgba(20,12,40,0.3); border: 1px solid rgba(167,139,250,0.06);
                    border-radius: 12px; padding: 16px; }
            """)
            cl = QVBoxLayout(card)
            cl.setSpacing(8)

            # 标题行
            header = QHBoxLayout()
            t = QLabel(f'{emoji_title}')
            t.setStyleSheet('font-size: 16px; font-weight: bold; color: #c4b0ff;')
            header.addWidget(t)

            sub = QLabel(subtitle)
            sub.setStyleSheet('font-size: 11px; color: rgba(167,139,250,0.3); padding-top: 3px;')
            header.addWidget(sub)
            header.addStretch()
            cl.addLayout(header)

            # 步骤
            for step_title, step_desc in steps:
                step_card = QFrame()
                step_card.setStyleSheet("""
                    QFrame { background: rgba(0,0,0,0.15); border-radius: 8px; padding: 8px 12px; }
                """)
                sl = QVBoxLayout(step_card)
                sl.setSpacing(2)
                sl.setContentsMargins(8, 6, 8, 6)

                st = QLabel(f'▸  {step_title}')
                st.setStyleSheet('font-size: 12px; font-weight: 600; color: rgba(196,176,255,0.7);')
                sl.addWidget(st)

                sd = QLabel(step_desc)
                sd.setWordWrap(True)
                sd.setStyleSheet('font-size: 11px; color: rgba(167,139,250,0.4); line-height: 1.5;')
                sl.addWidget(sd)

                cl.addWidget(step_card)

            layout.addWidget(card)

        # 底部提示
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame { background: rgba(124,92,250,0.06); border: 1px solid rgba(124,92,250,0.1);
                border-radius: 10px; padding: 16px; }
        """)
        fl = QVBoxLayout(footer)
        ft = QLabel('💡 提示')
        ft.setStyleSheet('font-size: 13px; font-weight: bold; color: rgba(196,176,255,0.6);')
        fl.addWidget(ft)
        tips = [
            '课表自动获取需要 Edge 浏览器支持，请确保已安装 Edge',
            '第一次使用课表功能时，可能需要登录教务系统',
            '数据目录在 user_data/，笔记保存在 user_data/notes/',
            '项目开源：github.com/huangxinglin/xiaoxing-assistant',
        ]
        for tip in tips:
            tl = QLabel(f'· {tip}')
            tl.setStyleSheet('font-size: 11px; color: rgba(167,139,250,0.25); padding: 2px 0;')
            fl.addWidget(tl)

        layout.addWidget(footer)
        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
