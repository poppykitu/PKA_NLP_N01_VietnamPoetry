"""
================================================================================
  MÔ-ĐUN BỘ LUẬT LOẠI TỪ NGỮ PHÁP TIẾNG VIỆT (VIETNAMESE POS GRAMMAR RULES)
  Tác giả: PKA NLP Team
  Mục đích: Cung cấp từ điển Đa Loại Từ (Polysemic Multi-POS Set), Ma trận chuyển tiếp
            ngữ pháp (POS Transition Matrix) và Bộ kiểm tra cú pháp 3-Tier POS Validator.
================================================================================
"""

import os
import sys
import pickle

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ------------------------------------------------------------------------------
# 1. TỪ ĐIỂN PHÂN LOẠI TỪ LOẠI (VIETNAMESE POS TAXONOMY DICTIONARY)
# ------------------------------------------------------------------------------
POS_TAXONOMY = {
    # R: Phó từ / Trạng từ chỉ thời gian, mức độ, tiếp diễn
    "R": {
        "vẫn", "đã", "sẽ", "đang", "cũng", "còn", "chẳng", "không", "chưa",
        "rất", "quá", "mãi", "luôn", "vừa", "mới", "từng", "hãy", "chớ"
    },

    # V: Động từ hành động, trạng thái, cảm xúc
    "V": {
        "bay", "rơi", "trôi", "đi", "về", "nhớ", "thương", "vương", "yêu",
        "mong", "chờ", "ngắm", "nghe", "thấy", "rủ", "mang", "nói", "cười",
        "khóc", "ngủ", "dậy", "bước", "qua", "đến", "chờ", "buồn", "sầu"
    },

    # N: Danh từ chung, danh từ chỉ sự vật, thiên nhiên, thời gian
    "N": {
        "trời", "mây", "sông", "núi", "đời", "người", "quê", "làng", "đường",
        "sương", "đêm", "ngày", "nhà", "sân", "hoa", "lá", "trăng", "sao",
        "tình", "duyên", "ngõ", "bờ", "bãi", "bến", "con", "mẹ", "cha", "anh", "em", "thương", "yêu"
    },

    # A: Tính từ chỉ đặc điểm, màu sắc, không gian, cảm xúc
    "A": {
        "xa", "cao", "dài", "rộng", "đầy", "xanh", "vàng", "hồng", "thắm",
        "tươi", "buồn", "sầu", "đẹp", "xinh", "ngọt", "đắng", "mặn", "nồng",
        "sâu", "vắng", "tím", "trắng", "ngát", "say", "thương", "yêu"
    },

    # P: Đại từ xưng hô, chỉ định
    "P": {
        "ta", "tôi", "em", "anh", "mẹ", "con", "người", "ai", "đâu", "nào",
        "đây", "đó", "này", "kia"
    },

    # E: Giới từ, hư từ liên kết
    "E": {
        "trên", "dưới", "trong", "ngoài", "giữa", "bên", "cùng", "với", "cho",
        "của", "từ", "tới", "sang", "vào", "về"
    }
}

# Tạo bảng tra ngược từ -> TẬP CÁC LOẠI TỪ KHẢ DĨ (Multi-POS Tag Set)
WORD_TO_POS_SET = {}
for pos_tag, words in POS_TAXONOMY.items():
    for w in words:
        w_clean = w.lower()
        if w_clean not in WORD_TO_POS_SET:
            WORD_TO_POS_SET[w_clean] = set()
        WORD_TO_POS_SET[w_clean].add(pos_tag)

# Nạp từ điển 29,224 từ vựng đã gán nhãn tự động từ pos_dict_full.pkl nếu có
POS_CACHE_FILE = "pos_dict_full.pkl"
if os.path.exists(POS_CACHE_FILE):
    try:
        with open(POS_CACHE_FILE, "rb") as f:
            full_pos_dict = pickle.load(f)
            for w, tags in full_pos_dict.items():
                if w not in WORD_TO_POS_SET:
                    WORD_TO_POS_SET[w] = set()
                WORD_TO_POS_SET[w].update(tags)
    except Exception:
        pass

