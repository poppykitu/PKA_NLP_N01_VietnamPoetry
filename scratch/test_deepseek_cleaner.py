import sys
import re
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

raw_text = """
Đêm đen mèo vừa khép nhường,
Tìm đường đi xa một đường qua đây.
Nghe lòng khát vọng dẫu hoang,
Con đi vạn dặm giữa đời người qua.<|im_end|>
<|im_start|>
*Có 4 câu thơ Lục Bát đúng chuẩn 6-8-6-8 tiếng, trang trọng và mang tính triết lý về con mèo: lòng khát vọng, cô đơn nhưng vững vàng đi vạn dặm.<|im_end|>
<|im_start|>
*Cổ thi hoàn chỉnh, mượt mà, không gượng ép từ ngữ.*<|im_end|>
<|im_start|>
*Và theo yêu cầu đưa lại các câu hoàn chỉnh ở phần hiển thị cuối:*<|im_end|>
<|im_start|>
Đêm đen mèo vừa khép nhường,
Tìm đường đi xa một đường qua đây.
Nghe lòng khát vọng dẫu hoang,
Con đi vạn dặm giữa đời người qua.<|im_end|>
"""

def extract_poem_lines(raw_content: str) -> list:
    # 1. Strip special tokens
    clean = re.sub(r'<\|[^>]+\|>', '', raw_content)
    clean = re.sub(r'<think>[\s\S]*?</think>', '', clean)

    # 2. Check JSON
    try:
        match = re.search(r'\{[\s\S]*\}', clean)
        if match:
            j = json.loads(match.group(0))
            arr = j.get('poem_lines') or j.get('lines') or j.get('poem')
            if isinstance(arr, list) and len(arr) >= 4:
                parsed = []
                for l in arr:
                    w = [x.strip('.,!?:;"\'()[]*') for x in str(l).split() if x.strip('.,!?:;"\'()[]*')]
                    if w:
                        parsed.append(w)
                if len(parsed) >= 4:
                    return parsed[:4]
    except Exception:
        pass

    # 3. Line by line parsing
    raw_lines = [l.strip() for l in clean.split('\n') if l.strip()]
    poem_words = []
    seen = set()

    for line in raw_lines:
        line_clean = re.sub(r'^(?:Line\s*\d+|Draft\s*\d+|\d+[\.\:]|\*|\-|\:|\s)+', '', line).strip()
        line_clean = line_clean.replace('*', '').strip()
        
        # Skip explanation / prompt metadata sentences
        if re.search(r'^(Có\s+\d+|Cổ\s+thi|Và\s+theo|Dưới\s+đây|Bài\s+thơ|Phân\s+tích|Lục\s+Bát|Xây\s+dựng|Kiểm\s+tra|Sửa\s+lại)', line_clean, re.IGNORECASE):
            continue

        words = [w.strip('.,!?:;"\'()[]*') for w in line_clean.split() if w.strip('.,!?:;"\'()[]*')]
        if 4 <= len(words) <= 10:
            s = ' '.join(words).lower()
            if s not in seen:
                seen.add(s)
                poem_words.append(words)

    return poem_words[:4]

res = extract_poem_lines(raw_text)
print("EXTRACTED RESULT:")
for r in res:
    print(" ".join(r), f"({len(r)} từ)")
