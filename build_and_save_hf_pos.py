from datasets import load_dataset
import pickle
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("[*] Đang nạp Từ Điển Tiếng Việt chuẩn từ Hugging Face 'tsdocode/vietnamese-dictionary'...")
ds = load_dataset("tsdocode/vietnamese-dictionary")["train"]

pos_map = {
    "danh từ": "N",
    "động từ": "V",
    "tính từ": "A",
    "đại từ": "P",
    "phó từ": "R",
    "trạng từ": "R",
    "phụ từ": "R",
    "trợ từ": "R",
    "giới từ": "PREP",
    "liên từ": "C",
    "kết từ": "C",
    "thán từ": "I",
    "cảm từ": "I",
    "số từ": "NUM",
    "định từ": "L",
}

mapped_words = {}
for item in ds:
    word = item["word"].strip().lower() if item["word"] else ""
    raw_pos = item["part_of_speech"].strip().lower() if item["part_of_speech"] else ""

    pos_code = pos_map.get(raw_pos, None)
    if not pos_code:
        for k, code in pos_map.items():
            if k in raw_pos:
                pos_code = code
                break

    if word and pos_code:
        if word not in mapped_words:
            mapped_words[word] = set()
        mapped_words[word].add(pos_code)

out_file = "hf_pos_dictionary.pkl"
with open(out_file, "wb") as f:
    pickle.dump(mapped_words, f)

print(f"[✓] Đã trích xuất và lưu Từ Điển Từ Loại Hugging Face '{out_file}' cho {len(mapped_words)} từ vựng Tiếng Việt!")
