"""
================================================================================
  KỊCH BẢN PHÂN LOẠI TỪ VỰNG TẬP THƠ BẰNG GOOGLE/GEMMA-4-12B-QAT LOCAL AI (LM STUDIO)
  Tác giả: PKA NLP Team
  Mục đích: Sử dụng mô hình AI Local google/gemma-4-12b-qat qua API LM Studio
            với định dạng JSON Schema để phân loại 100% chuẩn xác loại từ.
================================================================================
"""

import os
import re
import sys
import json
import pickle
import time
import requests
from dataset import load_huggingface_dataset

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class GemmaPOSClassifier:
    """
    Bộ Phân Loại Từ Loại Bằng Gemma-4-12B Local API (LM Studio)
    """
    def __init__(self, api_url: str = "http://127.0.0.1:1234/v1/chat/completions", model_name: str = "google/gemma-4-12b-qat"):
        self.api_url = api_url
        self.model_name = model_name

    def classify_batch_words_gemma(self, words_batch: list) -> dict:
        """
        Gửi danh sách các từ qua API LM Studio cho Gemma-4-12B phân loại loại từ
        (POS Tag: N - Danh từ, V - Động từ, A - Tính từ, R - Phó từ, P - Đại từ, E - Giới từ)
        bằng JSON Schema Enforced Format.
        """
        words_str = ", ".join(words_batch)
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "Bạn là chuyên gia Ngôn ngữ học Tiếng Việt. Mỗi từ Tiếng Việt có thể có NHIỀU loại từ (Polysemy). Hãy phân tích TẤT CẢ các loại từ khả dĩ cho từng từ dưới dạng mảng (list). Trả về 1 JSON object dạng: {\"classified_words\": [{\"word\": \"bọc\", \"pos\": [\"V\", \"N\"]}]}"
                },
                {
                    "role": "user",
                    "content": f"Hãy phân loại TẤT CẢ loại từ khả dĩ (POS Tags: N - Danh từ, V - Động từ, A - Tính từ, R - Phó từ, P - Đại từ, E - Giới từ) cho các từ sau: {words_str}"
                }
            ],
            "temperature": 0.1
        }

        try:
            res = requests.post(self.api_url, json=payload, timeout=300)
            if res.status_code != 200:
                print(f"   [LM Studio HTTP {res.status_code}] {res.text[:200]}")
                return {}
            res_data = res.json()
            content = res_data['choices'][0]['message']['content'].strip()
            if not content:
                print(f"   [Gemma Notice] Phản hồi rỗng từ LM Studio cho batch này.")
                return {}
            if content.startswith("```"):
                content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
                content = re.sub(r"\n?```$", "", content).strip()
            
            # Tìm chuỗi JSON trong content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            raw_json = json.loads(content)
            result = {}
            for item in raw_json.get('classified_words', []):
                w = item['word'].lower().strip()
                raw_pos = item.get('pos', ["N"])
                pos_set = set(raw_pos) if isinstance(raw_pos, list) else {str(raw_pos)}
                result[w] = {p.upper().strip() for p in pos_set}
            return result
        except Exception as e:
            print(f"   [Gemma Notice] Thông báo API ({e})...")
            return {}


def build_full_pos_taxonomy_gemma():
    print("=" * 80)
    print("[*] BẮT ĐẦU PHÂN LOẠI 100% TỪ VỰNG BẰNG GOOGLE/GEMMA-4-12B-QAT (LM STUDIO)...")
    print("=" * 80)

    classifier = GemmaPOSClassifier()
    corpus = load_huggingface_dataset(try_hf=True)

    # Trích xuất toàn bộ các từ duy nhất trong tập thơ
    all_vocab = set()
    for poem in corpus[:2000]:
        for line in poem:
            words = line if isinstance(line, list) else str(line).split()
            for w in words:
                clean_w = w.lower().strip(".,!?:;\"'()[]")
                if clean_w and len(clean_w) > 1:
                    all_vocab.add(clean_w)

    print(f"[*] Tổng số từ vựng duy nhất trích xuất từ tập thơ: {len(all_vocab):,} từ.")
    print(f"[*] Đang gửi các batch từ vựng đến local API Gemma-4-12B (http://127.0.0.1:1234)...")

    vocab_list = sorted(list(all_vocab))
    batch_size = 5
    output_pickle = "pos_dict_gemma.pkl"

    # Nạp lại checkpoint đã có nếu có sẵn
    gemma_pos_dict = {}
    if os.path.exists(output_pickle):
        try:
            with open(output_pickle, "rb") as f:
                gemma_pos_dict = pickle.load(f)
            print(f"[*] Đã nạp checkpoint trước đó: {len(gemma_pos_dict):,} từ đã phân loại.")
        except Exception:
            pass

    start_time = time.time()
    batch_idx = 0
    for i in range(0, len(vocab_list), batch_size):
        batch = vocab_list[i:i + batch_size]
        # Bỏ qua những từ đã được phân loại trong checkpoint
        unprocessed_batch = [w for w in batch if w not in gemma_pos_dict]
        if not unprocessed_batch:
            continue

        batch_idx += 1
        res = classifier.classify_batch_words_gemma(unprocessed_batch)
        if res:
            gemma_pos_dict.update(res)
            print(f"   [✓ Gemma-4-12B API] Đã phân loại xong batch {batch_idx} ({len(gemma_pos_dict)}/{len(vocab_list)} từ).")

            # Lưu checkpoint cứ sau mỗi 5 batch
            if batch_idx % 5 == 0:
                with open(output_pickle, "wb") as f:
                    pickle.dump(gemma_pos_dict, f)
                # Cập nhật file JSON liên tục
                json_export = {}
                for word, pos_set in gemma_pos_dict.items():
                    json_export[word] = list(pos_set)
                with open("pos_dict_gemma.json", "w", encoding="utf-8") as f:
                    json.dump(json_export, f, ensure_ascii=False, indent=2)
        else:
            print(f"   [Notice] Bỏ qua batch {batch_idx} bị lỗi API và tiếp tục batch tiếp theo...")
            continue

    if gemma_pos_dict:
        with open(output_pickle, "wb") as f:
            pickle.dump(gemma_pos_dict, f)

        # Xuất ra JSON readable
        json_export = {}
        for word, pos_set in gemma_pos_dict.items():
            json_export[word] = list(pos_set)
        with open("pos_dict_gemma.json", "w", encoding="utf-8") as f:
            json.dump(json_export, f, ensure_ascii=False, indent=2)

        print(f"\n[✓] BÁO CÁO HOÀN THÀNH:")
        print(f"    • Số từ vựng đã phân loại bằng Gemma-4-12B: {len(gemma_pos_dict):,} từ")
        print(f"    • File lưu trữ persistence chuẩn AI: '{output_pickle}'")
        print(f"    • File JSON readable: 'pos_dict_gemma.json'")
        print(f"    • Tổng thời gian thực hiện: {time.time() - start_time:.2f} giây")
        print("=" * 80)


if __name__ == "__main__":
    build_full_pos_taxonomy_gemma()
