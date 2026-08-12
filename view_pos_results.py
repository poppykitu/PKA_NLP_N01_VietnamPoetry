"""
================================================================================
  KỊCH BẢN XEM KẾT QUẢ PHÂN LOẠI TỪ LOẠI (POS CLASSIFICATION RESULT VIEWER)
  Tác giả: PKA NLP Team
  Mục đích: Đọc file persistence 'pos_dict_gemma.pkl' (và 'pos_dict_full.pkl')
            in ra bảng phân loại từ loại trực quan và xuất ra file 'pos_results.json'.
================================================================================
"""

import os
import sys
import json
import pickle

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

POS_NAMES = {
    "N": "Danh từ (Noun)",
    "V": "Động từ (Verb)",
    "A": "Tính từ (Adjective)",
    "R": "Phó từ/Trạng từ (Adverb)",
    "P": "Đại từ (Pronoun)",
    "E": "Giới từ (Preposition)"
}


def view_results(pkl_file: str = "pos_dict_gemma.pkl"):
    if not os.path.exists(pkl_file):
        pkl_file = "pos_dict_full.pkl"

    if not os.path.exists(pkl_file):
        print(f"[!] Chưa tìm thấy file kết quả '{pkl_file}'. Hãy chạy 'python build_full_pos_taxonomy.py' trước!")
        return

    print("=" * 80)
    print(f"[*] XEM KẾT QUẢ PHÂN LOẠI TỪ LOẠI TỪ FILE PERSISTENCE: '{pkl_file}'")
    print("=" * 80)

    with open(pkl_file, "rb") as f:
        pos_dict = pickle.load(f)

    # Chuyển đổi sang JSON readable
    json_export = {}
    for word, pos_set in pos_dict.items():
        pos_list = list(pos_set) if isinstance(pos_set, set) else [str(pos_set)]
        json_export[word] = [f"{p} ({POS_NAMES.get(p, 'Khác')})" for p in pos_list]

    # Lưu ra file JSON dễ đọc
    json_out_file = pkl_file.replace(".pkl", ".json")
    with open(json_out_file, "w", encoding="utf-8") as f:
        json.dump(json_export, f, ensure_ascii=False, indent=2)

    # In mẫu 40 từ đại diện lên Terminal
    print(f"[*] Tổng số từ vựng đã phân loại: {len(pos_dict):,} từ.")
    print(f"[✓] Đã xuất toàn bộ dữ liệu dễ đọc ra file: '{json_out_file}'\n")

    print(f"{'TỪ VỰNG':<25} | {'MÃ POS':<10} | {'TÊN LOẠI TỪ'}")
    print("-" * 65)

    sample_items = list(pos_dict.items())[:50]
    for word, pos_set in sample_items:
        pos_str = ", ".join(pos_set) if isinstance(pos_set, set) else str(pos_set)
        pos_name_str = ", ".join([POS_NAMES.get(p, "Khác") for p in pos_set]) if isinstance(pos_set, set) else POS_NAMES.get(str(pos_set), "")
        print(f"{word:<25} | {pos_str:<10} | {pos_name_str}")

    print("=" * 80)
    print(f"💡 Để xem TOÀN BỘ {len(pos_dict):,} từ phân loại, bạn hãy mở file JSON: '{json_out_file}'")


if __name__ == "__main__":
    view_results()
