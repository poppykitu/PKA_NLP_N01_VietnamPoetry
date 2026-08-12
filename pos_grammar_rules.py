"""
================================================================================
  MÔ-ĐUN BỘ LUẬT LOẠI TỪ NGỮ PHÁP TIẾNG VIỆT (VIETNAMESE POS GRAMMAR RULES)
  Tác giả: PKA NLP Team
  Mục đích: Cung cấp từ điển loại từ (POS Taxonomy), Ma trận chuyển tiếp hợp lệ
            (POS Transition Matrix) và Bộ kiểm tra cú pháp 2 từ (Bigram POS Validator).
================================================================================
"""

import sys

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
        "khóc", "ngủ", "dậy", "bước", "qua", "đến", "chờ"
    },

    # N: Danh từ chung, danh từ chỉ sự vật, thiên nhiên, thời gian
    "N": {
        "trời", "mây", "sông", "núi", "đời", "người", "quê", "làng", "đường",
        "sương", "đêm", "ngày", "nhà", "sân", "hoa", "lá", "trăng", "sao",
        "tình", "duyên", "ngõ", "bờ", "bãi", "bến", "con", "mẹ", "cha", "anh", "em"
    },

    # A: Tính từ chỉ đặc điểm, màu sắc, không gian, cảm xúc
    "A": {
        "xa", "cao", "dài", "rộng", "đầy", "xanh", "vàng", "hồng", "thắm",
        "tươi", "buồn", "sầu", "đẹp", "xinh", "ngọt", "đắng", "mặn", "nồng",
        "sâu", "vắng", "tím", "trắng", "ngát", "say"
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

# Tạo bảng tra ngược từ -> POS Tag
WORD_TO_POS = {}
for pos_tag, words in POS_TAXONOMY.items():
    for w in words:
        WORD_TO_POS[w.lower()] = pos_tag

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
# 3. CÁC HÀM TIỆN ÍCH KIỂM TRA & LỌC TỪ THEO BỘ LUẬT LOẠI TỪ
# ------------------------------------------------------------------------------
def get_word_pos(word: str) -> str:
    """
    Trả về nhãn POS (R, V, N, A, P, E) của từ. Nếu từ chưa có trong từ điển, mặc định là N.
    """
    w_clean = word.lower().strip(".,!?:;\"'()[]")
    return WORD_TO_POS.get(w_clean, "N")


def is_pos_sequence_valid(prev_word: str, current_word: str) -> bool:
    """
    Kiểm tra xem cặp 2 từ (prev_word, current_word) có THỎA MÃN LUẬT TỪ LOẠI hay không.
    Ví dụ:
      - is_pos_sequence_valid("vẫn", "vương") -> True  (Phó từ R -> Động từ V)
      - is_pos_sequence_valid("vẫn", "trời")  -> False (Phó từ R -> Danh từ N -> VI PHẠM!)
      - is_pos_sequence_valid("bay", "xa")    -> True  (Động từ V -> Tính từ A)
      - is_pos_sequence_valid("bay", "trời")  -> False (Động từ V -> Danh từ N không ngữ cảnh -> VI PHẠM!)
    """
    pos_prev = get_word_pos(prev_word)
    pos_curr = get_word_pos(current_word)

    valid_next_pos = VALID_POS_TRANSITIONS.get(pos_prev, {"V", "N", "A", "R", "E", "P"})

    # Quy tắc ngoại lệ loại trừ trực tiếp các cặp cụm từ vô nghĩa cụ thể
    invalid_exact_pairs = {
        ("vẫn", "trời"), ("vẫn", "mây"), ("vẫn", "sông"), ("vẫn", "núi"),
        ("bay", "trời"), ("bay", "đời"), ("bay", "người"),
        ("đã", "trời"), ("đã", "sông")
    }

    if (prev_word.lower(), current_word.lower()) in invalid_exact_pairs:
        return False

    return pos_curr in valid_next_pos


def filter_valid_followers(prev_word: str, candidate_words: list) -> list:
        """
        Lọc danh sách các từ ứng viên candidate_words, chỉ giữ lại những từ
        THỎA MÃN 100% LUẬT LOẠI TỪ khi đứng sau prev_word.
        """
        return [w for w in candidate_words if is_pos_sequence_valid(prev_word, w)]
