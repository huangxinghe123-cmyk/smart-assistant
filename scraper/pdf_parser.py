"""PDF课表解析器 v7 - 修复标题行污染和节次偏移"""
import re
import pdfplumber


def parse_course_pdf(pdf_path: str) -> list:
    with pdfplumber.open(pdf_path) as pdf:
        all_courses = []
        day_map = {'星期一': 1, '星期二': 2, '星期三': 3, '星期四': 4,
                   '星期五': 5, '星期六': 6, '星期日': 7}
        skip_names = ['学年第', '学期学号', '课程性质', '课程学时组成',
                      '周学时', '重修标记', '虚拟仿真', '讲课',
                      '上机', '课外', '打印时间', '学号']

        for page in pdf.pages:
            words = page.extract_words(keep_blank_chars=True, x_tolerance=2)

            # 找星期列位置
            day_cols = {}
            for w in words:
                for cn, num in day_map.items():
                    if cn in w['text']:
                        day_cols[num] = w['x0']
                        break
            if not day_cols:
                continue

            # 中点列边界
            sd = sorted(day_cols.keys())
            cols = {}
            for i, d in enumerate(sd):
                x0 = 0 if i == 0 else (day_cols[d] + day_cols[sd[i-1]]) / 2
                x1 = 9999 if i+1 >= len(sd) else (day_cols[d] + day_cols[sd[i+1]]) / 2
                cols[d] = (x0, x1)

            # 按y分组，忽略标题行(y<70)
            rows = {}
            for w in words:
                if w['text'] in ['上午', '下午', '晚上']:
                    continue
                if w['top'] < 70:  # 忽略标题行
                    continue
                yk = int(w['top'] / 4) * 4
                rows.setdefault(yk, []).append(w)

            cur_period = '1'
            cells = {}

            for y in sorted(rows):
                ws = sorted(rows[y], key=lambda w: w['x0'])
                first = ws[0]['text']
                # 节次标记
                if first in [str(n) for n in range(1, 11)] and len(ws) < 4:
                    cur_period = first
                    continue
                for w in ws:
                    cx = (w['x0'] + w['x1']) / 2
                    for d, (x0, x1) in cols.items():
                        if x0 <= cx <= x1:
                            cells.setdefault((cur_period, d), []).append(w['text'])
                            break

            # 解析每个单元格
            for (period, day), text_list in cells.items():
                text = ''.join(text_list)
                if '★' not in text:
                    continue
                # 提取课程名(★前面的文本，去掉非法前缀)
                names = re.findall(r'([^\★\u2605]+)★', text)
                for name in names:
                    # 清理：只保留最后一段（去掉前面的日期/星期前缀）
                    # 用中文正则找真正的课程名
                    parts = re.split(r'[\u4e00-\u9fff]{2,4}(?=[\u4e00-\u9fff]{2})', name)
                    real_name = ''
                    # 取最后一段"课程名"格式的
                    for p in reversed(re.split(r'星期[一二三四五六日]|时间段|节次', name)):
                        p = p.strip()
                        if p and len(p) >= 2 and not any(s in p for s in skip_names):
                            real_name = p
                            break
                    if not real_name:
                        real_name = name.strip()
                    
                    real_name = re.sub(r'^【.*?】', '', real_name).strip()
                    if len(real_name) < 2 or len(real_name) > 20:
                        continue
                    if any(s in real_name for s in skip_names):
                        continue

                    c = {'kcmc': real_name, 'xqj': day, 'jcs': period,
                         'cdmc': '', 'xm': '', 'zcd': ''}

                    pm = re.search(r'(\d+[–-]\d+)节', text)
                    if pm:
                        c['jcs'] = pm.group(1)
                    wm = re.search(r'(\d+[–-]\d+周(?:\([单双]\))?)', text)
                    if wm:
                        c['zcd'] = wm.group(1)
                    lm = re.search(r'场地[：:]?\s*([\w\-\u4e00-\u9fff]+)', text)
                    if lm:
                        loc = lm.group(1).strip()
                        if 2 <= len(loc) <= 20:
                            c['cdmc'] = loc
                    tm = re.search(r'教师[：:][\u4e00-\u9fff]{2,4}', text)
                    if tm:
                        teacher = tm.group(0).replace('教师', '').replace('：', '').replace(':', '').strip()
                        if len(teacher) >= 2:
                            c['xm'] = teacher

                    all_courses.append(c)

        # 去重
        seen = set()
        unique = []
        for c in all_courses:
            key = (c['kcmc'], c['xqj'], c['jcs'], c['xm'])
            if key not in seen:
                seen.add(key)
                unique.append(c)
        return unique
