"""
================================================================================
SECTION 6: ĐÁNH GIÁ OVERFITTING — KNESER-NEY vs LAPLACE SMOOTHING
================================================================================
Chạy file này độc lập để so sánh:
  - Train Perplexity vs Test Perplexity (phát hiện overfitting)
  - Laplace Smoothing (k=1.0) vs Kneser-Ney Smoothing (D=0.75)
  - Chất lượng thơ sinh ra từ mỗi mô hình

Cách chạy:
    python evaluate_overfitting.py         # Dùng Fallback corpus
    python evaluate_overfitting.py --hf    # Dùng HuggingFace dataset
================================================================================
"""

import sys
import os
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Import từ các module trong project
from dataset import load_huggingface_dataset, extract_luc_bat_data, FALLBACK_LUC_BAT_CORPUS
from ngram_model import NGramLanguageModel
from generator import LucBatPoemGenerator
from luc_bat_rules import check_luc_bat_poem_rules


def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    use_hf = "--hf" in sys.argv

    # =========================================================================
    # 1. Tải dữ liệu
    # =========================================================================
    print_section("1. TẢI DỮ LIỆU THƠ LỤC BÁT")
    raw_dataset = load_huggingface_dataset(
        "phamson02/vietnamese-poetry-corpus",
        try_hf=use_hf,
        use_cache=True
    )

    # raw_dataset có thể đã là danh sách bài tokenized nếu từ cache
    if raw_dataset and isinstance(raw_dataset[0], list) and isinstance(raw_dataset[0][0], list):
        luc_bat_data = raw_dataset  # đã tokenized
    else:
        luc_bat_data = extract_luc_bat_data(raw_dataset) if raw_dataset else []

    if not luc_bat_data:
        print("[!] Fallback sang Corpus dự phòng...")
        luc_bat_data = extract_luc_bat_data(FALLBACK_LUC_BAT_CORPUS)

    print(f"[✓] Tổng số bài Lục Bát: {len(luc_bat_data)}")

    # =========================================================================
    # 2. Tách Train / Test (80/20, shuffle để tránh bias thứ tự)
    # =========================================================================
    print_section("2. TÁCH TRAIN / TEST (80/20)")
    random.seed(42)
    data_shuffled = luc_bat_data[:]
    random.shuffle(data_shuffled)

    split = max(1, int(len(data_shuffled) * 0.8))
    train_data = data_shuffled[:split]
    test_data  = data_shuffled[split:]

    print(f"  Train: {len(train_data)} bài | Test: {len(test_data)} bài")

    if not test_data:
        print("[!] Dataset quá nhỏ (<2 bài), dùng train set làm test để tham khảo.")
        test_data = train_data

    # =========================================================================
    # 3. Huấn luyện Model 1: Laplace Smoothing (k=1.0)
    # =========================================================================
    print_section("3a. HUẤN LUYỆN MÔ HÌNH LAPLACE (k=1.0) — Baseline")
    min_f = 5 if (use_hf and len(train_data) > 100) else 1
    model_laplace = NGramLanguageModel(n=3, k=1.0, min_freq=min_f)
    model_laplace.train(train_data)

    # =========================================================================
    # 4. Huấn luyện Model 2: Kneser-Ney Smoothing (D=0.75)
    # =========================================================================
    print_section("3b. HUẤN LUYỆN MÔ HÌNH KNESER-NEY (D=0.75) — Improved")
    model_kn = NGramLanguageModel(n=3, k=0.1, min_freq=min_f, discount=0.75)
    model_kn.train(train_data)

    # =========================================================================
    # 5. Đánh giá Overfitting
    # =========================================================================
    print_section("4. ĐÁNH GIÁ OVERFITTING: LAPLACE vs KNESER-NEY")
    result = model_kn.evaluate_overfitting(train_data, test_data)

    # Tính thêm perplexity Laplace thủ công để so sánh đầy đủ
    train_ppl_laplace = model_laplace.compute_perplexity(train_data, use_kn=False)
    test_ppl_laplace  = model_laplace.compute_perplexity(test_data,  use_kn=False)
    gap_laplace = test_ppl_laplace / train_ppl_laplace if train_ppl_laplace > 0 else float('inf')

    print(f"\n  [Laplace riêng]  Train PPL: {train_ppl_laplace:.2f} | Test PPL: {test_ppl_laplace:.2f} | Gap: {gap_laplace:.3f}×")
    print(f"  [Kneser-Ney]     Train PPL: {result['train_ppl_kn']:.2f} | Test PPL: {result['test_ppl_kn']:.2f} | Gap: {result['gap_ratio_kn']:.3f}×")

    if result['gap_ratio_kn'] < gap_laplace:
        improvement = (gap_laplace - result['gap_ratio_kn']) / gap_laplace * 100
        print(f"\n  ✓ Kneser-Ney giảm overfitting gap {improvement:.1f}% so với Laplace!")
    else:
        print(f"\n  ⚠ Gap ratio tương đương (có thể do dataset quá nhỏ).")

    # =========================================================================
    # 6. So sánh chất lượng thơ sinh ra
    # =========================================================================
    print_section("5. SO SÁNH BÀI THƠ SINH RA")

    seeds = ["trời", "nắng", "truyện"]
    for seed in seeds:
        print(f"\n{'─' * 60}")
        print(f"  Seed: '{seed.upper()}'")
        print(f"{'─' * 60}")

        print("\n  [LAPLACE]")
        gen_laplace = LucBatPoemGenerator(model_laplace)
        poem_laplace = gen_laplace.generate_luc_bat_poem(seed, num_pairs=2)
        for i, line in enumerate(poem_laplace):
            indent = "        " if i % 2 == 1 else "     "
            print(f"{indent}{' '.join(line).capitalize()}")
        rules_l = check_luc_bat_poem_rules(poem_laplace)
        print(f"  → Luật thơ: {'✓ OK' if rules_l['valid'] else '✗ Lỗi: ' + '; '.join(rules_l['errors'][:2])}")

        print("\n  [KNESER-NEY]")
        gen_kn = LucBatPoemGenerator(model_kn)
        poem_kn = gen_kn.generate_luc_bat_poem(seed, num_pairs=2)
        for i, line in enumerate(poem_kn):
            indent = "        " if i % 2 == 1 else "     "
            print(f"{indent}{' '.join(line).capitalize()}")
        rules_kn = check_luc_bat_poem_rules(poem_kn)
        print(f"  → Luật thơ: {'✓ OK' if rules_kn['valid'] else '✗ Lỗi: ' + '; '.join(rules_kn['errors'][:2])}")

    print_section("HOÀN THÀNH ĐÁNH GIÁ OVERFITTING")
    print("  Kneser-Ney Smoothing đã thay thế Laplace trong ngram_model.py.")
    print("  Chạy main.py (--hf) để dùng mô hình KN mới cho toàn bộ pipeline.\n")


if __name__ == "__main__":
    main()
