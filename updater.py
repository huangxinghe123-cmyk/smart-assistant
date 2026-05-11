"""
小星助手自动更新模块
启动时检查版本 → 发现新版 → 提示下载
"""

import json, os, sys, threading
from pathlib import Path
from datetime import datetime

import requests


class UpdateChecker:
    """版本检查与自动更新"""

    def __init__(self):
        self.current_version = '1.0.0'
        self.remote_version = ''
        self.update_url = ''
        self.changelog = ''
        self.has_update = False
        self.app_dir = Path(__file__).parent

        # 读取当前版本
        ver_file = self.app_dir / 'version.json'
        if ver_file.exists():
            try:
                with open(ver_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_version = data.get('version', '1.0.0')
                    self.update_url = data.get('update_url', '')
            except:
                pass

    def check_in_background(self, callback=None):
        """后台检查更新（不阻塞UI）"""
        thread = threading.Thread(target=self._do_check, args=(callback,), daemon=True)
        thread.start()

    def _do_check(self, callback):
        """执行版本检查"""
        result = {'has_update': False, 'current': self.current_version,
                  'latest': '', 'changelog': '', 'error': ''}

        # 检查远程版本
        check_urls = [
            'https://raw.githubusercontent.com/huangxinglin/xiaoxing-assistant/main/version.json',
        ]

        for url in check_urls:
            try:
                resp = requests.get(url, timeout=5, verify=False)
                if resp.status_code == 200:
                    data = resp.json()
                    remote = data.get('version', '')
                    if self._compare_versions(remote, self.current_version) > 0:
                        result['has_update'] = True
                        result['latest'] = remote
                        result['changelog'] = data.get('changelog', '')
                        result['update_url'] = data.get('update_url', '')
                    else:
                        result['latest'] = remote
                    break
            except:
                continue

        if callback:
            callback(result)

    def _compare_versions(self, v1: str, v2: str) -> int:
        """版本比较: 1=v1>v2, -1=v1<v2, 0=相等"""
        try:
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]
            max_len = max(len(parts1), len(parts2))
            parts1 += [0] * (max_len - len(parts1))
            parts2 += [0] * (max_len - len(parts2))
            for a, b in zip(parts1, parts2):
                if a > b: return 1
                if a < b: return -1
            return 0
        except:
            return 0

    def get_update_info(self):
        return {
            'current': self.current_version,
            'latest': self.remote_version,
            'has_update': self.has_update,
            'changelog': self.changelog,
            'update_url': self.update_url,
        }
