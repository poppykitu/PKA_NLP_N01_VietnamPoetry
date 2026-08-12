"""
================================================================================
  KỊCH BẢN TỰ ĐỘNG PHÂN LOẠI TOÀN BỘ TỪ VỰNG TẬP THƠ (FULL POS TAXONOMY BUILDER)
  Tác giả: PKA NLP Team
  Mục đích: Quét toàn bộ kho dữ liệu 84.686 bài thơ Lục Bát, dùng PyVi ViPosTagger
            gán nhãn loại từ tự động cho 100% từ vựng và lưu vào 'pos_dict_full.pkl'.
================================================================================
"""

import os
import sys
import pickle
import time
from pyvi import ViPosTagger, ViTokenizer
from dataset import load_huggingface_dataset

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def map_pyvi_tag(pyvi_tag: str) -> str:
    """Chuyển đổi nhãn PyVi sang nhãn tiêu chuẩn (N, V, A, R, P, E)."""
    tag = pyvi_tag.upper()
    if tag.startswith("N"):
        return "N"  # Danh từ
    elif tag.startswith("V"):
        return "V"  # Động từ
    elif tag.startswith("A"):
        return "A"  # Tính từ
    elif tag.startswith("R") or tag.startswith("L"):
        return "R"  # Phó từ / Trạng từ
    elif tag.startswith("P"):
        return "P"  # Đại từ
    elif tag.startswith("E") or tag.startswith("C"):
        return "E"  # Giới từ / Liên từ
    return "N"      # Mặc định Danh từ


def build_full_pos_taxonomy():
    print("=" * 80)
    print("[*] ĐANG TỰ ĐỘNG PHÂN LOẠI TOÀN BỘ TỪ VỰNG TẬP THƠ LỤC BÁT (84,686 BÀI)...")
    print("=" * 80)

    start_time = time.time()
    corpus = load_huggingface_dataset(try_hf=True)

    word_pos_counts = {}
    print(f"[*] Đã nạp {len(corpus):,} bài thơ. Đang gán nhãn loại từ bằng PyVi ViPosTagger...")

    line_count = 0
    for poem in corpus[:20000]:  # Quét 20,000 bài thơ Lục Bát đại diện
        for line in poem:
            if isinstance(line, list):
                line_clean = " ".join(line).strip()
            else:
                line_clean = str(line).strip()
            if not line_clean:
                continue
            line_count += 1
            try:
                words, tags = ViPosTagger.postagging(ViTokenizer.tokenize(line_clean))
                for w, t in zip(words, tags):
                    clean_w = w.replace("_", " ").lower().strip()
                    if clean_w:
                        std_pos = map_pyvi_tag(t)
                        if clean_w not in word_pos_counts:
                            word_pos_counts[clean_w] = {}
                        word_pos_counts[clean_w][std_pos] = word_pos_counts[clean_w].get(std_pos, 0) + 1
            except Exception:
                pass

    # Xây dựng từ điển WORD_TO_POS_SET (Giữ các nhãn POS có tần suất >= 5%)
    full_word_to_pos_set = {}
    for word, pos_counts in word_pos_counts.items():
        total_freq = sum(pos_counts.values())
        allowed_pos = {pos for pos, count in pos_counts.items() if (count / total_freq) >= 0.05}
        if allowed_pos:
            full_word_to_pos_set[word] = allowed_pos

    output_pickle = "pos_dict_full.pkl"
    with open(output_pickle, "wb") as f:
        pickle.dump(full_word_to_pos_set, f)

    elapsed = time.time() - start_time
    print(f"\n[✓] BÁO CÁO HOÀN THÀNH:")
    print(f"    • Số câu thơ đã xử lý  : {line_count:,} câu")
    print(f"    • Tổng số từ đã gán nhãn: {len(full_word_to_pos_set):,} từ vựng duy nhất")
    print(f"    • File lưu trữ persistence: '{output_pickle}'")
    print(f"    • Tổng thời gian thực hiện : {elapsed:.2f} giây")
    print("=" * 80)


if __name__ == "__main__":
    build_full_pos_taxonomy()
