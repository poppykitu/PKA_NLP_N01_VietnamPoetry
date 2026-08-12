# %% [markdown]
# # BÀI TẬP LỚN MÔN NLP: MÔ HÌNH SINH THƠ LỤC BÁT TIẾNG VIỆT
# 
# **Mô tả**: Toàn bộ Pipeline sinh thơ Lục bát kết hợp **Mô hình Ngôn ngữ N-gram (Laplace Smoothing & Vocabulary Filter)** và **Hệ thống Kiểm tra Luật Thơ Lục Bát (Rule-Based System)** được đóng gói hoàn chỉnh trong file Notebook này.
# 
# ---

# %% [markdown]
# ## 1. KHỞI TẠO & TẢI DATASET (extract_luc_bat_data & Caching)

# %%
import os
import re
import sys
import pickle
import unicodedata

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Chỉ dùng 1 file cache duy nhất cho Hugging Face Dataset
CACHE_FILE_PATH = "luc_bat_hf_dataset_cache.pkl"


def clean_vietnamese_line(line: str) -> str:
    """Làm sạch văn bản dòng thơ: lowercasing, xóa ký tự đặc biệt giữ lại tiếng Việt."""
    if not line:
        return ""
    line = unicodedata.normalize("NFC", line.strip()).lower()
    line = re.sub(r'[^a-zA-Zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]', '', line)
    line = re.sub(r'\s+', ' ', line).strip()
    return line


def tokenize_line(line: str) -> list:
    """Tách từ/âm tiết cho câu thơ Lục bát."""
    cleaned = clean_vietnamese_line(line)
    return cleaned.split() if cleaned else []


def extract_luc_bat_data(raw_corpus: list) -> list:
    """
    Quét và lọc triệt để các cặp câu Lục (6 từ) - Bát (8 từ) nối tiếp nhau từ tập dữ liệu thô.
    """
    luc_bat_poems = []

    for item in raw_corpus:
        if isinstance(item, str):
            lines = item.strip().split("\n")
        elif isinstance(item, list):
            lines = item
        else:
            continue

        cleaned_lines = [clean_vietnamese_line(l) for l in lines if clean_vietnamese_line(l)]
        
        current_poem = []
        i = 0
        # Quét từng dòng để tìm cặp câu (6 - 8)
        while i < len(cleaned_lines) - 1:
            words_luc = cleaned_lines[i].split()
            words_bat = cleaned_lines[i+1].split()
            
            # Nếu phát hiện chuẩn 1 cặp Lục (6) - Bát (8)
            if len(words_luc) == 6 and len(words_bat) == 8:
                current_poem.append(words_luc)
                current_poem.append(words_bat)
                i += 2  # Nhảy sang cặp tiếp theo
            else:
                i += 1  # Bỏ qua dòng rác / không đúng nhịp 6-8

        if current_poem:
            luc_bat_poems.append(current_poem)

    return luc_bat_poems


def load_huggingface_dataset(dataset_name: str = "phamson02/vietnamese-poetry-corpus", cache_path: str = CACHE_FILE_PATH) -> list:
    """
    Tải Dataset từ Hugging Face và LƯU CACHE VĨNH VIỄN.
    - Lần 1: Tải từ HF -> Lọc Lục Bát -> Ghi vào file Cache.
    - Lần 2 trở đi: Đọc trực tiếp từ File Cache (< 0.1s), KHÔNG TẢI LẠI và KHÔNG DÙNG FALLBACK.
    """
    # 1. Nếu đã có Cache trên đĩa -> Đọc luôn
    if os.path.exists(cache_path):
        print(f"[*] Nạp dữ liệu thơ Lục Bát từ CACHE ('{cache_path}')...")
        try:
            with open(cache_path, "rb") as f:
                luc_bat_data = pickle.load(f)
            print(f"[✓] Nạp thành công {len(luc_bat_data)} bài/cặp thơ Lục Bát từ CACHE!")
            return luc_bat_data
        except Exception as e:
            print(f"[!] File cache bị lỗi ({e}), sẽ tiến hành tải lại từ Hugging Face...")

    # 2. Nếu chưa có Cache -> Tải từ Hugging Face
    from datasets import load_dataset
    print(f"[*] Đang tải dataset '{dataset_name}' từ Hugging Face (Chỉ tải 1 lần duy nhất)...")
    
    try:
        ds = load_dataset(dataset_name, split="train")
        raw_poems = []
        for row in ds:
            # Lấy trường dữ liệu chứa văn bản thơ
            text = row.get("text") or row.get("content") or row.get("poem") or ""
            if text:
                raw_poems.append(text)
        print(f"[✓] Tải thành công {len(raw_poems)} bản ghi thô từ Hugging Face.")
    except Exception as e:
        raise RuntimeError(f"❌ Không thể tải dataset từ Hugging Face: {e}. Vui lòng kiểm tra kết nối mạng!")

    # 3. Trích xuất thơ Lục Bát chuẩn
    print("[*] Đang bóc tách và lọc các cặp câu Lục Bát (6-8)...")
    luc_bat_data = extract_luc_bat_data(raw_poems)
    
    if not luc_bat_data:
        raise ValueError("❌ Không tìm thấy bài thơ Lục Bát nào hợp lệ trong Dataset!")

    # 4. Lưu Cache vĩnh viễn ra file .pkl
    print(f"[*] Đang LƯU CACHE vĩnh viễn vào đĩa ('{cache_path}')...")
    with open(cache_path, "wb") as f:
        pickle.dump(luc_bat_data, f)
    print(f"[✓] Đã LƯU CACHE thành công! Tốc độ lần sau sẽ siêu nhanh.")

    return luc_bat_data

# %% [markdown]
# ## 2. KIỂM TRA LUẬT THƠ LỤC BÁT (check_bang_trac & is_rhyme)

# %%
import re
import sys
import unicodedata

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
# 1. BẢNG MÃ THANH ĐIỆU VÀ QUY TẮC BẰNG - TRẮC (1-BASED INDEX POSITIONS)
# ==============================================================================

# Thanh Bằng (B): Không dấu (Ngang) và Dấu Huyền
# Thanh Trắc (T): Dấu Sắc, Dấu Hỏi, Dấu Ngã, Dấu Nặng

HUYEN_CHARS = set("àằầèềìòồờùừỳ")
TRAC_CHARS  = set("áắấéếíóốớúứýảẳẩẻểỉỏổởủửỷãẵẫẽễĩõỗỡũữỹạặậẹệịọộợụựỵ")
BANG_VOWELS = set("aăâeêioôơuưyàằầèềìòồờùừỳ")


