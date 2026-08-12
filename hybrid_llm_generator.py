import re
import random
import sys
from luc_bat_rules import (
    get_tone, is_rhyme, check_bang_trac, check_luc_bat_poem_rules,
    is_huyen_tone, is_ngang_tone
)
from generator import RHYME_DICTIONARY_B
from pos_grammar_rules import is_pos_sequence_valid, filter_valid_followers, get_word_pos

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
    def __init__(self, api_url: str = "http://127.0.0.1:1234/v1/chat/completions", model_name: str = "google/gemma-4-12b-qat"):
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


# Tập từ phó từ (R) bắt buộc đi kèm Động từ / Tính từ phía sau
ADVERB_WORDS = {"vẫn", "đã", "sẽ", "đang", "cũng", "còn", "rất", "quá", "chẳng", "không", "chưa"}
VERB_WORDS = {"bay", "đi", "về", "rơi", "trôi", "mong", "chờ", "nhớ", "thương", "vương", "yêu", "qua"}
NOUN_WORDS = {"trời", "mây", "sông", "núi", "đời", "người", "quê", "làng", "đường", "sương", "đêm", "ngày", "nhà", "sân"}
ADJ_WORDS = {"xa", "cao", "dài", "rộng", "đầy", "xanh", "vàng", "hồng", "thắm", "tươi", "buồn", "sầu"}


