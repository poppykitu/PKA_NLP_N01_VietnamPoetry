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


# Ngưỡng từ vựng tối thiểu: nếu cache có ít hơn giá trị này thì coi là STALE và rebuild
MIN_VOCAB_HF = 300    # Mô hình train từ HF dataset phải có ít nhất 300 từ
MIN_VOCAB_FALLBACK = 50  # Mô hình fallback có ít nhất 50 từ


def main(use_hf_dataset: bool = False, force_rebuild: bool = False):
    model_cache_file = "ngram_model_hf.pkl" if use_hf_dataset else "ngram_model_fallback.pkl"
    ngram_lm = None
    min_vocab = MIN_VOCAB_HF if use_hf_dataset else MIN_VOCAB_FALLBACK

    # 1. Thử nạp Mô hình từ CACHE (Model Caching)
    if not force_rebuild and os.path.exists(model_cache_file):
        print_section_header("1 & 4. NẠP MÔ HÌNH N-GRAM TỪ CACHE ĐÃ LƯU")
        candidate = NGramLanguageModel.load_model(model_cache_file)

        # Kiểm tra cache có đủ lớn không (tránh dùng cache STALE từ fallback)
        # Và kiểm tra cache có KN counters không (cache cũ Laplace-only cần rebuild)
        if candidate is not None and candidate.vocab_size >= min_vocab and candidate.num_unique_bigrams > 0:
            ngram_lm = candidate
        elif candidate is not None:
            if candidate.num_unique_bigrams == 0:
                print(f"[!] Cache '{model_cache_file}' là phiên bản cũ (Laplace-only, chưa có Kneser-Ney).")
            else:
                print(f"[!] Cache '{model_cache_file}' quá nhỏ (vocab={candidate.vocab_size} < {min_vocab} từ).")
            print(f"[!] Tiến hành REBUILD với Kneser-Ney Smoothing...")

    # 2. Nếu chưa có Cache hoặc Cache STALE -> Tiến hành nạp dữ liệu và huấn luyện từ đầu
    if ngram_lm is None:
        print_section_header("1. KHỞI TẠO & TẢI DATASET THƠ TIẾNG VIỆT")
        raw_dataset = load_huggingface_dataset("phamson02/vietnamese-poetry-corpus", try_hf=use_hf_dataset, use_cache=not force_rebuild)

        print_section_header("2. TIỀN XỬ LÝ & LỌC BÀI THƠ LỤC BÁT THUẦN TÚY (EXTRACT_LUC_BAT_DATA)")
        luc_bat_data = extract_luc_bat_data(raw_dataset) if isinstance(raw_dataset, list) and len(raw_dataset) > 0 and isinstance(raw_dataset[0], str) else raw_dataset

        if not luc_bat_data:
            print("[!] Không tìm thấy dữ liệu thơ Lục bát từ Hugging Face. Chuyển sang Fallback Corpus...")
            luc_bat_data = extract_luc_bat_data(FALLBACK_LUC_BAT_CORPUS)

        print(f"[✓] Tổng số bài thơ Lục bát thuần túy hợp lệ thu thập được: {len(luc_bat_data)}")

        print_section_header("4. HUẤN LUYỆN MÔ HÌNH N-GRAM (KNESER-NEY SMOOTHING) & LỌC TỪ VỰNG")
        min_f = 5 if (use_hf_dataset and len(luc_bat_data) > 100) else 1
        ngram_lm = NGramLanguageModel(n=3, k=0.1, min_freq=min_f, discount=0.75)

        train_size = max(1, int(len(luc_bat_data) * 0.8))
        train_poems = luc_bat_data[:train_size]
        test_poems  = luc_bat_data[train_size:]
        ngram_lm.train(train_poems)

        # Đánh giá Overfitting ngay sau khi train
        if test_poems:
            ngram_lm.evaluate_overfitting(train_poems, test_poems)
        else:
            print("[!] Không đủ dữ liệu để tách test set, bỏ qua đánh giá overfitting.")

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

        generated_poem, best_eval, _ = generator.generate_best_poem(seed_word=seed, num_pairs=2, num_candidates=5)

        print(f"\n[BÀI THƠ LỤC BÁT XUẤT SẮC NHẤT ĐƯỢC MÔ HÌNH LỰA CHỌN (ĐIỂM TỔNG: {best_eval['total_score']}/100)]:")
        for line_i, line_words in enumerate(generated_poem):
            indent = "      " if line_i % 2 == 1 else "   "
            line_text = " ".join(line_words).capitalize()
            print(f"{indent}{line_text}")

        print("\n[BẢNG TỰ ĐÁNH GIÁ VÀ PHÂN TÍCH CHẤT LƯỢNG 5 TIÊU CHÍ]:")
        print(f"   1. Điểm Luật & Âm Điệu (25đ): {best_eval['rule_score']}/25.0")
        print(f"   2. Điểm Nhịp Đôi PMI (25đ)  : {best_eval['couplet_score']}/25.0")
        print(f"   3. Điểm Từ Vựng Thi Ca (20đ): {best_eval['poetic_score']}/20.0")
        print(f"   4. Điểm Anti-Repetition (15đ): {best_eval['repetition_score']}/15.0")
        print(f"   5. Điểm Mượt Mà Toàn Bài(15đ): {best_eval['coherence_score']}/15.0")

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
