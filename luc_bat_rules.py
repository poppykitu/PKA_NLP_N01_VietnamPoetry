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

def is_huyen_tone(word: str) -> bool:
    """Kiểm tra từ có mang Dấu Huyền hay không."""
    word = normalize_vietnamese(word)
    return any(c in HUYEN_CHARS for c in word)


def is_ngang_tone(word: str) -> bool:
    """Kiểm tra từ có phải Thanh Ngang (thanh Bằng không dấu) hay không."""
    word = normalize_vietnamese(word)
    return get_tone(word) == "B" and not is_huyen_tone(word)
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

        # Quy tắc Tiểu đối Bằng-Thanh (Tiếng 6 và Tiếng 8 phải đối lập giữa Ngang và Huyền)
        if tones[5] == "B" and tones[7] == "B":
            huyen_6 = is_huyen_tone(words[5])
            huyen_8 = is_huyen_tone(words[7])
            if huyen_6 == huyen_8:
                type_name = "Thanh Huyền" if huyen_6 else "Thanh Ngang"
                errors.append(
                    f"Lỗi Tiểu đối Bằng-Thanh: Tiếng thứ 6 ('{words[5]}') và Tiếng thứ 8 ('{words[7]}') "
                    f"của câu Bát không được cùng mang {type_name} (phải 1 Ngang, 1 Huyền)."
                )

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