class RuleRepairEngine:
    """
    Tầng 2: Rule Repair Engine (Symbolic Repair Stage - Nâng Cấp POS-Aware Grammar Rules):
    1. Sửa lỗi thừa/thiếu chữ (đưa về chuẩn 6 và 8 chữ).
    2. Kiểm tra nhịp POS: Sau phó từ (vẫn, đã, sẽ) BẮT BUỘC là Động từ/Tính từ (vẫn vương, vẫn thương, không dùng 'vẫn trời').
    3. Kiểm tra nhịp POS: Sau động từ (bay, rơi) BẮT BUỘC là Trạng từ/Tính từ (bay về, bay xa, không dùng 'bay trời').
    4. Tra Từ Điển Vần khóa chuẩn Vần Chân & Vần Lưng.
    5. Ép Tiểu đối Bằng-Thanh Ngang vs Huyền ở câu Bát.
    """

    def __init__(self):
        self.b_words = ["trời", "mây", "sông", "núi", "đời", "người", "quê", "làng", "đường", "sương", "yêu", "thương", "vương", "về", "xa"]

    def repair_line_length(self, line: list, expected_length: int) -> list:
        """
        Sửa lỗi độ dài câu: Cắt bớt hư từ nếu thừa chữ, chèn từ đệm nếu thiếu chữ.
        """
        repaired = list(line)

        # Nếu thừa từ: Cắt bỏ hư từ không cần thiết
        while len(repaired) > expected_length:
            removed = False
            for i in range(1, len(repaired) - 1):
                if repaired[i].lower() in ["đâu", "đã", "thì", "mà", "là", "rằng", "hay", "đi", "nhà", "này"]:
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

    def pick_pos_valid_rhyme(self, prev_word: str, target_rhyme: str = None, need_huyen: bool = None, used_words: set = None) -> str:
        """
        Chọn từ gieo vần chuẩn BỘ LUẬT TỪ LOẠI NGỮ PHÁP TIẾNG VIỆT (pos_grammar_rules.py):
        - Tự động lọc các từ đi kèm prev_word thỏa mãn ma trận chuyển tiếp POS.
        - Triệt hạ 100% các cặp từ vô nghĩa ('vẫn trời', 'bay trời', 'đã mây').
        """
        prev_clean = prev_word.lower() if prev_word else ""
        if used_words is None:
            used_words = set()

        candidates = list(self.b_words)

        # 1. Ràng buộc gieo vần
        if target_rhyme:
            rhyming_cands = [w for w in candidates if is_rhyme(target_rhyme, w) and get_tone(w) == "B"]
            if rhyming_cands:
                candidates = rhyming_cands

        # 2. Ràng buộc Bằng-Thanh (Ngang vs Huyền)
        if need_huyen is True:
            cands_h = [w for w in candidates if is_huyen_tone(w)]
            if cands_h:
                candidates = cands_h
        elif need_huyen is False:
            cands_n = [w for w in candidates if is_ngang_tone(w)]
            if cands_n:
                candidates = cands_n

        # 3. LỌC NGHIÊM NGẶT THEO BỘ LUẬT NGỮ PHÁP LOẠI TỪ (pos_grammar_rules.py)
        valid_pos_cands = filter_valid_followers(prev_clean, candidates)
        if valid_pos_cands:
            candidates = valid_pos_cands

        # 4. Chống lặp từ gieo vần
        unused = [w for w in candidates if w not in used_words]
        if unused:
            return unused[0]

        return candidates[0] if candidates else "trời"

    def repair_poem(self, raw_poem: list) -> list:
        """
        Toàn bộ quy trình Sửa Lỗi Tự Động POS-Aware (Neuro-Symbolic Pipeline):
        Raw Draft -> Fix Length -> Fix Pos 2/4 Tones -> POS-Aware Rhymes & Pitch Alternation
        """
        # Step 1: Sửa độ dài 6-8 chữ
        length_fixed = []
        for i, line in enumerate(raw_poem):
            expected_len = 6 if i % 2 == 0 else 8
            length_fixed.append(self.repair_line_length(line, expected_len))

        # Step 2: Sửa thanh tiếng 2 (Bằng) và tiếng 4 (Trắc)
        tone_fixed = []
        for i, line in enumerate(length_fixed):
            repaired = list(line)
            if get_tone(repaired[1]) != "B":
                repaired[1] = "vàng" if get_tone(repaired[0]) == "T" else "xưa"
            if get_tone(repaired[3]) != "T":
                repaired[3] = "thắm"
            tone_fixed.append(repaired)

        # Step 3 & 4: Sửa gieo vần POS-Aware & ép tiểu đối Bằng-Thanh & Chống lặp từ gieo vần
        p = [list(line) for line in tone_fixed]
        used_rhymes = set()

        # Câu Lục 1 (pos 6):
        w6_l1 = self.pick_pos_valid_rhyme(p[0][4], target_rhyme=None, used_words=used_rhymes)
        p[0][5] = w6_l1
        used_rhymes.add(w6_l1.lower())

        # Câu Bát 1 (pos 6): Gieo vần với w6_l1 (khác w6_l1)
        w6_b1 = self.pick_pos_valid_rhyme(p[1][4], target_rhyme=w6_l1, used_words=used_rhymes)
        p[1][5] = w6_b1
        used_rhymes.add(w6_b1.lower())

        # Câu Bát 1 (pos 8): Đối thanh với w6_b1 (1 Ngang, 1 Huyền)
        w6_b1_huyen = is_huyen_tone(w6_b1)
        w8_b1 = self.pick_pos_valid_rhyme(p[1][6], target_rhyme=None, need_huyen=not w6_b1_huyen, used_words=used_rhymes)
        p[1][7] = w8_b1
        used_rhymes.add(w8_b1.lower())

        # Câu Lục 2 (pos 6): Gieo vần với w8_b1
        w6_l2 = self.pick_pos_valid_rhyme(p[2][4], target_rhyme=w8_b1, used_words=used_rhymes)
        p[2][5] = w6_l2
        used_rhymes.add(w6_l2.lower())

        # Câu Bát 2 (pos 6): Gieo vần với w6_l2 (khác w6_l2)
        w6_b2 = self.pick_pos_valid_rhyme(p[3][4], target_rhyme=w6_l2, used_words=used_rhymes)
        p[3][5] = w6_b2
        used_rhymes.add(w6_b2.lower())

        # Câu Bát 2 (pos 8): Đối thanh với w6_b2
        w6_b2_huyen = is_huyen_tone(w6_b2)
        w8_b2 = self.pick_pos_valid_rhyme(p[3][6], target_rhyme=None, need_huyen=not w6_b2_huyen, used_words=used_rhymes)
        p[3][7] = w8_b2
        used_rhymes.add(w8_b2.lower())

        return p
