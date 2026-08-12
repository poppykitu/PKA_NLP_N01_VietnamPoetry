import os
import re
import sys
import pickle
import unicodedata

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CACHE_FILE_PATH = "luc_bat_data_cache.pkl"

# ==============================================================================
# BỘ DỮ LIỆU DỰ PHÒNG (FALLBACK CORPUS THƠ LỤC BÁT)
# ==============================================================================
FALLBACK_LUC_BAT_CORPUS = [
    """Trăm năm trong cõi người ta
Chữ tài chữ mệnh khéo là ghét nhau
Trải qua một cuộc bể dâu
Những điều trông thấy mà đau đứt lòng""",

    """Thân em như chẽn lúa đòng đòng
Phất phơ dưới ngọn nắng hồng ban mai
Nắng mưa từ thuở bào thai
Nuôi con khôn lớn đắng cay nguyện trì""",

    """Cánh cò bay cả cõi trời
Lúa reo ngàn dặm nụ cười đơm hoa
Sông xanh nối dải quê nhà
Tình quê gắn bó thiết tha trọn đời""",

    """Nắng hè buông nhẹ thềm hoa
Đêm nay trăng sáng ngàn xa mây mờ
Gió về ru nhẹ giấc mơ
Đường xưa kỷ niệm đợi chờ người sang""",

    """Công cha như núi Thái Sơn
Nghĩa mẹ như nước trong nguồn chảy ra
Một lòng thờ mẹ kính cha
Cho tròn chữ hiếu mới là đạo con""",

    """Đêm mưa nghe tiếng thở dài
Sương rơi lành lạnh u hoài ngàn năm
Đèn khuya le lói trong đêm
Thương ai một bóng âm thầm đợi trông""",

    """Bên sông gió thổi rào rạt
Mây trôi lặng lẽ ngút ngàn đường xa
Tình xưa như một bài ca
Nhớ ai năm tháng thiết tha điệu đàn"""
]


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


def is_valid_luc_bat_structure(lines: list) -> bool:
    """Kiểm tra cấu trúc Thơ Lục Bát thuần túy: Các cặp câu luân phiên 6 - 8 từ, chẵn dòng."""
    cleaned_lines = [clean_vietnamese_line(l) for l in lines if clean_vietnamese_line(l)]
    if len(cleaned_lines) < 2 or len(cleaned_lines) % 2 != 0:
        return False

    for i, line in enumerate(cleaned_lines):
        words = line.split()
        expected_len = 6 if i % 2 == 0 else 8
        if len(words) != expected_len:
            return False

    return True


def extract_luc_bat_data(raw_corpus: list) -> list:
    """Lọc các bài thơ Lục bát thuần túy từ tập dữ liệu thô."""
    luc_bat_poems = []

    for item in raw_corpus:
        if isinstance(item, str):
            lines = item.strip().split("\n")
        elif isinstance(item, list):
            lines = item
        else:
            continue

        lines = [clean_vietnamese_line(l) for l in lines if clean_vietnamese_line(l)]

        if is_valid_luc_bat_structure(lines):
            tokenized_poem = [tokenize_line(l) for l in lines]
            luc_bat_poems.append(tokenized_poem)

    return luc_bat_poems


def load_huggingface_dataset(dataset_name: str = "phamson02/vietnamese-poetry-corpus", try_hf: bool = False, use_cache: bool = True) -> list:
    """
    Tải Dataset có TÍCH HỢP LƯU CACHE đĩa đệm (luc_bat_data_cache.pkl).
    Nếu cache tồn tại, nạp ngay lập tức (<0.1 giây) cho những lần chạy sau.
    """
    cache_path = f"hf_cache_{dataset_name.replace('/', '_')}.pkl" if try_hf else "fallback_cache.pkl"

    # Kiểm tra Cache nếu sử dụng
    if use_cache and os.path.exists(cache_path):
        try:
            print(f"[*] Nạp dữ liệu thơ Lục bát đã xử lý từ CACHE ('{cache_path}')...")
            with open(cache_path, "rb") as f:
                cached_data = pickle.load(f)
            print(f"[✓] Nạp thành công {len(cached_data)} bài thơ Lục bát từ CACHE!")
            return cached_data
        except Exception as e:
            print(f"[!] Không thể đọc cache ({e}), sẽ xử lý lại dữ liệu...")

    # Nếu không có cache -> Xử lý dữ liệu
    if not try_hf:
        print("[*] Đang xử lý Tập Dữ Liệu Thơ Lục Bát Dự Phòng (Fallback Corpus)...")
        raw_poems = FALLBACK_LUC_BAT_CORPUS
    else:
        try:
            from datasets import load_dataset
            print(f"[*] Đang tải dataset '{dataset_name}' từ Hugging Face...")
            ds = load_dataset(dataset_name, split="train")
            raw_poems = []
            for row in ds:
                text = row.get("text") or row.get("content") or row.get("poem") or ""
                if text:
                    raw_poems.append(text)
            print(f"[✓] Tải thành công {len(raw_poems)} bài thơ thô từ Hugging Face.")
        except Exception as e:
            print(f"[!] Không thể tải Hugging Face dataset ({e}). Dùng Fallback Corpus...")
            raw_poems = FALLBACK_LUC_BAT_CORPUS

    # Lọc thơ Lục bát thuần túy
    luc_bat_data = extract_luc_bat_data(raw_poems)

    # Lưu Cache cho các lần chạy sau
    if use_cache and luc_bat_data:
        try:
            print(f"[*] Đang LƯU CACHE dữ liệu vào đĩa ('{cache_path}')...")
            with open(cache_path, "wb") as f:
                pickle.dump(luc_bat_data, f)
            print(f"[✓] Đã LƯU CACHE thành công!")
        except Exception as e:
            print(f"[!] Không thể ghi cache ({e}).")

    return luc_bat_data
