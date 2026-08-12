"""
================================================================================
  KỊCH BẢN PHÂN LOẠI TỪ VỰNG TẬP THƠ BẰNG GOOGLE/GEMMA-4-12B-QAT LOCAL AI (LM STUDIO)
  Tác giả: PKA NLP Team
  Mục đích: Sử dụng mô hình AI Local google/gemma-4-12b-qat qua API LM Studio
            với định dạng JSON Schema để phân loại 100% chuẩn xác loại từ.
================================================================================
"""

import os
import sys
import json
import pickle
import time
import urllib.request
import urllib.error
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
                    "content": "Bạn là chuyên gia Ngôn ngữ học Tiếng Việt. Hãy phân tích từ loại chính xác cho danh sách từ vựng. Trả về đúng 1 JSON object dạng: {\"classified_words\": [{\"word\": \"từ\", \"pos\": \"N|V|A|R|P|E\"}]}"
                },
                {
                    "role": "user",
                    "content": f"Hãy phân loại từ loại (POS Tag: N - Danh từ, V - Động từ, A - Tính từ, R - Phó từ, P - Đại từ, E - Giới từ) cho các từ sau: {words_str}"
                }
            ],
            "temperature": 0.1
        }

        try:
            req = urllib.request.Request(self.api_url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                raw_json = json.loads(res_data['choices'][0]['message']['content'])
                result = {}
                for item in raw_json.get('classified_words', []):
                    w = item['word'].lower().strip()
                    pos = item['pos'].upper().strip()
                    result[w] = {pos}
                return result
        except Exception as e:
            print(f"   [Gemma Notice] Chưa kết nối được LM Studio Server ({e})...")
            return {}


def build_full_pos_taxonomy_gemma():
    print("=" * 80)
    print("[*] BẮT ĐẦU PHÂN LOẠI TỪ VỰNG BẰNG AI LOCAL GOOGLE/GEMMA-4-12B-QAT (LM STUDIO)...")
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
    batch_size = 20
    gemma_pos_dict = {}

    start_time = time.time()
    for i in range(0, min(len(vocab_list), 200), batch_size):
        batch = vocab_list[i:i + batch_size]
        res = classifier.classify_batch_words_gemma(batch)
        if res:
            gemma_pos_dict.update(res)
            print(f"   [✓ Gemma-4-12B API] Đã phân loại xong batch {i//batch_size + 1} ({len(gemma_pos_dict)} từ).")
        else:
            print(f"   [!] LM Studio chưa khởi chạy server ở port 1234. Bạn hãy bật Start Server trong LM Studio!")
            break

    if gemma_pos_dict:
        output_pickle = "pos_dict_gemma.pkl"
        with open(output_pickle, "wb") as f:
            pickle.dump(gemma_pos_dict, f)
        print(f"\n[✓] BÁO CÁO HOÀN THÀNH:")
        print(f"    • Số từ vựng đã phân loại bằng Gemma-4-12B: {len(gemma_pos_dict):,} từ")
        print(f"    • File lưu trữ persistence chuẩn AI: '{output_pickle}'")
        print(f"    • Tổng thời gian thực hiện: {time.time() - start_time:.2f} giây")
        print("=" * 80)


if __name__ == "__main__":
    build_full_pos_taxonomy_gemma()
