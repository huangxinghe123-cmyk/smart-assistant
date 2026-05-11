"""
v15 - 简约版（修复PowerShell编码损坏 + 修复JS孤立法}
只做三件事：
1. 打开 Edge -> 用户登录
2. 提取 Cookie（仅 csmzxy.edu.cn 域）
3. 提取当前默认周课表（作为 API 失败的降级方案）
课表获取主逻辑交给 pages.py -> scraper.set_cookies() + fetch_semester()
"""
import asyncio, os, subprocess, traceback
from datetime import datetime
from urllib.parse import quote


class AutoLogin:
    WEB_PAGE = 'https://jwxt.csmzxy.edu.cn/jwglxt/kbcx/xskbcx_cxXskbcxIndex.html?gnmkdm=N253508&layout=default'
    LOGIN_URL = ('https://authserver.csmzxy.edu.cn/authserver/login?service=https%3A%2F%2Fehall.csmzxy.edu.cn'
                 '%2Flogin%3Fservice%3Dhttps%3A%2F%2Fehall.csmzxy.edu.cn%2Fnew%2Findex.html')
    EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

    def __init__(self):
        self.result = {
            'success': False, 'data': None, 'student': {},
            'message': '', 'cookies': '',
        }

    def log(self, msg):
        print(f'  [{datetime.now().strftime("%H:%M:%S")}] {msg}')

    async def _extract_table(self, page) -> list:
        """从列表视图表格提取课程（使用 kblist_table ID 查找）"""
        data = await page.evaluate('''() => {
            const table = document.getElementById("kblist_table");
            if (!table) return null;
            const rows = table.querySelectorAll("tr");
            const courses = [];
            let day = 0;
            const dayMap = {"星期一":1,"星期二":2,"星期三":3,"星期四":4,"星期五":5,"星期六":6,"星期日":7};

            for (let i = 0; i < rows.length; i++) {
                const cells = rows[i].querySelectorAll("td, th");
                if (cells.length === 1) {
                    const t = cells[0].textContent.trim();
                    if (dayMap[t]) { day = dayMap[t]; }
                    continue;
                }
                if (cells.length < 2) continue;
                if (day === 0) continue;

                const periodText = cells[0].textContent.trim();
                const courseText = cells[1].textContent.trim();
                if (periodText === "节次" || courseText === "课表信息") continue;
                if (periodText.length > 10 || courseText.length < 2) continue;

                let name = courseText.replace(/^【.*?】/, "").trim();
                const wi = name.indexOf("周数");
                if (wi > 0) name = name.substring(0, wi).trim();
                if (!name || name.length < 2) continue;

                let weeks = "", loc = "", teacher = "";
                const wm = courseText.match(/周数[：:]([^上]+)/);
                if (wm) weeks = wm[1].trim();
                const lm = courseText.match(/上课地点[：:]([^教]+)/);
                if (lm) loc = lm[1].trim();
                const tm = courseText.match(/教师[：:]([^教]+?)(?:教学班|$)/);
                if (tm) teacher = tm[1].trim();

                courses.push({
                    kcmc: name, xqj: day, jcs: periodText,
                    cdmc: loc, xm: teacher, zcd: weeks
                });
            }
            return courses;
        }''')
        return data if isinstance(data, list) else []

    async def _collect_target_cookies(self, page) -> str:
        """只收集 csmzxy.edu.cn 域名的 Cookie"""
        await asyncio.sleep(2)
        all_cookies = await page.context.cookies()
        target = [c for c in all_cookies if 'csmzxy.edu.cn' in c.get('domain', '')]
        return '; '.join([f"{c['name']}={c['value']}" for c in target])

    async def run(self, username: str, password: str) -> dict:
        self.result = {'success': False, 'data': None, 'student': {}, 'message': '', 'cookies': ''}
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as pw:
                browser = None
                try:
                    browser = await pw.chromium.connect_over_cdp('http://localhost:9222')
                    self.log('已连接 Edge')
                except:
                    if not os.path.exists(self.EDGE_PATH):
                        self.EDGE_PATH = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
                    subprocess.Popen([self.EDGE_PATH, '--remote-debugging-port=9222'], shell=True)
                    for _ in range(12):
                        await asyncio.sleep(1)
                        try:
                            browser = await pw.chromium.connect_over_cdp('http://localhost:9222')
                            break
                        except:
                            pass
                if not browser:
                    self.result['message'] = '无法启动 Edge'
                    return self.result

                ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = await ctx.new_page()

                self.log('打开登录页面，请在 Edge 中登录...')
                await page.goto(self.LOGIN_URL, wait_until='domcontentloaded', timeout=30000)
                for _ in range(240):
                    await asyncio.sleep(0.5)
                    try:
                        if 'authserver/login' not in page.url:
                            self.log('登录完成')
                            break
                    except:
                        pass

                self.log('打开课表页面...')
                try:
                    await page.goto(self.WEB_PAGE, wait_until='domcontentloaded', timeout=30000)
                    await asyncio.sleep(3)
                except:
                    pass

                if '错误提示' in await page.content():
                    self.log('课表页加载失败，尝试SSO...')
                    sso = 'https://authserver.csmzxy.edu.cn/authserver/login?service=' + quote(self.WEB_PAGE, safe='')
                    await page.goto(sso, timeout=30000)
                    await asyncio.sleep(5)
                    await page.goto(self.WEB_PAGE, timeout=30000)
                    await asyncio.sleep(3)

                cookie_str = await self._collect_target_cookies(page)
                self.result['cookies'] = cookie_str
                n = len(cookie_str.split(';')) if cookie_str else 0
                self.log(f'Cookie: {n} 个')

                # 切换到列表视图（网格视图无法解析课表数据）
                self.log('切换到列表视图...')
                try:
                    list_tab = await page.query_selector('a[href="#kblist"]')
                    if list_tab:
                        await list_tab.click()
                        await asyncio.sleep(2)
                        self.log('已切换到列表视图')
                    else:
                        # 尝试点击第二个tab
                        tabs = await page.query_selector_all('.nav-tabs a')
                        for tab in tabs:
                            text = await tab.inner_text()
                            if '列表' in text:
                                await tab.click()
                                await asyncio.sleep(2)
                                self.log('已点击"列表"选项卡')
                                break
                except Exception as e:
                    self.log(f'切换视图时出错: {e}')

                params = await page.evaluate('''() => {
                    const xnm = document.querySelector("[name=xnm]");
                    const xqm = document.querySelector("[name=xqm]");
                    return { xnm: xnm ? xnm.value : "2025", xqm: xqm ? xqm.value : "12" };
                }''')
                self.result['xnm'] = params['xnm']
                self.result['xqm'] = params['xqm']
                self.log(f'学年: {self.result["xnm"]}, 学期: {self.result["xqm"]}')

                courses = await self._extract_table(page)
                if courses:
                    self.result['data'] = {'kbList': courses, 'xsxx': {}}
                    self.result['success'] = True
                    self.log(f'默认周课表: {len(courses)} 门')
                else:
                    if not self.result.get('message'):
                        self.result['message'] = '未能提取到课表数据'

                await browser.close()

        except Exception as e:
            tb = traceback.format_exc()[:300]
            self.result['message'] = f'{type(e).__name__}: {str(e)[:120]}'
            self.log(f'异常: {str(e)[:120]}')
            self.log(f'  {tb}')
        return self.result


def run_auto_login(username: str, password: str) -> dict:
    return asyncio.run(AutoLogin().run(username, password))
