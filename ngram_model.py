import math
import os
import sys
import pickle
import unicodedata
from collections import defaultdict, Counter

try:
    from pyvi import ViPosTagger, ViTokenizer
    HAS_PYVI = True
except ImportError:
    HAS_PYVI = False

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

VIETNAMESE_VOWELS = set("aăâeêioôơuưyàằầèềìòồờùừỳáắấéếíóốớúứýảẳẩẻểỉỏổởủửỷãẵẫẽễĩõỗỡũữỹạặậẹệịọộợụựỵ")


def is_valid_vietnamese_syllable(word: str) -> bool:
    """Kiểm tra một từ/âm tiết có phải từ Tiếng Việt hợp lệ hay không."""
    if not word or len(word) < 1 or len(word) > 7:
        return False
    word = unicodedata.normalize("NFC", word.strip().lower())
    if any(c in "fjwz" for c in word):
        return False
    return any(c in VIETNAMESE_VOWELS for c in word)


class NGramLanguageModel:
    """
    Mô hình Ngôn ngữ N-gram nâng cao với Kneser-Ney Smoothing (Interpolated).

    Kneser-Ney Smoothing ưu việt hơn Laplace vì sử dụng "continuation probability":
    - Đếm số lượng context khác nhau mà một từ w xuất hiện (thay vì đếm tổng tần suất).
    - Từ xuất hiện đa dạng ngữ cảnh được ưu tiên hơn từ chỉ lặp lại 1 pattern cố định.
    - Giảm thiểu overfitting trên tập dữ liệu nhỏ (như thơ Lục Bát).
    """

    def __init__(self, n: int = 3, k: float = 0.1, min_freq: int = 2, discount: float = 0.75):
        self.n = n
        self.k = k                  # Giữ lại cho Laplace fallback reference
        self.min_freq = min_freq
        self.discount = discount    # Hệ số giảm (D) của Kneser-Ney, chuẩn = 0.75

        # --- Laplace Smoothing counters (giữ lại để tham chiếu) ---
        self.ngram_counts = Counter()
        self.context_counts = Counter()
        self.word_counts = Counter()

        # --- Kneser-Ney Smoothing counters ---
        # continuation_counts[w] = số context (w_{n-1}) khác nhau mà w xuất hiện là từ cuối
        self.continuation_counts = Counter()
        # bigram_continuation_counts[(w1, w2)] = số prefix w0 khác nhau mà bigram (w0,w1) dẫn đến w2
        self.bigram_continuation_counts = Counter()
        # num_unique_bigrams: tổng số bigram unique (để tính P_KN unigram)
        self.num_unique_bigrams = 0
        # num_unique_trigrams_per_context[(w1,w2)]: số w3 unique đi theo context (w1,w2)
        self.num_unique_continuations_per_context = Counter()
        # num_unique_bigrams_per_unigram[w1]: số w2 unique đi theo w1
        self.num_unique_bigram_continuations_per_context = Counter()

        # --- Semantic Co-occurrence (Poem-level) ---
        # poem_cooccurrence[(w1, w2)] = số bài thơ mà w1 và w2 cùng xuất hiện
        # Dùng để xây dựng "topic word pool" cho mỗi seed word khi sinh thơ
        self.poem_cooccurrence = Counter()

        # --- PMI (Pointwise Mutual Information) ---
        # _pmi_cache: dict lười — chỉ được tính 1 lần khi gọi get_bigram_pmi lần đầu
        # Không lưu vào cache file để tiết kiệm bộ nhớ (tính lại chỉ mất vài giây)
        self._pmi_cache: dict = {}
        self._pmi_ready: bool = False

        # --- POS (Part-of-Speech) N-gram model ---
        self.pos_word_counts = defaultdict(Counter)
        self.pos_word_dict: dict = {}      # {word: pos_tag}
        self.pos_ngram_counts = Counter()   # (p1, p2, p3) -> count
        self.pos_bigram_counts = Counter()  # (p1, p2) -> count
        self.pos_unigram_counts = Counter() # p1 -> count

        self.vocab = set()
        self.vocab_size = 0
        self.total_words = 0

        self.BOS = "<BOS>"
        self.EOS = "<EOS>"

    def train(self, tokenized_poems: list):
        """Huấn luyện mô hình N-gram với Kneser-Ney Smoothing + Poem Co-occurrence."""
        print(f"[*] Đang huấn luyện Mô hình {self.n}-gram Language Model (Kneser-Ney Smoothing)...")
        self.ngram_counts.clear()
        self.context_counts.clear()
        self.word_counts.clear()
        self.continuation_counts.clear()
        self.bigram_continuation_counts.clear()
        self.num_unique_bigrams = 0
        self.num_unique_continuations_per_context.clear()
        self.num_unique_bigram_continuations_per_context.clear()
        self.poem_cooccurrence.clear()
        self.pos_word_counts.clear()
        self.pos_word_dict.clear()
        self.pos_ngram_counts.clear()
        self.pos_bigram_counts.clear()
        self.pos_unigram_counts.clear()
        self.vocab.clear()

        # Bước 1: Đếm tần suất âm tiết
        for poem in tokenized_poems:
            for line in poem:
                for word in line:
                    if is_valid_vietnamese_syllable(word):
                        self.word_counts[word] += 1

        # Bước 2: Tạo từ vựng chuẩn
        for w, count in self.word_counts.items():
            if count >= self.min_freq:
                self.vocab.add(w)

        if len(self.vocab) < 50:
            for w in self.word_counts:
                self.vocab.add(w)

        # Bước 3: Đếm N-gram, Context, Continuation, và Poem Co-occurrence
        unique_bigrams_set = set()  # Dùng để đếm num_unique_bigrams

        # Từ chức năng phổ biến — bỏ qua khi tính co-occurrence để tập trung content words
        FUNCTION_WORDS = {
            "là", "của", "và", "trong", "có", "được", "cho", "này", "đó",
            "một", "những", "các", "mà", "khi", "thì", "như", "hay", "hoặc",
            "với", "về", "từ", "đến", "ra", "vào", "lên", "xuống", "qua",
            "bị", "bởi", "lại", "đã", "sẽ", "đang", "cũng", "rồi", "vẫn",
        }

        for poem in tokenized_poems:
            # --- Poem Co-occurrence: tối ưu cho dataset lớn ---
            # Lấy content words (loại function words), tối đa 15 từ phổ biến nhất trong bài
            poem_word_freq: Counter = Counter()
            for line in poem:
                for w in line:
                    if w in self.vocab and w not in FUNCTION_WORDS:
                        poem_word_freq[w] += 1

            # Chỉ lấy top-15 content words để giảm số cặp (15*14/2 = 105 cặp tối đa)
            top_content_words = [w for w, _ in poem_word_freq.most_common(15)]

            # Đếm cặp từ đồng xuất hiện (thứ tự từ điển để tránh đếm 2 lần)
            top_content_words_sorted = sorted(top_content_words)
            for i, w1 in enumerate(top_content_words_sorted):
                for w2 in top_content_words_sorted[i + 1:]:
                    self.poem_cooccurrence[(w1, w2)] += 1

            # --- N-gram counting ---
            for line in poem:
                filtered_line = [w for w in line if w in self.vocab]
                if len(filtered_line) < 2:
                    continue

                padded_line = [self.BOS] * (self.n - 1) + filtered_line + [self.EOS]

                for i in range(len(padded_line) - self.n + 1):
                    ngram = tuple(padded_line[i: i + self.n])
                    context = tuple(padded_line[i: i + self.n - 1])
                    word = padded_line[i + self.n - 1]

                    # Laplace counters
                    self.ngram_counts[ngram] += 1
                    self.context_counts[context] += 1

                    # KN: Continuation count cho unigram (word)
                    self.continuation_counts[word] += 1
                    unique_bigrams_set.add((context[-1] if context else self.BOS, word))

                    # KN: Đếm số w unique theo sau mỗi context
                    self.num_unique_continuations_per_context[context] += 1

                    # Đối với bigram (n>=3): đếm continuation cho bigram level
                    if self.n >= 3 and len(context) >= 2:
                        self.bigram_continuation_counts[(context[-1], word)] += 1
                        self.num_unique_bigram_continuations_per_context[context[-2:]] += 1

        # --- Bước 4: Trích xuất chuỗi POS (Part-of-Speech) và huấn luyện POS N-gram ---
        if HAS_PYVI:
            print("  [*] Đang trích xuất POS sequence và huấn luyện POS N-gram (PyVi)...", flush=True)
            for poem in tokenized_poems:
                for line in poem:
                    if len(line) < 2:
                        continue
                    line_str = " ".join(line)
                    try:
                        tokens, tags = ViPosTagger.postagging(ViTokenizer.tokenize(line_str))
                        pos_line = []
                        for tok, tag in zip(tokens, tags):
                            words = tok.split("_")
                            for w in words:
                                w_clean = w.lower()
                                if w_clean in self.vocab:
                                    self.pos_word_counts[w_clean][tag] += 1
                                    pos_line.append(tag)

                        if len(pos_line) >= 2:
                            padded_pos = [self.BOS] * (self.n - 1) + pos_line + [self.EOS]
                            for i in range(len(padded_pos) - self.n + 1):
                                p_ngram = tuple(padded_pos[i : i + self.n])
                                p_ctx = tuple(padded_pos[i : i + self.n - 1])
                                p_word = padded_pos[i + self.n - 1]
                                self.pos_ngram_counts[p_ngram] += 1
                                self.pos_bigram_counts[p_ctx] += 1
                                self.pos_unigram_counts[p_word] += 1
                    except Exception:
                        continue

            # Chốt POS tag có tần suất cao nhất cho từng từ trong dictionary
            for w, count_map in self.pos_word_counts.items():
                if count_map:
                    self.pos_word_dict[w] = count_map.most_common(1)[0][0]

            print(f"  [✓] Trích xuất POS hoàn tất: {len(self.pos_word_dict):,} từ vựng đã được gán POS tag.")

        # Tính tổng số bigram unique thực sự
        self.num_unique_bigrams = len(unique_bigrams_set)

        # Chuyển continuation_counts thành unique-context counts
        unique_pair_by_word = Counter()
        for (prev_w, w) in unique_bigrams_set:
            unique_pair_by_word[w] += 1
        self.continuation_counts = unique_pair_by_word

        self.vocab_size = len(self.vocab)
        print(f"[✓] Huấn luyện hoàn tất! (Kneser-Ney D={self.discount})")
        print(f"    - Từ vựng Tiếng Việt chuẩn (Vocab Size): {self.vocab_size} từ")
        print(f"    - Tổng số mẫu {self.n}-gram unique: {len(self.ngram_counts)}")
        print(f"    - Tổng số bigram unique (KN base): {self.num_unique_bigrams}")
        print(f"    - Tổng số cặp từ đồng xuất hiện (Co-occurrence): {len(self.poem_cooccurrence)}")

    # =========================================================================
    # KNESER-NEY SMOOTHING — CORE METHODS
    # =========================================================================

    def _kn_unigram_prob(self, word: str) -> float:
        """
        P_KN(w) = continuation_count(w) / num_unique_bigrams
        "Từ này xuất hiện theo sau bao nhiêu context khác nhau?"
        """
        if self.num_unique_bigrams == 0:
            return 1.0 / max(self.vocab_size, 1)
        return self.continuation_counts.get(word, 0) / self.num_unique_bigrams

    def _kn_bigram_prob(self, word: str, prev_word: str) -> float:
        """
        P_KN(w | prev_word) — Bigram level Kneser-Ney (interpolated):
        = max(C(prev_word, word) - D, 0) / C(prev_word)
          + lambda(prev_word) * P_KN_unigram(word)
        """
        D = self.discount
        bigram = (prev_word, word)
        count_bigram = self.ngram_counts.get(bigram, 0) if self.n == 2 else 0

        # Dùng context_counts cho bigram context nếu n=2, hoặc tra counter KN riêng
        # Với n=3, bigram = context của trigram
        context_key = (prev_word,)
        count_context = self.context_counts.get(context_key, 0)

        if count_context == 0:
            return self._kn_unigram_prob(word)

        # Numerator: max(count - D, 0)
        numerator = max(count_bigram - D, 0)

        # Lambda (backoff weight): D * num_unique_types / count_context
        num_unique_following = self.num_unique_continuations_per_context.get(context_key, 0)
        lambda_w = (D * num_unique_following) / count_context if count_context > 0 else 1.0

        return numerator / count_context + lambda_w * self._kn_unigram_prob(word)

    def get_kn_probability(self, word: str, context: tuple) -> float:
        """
        Tính xác suất Kneser-Ney Interpolated P_KN(word | context).

        Với trigram (n=3):
          P_KN(w | w1, w2) = max(C(w1,w2,w) - D, 0) / C(w1,w2)
                            + lambda(w1,w2) * P_KN(w | w2)

        Với bigram (n=2):
          P_KN(w | w1) — dùng bigram level

        Fallback về unigram KN nếu context rỗng.
        """
        D = self.discount

        # Chuẩn hóa context
        if len(context) > self.n - 1:
            context = context[-(self.n - 1):]
        elif len(context) < self.n - 1:
            context = (self.BOS,) * (self.n - 1 - len(context)) + context

        if self.n == 1 or not context:
            return self._kn_unigram_prob(word)

        # Trigram level (n=3): P_KN(w | w1, w2)
        if self.n >= 3 and len(context) >= 2:
            count_context = self.context_counts.get(context, 0)

            if count_context == 0:
                # Backoff sang bigram KN với context[-1]
                return self._kn_bigram_prob(word, context[-1])

            ngram = context + (word,)
            count_ngram = self.ngram_counts.get(ngram, 0)

            numerator = max(count_ngram - D, 0)

            # Lambda(context): D * số từ unique theo sau context / count_context
            num_unique_following = self.num_unique_continuations_per_context.get(context, 0)
            lambda_ctx = (D * num_unique_following) / count_context

            # Bigram backoff: P_KN(w | w2)
            backoff = self._kn_bigram_prob(word, context[-1])

            return numerator / count_context + lambda_ctx * backoff

        # Bigram level (n=2)
        return self._kn_bigram_prob(word, context[-1])

    # =========================================================================
    # LAPLACE SMOOTHING (giữ lại để tham chiếu / so sánh)
    # =========================================================================

    def get_probability(self, word: str, context: tuple) -> float:
        """Tính xác suất điều kiện P(word | context) với Laplace Smoothing (tham chiếu)."""
        if len(context) > self.n - 1:
            context = context[-(self.n - 1):]
        elif len(context) < self.n - 1:
            context = (self.BOS,) * (self.n - 1 - len(context)) + context

        ngram = context + (word,)
        count_ngram = self.ngram_counts[ngram]
        count_context = self.context_counts[context]

        vocab_size = self.vocab_size if self.vocab_size > 0 else 1
        prob = (count_ngram + self.k) / (count_context + self.k * vocab_size)
        return prob

    # =========================================================================
    # CANDIDATE SELECTION — dùng Kneser-Ney
    # =========================================================================

    def get_candidate_probabilities(self, context: tuple, candidate_words: list = None) -> list:
        """
        Lấy danh sách các từ ứng viên tiếp theo dựa trên context.
        Sử dụng Kneser-Ney probability để xếp hạng.
        """
        if len(context) > self.n - 1:
            context = context[-(self.n - 1):]
        elif len(context) < self.n - 1:
            context = (self.BOS,) * (self.n - 1 - len(context)) + context

        words_to_eval = candidate_words if candidate_words is not None else list(self.vocab)

        results = []
        for word in words_to_eval:
            if word in (self.BOS, self.EOS):
                continue
            # Dùng Kneser-Ney probability (không nhân tần suất để tránh popularity bias)
            prob = self.get_kn_probability(word, context)
            results.append((word, prob))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    # =========================================================================
    # PERPLEXITY — dùng Kneser-Ney
    # =========================================================================

    def compute_perplexity(self, test_poems: list, use_kn: bool = True) -> float:
        """Tính chỉ số Perplexity trên tập kiểm thử. Mặc định dùng Kneser-Ney."""
        total_log_prob = 0.0
        total_words_count = 0

        for poem in test_poems:
            for line in poem:
                filtered_line = [w for w in line if w in self.vocab]
                if not filtered_line:
                    continue

                padded_line = [self.BOS] * (self.n - 1) + filtered_line + [self.EOS]

                for i in range(self.n - 1, len(padded_line)):
                    word = padded_line[i]
                    context = tuple(padded_line[i - self.n + 1: i])

                    if use_kn:
                        prob = self.get_kn_probability(word, context)
                    else:
                        prob = self.get_probability(word, context)

                    # Clamp để tránh log(0)
                    prob = max(prob, 1e-10)
                    total_log_prob += math.log(prob)
                    total_words_count += 1

        if total_words_count == 0:
            return float('inf')

        ppl = math.exp(-total_log_prob / total_words_count)
        return ppl

    # =========================================================================
    # ĐÁNH GIÁ OVERFITTING
    # =========================================================================

    def evaluate_overfitting(self, train_poems: list, test_poems: list) -> dict:
        """
        So sánh Train Perplexity vs Test Perplexity để phát hiện overfitting.

        Returns:
            dict với keys:
                - train_ppl_kn: Perplexity trên train set (Kneser-Ney)
                - test_ppl_kn:  Perplexity trên test set (Kneser-Ney)
                - train_ppl_laplace: Perplexity trên train set (Laplace)
                - test_ppl_laplace:  Perplexity trên test set (Laplace)
                - gap_ratio_kn:      test_ppl_kn / train_ppl_kn
                - gap_ratio_laplace: test_ppl_laplace / train_ppl_laplace
                - verdict: "KHÔNG OVERFIT", "OVERFIT VỪA", "OVERFIT NẶNG"
        """
        print("[*] Đang tính Perplexity để đánh giá Overfitting...")

        train_ppl_kn      = self.compute_perplexity(train_poems, use_kn=True)
        test_ppl_kn       = self.compute_perplexity(test_poems,  use_kn=True)
        train_ppl_laplace = self.compute_perplexity(train_poems, use_kn=False)
        test_ppl_laplace  = self.compute_perplexity(test_poems,  use_kn=False)

        gap_ratio_kn      = test_ppl_kn / train_ppl_kn       if train_ppl_kn > 0 else float('inf')
        gap_ratio_laplace = test_ppl_laplace / train_ppl_laplace if train_ppl_laplace > 0 else float('inf')

        if gap_ratio_kn < 2.0:
            verdict = "✓ KHÔNG OVERFIT (gap < 2×)"
        elif gap_ratio_kn < 4.0:
            verdict = "⚠ OVERFIT VỪA (gap 2–4×)"
        else:
            verdict = "✗ OVERFIT NẶNG (gap > 4×)"

        result = {
            "train_ppl_kn":      round(train_ppl_kn, 2),
            "test_ppl_kn":       round(test_ppl_kn, 2),
            "train_ppl_laplace": round(train_ppl_laplace, 2),
            "test_ppl_laplace":  round(test_ppl_laplace, 2),
            "gap_ratio_kn":      round(gap_ratio_kn, 3),
            "gap_ratio_laplace": round(gap_ratio_laplace, 3),
            "verdict": verdict,
        }

        # In bảng so sánh
        print("\n" + "=" * 60)
        print("  ĐÁNH GIÁ OVERFITTING: LAPLACE vs KNESER-NEY")
        print("=" * 60)
        print(f"  {'Metric':<30} {'Laplace':>10} {'Kneser-Ney':>12}")
        print("-" * 60)
        print(f"  {'Train Perplexity':<30} {train_ppl_laplace:>10.2f} {train_ppl_kn:>12.2f}")
        print(f"  {'Test  Perplexity':<30} {test_ppl_laplace:>10.2f} {test_ppl_kn:>12.2f}")
        print(f"  {'Gap Ratio (test/train)':<30} {gap_ratio_laplace:>10.3f} {gap_ratio_kn:>12.3f}")
        print("=" * 60)
        print(f"  Kết luận (KN): {verdict}")
        print("=" * 60)

        return result

    # =========================================================================
    # SEMANTIC CO-OCCURRENCE — TOPIC WORD API
    # =========================================================================

    def get_topic_words(self, seed_word: str, top_k: int = 25) -> dict:
        """
        Lấy top-k từ có tần suất đồng xuất hiện cao nhất với seed_word trong các bài thơ.

        Returns:
            dict {word: normalized_score} — điểm số [0.0, 1.0]
            Dùng để boost xác suất chọn từ cùng chủ đề với seed.
        """
        seed = seed_word.strip().lower() if seed_word else ""
        if not seed or not self.poem_cooccurrence:
            return {}

        # Tìm tất cả cặp có chứa seed word
        related = Counter()
        for (w1, w2), count in self.poem_cooccurrence.items():
            if w1 == seed:
                related[w2] += count
            elif w2 == seed:
                related[w1] += count

        if not related:
            return {}

        # Normalize về [0, 1]
        top = related.most_common(top_k)
        max_score = top[0][1] if top else 1
        return {w: count / max_score for w, count in top}

    def build_pmi_cache(self):
        """
        Xây dựng bảng PMI (Pointwise Mutual Information) cho tất cả bigram trong vocab.
        PMI(w1, w2) = log2( P(w1,w2) / (P(w1) * P(w2)) )
          > 0: cặp xuất hiện nhiều hơn ngẫu nhiên → liên quan ngữ nghĩa / ngữ pháp
          < 0: cặp xuất hiện ít hơn ngẫu nhiên → ghép ngẫu nhiên, không tự nhiên
        Chỉ tính 1 lần (lazy), lưu vào self._pmi_cache.
        """
        import math
        if self._pmi_ready:
            return

        print("[*] Đang xây dựng PMI cache (chỉ chạy 1 lần)...", flush=True)

        total_words = sum(self.word_counts.values())
        if total_words == 0:
            self._pmi_ready = True
            return

        # Tính P(w) cho tất cả từ
        p_word = {w: c / total_words for w, c in self.word_counts.items()}

        # Xây dựng bigram counts từ context_counts
        # context_counts[(w1,)] = tổng số lần w1 xuất hiện làm prefix của ngram 2-gram
        # → Đây là số lần bigram (w1, *) xuất hiện, tức là count(w1) trong ngram
        # Ta cần count(w1, w2): lấy từ ngram_counts[(w1, w2, *)] tổng theo w3

        # Với n=3: ngram_counts[(w1,w2,w3)] → đếm bigram (w1,w2) = Σ_w3 ngram_counts[(w1,w2,w3)]
        bigram_counts: Counter = Counter()
        for ngram, count in self.ngram_counts.items():
            if len(ngram) == self.n:
                bigram = ngram[:2]  # (w1, w2) cho trigram model
                bigram_counts[bigram] += count

        total_bigrams = sum(bigram_counts.values())
        if total_bigrams == 0:
            self._pmi_ready = True
            return

        # Tính PMI cho mỗi bigram
        pmi_dict = {}
        for (w1, w2), count in bigram_counts.items():
            if w1 not in p_word or w2 not in p_word:
                continue
            p_w1w2 = count / total_bigrams
            denom = p_word[w1] * p_word[w2]
            if denom <= 0:
                continue
            pmi = math.log2(p_w1w2 / denom)
            pmi_dict[(w1, w2)] = pmi

        self._pmi_cache = pmi_dict
        self._pmi_ready = True
        print(f"[✓] PMI cache xây dựng xong: {len(pmi_dict):,} cặp bigram.", flush=True)

    def get_bigram_pmi(self, w1: str, w2: str) -> float:
        """
        Trả về PMI(w1, w2). Nếu cặp chưa thấy trong corpus → trả về -inf.
        Gọi build_pmi_cache() tự động nếu chưa sẵn sàng.
        """
        if not self._pmi_ready:
            self.build_pmi_cache()
        return self._pmi_cache.get((w1, w2), float("-inf"))

    # =========================================================================
    # POS (Part-of-Speech) Methods
    # =========================================================================

    def get_word_pos(self, word: str) -> str:
        """Lấy POS tag của từ. Mặc định 'N' nếu không tìm thấy."""
        if not word or word in (self.BOS, self.EOS):
            return "N"
        w_clean = word.strip().lower()
        return self.pos_word_dict.get(w_clean, "N")

    def get_pos_transition_prob(self, context_pos: tuple, candidate_pos: str) -> float:
        """
        Tính xác suất chuyển tiếp POS: P(candidate_pos | context_pos)
        Smooth laplace nhỏ để tránh phân chia 0.
        """
        if not self.pos_bigram_counts and not self.pos_ngram_counts:
            return 1.0

        if len(context_pos) >= 2:
            ngram = tuple(list(context_pos[-2:]) + [candidate_pos])
            bigram = tuple(context_pos[-2:])
            c_ngram = self.pos_ngram_counts.get(ngram, 0)
            c_bigram = self.pos_bigram_counts.get(bigram, 0)
            if c_bigram > 0:
                return (c_ngram + 1e-4) / (c_bigram + 1e-4 * 30.0)

        if context_pos:
            last_pos = context_pos[-1]
            bigram = (last_pos, candidate_pos)
            c_bigram = self.pos_bigram_counts.get(bigram, 0)
            c_unigram = self.pos_unigram_counts.get(last_pos, 0)
            if c_unigram > 0:
                return (c_bigram + 1e-4) / (c_unigram + 1e-4 * 30.0)

        return 1.0 / 30.0




    # =========================================================================

    def save_model(self, file_path: str = "ngram_model_cache.pkl"):
        """Lưu toàn bộ tham số mô hình (bao gồm KN + Co-occurrence) ra file Cache."""
        try:
            print(f"[*] Đang LƯU CACHE mô hình N-gram (KN+Cooc) vào file '{file_path}'...")
            state = {
                "n": self.n,
                "k": self.k,
                "min_freq": self.min_freq,
                "discount": self.discount,
                "ngram_counts": self.ngram_counts,
                "context_counts": self.context_counts,
                "word_counts": self.word_counts,
                "vocab": self.vocab,
                "vocab_size": self.vocab_size,
                # KN-specific
                "continuation_counts": self.continuation_counts,
                "bigram_continuation_counts": self.bigram_continuation_counts,
                "num_unique_bigrams": self.num_unique_bigrams,
                "num_unique_continuations_per_context": self.num_unique_continuations_per_context,
                "num_unique_bigram_continuations_per_context": self.num_unique_bigram_continuations_per_context,
                # Semantic co-occurrence
                "poem_cooccurrence": self.poem_cooccurrence,
                # POS N-gram model
                "pos_word_dict": self.pos_word_dict,
                "pos_ngram_counts": self.pos_ngram_counts,
                "pos_bigram_counts": self.pos_bigram_counts,
                "pos_unigram_counts": self.pos_unigram_counts,
            }
            with open(file_path, "wb") as f:
                pickle.dump(state, f)
            print(f"[✓] Đã LƯU CACHE Mô hình thành công!")
        except Exception as e:
            print(f"[!] Không thể lưu cache mô hình ({e}).")

    @classmethod
    def load_model(cls, file_path: str = "ngram_model_cache.pkl"):
        """Nạp nhanh mô hình N-gram đã huấn luyện từ file Cache (<0.1 giây)."""
        if not os.path.exists(file_path):
            return None
        try:
            print(f"[*] Nạp Mô hình N-gram từ CACHE ('{file_path}')...")
            with open(file_path, "rb") as f:
                state = pickle.load(f)

            model = cls(
                n=state["n"],
                k=state.get("k", 0.1),
                min_freq=state["min_freq"],
                discount=state.get("discount", 0.75),
            )
            model.ngram_counts   = state["ngram_counts"]
            model.context_counts = state["context_counts"]
            model.word_counts    = state["word_counts"]
            model.vocab          = state["vocab"]
            model.vocab_size     = state["vocab_size"]

            # KN-specific — tương thích ngược nếu cache cũ không có
            model.continuation_counts = state.get("continuation_counts", Counter())
            model.bigram_continuation_counts = state.get("bigram_continuation_counts", Counter())
            model.num_unique_bigrams = state.get("num_unique_bigrams", 0)
            model.num_unique_continuations_per_context = state.get(
                "num_unique_continuations_per_context", Counter()
            )
            model.num_unique_bigram_continuations_per_context = state.get(
                "num_unique_bigram_continuations_per_context", Counter()
            )
            # Semantic co-occurrence — tương thích ngược
            model.poem_cooccurrence = state.get("poem_cooccurrence", Counter())

            # POS N-gram model — tương thích ngược
            model.pos_word_dict      = state.get("pos_word_dict", {})
            model.pos_ngram_counts   = state.get("pos_ngram_counts", Counter())
            model.pos_bigram_counts  = state.get("pos_bigram_counts", Counter())
            model.pos_unigram_counts = state.get("pos_unigram_counts", Counter())

            # Nếu cache cũ chưa có KN counters → đánh dấu cần rebuild
            if model.num_unique_bigrams == 0 and model.vocab_size > 0:
                print("[!] Cache cũ không có Kneser-Ney counters. Cần rebuild (--rebuild).")
            if not model.poem_cooccurrence and model.vocab_size > 0:
                print("[!] Cache cũ không có Co-occurrence. Cần rebuild (--rebuild) để dùng semantic scoring.")

            print(f"[✓] Nạp Mô hình từ CACHE thành công!")
            print(f"    - Kích thước từ vựng: {model.vocab_size} từ")
            print(f"    - Kích thước N-gram: {len(model.ngram_counts)} mẫu")
            return model
        except Exception as e:
            print(f"[!] Lỗi khi nạp cache mô hình ({e}).")
            return None