# ------------------------------------------------------------------------------
# 2. MA TRẬN QUY TẮC CHUYỂN TIẾP NGỮ PHÁP (POS TRANSITION MATRIX)
# Key: POS của từ đứng trước -> Value: Tập hợp các POS HỢP LỆ được phép đứng sau
# ------------------------------------------------------------------------------
VALID_POS_TRANSITIONS = {
    # Phó từ ("vẫn", "đã") BẮT BUỘC đi với Động từ / Tính từ. CẤM Danh từ ("vẫn trời")!
    "R": {"V", "A"},

    # Động từ ("bay", "ngắm") đi với Động từ hướng, Trạng/Tính từ, Danh từ ("bay xa", "ngắm mây"). CẤM ("bay trời")!
    "V": {"V", "A", "N", "E"},

    # Danh từ ("sân", "đường") đi với Danh từ ("sân nhà"), Tính từ ("đường xa"), Động từ ("sông trôi").
    "N": {"A", "V", "N", "E"},

    # Tính từ ("xanh", "cao") đi với Tính từ ("xanh thắm"), Danh từ ("xanh trời").
    "A": {"A", "N", "V", "E"},

    # Giới từ ("trên", "dưới") BẮT BUỘC đi với Danh từ / Đại từ ("trên trời", "trong làng").
    "E": {"N", "P", "A"},

    # Đại từ ("anh", "em") đi với Động từ ("anh yêu"), Tính từ ("em đẹp"), Phó từ ("anh đã").
    "P": {"V", "A", "R", "N"}
}

# ------------------------------------------------------------------------------
# 3. CÁC HÀM TIỆN ÍCH KIỂM TRA ĐA TỪ LOẠI (MULTI-POS VALIDATOR)
# ------------------------------------------------------------------------------
def get_word_pos_set(word: str) -> set:
    """
    Trả về TẬP LOẠI TỪ KHẢ DĨ (Set of POS tags) của từ (Ví dụ: 'thương' -> {'V', 'N', 'A'}).
    Nếu từ chưa có trong từ điển, mặc định trả về {'N'}.
    """
    w_clean = word.lower().strip(".,!?:;\"'()[]")
    return WORD_TO_POS_SET.get(w_clean, {"N"})


def is_pos_sequence_valid(prev_word: str, current_word: str, llm_pos_tag: str = None) -> bool:
    """
    Kiểm tra xem cặp 2 từ (prev_word, current_word) có THỎA MÃN LUẬT TỪ LOẠI hay không
    bằng thuật toán Giao Tập Hợp (Intersection Check).
    """
    pos_prev_set = get_word_pos_set(prev_word)

    # Nếu có nhãn POS động từ LLM (Tier 1 Gemma JSON Schema), ưu tiên dùng nhãn LLM
    if llm_pos_tag:
        pos_curr_set = {llm_pos_tag}
    else:
        pos_curr_set = get_word_pos_set(current_word)

    # Tính tập hợp các POS hợp lệ có thể đứng sau prev_word
    allowed_next_pos = set()
    for p in pos_prev_set:
        allowed_next_pos.update(VALID_POS_TRANSITIONS.get(p, {"V", "N", "A", "R", "E", "P"}))

    # Loại trừ trực tiếp các cặp cụm từ vô nghĩa cụ thể
    invalid_exact_pairs = {
        ("vẫn", "trời"), ("vẫn", "mây"), ("vẫn", "sông"), ("vẫn", "núi"),
        ("bay", "trời"), ("bay", "đời"), ("bay", "người"),
        ("đã", "trời"), ("đã", "sông")
    }

    if (prev_word.lower(), current_word.lower()) in invalid_exact_pairs:
        return False

    # Giao của tập POS hiện tại với tập POS hợp lệ phải khác Rỗng
    return len(pos_curr_set.intersection(allowed_next_pos)) > 0


def filter_valid_followers(prev_word: str, candidate_words: list) -> list:
    """
    Lọc danh sách các từ ứng viên candidate_words, chỉ giữ lại những từ
    THỎA MÃN 100% LUẬT LOẠI TỪ khi đứng sau prev_word.
    """
    return [w for w in candidate_words if is_pos_sequence_valid(prev_word, w)]
