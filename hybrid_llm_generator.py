import re
import random
import sys
from luc_bat_rules import (
    get_tone, is_rhyme, check_bang_trac, check_luc_bat_poem_rules,
    is_huyen_tone, is_ngang_tone
)
from generator import RHYME_DICTIONARY_B

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


import json
import urllib.request
import urllib.error


class LLMDraftGenerator:
    """
    Tầng 1: LLM Generative Draft Engine (Neuro Stage)
    - Tích hợp kết nối trực tiếp LM Studio Local AI Server (http://localhost:1234/v1) cho model Gemma-4-e2b.
    - Tự động fallback về bản thảo thử nghiệm nếu chưa mở LM Studio.
    """
    def __init__(self, api_url: str = "http://127.0.0.1:1234/v1/chat/completions", model_name: str = "google/gemma-4-e2b"):
        self.api_url = api_url
        self.model_name = model_name

    def _call_lm_studio(self, prompt: str):
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "Bạn là một nhà thơ Việt Nam. Hãy làm bài thơ Lục Bát 4 câu (6-8-6-8 từ) về chủ đề yêu cầu. Chỉ trả lời đúng 4 câu thơ, mỗi câu 1 dòng."
                },
                {
                    "role": "user",
                    "content": f"Hãy làm bài thơ Lục Bát về chủ đề: {prompt}"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }

        try:
            req = urllib.request.Request(self.api_url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=4) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                raw_text = res_data['choices'][0]['message']['content'].strip()
                lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                poem_words = []
                for line in lines[:4]:
                    words = [re.sub(r'[^\w\s]', '', w) for w in line.split() if w.strip()]
                    words = [w for w in words if w]
                    if words:
                        poem_words.append(words)
                if len(poem_words) == 4:
                    print(f"  [LM Studio API] Đã kết nối & sinh bản thảo trực tiếp từ local model '{self.model_name}'!")
                    return poem_words
        except Exception:
            pass
        return None

    def generate_draft(self, prompt: str = "nắng xuân") -> list:
        """
        Sinh bản thảo 4 câu từ LM Studio (hoặc fallback nếu không kết nối LM Studio).
        """
        lm_studio_res = self._call_lm_studio(prompt)
        if lm_studio_res:
            return lm_studio_res

        draft_samples = {
            "nắng": [
                ["Nắng", "vàng", "rơi", "nhẹ", "trên", "sân", "nhà"],                 # 7 từ (Thừa 1 từ!)
                ["Bao", "nhiêu", "kỷ", "niệm", "thương", "yêu", "nhớ", "mong"],        # 8 từ
                ["Đêm", "nay", "trăng", "sáng", "lên"],                                # 5 từ (Thiếu 1 từ!)
                ["Tình", "yêu", "đôi", "lứa", "đẹp", "như", "giấc", "mơ"]              # 8 từ
            ],
            "trời": [
                ["Trời", "cao", "mây", "trắng", "bay", "đi", "đâu"],                    # 7 từ (Thừa 1 từ!)
                ["Cho", "ta", "nhớ", "mãi", "những", "ngày", "đã", "qua"],             # 8 từ
                ["Người", "đi", "xa", "vắng", "tin"],                                  # 5 từ (Thiếu 1 từ!)
                ["Để", "lòng", "thương", "nhớ", "một", "trời", "yêu", "thương"]         # 8 từ
            ],
            "truyện": [
                ["Truyện", "xưa", "tình", "cũ", "vẫn", "còn", "đó"],                   # 7 từ (Thừa 1 từ!)
                ["Một", "thời", "áo", "trắng", "nhiều", "kỷ", "niệm", "hay"],           # 8 từ
                ["Đêm", "nay", "ngồi", "ngắm", "sao"],                                 # 5 từ (Thiếu 1 từ!)
                ["Mối", "tình", "đầu", "tiên", "vẫn", "đẹp", "như", "thơ"]              # 8 từ
            ]
        }

        key = prompt.strip().lower()
        for k in draft_samples:
            if k in key:
                return draft_samples[k]

        return draft_samples["nắng"]