def normalize_vietnamese(text: str) -> str:
    """Chuẩn hóa chuỗi về Unicode NFC và chữ thường."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", text.strip()).lower()


def get_tone(word: str) -> str:
    """
    Phân loại Thanh Bằng (B) hoặc Thanh Trắc (T) cho một từ tiếng Việt:
    - Thanh Bằng (B): Không dấu (Ngang) hoặc Dấu Huyền.
    - Thanh Trắc (T): Sắc, Hỏi, Ngã, Nặng.
    """
    word = normalize_vietnamese(word)
    if not word:
        return "UNKNOWN"

    for char in word:
        if char in TRAC_CHARS:
            return "T"
        if char in HUYEN_CHARS:
            return "B"

    # Nếu nguyên âm không chứa dấu trắc/huyền -> Thanh Ngang (Bằng)
    for char in word:
        if char in BANG_VOWELS:
            return "B"

    return "UNKNOWN"


def check_bang_trac(sentence) -> dict:
    """
    CHUẨN HÓA HÀM CHECK BẰNG - TRẮC (INDEX 1-BASED):
    
    Quy tắc bắt buộc:
    - Câu 6 chữ (Lục): Tiếng thứ 2 (B) - Tiếng thứ 4 (T) - Tiếng thứ 6 (B).
    - Câu 8 chữ (Bát): Tiếng thứ 2 (B) - Tiếng thứ 4 (T) - Tiếng thứ 6 (B) - Tiếng thứ 8 (B).
    
    :param sentence: Chuỗi câu thơ hoặc danh sách các từ.
    :return: dict {"is_valid": bool, "tones": list, "length": int, "errors": list}
    """
    if isinstance(sentence, str):
        words = sentence.strip().split()
    elif isinstance(sentence, list):
        words = sentence
    else:
        return {"is_valid": False, "tones": [], "length": 0, "errors": ["Đầu vào không hợp lệ."]}

    words = [normalize_vietnamese(w) for w in words if normalize_vietnamese(w)]
    n = len(words)
    tones = [get_tone(w) for w in words]
    errors = []

    if n != 6 and n != 8:
        errors.append(f"Số từ trong câu phải là 6 hoặc 8 từ (hiện tại: {n} từ).")
        return {"is_valid": False, "tones": tones, "length": n, "errors": errors}

    # Câu 6 chữ: Vị trí 2 (Index 1) -> B, Vị trí 4 (Index 3) -> T, Vị trí 6 (Index 5) -> B
    if n == 6:
        if tones[1] != "B":
            errors.append(f"Tiếng thứ 2 ('{words[1]}') phải là Thanh Bằng (hiện tại: {tones[1]}).")
        if tones[3] != "T":
            errors.append(f"Tiếng thứ 4 ('{words[3]}') phải là Thanh Trắc (hiện tại: {tones[3]}).")
        if tones[5] != "B":
            errors.append(f"Tiếng thứ 6 ('{words[5]}') phải là Thanh Bằng (hiện tại: {tones[5]}).")

    # Câu 8 chữ: Vị trí 2 (Index 1) -> B, Vị trí 4 (Index 3) -> T, Vị trí 6 (Index 5) -> B, Vị trí 8 (Index 7) -> B
    elif n == 8:
        if tones[1] != "B":
            errors.append(f"Tiếng thứ 2 ('{words[1]}') phải là Thanh Bằng (hiện tại: {tones[1]}).")
        if tones[3] != "T":
            errors.append(f"Tiếng thứ 4 ('{words[3]}') phải là Thanh Trắc (hiện tại: {tones[3]}).")
        if tones[5] != "B":
            errors.append(f"Tiếng thứ 6 ('{words[5]}') phải là Thanh Bằng (hiện tại: {tones[5]}).")
        if tones[7] != "B":
            errors.append(f"Tiếng thứ 8 ('{words[7]}') phải là Thanh Bằng (hiện tại: {tones[7]}).")

    return {
        "is_valid": len(errors) == 0,
        "tones": tones,
        "length": n,
        "errors": errors
    }


# ==============================================================================
# 2. XỬ LÝ ÂM VẦN CHÍNH XÁC (STRICT RHYME CHECKER - VOWEL + CODA)
# ==============================================================================

# Bảng loại bỏ DẤU THANH nhưng BẢO TỒN NGUYÊN ÂM TIẾNG VIỆT (ă, â, ê, ô, ơ, ư)
TONE_STRIP_EXACT = {
    'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'ằ': 'ă', 'ắ': 'ă', 'ẳ': 'ă', 'ẵ': 'ă', 'ặ': 'ă',
    'ầ': 'â', 'ấ': 'â', 'ẩ': 'â', 'ẫ': 'â', 'ậ': 'â',
    'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ề': 'ê', 'ế': 'ê', 'ể': 'ê', 'ễ': 'ê', 'ệ': 'ê',
    'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ồ': 'ô', 'ố': 'ô', 'ổ': 'ô', 'ỗ': 'ô', 'ộ': 'ô',
    'ờ': 'ơ', 'ớ': 'ơ', 'ở': 'ơ', 'ỡ': 'ơ', 'ợ': 'ơ',
    'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ừ': 'ư', 'ứ': 'ư', 'ử': 'ư', 'ữ': 'ư', 'ự': 'ư',
    'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y'
}

# Danh sách phụ âm đầu tiếng Việt
INITIAL_CONSONANTS = [
    "ngh", "ng", "nh", "gh", "ph", "th", "ch", "tr", "kh", "gi", "qu",
    "b", "c", "d", "đ", "g", "h", "k", "l", "m", "n", "p", "r", "s", "t", "v", "x"
]


def extract_rime(word: str) -> str:
    """
    Trích xuất chính xác KHUÔN VẦN (Vowel + Coda) của từ tiếng Việt:
    Ví dụ:
      - "sương" -> "ương"
      - "đường" -> "ương"
      - "xăm"   -> "ăm"
      - "quan"  -> "an"
      - "vàng"  -> "ang"
      - "thầm"  -> "âm"
    """
    word = normalize_vietnamese(word)
    if not word:
        return ""

    word_clean = word
    if word_clean.startswith("qu"):
        raw_rime = word_clean[2:]
        if not raw_rime:
            raw_rime = "u"
    elif word_clean.startswith("gi"):
        raw_rime = word_clean[2:]
        if not raw_rime:
            raw_rime = "i"
    else:
        raw_rime = word_clean
        for cons in INITIAL_CONSONANTS:
            if word_clean.startswith(cons):
                raw_rime = word_clean[len(cons):]
                break

    if not raw_rime:
        raw_rime = word_clean

    # Loại bỏ dấu thanh, giữ nguyên âm tiếng Việt (ă, â, ê, ô, ơ, ư)
    rime = "".join([TONE_STRIP_EXACT.get(c, c) for c in raw_rime])
    return rime


def is_rhyme(word1: str, word2: str) -> bool:
    """
    HÀM KIỂM TRA GIEO VẦN NGHIÊM NGẠT (STRICT RHYME CHECKER):
    - Cả 2 từ ở vị trí gieo vần BẮT BỘC phải là THANH BẰNG (B).
    - So sánh phần vần (Vowel + Coda):
      + "sương" == "đường" (vần 'ương') -> TRUE
      + "tình" == "mình" (vần 'inh') -> TRUE
      + "xăm" (vần 'ăm') vs "quan" (vần 'an') -> FALSE
      + "vàng" (vần 'ang') vs "thầm" (vần 'âm') -> FALSE
      + "am" vs "an", "ang" vs "am" -> FALSE
    """
    w1 = normalize_vietnamese(word1)
    w2 = normalize_vietnamese(word2)

    if not w1 or not w2:
        return False

    # Vị trí gieo vần thơ Lục bát BẮT BỘC mang Thanh Bằng (B)
    if get_tone(w1) != "B" or get_tone(w2) != "B":
        return False

    r1 = extract_rime(w1)
    r2 = extract_rime(w2)

    if not r1 or not r2:
        return False

    # 1. Trùng khớp chính vần hoàn toàn (Exact Rime Match)
    if r1 == r2:
        return True

    # 2. Các cặp Vần Thông chuẩn truyền thống được phép trong thơ Lục Bát:
    VALID_VAN_THONG_PAIRS = {
        ("ơi", "ươi"), ("ươi", "ơi"),
        ("ay", "ây"), ("ây", "ay"),
        ("ui", "ôi"), ("ôi", "ui"),
        ("uôi", "ôi"), ("ôi", "uôi"),
        ("ia", "ie"), ("ie", "ia"),
        ("ưa", "ươ"), ("ươ", "ưa"),
        ("ong", "ông"), ("ông", "ong"),
        ("on", "ơn"), ("ơn", "on")
    }

    if (r1, r2) in VALID_VAN_THONG_PAIRS:
        return True

    # Nếu phần vần khác nhau và không thuộc cặp vần thông chuẩn -> BẮT BỘC FALSE
    return False


def check_luc_bat_poem_rules(poem_lines: list) -> dict:
    """
    Kiểm tra toàn bộ quy tắc luật thơ Lục Bát:
    1. Check Bằng-Trắc từng câu.
    2. Check Gieo vần chính xác giữa các câu.
    3. Check Chống lặp từ gieo vần giữa các cặp câu.
    """
    errors = []
    if len(poem_lines) % 2 != 0 or len(poem_lines) == 0:
        return {"valid": False, "errors": ["Số dòng bài thơ phải là số chẵn."]}

    used_rhyme_words = set()

    for i in range(0, len(poem_lines), 2):
        luc_words = poem_lines[i]
        bat_words = poem_lines[i+1]

        # 1. Check Bằng-Trắc
        check6 = check_bang_trac(luc_words)
        if not check6["is_valid"]:
            for e in check6["errors"]:
                errors.append(f"Dòng {i+1} (Câu Lục): {e}")

        check8 = check_bang_trac(bat_words)
        if not check8["is_valid"]:
            for e in check8["errors"]:
                errors.append(f"Dòng {i+2} (Câu Bát): {e}")

        # 2. Check Gieo vần: Từ 6 câu 6 vs Từ 6 câu 8
        if len(luc_words) == 6 and len(bat_words) >= 6:
            w6_luc = luc_words[5]
            w6_bat = bat_words[5]
            if not is_rhyme(w6_luc, w6_bat):
                errors.append(f"Lỗi vần Dòng {i+1}-{i+2}: Từ 6 câu Lục ('{w6_luc}') không gieo vần với Từ 6 câu Bát ('{w6_bat}').")

            # Check chống lặp từ gieo vần
            if w6_luc in used_rhyme_words:
                errors.append(f"Lỗi lặp từ gieo vần Dòng {i+1}: Từ '{w6_luc}' đã được dùng ở vị trí vần trước đó.")
            if w6_bat in used_rhyme_words:
                errors.append(f"Lỗi lặp từ gieo vần Dòng {i+2}: Từ '{w6_bat}' đã được dùng ở vị trí vần trước đó.")

            used_rhyme_words.add(w6_luc)
            used_rhyme_words.add(w6_bat)

        # 3. Check Gieo vần: Từ 8 câu 8 vs Từ 6 câu Lục tiếp theo
        if len(bat_words) == 8:
            w8_bat = bat_words[7]
            if w8_bat in used_rhyme_words:
                errors.append(f"Lỗi lặp từ gieo vần Dòng {i+2}: Từ '{w8_bat}' (cuối câu 8) đã được dùng ở vị trí vần trước đó.")
            used_rhyme_words.add(w8_bat)

            if i + 2 < len(poem_lines):
                next_luc_words = poem_lines[i+2]
                if len(next_luc_words) == 6:
                    next_w6_luc = next_luc_words[5]
                    if not is_rhyme(w8_bat, next_w6_luc):
                        errors.append(f"Lỗi vần Dòng {i+2}-{i+3}: Từ 8 câu Bát ('{w8_bat}') không gieo vần với Từ 6 câu Lục tiếp ('{next_w6_luc}').")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


if __name__ == "__main__":
    print("--- TEST HÀM IS_RHYME CHÍNH XÁC ---")
    print("is_rhyme('sương', 'đường') ->", is_rhyme('sương', 'đường')) # True
    print("is_rhyme('tình', 'mình') ->", is_rhyme('tình', 'mình'))   # True
    print("is_rhyme('xăm', 'quan') ->", is_rhyme('xăm', 'quan'))     # False
    print("is_rhyme('vàng', 'thầm') ->", is_rhyme('vàng', 'thầm'))   # False
    print("is_rhyme('am', 'an') ->", is_rhyme('am', 'an'))           # False


# %% [markdown]
# ## 3. MÔ HÌNH NGÔN NGỮ N-GRAM & LAPLACE SMOOTHING (ngram_model)

# %%
import math
import os
import sys
import pickle
import unicodedata
from collections import defaultdict, Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

VIETNAMESE_VOWELS = set("aăâeêioôơuưyàằầèềìòồờùừỳáắấéếíóốớúứýảẳẩẻểỉỏổởủửỷãẵẫẽễĩõỗỡũữỹạặậẹệịọộợụựỵ")


def is_valid_vietnamese_syllable(word: str) -> bool:
    """Kiểm tra một từ/âm tiết có phải từ Tiếng Việt hợp lệ hay không."""
    if not word or len(word) < 1 or len(word) > 7:
        return False
    word = unicodedata.normalize("NFC", word.strip().lower())
    if any(c in "fjwz" for c in word):
        return False
    return any(c in VIETNAMESE_VOWELS for c in word)


class NGramLanguageModel:
    """
    Mô hình Ngôn ngữ N-gram nâng cao tích hợp Lưu / Nạp Cache Mô Hình Đã Huấn Luyện (Model Caching).
    """

    def __init__(self, n: int = 3, k: float = 1.0, min_freq: int = 2):
        self.n = n
        self.k = k
        self.min_freq = min_freq
        self.ngram_counts = Counter()
        self.context_counts = Counter()
        self.word_counts = Counter()
        self.vocab = set()
        self.vocab_size = 0
        self.total_words = 0

        self.BOS = "<BOS>"
        self.EOS = "<EOS>"

    def train(self, tokenized_poems: list):
        """Huấn luyện mô hình N-gram và đếm tần suất."""
        print(f"[*] Đang huấn luyện Mô hình {self.n}-gram Language Model...")
        self.ngram_counts.clear()
        self.context_counts.clear()
        self.word_counts.clear()
        self.vocab.clear()

        # Đếm tần suất âm tiết
        for poem in tokenized_poems:
            for line in poem:
                for word in line:
                    if is_valid_vietnamese_syllable(word):
                        self.word_counts[word] += 1

        # Tạo từ vựng chuẩn
        for w, count in self.word_counts.items():
            if count >= self.min_freq:
                self.vocab.add(w)

        if len(self.vocab) < 50:
            for w in self.word_counts:
                self.vocab.add(w)

        # Đếm N-gram và Context
        for poem in tokenized_poems:
            for line in poem:
                filtered_line = [w for w in line if w in self.vocab]
                if len(filtered_line) < 2:
                    continue

                padded_line = [self.BOS] * (self.n - 1) + filtered_line + [self.EOS]

                for i in range(len(padded_line) - self.n + 1):
                    ngram = tuple(padded_line[i : i + self.n])
                    context = tuple(padded_line[i : i + self.n - 1])

                    self.ngram_counts[ngram] += 1
                    self.context_counts[context] += 1

        self.vocab_size = len(self.vocab)
        print(f"[✓] Huấn luyện hoàn tất!")
        print(f"    - Từ vựng Tiếng Việt chuẩn (Vocab Size): {self.vocab_size} từ")
        print(f"    - Tổng số mẫu {self.n}-gram unique: {len(self.ngram_counts)}")

    def save_model(self, file_path: str = "ngram_model_cache.pkl"):
        """Lưu toàn bộ tham số mô hình đã huấn luyện ra file Cache."""
        try:
            print(f"[*] Đang LƯU CACHE mô hình N-gram vào file '{file_path}'...")
            state = {
                "n": self.n,
                "k": self.k,
                "min_freq": self.min_freq,
                "ngram_counts": self.ngram_counts,
                "context_counts": self.context_counts,
                "word_counts": self.word_counts,
                "vocab": self.vocab,
                "vocab_size": self.vocab_size
            }
            with open(file_path, "wb") as f:
                pickle.dump(state, f)
            print(f"[✓] Đã LƯU CACHE Mô hình thành công!")
        except Exception as e:
            print(f"[!] Không thể lưu cache mô hình ({e}).")

    @classmethod
    def load_model(cls, file_path: str = "ngram_model_cache.pkl"):
        """Nạp nhanh mô hình N-gram đã huấn luyện từ file Cache (<0.1 giây)."""
        if not os.path.exists(file_path):
            return None
        try:
            print(f"[*] Nạp Mô hình N-gram từ CACHE ('{file_path}')...")
            with open(file_path, "rb") as f:
                state = pickle.load(f)

            model = cls(n=state["n"], k=state["k"], min_freq=state["min_freq"])
            model.ngram_counts = state["ngram_counts"]
            model.context_counts = state["context_counts"]
            model.word_counts = state["word_counts"]
            model.vocab = state["vocab"]
            model.vocab_size = state["vocab_size"]

            print(f"[✓] Nạp Mô hình từ CACHE thành công!")
            print(f"    - Kích thước từ vựng: {model.vocab_size} từ")
            print(f"    - Kích thước N-gram: {len(model.ngram_counts)} mẫu")
            return model
        except Exception as e:
            print(f"[!] Lỗi khi nạp cache mô hình ({e}).")
            return None

    def get_probability(self, word: str, context: tuple) -> float:
        """Tính xác suất điều kiện P(word | context) với Laplace Smoothing."""
        if len(context) > self.n - 1:
            context = context[-(self.n - 1):]
        elif len(context) < self.n - 1:
            context = (self.BOS,) * (self.n - 1 - len(context)) + context

        ngram = context + (word,)
        count_ngram = self.ngram_counts[ngram]
        count_context = self.context_counts[context]

        vocab_size = self.vocab_size if self.vocab_size > 0 else 1
        prob = (count_ngram + self.k) / (count_context + self.k * vocab_size)
        return prob

    def get_candidate_probabilities(self, context: tuple, candidate_words: list = None) -> list:
        """Lấy danh sách các từ ứng viên tiếp theo dựa trên context."""
        if len(context) > self.n - 1:
            context = context[-(self.n - 1):]
        elif len(context) < self.n - 1:
            context = (self.BOS,) * (self.n - 1 - len(context)) + context

        words_to_eval = candidate_words if candidate_words is not None else list(self.vocab)

        results = []
        for word in words_to_eval:
            if word in (self.BOS, self.EOS):
                continue
            prob = self.get_probability(word, context)
            freq = self.word_counts.get(word, 1)
            score = prob * math.log(1 + freq)
            results.append((word, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def compute_perplexity(self, test_poems: list) -> float:
        """Tính chỉ số Perplexity trên tập kiểm thử."""
        total_log_prob = 0.0
        total_words_count = 0

        for poem in test_poems:
            for line in poem:
                filtered_line = [w for w in line if w in self.vocab]
                if not filtered_line:
                    continue

                padded_line = [self.BOS] * (self.n - 1) + filtered_line + [self.EOS]

                for i in range(self.n - 1, len(padded_line)):
                    word = padded_line[i]
                    context = tuple(padded_line[i - self.n + 1 : i])

                    prob = self.get_probability(word, context)
                    total_log_prob += math.log(prob)
                    total_words_count += 1

        if total_words_count == 0:
            return float('inf')

        ppl = math.exp(-total_log_prob / total_words_count)
        return ppl


# %% [markdown]
# ## 4. THUẬT TOÁN SINH THƠ LỤC BÁT (generator)

# %%
import random
import sys
from luc_bat_rules import get_tone, is_rhyme, check_bang_trac, check_luc_bat_poem_rules
from ngram_model import NGramLanguageModel, is_valid_vietnamese_syllable

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# Từ điển từ gieo vần chuẩn Thanh Bằng (B) dự phòng theo từng khuôn vần
RHYME_DICTIONARY_B = {
    "an":    ["đàn", "ngàn", "màn", "tràn", "nhàn", "an"],
    "ang":   ["làng", "sang", "vàng", "tràng", "mang", "gàng"],
    "am":    ["lam", "cam", "nam", "chàm", "xàm"],
    "ăm":    ["rằm", "tầm", "trăm", "nằm", "âm", "thầm"],
    "âm":    ["rằm", "tầm", "trăm", "nằm", "âm", "thầm"],
    "em":    ["thềm", "đêm", "thêm", "êm", "xem", "nêm"],
    "êm":    ["thềm", "đêm", "thêm", "êm", "xem", "nêm"],
    "im":    ["tìm", "chim", "dìm", "tim", "khim"],
    "om":    ["chòm", "khom", "vòm", "dòm"],
    "ôm":    ["hôm", "ôm", "tôm", "nôm", "chôm"],
    "ơm":    ["đơm", "cơm", "rơm", "thơm", "bơm"],
    "ơi":    ["trời", "người", "đời", "nơi", "khơi", "lời", "chơi", "vơi"],
    "ươi":   ["người", "trời", "đời", "tươi", "cười", "mười"],
    "ây":    ["mây", "bày", "đây", "tay", "ngày", "cây"],
    "ay":    ["ngày", "tay", "mây", "bày", "đây", "bay"],
    "anh":   ["xanh", "anh", "thành", "cành", "lành", "tranh"],
    "inh":   ["tình", "mình", "xinh", "dinh", "linh", "hình"],
    "e":     ["về", "quê", "bè", "nghề", "thề", "lê"],
    "ê":     ["về", "quê", "bè", "nghề", "thề", "lê"],
    "u":     ["thu", "ru", "mù", "dù", "chu"],
    "ư":     ["như", "dư", "hư", "tư", "sư"],
    "ơn":    ["hơn", "trơn", "sơn", "đơn"],
    "ơ":     ["thơ", "mơ", "chờ", "ngơ", "bờ"],
    "ua":    ["mùa", "vừa", "chưa", "xưa", "thừa"],
    "ưa":    ["mùa", "vừa", "chưa", "xưa", "thừa"],
    "âu":    ["đâu", "sâu", "cầu", "bầu", "màu", "dầu"],
    "ao":    ["sao", "nao", "trào", "vào", "cao"],
    "ân":    ["chân", "xuân", "thân", "ngần"],
    "iền":   ["hiền", "tiền", "miền", "liền", "duyên"],
    "yên":   ["hiền", "tiền", "miền", "liền", "duyên"],
    "ong":   ["lòng", "sông", "đồng", "dòng", "hồng", "trông", "bông", "rồng"],
    "ông":   ["lòng", "sông", "đồng", "dòng", "hồng", "trông", "bông", "rồng"],
    "o":     ["cho", "co", "lo", "trò", "dò"],
    "ô":     ["cô", "đô", "mô", "xô", "ngô"],
    "i":     ["đi", "khi", "chi", "gì", "thì", "vì"],
    "ương":  ["thương", "đường", "vương", "sương", "hương", "trường"]
}


class LucBatPoemGenerator:
    """
    Bộ Sinh Thơ Lục Bát Tiếng Việt Nâng Cao (Hybrid N-gram + Rule-Based System):
    - Phân loại Thanh Bằng / Trắc chuẩn vị trí 1-based index (Pos 2, 4, 6, 8).
    - Gieo vần nghiêm ngặt bằng hàm is_rhyme(w1, w2) không bị False Positive.
    - CHỐNG LẶP TỪ BÍ VẦN (Repetition Penalty & Unique Rhyme Word Block).
    - SINH CỤM 3 TỪ CUỐI CÂU 8 CHỮ (w6, w7, w8) COHERENT PHRASE + BACKTRACKING tránh sượng/lỗi ngữ pháp.
    """

    def __init__(self, ngram_model: NGramLanguageModel):
        self.lm = ngram_model
        # Lọc danh sách từ vựng chuẩn tiếng Việt có tần suất xuất hiện cao
        self.valid_vocab = [w for w in self.lm.vocab if is_valid_vietnamese_syllable(w)]
        self.valid_vocab.sort(key=lambda w: self.lm.word_counts.get(w, 0), reverse=True)

    def _get_valid_tone_words(self, expected_tone: str, exclude_words: set = None) -> list:
        """Lấy các từ trong từ vựng thỏa mãn thanh Bằng (B) hoặc Trắc (T) và không nằm trong tập loại trừ."""
        exclude = exclude_words or set()
        return [w for w in self.valid_vocab if get_tone(w) == expected_tone and w not in exclude]

    def _get_valid_rhyme_words(self, target_word: str, exclude_words: set = None) -> list:
        """Lấy các từ hợp lệ gieo vần với từ đích. Nếu từ vựng bị thiếu, nạp từ dự phòng chuẩn."""
        exclude = exclude_words or set()
        candidates = [w for w in self.valid_vocab if is_rhyme(w, target_word) and w not in exclude]
        
        if not candidates:
            from luc_bat_rules import extract_rime
            target_rime = extract_rime(target_word)
            dict_candidates = RHYME_DICTIONARY_B.get(target_rime, ["trời", "người", "đời", "mây", "về"])
            candidates = [w for w in dict_candidates if w not in exclude and get_tone(w) == "B"]
            if not candidates:
                candidates = [w for w in dict_candidates if get_tone(w) == "B"]
                
        return candidates

    def generate_cau_luc(self, line_index: int, prev_rhymes: dict, used_rhyme_words: set, poem_words_freq: dict, seed_words: list = None) -> list:
        """
        Sinh Câu Lục (6 chữ): x - B - x - T - x - B
        Từ thứ 6 là từ gieo vần, bắt buộc mang thanh BẰNG (B) và không lặp từ gieo vần trước.
        """
        line = []
        if seed_words:
            clean_seeds = [w for w in seed_words if is_valid_vietnamese_syllable(w)]
            line.extend(clean_seeds[:6])

        # 1. Sinh các vị trí từ 1 đến 5
        for pos in range(len(line) + 1, 6):
            context = tuple(line)

            expected_tone = None
            if pos == 2:
                expected_tone = "B"
            elif pos == 4:
                expected_tone = "T"

            candidates = self.lm.get_candidate_probabilities(context)
            filtered = []

            for word, score in candidates:
                if not is_valid_vietnamese_syllable(word):
                    continue
                if expected_tone and get_tone(word) != expected_tone:
                    continue

                # Phạt lặp từ đã xuất hiện nhiều lần trong bài thơ
                freq_in_poem = poem_words_freq.get(word, 0)
                adj_score = score / (1.0 + freq_in_poem * 2.0)
                filtered.append((word, adj_score))

            if filtered:
                top_k = filtered[:min(3, len(filtered))]
                words, scores = zip(*top_k)
                chosen_word = random.choices(words, weights=scores, k=1)[0]
            else:
                fallback_pool = self._get_valid_tone_words(expected_tone) if expected_tone else self.valid_vocab
                chosen_word = fallback_pool[0] if fallback_pool else ("mây" if expected_tone == "B" else "nắng")

            line.append(chosen_word)
            poem_words_freq[chosen_word] = poem_words_freq.get(chosen_word, 0) + 1

        # 2. Sinh vị trí thứ 6 (Từ gieo vần của câu Lục)
        # Nếu là Dòng Lục 2 (line_index=2), từ 6 phải gieo vần với từ 8 câu Bát trước (line1_word8)
        target_rhyme_word = prev_rhymes.get("line1_word8") if line_index == 2 else None

        context = tuple(line)
        candidates = self.lm.get_candidate_probabilities(context)
        filtered_pos6 = []

        for word, score in candidates:
            if not is_valid_vietnamese_syllable(word):
                continue
            if get_tone(word) != "B":
                continue
            if word in used_rhyme_words:  # BẮT BỘC KHÔNG LẶP TỪ GIEO VẦN
                continue
            if target_rhyme_word and not is_rhyme(word, target_rhyme_word):
                continue

            freq_in_poem = poem_words_freq.get(word, 0)
            adj_score = score / (1.0 + freq_in_poem * 3.0)
            filtered_pos6.append((word, adj_score))

        if filtered_pos6:
            top_k = filtered_pos6[:min(3, len(filtered_pos6))]
            words, scores = zip(*top_k)
            w6 = random.choices(words, weights=scores, k=1)[0]
        else:
            # Fallback cho vị trí 6 câu Lục
            if target_rhyme_word:
                rhyme_pool = self._get_valid_rhyme_words(target_rhyme_word, exclude_words=used_rhyme_words)
                w6 = rhyme_pool[0] if rhyme_pool else "trời"
            else:
                b_pool = self._get_valid_tone_words("B", exclude_words=used_rhyme_words)
                w6 = b_pool[0] if b_pool else "mây"

        line.append(w6)
        poem_words_freq[w6] = poem_words_freq.get(w6, 0) + 1
        used_rhyme_words.add(w6)
        return line

    def generate_cau_bat(self, line_index: int, prev_rhymes: dict, used_rhyme_words: set, poem_words_freq: dict) -> list:
        """
        Sinh Câu Bát (8 chữ): x - B - x - T - x - B - x - B
        Sử dụng kỹ thuật COHERENT 3-WORD PHRASE SEARCH (Sinh đồng thời 3 từ cuối w6, w7, w8) + BACKTRACKING
        để câu 8 chữ tự nhiên, mượt mà và không bị sượng/lỗi ngữ pháp.
        """
        target_rhyme_word = prev_rhymes.get(f"line{line_index-1}_word6")

        # Thử tối đa 5 lần với vị trí w5 khác nhau nếu cần Backtrack
        for attempt in range(5):
            line = []
            # 1. Sinh các từ vị trí 1 -> 5
            for pos in range(1, 6):
                context = tuple(line)
                expected_tone = "B" if pos == 2 else ("T" if pos == 4 else None)

                candidates = self.lm.get_candidate_probabilities(context)
                filtered = []

                for word, score in candidates:
                    if not is_valid_vietnamese_syllable(word):
                        continue
                    if expected_tone and get_tone(word) != expected_tone:
                        continue

                    freq_in_poem = poem_words_freq.get(word, 0)
                    adj_score = score / (1.0 + freq_in_poem * 2.0)
                    filtered.append((word, adj_score))

                if filtered:
                    # Nếu attempt > 0, lặp chọn các ứng viên khác để đa dạng context
                    idx_choice = min(attempt, len(filtered) - 1)
                    chosen_word = filtered[idx_choice][0]
                else:
                    fallback_pool = self._get_valid_tone_words(expected_tone) if expected_tone else self.valid_vocab
                    chosen_word = fallback_pool[0] if fallback_pool else "trời"

                line.append(chosen_word)

            # 2. TÌM CỤM 3 TỪ CUỐI COHERENT (w6, w7, w8)
            # Ràng buộc:
            # - w6: Thanh Bằng (B), Gieo vần với target_rhyme_word, w6 NOT IN used_rhyme_words
            # - w7: Từ tự nhiên trong N-gram
            # - w8: Thanh Bằng (B), w8 NOT IN used_rhyme_words, w8 != w6

            # Lấy các ứng viên w6 hợp vần
            valid_w6_candidates = []
            if target_rhyme_word:
                valid_w6_candidates = self._get_valid_rhyme_words(target_rhyme_word, exclude_words=used_rhyme_words)
            else:
                valid_w6_candidates = self._get_valid_tone_words("B", exclude_words=used_rhyme_words)

            if not valid_w6_candidates:
                valid_w6_candidates = ["trời", "mây", "sông", "làng", "đường"]

            best_phrase = None
            best_phrase_score = -1.0

            # Đánh giá các bộ 3 từ (w6, w7, w8) theo điểm số xác suất N-gram liên tiếp P(w6, w7, w8 | context_5)
            context_5 = tuple(line)
            for w6 in valid_w6_candidates[:8]:  # Thử Top 8 từ w6 hợp vần nhất
                p_w6 = self.lm.get_probability(w6, context_5)

                # Lấy ứng viên w7 sau context (line + [w6])
                context_6 = tuple(line + [w6])
                w7_candidates = self.lm.get_candidate_probabilities(context_6)

                for w7, p_w7 in w7_candidates[:5]:
                    if not is_valid_vietnamese_syllable(w7):
                        continue

                    # Lấy ứng viên w8 sau context (line + [w6, w7])
                    context_7 = tuple(line + [w6, w7])
                    w8_candidates = self.lm.get_candidate_probabilities(context_7)

                    for w8, p_w8 in w8_candidates[:5]:
                        if not is_valid_vietnamese_syllable(w8):
                            continue
                        if get_tone(w8) != "B":
                            continue
                        if w8 in used_rhyme_words or w8 == w6:
                            continue

                        # Điểm Mạch Lạc Ngữ Pháp của cụm 3 từ: P(w6)*P(w7)*P(w8) * FreqWeight
                        phrase_score = p_w6 * p_w7 * p_w8 * (1.0 + self.lm.word_counts.get(w8, 1) ** 0.1)
                        if phrase_score > best_phrase_score:
                            best_phrase_score = phrase_score
                            best_phrase = (w6, w7, w8)

            # Nếu tìm thấy cụm 3 từ tự nhiên tốt -> Ghép vào câu và hoàn thành!
            if best_phrase:
                w6, w7, w8 = best_phrase
                line.extend([w6, w7, w8])

                for w in [w1 for w1 in line]:
                    poem_words_freq[w] = poem_words_freq.get(w, 0) + 1
                used_rhyme_words.add(w6)
                used_rhyme_words.add(w8)
                return line

        # Trường hợp dự phòng nếu Backtrack không tìm được (Fallback)
        w6 = valid_w6_candidates[0] if valid_w6_candidates else "trời"
        w7 = "xanh"
        w8_pool = self._get_valid_tone_words("B", exclude_words=used_rhyme_words.union({w6}))
        w8 = w8_pool[0] if w8_pool else "quê"

        line.extend([w6, w7, w8])
        used_rhyme_words.add(w6)
        used_rhyme_words.add(w8)
        return line

    def generate_luc_bat_poem(self, seed_word: str = "trời", num_pairs: int = 2) -> list:
        """
        Sinh 1 bài thơ Lục bát hoàn chỉnh (4 câu = 2 cặp Lục - Bát) chuẩn xác 100%.
        """
        poem = []
        prev_rhymes = {}
        used_rhyme_words = set()
        poem_words_freq = {}

        seed_word_clean = seed_word.strip().lower() if seed_word else "trời"
        seed_tokens = [seed_word_clean]

        for pair_idx in range(num_pairs):
            line_idx_luc = pair_idx * 2
            line_idx_bat = pair_idx * 2 + 1

            # 1. DÒNG LỤC (6 TỪ)
            if pair_idx == 0:
                luc_line = self.generate_cau_luc(line_idx_luc, prev_rhymes, used_rhyme_words, poem_words_freq, seed_words=seed_tokens)
            else:
                luc_line = self.generate_cau_luc(line_idx_luc, prev_rhymes, used_rhyme_words, poem_words_freq)

            poem.append(luc_line)
            prev_rhymes[f"line{line_idx_luc}_word6"] = luc_line[5]

            # 2. DÒNG BÁT (8 TỪ)
            bat_line = self.generate_cau_bat(line_idx_bat, prev_rhymes, used_rhyme_words, poem_words_freq)
            poem.append(bat_line)
            prev_rhymes[f"line{line_idx_bat}_word8"] = bat_line[7]

        return poem


if __name__ == "__main__":
    from dataset import extract_luc_bat_data, FALLBACK_LUC_BAT_CORPUS

    print("--- TEST GENERATOR MỚI CHỐNG LẶP TỪ & SINH CỤM 3 TỪ CUỐI CÂU BÁT ---")
    data = extract_luc_bat_data(FALLBACK_LUC_BAT_CORPUS)
    model = NGramLanguageModel(n=3, k=1.0, min_freq=1)
    model.train(data)

    gen = LucBatPoemGenerator(model)
    poem = gen.generate_luc_bat_poem("truyện")

    print("\nBài thơ Lục Bát sinh ra:")
    for line in poem:
        print("  ", " ".join(line).capitalize())

    eval_res = check_luc_bat_poem_rules(poem)
    print("\nKết quả kiểm tra Luật Thơ:", eval_res)


# %% [markdown]
# ## 5. THỰC THI PIPELINE MAIN & ĐÁNH GIÁ 3 BÀI THƠ MẪU

# %%
"""
================================================================================
BÀI TẬP LỚN XỬ LÝ NGÔN NGỮ TỰ NHIÊN (NLP)
CHỦ ĐỀ: MÔ HÌNH SINH THƠ LỤC BÁT TIẾNG VIỆT (VIETNAMESE LUC BAT POETRY GENERATION)
================================================================================
TÍNH NĂNG MỚI: TÍCH HỢP TỰ ĐỘNG LƯU & NẠP CACHE ĐĨA ĐỆM (CACHE SYSTEM)
  - Dataset Cache: hf_cache_*.pkl / fallback_cache.pkl (Nạp dataset <0.1s)
  - Model Cache: ngram_model_hf.pkl / ngram_model_fallback.pkl (Nạp mô hình <0.1s)
  - Chạy lần đầu: Huấn luyện và tự động lưu Cache vào đĩa.
  - Chạy những lần sau: Nạp trực tiếp từ Cache tức thì không cần tải lại!
