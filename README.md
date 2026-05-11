# ✦ 小星助手 XiaoXing Assistant

<div align="center">

**一站式桌面工具 · 课表管理 · 趣味工具 · 小游戏**

![Python](https://img.shields.io/badge/Python-3.10+-8A2BE2)
![PySide6](https://img.shields.io/badge/PySide6-6.6+-6B4FF6)
![Platform](https://img.shields.io/badge/Platform-Windows-4F46E5)
![License](https://img.shields.io/badge/License-MIT-8B5CF6)

</div>

---

## ✨ 功能一览

| 模块 | 功能 | 说明 |
|------|------|------|
| 📚 **课表管理** | 一键获取教务课表 | 自动登录教务系统，DOM 提取课表数据，支持周次切换和 Excel 导出 |
| 🎮 **趣味工具** | 亲戚称呼计算器 | 输入关系链自动推导称呼 |
| | 年龄计算器 | 精确到天，含生肖星座、已活天数 |
| 🎯 **小游戏** | 井字棋 | 对战 AI，支持双人模式 |
| | 猜数字 | AI 选数，范围自由调整 |
| 🔧 **工具箱** | JSON 格式化 / 时间戳转换 | 开发辅助工具 |
| 📝 **记事本** | 笔记管理 | 创建、保存、删除笔记 |
| 📖 **使用说明** | 功能指引 | 完整的操作指南 |
| ⚙️ **设置** | 个性化配置 | 应用信息、数据管理 |

---

## 🚀 快速开始

### 下载即用

从 [Releases](https://github.com/huangxinglin/smart-assistant/releases) 下载 `小星助手.exe`，双击运行即可。

### 从源码运行

```bash
# 克隆仓库
git clone https://github.com/huangxinglin/smart-assistant.git
cd smart-assistant

# 安装依赖
pip install -r requirements.txt

# 安装浏览器驱动（课表获取需要）
playwright install chromium

# 运行
python main.py
```

### 打包为 EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon "assets/app_icon.ico" ^
  --name "小星助手" --add-data "assets;assets" ^
  --add-data "scraper;scraper" --add-data "ui;ui" ^
  --add-data "config;config" --add-data "version.json;." ^
  --hidden-import playwright.async_api ^
  --hidden-import playwright.sync_api ^
  --collect-all playwright main.py
```

---

## 🏗️ 项目结构

```
小星助手/
├── main.py                 # 入口文件
├── ui/                     # UI 界面
│   ├── pages.py            # 课表管理 / 工具箱 / 记事本
│   ├── fun_tools.py        # 趣味工具（亲戚计算器、年龄计算器）
│   ├── games.py            # 小游戏（井字棋、猜数字）
│   ├── help_page.py        # 使用说明
│   ├── settings_page.py    # 设置
│   └── login_screen.py     # 登录（已废弃）
├── scraper/                # 教务系统爬虫
│   ├── course_scraper.py   # 课表爬取与解析
│   └── auto_login.py       # 浏览器自动登录
├── assets/                 # 资源文件
│   ├── app_icon.png        # 应用图标
│   └── style.qss           # 样式文件
├── config/                 # 配置文件
├── version.json            # 版本信息
├── requirements.txt        # Python 依赖
└── README.md               # 本文件
```

---

## 🎨 设计风格

- **配色**：深空蓝紫渐变（`#0d0a20` ~ `#0e0b24`）
- **质感**：毛玻璃半透明卡片 + 紫粉渐变按钮
- **字体**：微软雅黑，支持中英文混排
- **架构**：PySide6 无边框窗口，自定义标题栏与侧边导航

---

## 📊 课表获取原理

```
用户点击"一键获取"
       ↓
Playwright 连接 Edge 调试端口
       ↓
打开教务系统登录页 → 用户在 Edge 中登录
       ↓
导航到课表页面 → 切换到列表视图
       ↓
从 DOM 提取课程数据（不依赖 API）
       ↓
解析展示在课表表格中
```

> 由于教务系统移动端 API 不稳定，本项目采用 **DOM 提取** 方案，确保稳定可靠。

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| PySide6 | 桌面 GUI 框架 |
| Playwright | 浏览器自动化（课表获取） |
| Requests | HTTP 请求（API 备用） |
| openpyxl | Excel 导出 |
| PyInstaller | EXE 打包 |
| Pillow | 图标生成 |

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

**作者**：[星星](https://github.com/huangxinglin)

---

<div align="center">
  <sub>Made with ❤️ by 星星 · 长沙民政职业技术学院 大数据2531班</sub>
  <br>
  <sub>✨ 小星助手 — 你的桌面智能伴侣</sub>
</div>
