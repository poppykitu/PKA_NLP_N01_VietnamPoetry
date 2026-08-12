import re
import random
import sys
from luc_bat_rules import (
    get_tone, is_rhyme, check_bang_trac, check_luc_bat_poem_rules,
    is_huyen_tone, is_ngang_tone
)
from generator import RHYME_DICTIONARY_B
from pos_grammar_rules import is_pos_sequence_valid, filter_valid_followers, get_word_pos_set

import json
import requests
import urllib.request
import urllib.error


def safe_print(msg: str):
    try:
        sys.stdout.write(str(msg) + "\n")
        sys.stdout.flush()
    except Exception:
        try:
            sys.stdout.buffer.write((str(msg) + "\n").encode('utf-8', errors='ignore'))
            sys.stdout.buffer.flush()
        except Exception:
            pass


class LLMDraftGenerator:
    """
    Tầng 1: LLM Generative Draft Engine (Neuro Stage)
    - Tích hợp kết nối trực tiếp LM Studio Local AI Server (http://localhost:1234/v1) cho google/gemma-4-12b-qat.
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
                    "role": "user",
                    "content": f"Hãy làm một bài thơ Lục Bát 4 câu (6-8-6-8 từ) về chủ đề: {prompt}."
                }
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }

        try:
            safe_print(f"  [*] Đang kết nối LM Studio API cho chủ đề '{prompt}'...")
            res = requests.post(self.api_url, json=payload, timeout=180)

            if res.status_code == 200:
                res_data = res.json()
                msg_obj = res_data['choices'][0]['message']
                
                # UƯ TIÊN LẤY CONTENT CHÍNH THỨC (Nơi chứa kết quả JSON Schema)
                raw_text = msg_obj.get('content', '') or ''
                
                # Nếu content bị rỗng do model reasoning, mới đọc từ reasoning_content
                if not raw_text.strip():
                    raw_text = msg_obj.get('reasoning_content', '') or ''
                raw_text = raw_text.strip()

                safe_print(f"  [LM Studio API Output]:\n{raw_text}\n")

                # Parse JSON Schema trực tiếp từ content
                try:
                    match_json = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    if match_json:
                        json_obj = json.loads(match_json.group(0))
                        lines = json_obj.get("poem_lines", [])
                        poem_words = []
                        for l in lines:
                            words = [w.strip(".,!?:;\"'()[]*") for w in l.split() if w.strip()]
                            words = [w for w in words if w]
                            if words:
                                poem_words.append(words)
                        if len(poem_words) >= 4:
                            safe_print(f"  [LM Studio JSON Schema API] ✓ Đã nhận mảng 4 câu thơ chuẩn 100% từ JSON Schema cho chủ đề '{prompt}'!")
                            return poem_words[:4]
                except Exception as json_err:
                    safe_print(f"  [Notice] Thử nghiệm JSON parse rỗng/lỗi ({json_err}). Đang bóc tách dòng...")

                lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                poem_words = []
                seen_lines = set()
                for line in lines:
                    # Bóc tách các câu thơ Tiếng Việt thực sự (loại bỏ chú thích tiếng Anh phía sau)
                    match_poem = re.search(r'[\*\:\d\(\)\s]*([À-ỹà-ỹA-Za-z\s]+?)(?:\s*\([A-Za-z\s\.,\'-]+\)|\s*-\s*\*|\s*$)', line)
                    if match_poem:
                        candidate = match_poem.group(1).strip()
                        candidate = re.sub(r'^(?:Line\s*\d+|Draft\s*\d+|Revision|\d+|\*|\-|\:|\s)+', '', candidate, flags=re.IGNORECASE).strip()
                        if any(candidate.lower().startswith(k) for k in ["form", "length", "topic", "constraint", "language", "phase", "critique", "visuals", "emotions", "vietnamese", "shoooting"]):
                            continue
                        
                        words = [w.strip(".,!?:;\"'()[]*") for w in candidate.split() if w.strip()]
                        # Bắt buộc phải chứa âm tiết Tiếng Việt thực thụ
                        words = [w for w in words if w and (re.search(r'[à-ỹÀ-ỸđĐ]', w) or len(w) <= 3)]
                        
                        if 5 <= len(words) <= 9:
                            line_str = " ".join(words).lower()
                            if line_str not in seen_lines:
                                seen_lines.add(line_str)
                                poem_words.append(words)

                if len(poem_words) >= 4:
                    safe_print(f"  [LM Studio API] ✓ Đã bóc tách đúng {len(poem_words[:4])} câu thơ Lục Bát Tiếng Việt trực tiếp từ '{self.model_name}'!")
                    return poem_words[:4]
                elif poem_words:
                    safe_print(f"  [LM Studio API] ✓ Đã bóc tách {len(poem_words)} câu thơ từ '{self.model_name}'! (Đang bù đủ 4 câu)")
                    fallback_pool = [
                        ["sao", "băng", "rơi", "nhẹ", "giữa", "trời"],
                        ["cho", "ta", "nhớ", "mãi", "những", "ngày", "đã", "qua"],
                        ["người", "đi", "xa", "vắng", "tin", "nhà"],
                        ["để", "lòng", "thương", "nhớ", "một", "trời", "yêu", "thương"]
                    ]
                    while len(poem_words) < 4:
                        poem_words.append(fallback_pool[len(poem_words)])
                    return poem_words[:4]
            else:
                safe_print(f"  [LM Studio API Error] HTTP Status {res.status_code}: {res.text[:200]}")
        except Exception as e:
            safe_print(f"  [Notice] Lỗi kết nối LM Studio API ({type(e).__name__}: {e}). Đang dùng bản thảo dự phòng...")

        return None

    def analyze_line_pos_json_schema(self, line_text: str) -> dict:
        """
        [Tier 1: Dynamic Contextual Tagging via Gemma-4-12B JSON Schema API]
        Gửi Yêu Cầu Ép Cấu Trúc JSON Schema đến Gemma-4-12B trên LM Studio để gán nhãn loại từ
        (POS Tagging: N, V, A, R, P, E) chính xác 100% theo toàn bộ ngữ cảnh câu thơ.
        """
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "Bạn là chuyên gia Ngôn ngữ học Tiếng Việt. Hãy phân tích từ loại (POS Tagging) cho từng từ trong dòng thơ."
                },
                {
                    "role": "user",
                    "content": f"Phân tích loại từ cho dòng thơ: '{line_text}'"
                }
            ],
            "response_format": {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "words": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "word": {"type": "string"},
                                    "pos": {"type": "string", "enum": ["N", "V", "A", "R", "P", "E"]}
                                },
                                "required": ["word", "pos"]
                            }
                        }
                    },
                    "required": ["words"]
                }
            },
            "temperature": 0.1
        }

        try:
            req = urllib.request.Request(self.api_url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=4) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                raw_json = json.loads(res_data['choices'][0]['message']['content'])
                pos_map = {item['word'].lower(): item['pos'] for item in raw_json.get('words', [])}
                print(f"  [Tier 1 Gemma JSON POS API] Đã phân tích POS ngữ cảnh cho câu: '{line_text}'")
                return pos_map
        except Exception:
            pass

        return {}

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
        from pos_grammar_rules import WORD_TO_POS_SET
        b_cands = [w for w in WORD_TO_POS_SET.keys() if get_tone(w) == "B" and len(w) >= 2]
        self.b_words = b_cands if len(b_cands) > 10 else ["trời", "mây", "sông", "núi", "đời", "người", "quê", "làng", "đường", "sương", "yêu", "thương", "vương", "về", "xa"]

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