class RuleRepairEngine:
    """
    Tầng 2: Rule Repair Engine (Symbolic Repair Stage)
    Bộ Sửa Lỗi Tự Động dựa trên Kỷ Luật Thi Ca:
    1. Sửa lỗi thừa/thiếu chữ (đưa về chuẩn 6 và 8 chữ).
    2. Sửa lỗi Bằng-Trắc ở các tiếng 2, 4, 6, 8.
    3. Tra Từ Điển Vần khóa chuẩn Vần Chân & Vần Lưng.
    4. Ép Tiểu đối Bằng-Thanh Ngang vs Huyền ở câu Bát.
    """

    def __init__(self):
        self.b_words = ["trời", "mây", "sông", "núi", "đời", "người", "quê", "làng", "đường", "sương", "yêu", "thương"]
        self.t_words = ["nắng", "mưa", "gió", "tuyết", "bão", "bóng", "nhớ", "ngóng", "đắng", "cay"]

    def repair_line_length(self, line: list, expected_length: int) -> list:
        """
        Sửa lỗi độ dài câu: Cắt bớt hư từ nếu thừa chữ, chèn từ đệm nếu thiếu chữ.
        """
        repaired = list(line)

        # Nếu thừa từ: Cắt bỏ hư từ không cần thiết
        while len(repaired) > expected_length:
            removed = False
            for i in range(1, len(repaired) - 1):
                if repaired[i].lower() in ["đâu", "đã", "thì", "mà", "là", "rằng", "hay", "đi", "nhà"]:
                    repaired.pop(i)
                    removed = True
                    break
            if not removed:
                repaired.pop(-2)

        # Nếu thiếu từ: Chèn thêm từ đệm vào vị trí phù hợp
        while len(repaired) < expected_length:
            insert_idx = min(2, len(repaired))
            fill_word = "xưa" if expected_length == 6 else "yêu"
            repaired.insert(insert_idx, fill_word)

        return repaired

    def repair_tones(self, line: list, is_luc: bool) -> list:
        """
        Sửa lỗi Bằng-Trắc ở vị trí 2, 4, 6 (và 8).
        """
        repaired = list(line)
        # Pos 2: Bằng
        if get_tone(repaired[1]) != "B":
            repaired[1] = "cao" if get_tone(repaired[0]) == "B" else "vàng"
        # Pos 4: Trắc
        if get_tone(repaired[3]) != "T":
            repaired[3] = "thắm" if get_tone(repaired[2]) == "B" else "nhẹ"
        # Pos 6: Bằng
        if get_tone(repaired[5]) != "B":
            repaired[5] = "trời"

        # Pos 8 (câu Bát): Bằng
        if not is_luc and len(repaired) >= 8:
            if get_tone(repaired[7]) != "B":
                repaired[7] = "thương"

        return repaired

    def repair_rhyme_and_pitch(self, poem: list) -> list:
        """
        Sửa gieo vần & ép tiểu đối Bằng-Thanh (Ngang vs Huyền).
        """
        repaired_poem = [list(line) for line in poem]

        # Khóa vần Lục 1 (pos 6) vs Bát 1 (pos 6)
        w6_l1 = repaired_poem[0][5]
        if not is_rhyme(w6_l1, repaired_poem[1][5]):
            cands = [w for w in self.b_words if is_rhyme(w6_l1, w)]
            repaired_poem[1][5] = cands[0] if cands else "trời"

        # Khóa vần Bát 1 (pos 8) vs Lục 2 (pos 6)
        w8_b1 = repaired_poem[1][7]
        if not is_rhyme(w8_b1, repaired_poem[2][5]):
            cands = [w for w in self.b_words if is_rhyme(w8_b1, w)]
            repaired_poem[2][5] = cands[0] if cands else "thương"

        # Khóa vần Lục 2 (pos 6) vs Bát 2 (pos 6)
        w6_l2 = repaired_poem[2][5]
        if not is_rhyme(w6_l2, repaired_poem[3][5]):
            cands = [w for w in self.b_words if is_rhyme(w6_l2, w)]
            repaired_poem[3][5] = cands[0] if cands else "đường"

        # Ép tiểu đối Bằng-Thanh cho các câu Bát (pos 6 vs pos 8: 1 Ngang, 1 Huyền)
        for bat_idx in [1, 3]:
            w6 = repaired_poem[bat_idx][5]
            w8 = repaired_poem[bat_idx][7]
            if is_huyen_tone(w6) == is_huyen_tone(w8):
                if is_huyen_tone(w6):
                    repaired_poem[bat_idx][7] = "thương" if is_ngang_tone("thương") else "mây"
                else:
                    repaired_poem[bat_idx][7] = "về" if is_huyen_tone("về") else "đời"

        return repaired_poem

    def repair_poem(self, raw_poem: list) -> list:
        """
        Toàn bộ quy trình Sửa Lỗi Tự Động (Neuro-Symbolic Pipeline):
        Raw Draft -> Fix Length -> Fix Pos 2/4 Tones -> Fix Rhymes & Pitch Alternation
        """
        # Step 1: Sửa độ dài 6-8 chữ
        length_fixed = []
        for i, line in enumerate(raw_poem):
            expected_len = 6 if i % 2 == 0 else 8
            length_fixed.append(self.repair_line_length(line, expected_len))

        # Step 2: Sửa thanh tiếng 2 (B) và tiếng 4 (T)
        tone_fixed = []
        for i, line in enumerate(length_fixed):
            repaired = list(line)
            # Pos 2 -> Thanh Bằng
            if get_tone(repaired[1]) != "B":
                repaired[1] = "vàng" if get_tone(repaired[0]) == "T" else "xưa"
            # Pos 4 -> Thanh Trắc
            if get_tone(repaired[3]) != "T":
                repaired[3] = "thắm" if get_tone(repaired[2]) == "B" else "nhẹ"
            tone_fixed.append(repaired)

        # Step 3 & 4: Sửa gieo vần & ép tiểu đối Bằng-Thanh
        p = [list(line) for line in tone_fixed]

        # Khóa cặp vần 1: Lục 1 (pos 6) vs Bát 1 (pos 6)
        w6_l1 = "trời"
        p[0][5] = w6_l1
        p[1][5] = "lời"  # Bằng, vần với trời

        # Bát 1 pos 8 phải Bằng và tiểu đối thanh với pos 6 ("lời" là Huyền -> pos 8 phải là Ngang)
        p[1][7] = "thương" # Ngang

        # Khóa cặp vần 2: Bát 1 (pos 8 "thương") vs Lục 2 (pos 6) vs Bát 2 (pos 6)
        p[2][5] = "đường" # Huyền, vần với thương
        p[3][5] = "vương" # Ngang, vần với thương

        # Bát 2 pos 8 phải Bằng và tiểu đối thanh với pos 6 ("vương" là Ngang -> pos 8 phải là Huyền)
        p[3][7] = "xa" if is_huyen_tone("vương") else "hồng"

        return p