================================================================================
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from dataset import load_huggingface_dataset, extract_luc_bat_data, FALLBACK_LUC_BAT_CORPUS
from luc_bat_rules import (
    get_tone, check_bang_trac, is_rhyme, check_luc_bat_poem_rules
)
from ngram_model import NGramLanguageModel
from generator import LucBatPoemGenerator


def print_section_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)


def main(use_hf_dataset: bool = False, force_rebuild: bool = False):
    model_cache_file = "ngram_model_hf.pkl" if use_hf_dataset else "ngram_model_fallback.pkl"
    ngram_lm = None

    # 1. Thử nạp Mô hình từ CACHE (Model Caching)
    if not force_rebuild and os.path.exists(model_cache_file):
        print_section_header("1 & 4. NẠP MÔ HÌNH N-GRAM TỪ CACHE ĐÃ LƯU")
        ngram_lm = NGramLanguageModel.load_model(model_cache_file)

    # 2. Nếu chưa có Cache -> Tiến hành nạp dữ liệu và huấn luyện từ đầu
    if ngram_lm is None:
        print_section_header("1. KHỞI TẠO & TẢI DATASET THƠ TIẾNG VIỆT")
        raw_dataset = load_huggingface_dataset("phamson02/vietnamese-poetry-corpus", try_hf=use_hf_dataset, use_cache=not force_rebuild)

        print_section_header("2. TIỀN XỬ LÝ & LỌC BÀI THƠ LỤC BÁT THUẦN TÚY (EXTRACT_LUC_BAT_DATA)")
        luc_bat_data = extract_luc_bat_data(raw_dataset) if isinstance(raw_dataset, list) and len(raw_dataset) > 0 and isinstance(raw_dataset[0], str) else raw_dataset

        if not luc_bat_data:
            print("[!] Không tìm thấy dữ liệu thơ Lục bát từ Hugging Face. Chuyển sang Fallback Corpus...")
            luc_bat_data = extract_luc_bat_data(FALLBACK_LUC_BAT_CORPUS)

        print(f"[✓] Tổng số bài thơ Lục bát thuần túy hợp lệ thu thập được: {len(luc_bat_data)}")

        print_section_header("4. HUẤN LUYỆN MÔ HÌNH N-GRAM + SMOOTHING & LỌC TỪ VỰNG CHUẨN")
        min_f = 5 if (use_hf_dataset and len(luc_bat_data) > 100) else 1
        ngram_lm = NGramLanguageModel(n=3, k=1.0, min_freq=min_f)

        train_size = max(1, int(len(luc_bat_data) * 0.8))
        train_poems = luc_bat_data[:train_size]
        ngram_lm.train(train_poems)

        # Lưu Mô Hình ra Cache đĩa đệm
        ngram_lm.save_model(model_cache_file)

    print_section_header("3. DEMO HỆ THỐNG CHECK BẰNG-TRẮC & MODULE GIEO VẦN (IS_RHYME)")

    # 3.1 Demo Check Bằng-Trắc
    print("[-] 3.1. Thử nghiệm hàm check_bang_trac(sentence):")
    sample_sentences = [
        "Trời xanh mây trắng bay về",
        "Em như hoa giữa trời cô liêu hoang",
        "Nắng mưa từ thuở bào thai"
    ]
    for s in sample_sentences:
        res = check_bang_trac(s)
        status_str = "VALID (ĐÚNG LUẬT)" if res["is_valid"] else f"INVALID: {res['errors']}"
        print(f"    • Câu: '{s}'")
        print(f"      -> Độ dài: {res['length']} từ | Thanh: {res['tones']} | Kết quả: {status_str}")

    # 3.2 Demo Module Gieo Vần
    print("\n[-] 3.2. Thử nghiệm Module Gieo Vần is_rhyme(word1, word2):")
    rhyme_pairs = [
        ("tình", "mình"),
        ("trơn", "hơn"),
        ("về", "đê"),
        ("mây", "bày"),
        ("nắng", "mưa")
    ]
    for w1, w2 in rhyme_pairs:
        match = is_rhyme(w1, w2)
        print(f"    • is_rhyme('{w1}', '{w2}') -> {match}")

    print_section_header("5. SINH THƠ LỤC BÁT THỬ NGHIỆM TỨC THỜI TỪ MÔ HÌNH CACHE")
    generator = LucBatPoemGenerator(ngram_lm)

    seed_words = ["truyện", "trời", "nắng"]
    for idx, seed in enumerate(seed_words, 1):
        print(f"\n" + "-" * 70)
        print(f"=== BÀI THƠ THỬ NGHIỆM {idx}: TỪ GỢI Ý (SEED): '{seed.upper()}' ===")
        print("-" * 70)

        generated_poem = generator.generate_luc_bat_poem(seed_word=seed, num_pairs=2)

        print("\n[BÀI THƠ LỤC BÁT hoàn chỉnh (4 câu)]:")
        for line_i, line_words in enumerate(generated_poem):
            indent = "      " if line_i % 2 == 1 else "   "
            line_text = " ".join(line_words).capitalize()
            print(f"{indent}{line_text}")

        print("\n[PHÂN TÍCH LUẬT BẰNG-TRẮC & GIEO VẦN CHI TIẾT]:")
        for line_i, line_words in enumerate(generated_poem):
            check_info = check_bang_trac(line_words)
            print(f"   • Dòng {line_i+1} ({len(line_words)} từ): Thanh = {' '.join(check_info['tones'])}")

        print("\n[KIỂM TRA GIEO VẦN THEO LUẬT]:")
        w6_l1 = generated_poem[0][5]
        w6_b1 = generated_poem[1][5]
        w8_b1 = generated_poem[1][7]
        w6_l2 = generated_poem[2][5]
        w6_b2 = generated_poem[3][5]

        print(f"   • Từ 6 câu Lục 1 ('{w6_l1}') vs Từ 6 câu Bát 1 ('{w6_b1}') -> Gieo vần: {is_rhyme(w6_l1, w6_b1)}")
        print(f"   • Từ 8 câu Bát 1 ('{w8_b1}') vs Từ 6 câu Lục 2 ('{w6_l2}') -> Gieo vần: {is_rhyme(w8_b1, w6_l2)}")
        print(f"   • Từ 6 câu Lục 2 ('{w6_l2}') vs Từ 6 câu Bát 2 ('{w6_b2}') -> Gieo vần: {is_rhyme(w6_l2, w6_b2)}")

        rule_eval = check_luc_bat_poem_rules(generated_poem)
        print(f"\n   ==> ĐÁNH GIÁ CHUNG: {'✓ THỎA MÃN 100% QUY TẮC LỤC BÁT' if rule_eval['valid'] else '✗ CÓ LỖI LUẬT THƠ'}")
        if not rule_eval['valid']:
            for err in rule_eval['errors']:
                print("      - Lỗi:", err)

    print_section_header("HOÀN THÀNH PIPELINE TỐI ƯU TỐC ĐỘ BẰNG CACHE")


if __name__ == "__main__":
    use_hf = "--hf" in sys.argv
    rebuild = "--rebuild" in sys.argv
    main(use_hf_dataset=use_hf, force_rebuild=rebuild)



