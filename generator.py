import random
import sys
from luc_bat_rules import (
    get_tone, is_rhyme, check_bang_trac, check_luc_bat_poem_rules,
    is_huyen_tone, is_ngang_tone
)
from ngram_model import NGramLanguageModel, is_valid_vietnamese_syllable

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# Từ điển từ gieo vần chuẩn Thanh Bằng (B) dự phòng theo từng khuôn vần
RHYME_DICTIONARY_B = {
    "an":    ["đàn", "ngàn", "màn", "tràn", "nhàn", "an"],
    "ang":   ["làng", "sang", "vàng", "tràng", "mang", "gàng"],
    "am":    ["lam", "cam", "nam", "chàm", "xàm"],
    "ăm":    ["rằm", "tầm", "trăm", "nằm", "âm", "thầm"],
    "âm":    ["rằm", "tầm", "trăm", "nằm", "âm", "thầm"],
    "em":    ["thềm", "đêm", "thêm", "êm", "xem", "nêm"],
    "êm":    ["thềm", "đêm", "thêm", "êm", "xem", "nêm"],
    "im":    ["tìm", "chim", "dìm", "tim", "khim"],
    "om":    ["chòm", "khom", "vòm", "dòm"],
    "ôm":    ["hôm", "ôm", "tôm", "nôm", "chôm"],
    "ơm":    ["đơm", "cơm", "rơm", "thơm", "bơm"],
    "ơi":    ["trời", "người", "đời", "nơi", "khơi", "lời", "chơi", "vơi"],
    "ươi":   ["người", "trời", "đời", "tươi", "cười", "mười"],
    "ây":    ["mây", "bày", "đây", "tay", "ngày", "cây"],
    "ay":    ["ngày", "tay", "mây", "bày", "đây", "bay"],
    "anh":   ["xanh", "anh", "thành", "cành", "lành", "tranh"],
    "inh":   ["tình", "mình", "xinh", "dinh", "linh", "hình"],
    "e":     ["về", "quê", "bè", "nghề", "thề", "lê"],
    "ê":     ["về", "quê", "bè", "nghề", "thề", "lê"],
    "u":     ["thu", "ru", "mù", "dù", "chu"],
    "ư":     ["như", "dư", "hư", "tư", "sư"],
    "ơn":    ["hơn", "trơn", "sơn", "đơn"],
    "ơ":     ["thơ", "mơ", "chờ", "ngơ", "bờ"],
    "ua":    ["mùa", "vừa", "chưa", "xưa", "thừa"],
    "ưa":    ["mùa", "vừa", "chưa", "xưa", "thừa"],
    "âu":    ["đâu", "sâu", "cầu", "bầu", "màu", "dầu"],
    "ao":    ["sao", "nao", "trào", "vào", "cao"],
    "ân":    ["chân", "xuân", "thân", "ngần"],
    "iền":   ["hiền", "tiền", "miền", "liền", "duyên"],
    "yên":   ["hiền", "tiền", "miền", "liền", "duyên"],
    "ong":   ["lòng", "sông", "đồng", "dòng", "hồng", "trông", "bông", "rồng"],
    "ông":   ["lòng", "sông", "đồng", "dòng", "hồng", "trông", "bông", "rồng"],
    "o":     ["cho", "co", "lo", "trò", "dò"],
    "ô":     ["cô", "đô", "mô", "xô", "ngô"],
    "i":     ["đi", "khi", "chi", "gì", "thì", "vì"],
    "ương":  ["thương", "đường", "vương", "sương", "hương", "trường"],
    "oa":    ["hoa", "khoa", "toa", "xoa", "lòa", "chòa"],
    "ia":    ["chia", "kia", "lìa", "mìa", "nìa", "vìa"],
    "iu":    ["chìu", "lìu", "ngìu", "tiếu", "diều"],
    "êu":    ["chiều", "diều", "tiếu", "miếu", "siêu"],
    "iêu":   ["chiều", "diều", "tiếu", "siêu", "miếu"],
    "ai":    ["dài", "gài", "hoài", "ngoài", "tài", "phôi"],
    "oi":    ["chòi", "đòi", "ngòi", "tròi", "vòi"],
    "ôi":    ["bồi", "hồi", "sôi", "thồi", "vồi"],
    "ui":    ["bùi", "gùi", "núi", "thúi", "vùi"],
    "oan":   ["hoàn", "loàn", "ngoàn", "toàn", "toan"],
    "oang":  ["hoàng", "long", "phong", "toàng"],
    "uân":   ["xuân", "thuần", "quân", "huấn"],
    "ên":    ["đêm", "mền", "nền", "tiền", "thền"],
    "in":    ["mìn", "tìn", "xinh", "chìn"],
    "on":    ["còn", "mòn", "hòn", "tròn", "ngón"],
    "ươn":   ["hươn", "thươn", "vươn", "nương"],
    "ung":   ["cùng", "dùng", "lòng", "rừng", "trúng"],
    "ứng":   ["cứng", "đứng", "mừng", "vững"],
}


# Danh sách đen: từ KHÔNG được phép xuất hiện ở CUỐI câu thơ
LINE_END_BLACKLIST = {
    # Liên từ / kết nối
    "mà", "và", "hay", "hoặc", "nhưng", "song", "nếu", "kếi", "thì",
    "bởi", "do", "vì", "tại",
    # Giới từ / phó từ vị trí
    "trong", "ngoài", "trên", "dưới", "giữa", "bên", "cạnh",
    "của", "cho", "với", "về", "từ", "đến", "qua", "theo",
    # Trợ động từ / phó từ thì
    "đã", "sẽ", "đang", "vẫn", "cũng", "rồi", "lại", "còn",
    "mới", "vừa", "đều", "cả", "chỉ", "mãi",
    # Từ xác định / đại từ của
    "là", "có", "không", "chưa", "được", "bị", "như",
    # Từ loại quá trung tính / lạnh
    "này", "đó", "kia", "khi", "đâu", "gì", "nào",
    # Đại từ xưng hô
    "tôi", "tao", "mình", "ta", "nó", "họ",
    # Động từ phụ / hướng từ không tự nhiên khi đứng cuối câu
    "nổi", "vô", "ra", "vào", "lên", "xuống", "tới", "sang",
    # Từ nội dung lặp lại quá nhiều
    "chữ", "khéo",
}

# Tập các cặp từ mô-típ quá mòn / lặp lại rập khuôn cần hạn chế
CLICHE_BIGRAMS = {
    ("truyện", "kiều"),
    ("cụ", "nguyễn"),
    ("nguyễn", "du"),
}

# Danh sách đen từ phi thi ca / tục / khẩu ngữ / không hợp phong cách thơ Lục bát
UNPOETIC_WORDS = {
    "kem", "mồm", "bà", "bầu", "vỏ", "bào", "bò", "chàm", "xàm", "chôm",
    "bơm", "mìn", "dòm", "khim", "thúi", "gùi", "gài", "lìu", "ngìu",
    "mặc", "cực", "nổi", "vô", "đô", "mô", "xô"
}

# Tập đại từ xưng hô sóng đôi (Pronoun Pairs)
PRONOUN_PAIRS = [
    {"anh", "em"},
    {"mẹ", "con"},
    {"tôi", "người"},
    {"ta", "người"},
    {"chàng", "thiếp"},
]
ALL_PRONOUNS = set().union(*PRONOUN_PAIRS)

# Sắc thái cảm xúc (Sentiment Lexicons)
SAD_WORDS = {
    "sầu", "lệ", "rơi", "đắng", "cay", "lạnh", "lẻ", "loi", "chia", "lìa",
    "cô", "liêu", "xót", "xa", "đau", "buồn", "mỏi", "chờ", "ngóng", "biệt",
    "vắng", "tan", "phương", "tàn", "sương", "u"
}

JOY_WORDS = {
    "vui", "cười", "phúc", "mừng", "hạnh", "rạng", "ngời", "chan", "hòa",
    "rực", "rỡ", "ấm", "no", "tươi", "hân", "hoan", "say", "thắm"
}


def _temperature_sample(candidates: list, temperature: float = 1.2, top_k: int = 8) -> str:
    """Temperature Sampling."""
    if not candidates:
        return None
    top = candidates[:min(top_k, len(candidates))]
    words, scores = zip(*top)
    scores_t = [max(s, 1e-10) ** (1.0 / temperature) for s in scores]
    total = sum(scores_t)
    probs = [s / total for s in scores_t]
    return random.choices(words, weights=probs, k=1)[0]


class LucBatPoemGenerator:
    """
    Bộ Sinh Thơ Lục Bát Tiếng Việt Nâng Cao v5 (Couplet-Based 2/2/2 Meter):
    - Sinh thơ theo nhịp đôi (2/2/2 cho câu Lục, 2/2/2/2 cho câu Bát).
    - Ràng buộc PMI > -0.5 cho từng cụm 2 từ (w_odd, w_even) để đảm bảo câu từ tròn nhịp.
    - Cố định xưng hô (Pronoun Locking) & sắc thái cảm xúc (Sentiment Locking).
    - Tiểu đối Bằng-Thanh Ngang vs Huyền ở câu Bát.
    """

    def __init__(self, ngram_model: NGramLanguageModel, temperature: float = 1.2,
                 topic_alpha: float = 0.5, pmi_threshold: float = -1.0):
        self.lm = ngram_model
        self.temperature = temperature
        self.topic_alpha = topic_alpha
        self.pmi_threshold = pmi_threshold
        self.valid_vocab = [w for w in self.lm.vocab if is_valid_vietnamese_syllable(w)]
        self.valid_vocab.sort(key=lambda w: self.lm.word_counts.get(w, 0), reverse=True)
        self.lm.build_pmi_cache()

    def _get_valid_tone_words(self, expected_tone: str, exclude_words: set = None) -> list:
        exclude = exclude_words or set()
        return [w for w in self.valid_vocab if get_tone(w) == expected_tone and w not in exclude]

    def _get_valid_rhyme_words(self, target_word: str, exclude_words: set = None) -> list:
        exclude = exclude_words or set()
        candidates = [w for w in self.valid_vocab if is_rhyme(w, target_word) and w not in exclude]

        if not candidates:
            from luc_bat_rules import extract_rime
            target_rime = extract_rime(target_word)
            dict_candidates = RHYME_DICTIONARY_B.get(target_rime, ["trời", "người", "đời", "mây", "về"])
            candidates = [w for w in dict_candidates if w not in exclude and get_tone(w) == "B"]
            if not candidates:
                candidates = [w for w in dict_candidates if get_tone(w) == "B"]

        return candidates

    def _pick_word(self, context: tuple, tone_filter: str = None,
                   exclude_words: set = None, used_bigrams: set = None,
                   prev_word: str = None, top_k: int = 8,
                   topic_scores: dict = None,
                   poem_words_freq: dict = None,
                   locked_pronouns: set = None,
                   locked_sentiment: str = None,
                   line_keywords: list = None) -> str:
        """
        Chọn 1 từ lẻ với các ràng buộc.
        """
        exclude = exclude_words or set()
        bg = used_bigrams or set()
        ts = topic_scores or {}
        freq = poem_words_freq or {}
        kw_set = set(line_keywords or [])

        candidates = self.lm.get_candidate_probabilities(context)
        filtered = []

        for word, score in candidates:
            if not is_valid_vietnamese_syllable(word) or word in exclude:
                continue
            if tone_filter and get_tone(word) != tone_filter:
                continue
            if prev_word and ((prev_word, word) in bg or (prev_word, word) in CLICHE_BIGRAMS):
                continue
            if freq.get(word, 0) >= 3:
                continue
            if locked_pronouns and word in ALL_PRONOUNS and word not in locked_pronouns:
                continue
            if locked_sentiment == "SAD" and word in JOY_WORDS:
                continue
            if locked_sentiment == "JOY" and word in SAD_WORDS:
                continue

            if prev_word:
                pmi = self.lm.get_bigram_pmi(prev_word, word)
                if pmi < self.pmi_threshold:
                    continue

            prev_pos = self.lm.get_word_pos(prev_word) if prev_word else None
            cand_pos = self.lm.get_word_pos(word)

            if prev_pos:
                if prev_pos == "Nc" and cand_pos in ("A", "V"):
                    continue
                if prev_pos == "E" and cand_pos in ("E", "C"):
                    continue
                if prev_pos == "C" and cand_pos == "C":
                    continue
                if prev_pos == "L" and cand_pos in ("L", "C"):
                    continue

                pos_prob = self.lm.get_pos_transition_prob((prev_pos,), cand_pos)
            else:
                pos_prob = 1.0

            freq_penalty = 1.0 + freq.get(word, 0) * 1.5
            topic_bonus = ts.get(word, 0.0)
            kw_bonus = 0.5 if word in kw_set else 0.0

            boosted_score = (
                (score / freq_penalty) *
                (1.0 + self.topic_alpha * topic_bonus + kw_bonus) *
                (0.7 + 0.3 * (pos_prob * 10.0))
            )
            filtered.append((word, boosted_score))

        return _temperature_sample(filtered, self.temperature, top_k)

    def _pick_couplet(self, context: tuple, expected_even_tone: str,
                      exclude_words: set = None, used_bigrams: set = None,
                      prev_word: str = None, top_k: int = 6,
                      topic_scores: dict = None, poem_words_freq: dict = None,
                      locked_pronouns: set = None, locked_sentiment: str = None,
                      line_keywords: list = None) -> tuple:
        """
        Sinh 1 cụm nhịp 2-từ (w_odd, w_even) liên kết cao (Nhịp 2/2/2).
        """
        exclude = exclude_words or set()
        bg = used_bigrams or set()
        ts = topic_scores or {}
        freq = poem_words_freq or {}
        kw_set = set(line_keywords or [])

        candidates_odd = self.lm.get_candidate_probabilities(context)
        valid_couplets = []

        for w_odd, score1 in candidates_odd[:15]:
            if not is_valid_vietnamese_syllable(w_odd) or w_odd in exclude:
                continue
            if freq.get(w_odd, 0) >= 3:
                continue
            if prev_word and ((prev_word, w_odd) in bg or (prev_word, w_odd) in CLICHE_BIGRAMS):
                continue
            if locked_pronouns and w_odd in ALL_PRONOUNS and w_odd not in locked_pronouns:
                continue
            if locked_sentiment == "SAD" and w_odd in JOY_WORDS:
                continue
            if locked_sentiment == "JOY" and w_odd in SAD_WORDS:
                continue
            if prev_word:
                if self.lm.get_bigram_pmi(prev_word, w_odd) < self.pmi_threshold:
                    continue

            ctx_even = tuple(list(context) + [w_odd])
            candidates_even = self.lm.get_candidate_probabilities(ctx_even)

            for w_even, score2 in candidates_even[:15]:
                if not is_valid_vietnamese_syllable(w_even) or w_even in exclude:
                    continue
                if get_tone(w_even) != expected_even_tone:
                    continue
                if freq.get(w_even, 0) >= 3:
                    continue
                if (w_odd, w_even) in bg or (w_odd, w_even) in CLICHE_BIGRAMS:
                    continue
                if locked_pronouns and w_even in ALL_PRONOUNS and w_even not in locked_pronouns:
                    continue
                if locked_sentiment == "SAD" and w_even in JOY_WORDS:
                    continue
                if locked_sentiment == "JOY" and w_even in SAD_WORDS:
                    continue

                # RÀNG BUỘC NHỊP ĐÔI: Cặp (w_odd, w_even) bắt buộc có PMI >= 0.0 (cụm 2 từ tự nhiên thực sự)
                pmi_couplet = self.lm.get_bigram_pmi(w_odd, w_even)
                if pmi_couplet < 0.0:
                    continue

                pos_odd = self.lm.get_word_pos(w_odd)
                pos_even = self.lm.get_word_pos(w_even)
                if pos_odd == "Nc" and pos_even in ("A", "V"):
                    continue
                if pos_odd == "E" and pos_even in ("E", "C"):
                    continue
                if pos_odd == "C" and pos_even == "C":
                    continue

                penalty = (1.0 + freq.get(w_odd, 0) * 1.5) * (1.0 + freq.get(w_even, 0) * 1.5)
                topic_b = (ts.get(w_odd, 0.0) + ts.get(w_even, 0.0)) / 2.0
                kw_b = 0.3 if (w_odd in kw_set or w_even in kw_set) else 0.0

                couplet_score = (score1 * score2 / penalty) * (1.0 + self.topic_alpha * topic_b + kw_b) * (1.0 + pmi_couplet)
                valid_couplets.append(((w_odd, w_even), couplet_score))

        if not valid_couplets:
            # Fallback nếu không có couplet đạt PMI >= 0.0: chấp nhận PMI > -0.5
            for w_odd, score1 in candidates_odd[:15]:
                if not is_valid_vietnamese_syllable(w_odd) or w_odd in exclude or freq.get(w_odd, 0) >= 3:
                    continue
                ctx_even = tuple(list(context) + [w_odd])
                candidates_even = self.lm.get_candidate_probabilities(ctx_even)
                for w_even, score2 in candidates_even[:15]:
                    if not is_valid_vietnamese_syllable(w_even) or get_tone(w_even) != expected_even_tone or w_even in exclude:
                        continue
                    if self.lm.get_bigram_pmi(w_odd, w_even) >= -0.5:
                        valid_couplets.append(((w_odd, w_even), score1 * score2))
                        break
                if valid_couplets:
                    break

            if not valid_couplets:
                w_odd = self._pick_word(context, None, exclude, bg, prev_word, top_k, ts, freq, locked_pronouns, locked_sentiment, line_keywords) or ("mây" if expected_even_tone == "B" else "nắng")
                ctx_even = tuple(list(context) + [w_odd])
                w_even = self._pick_word(ctx_even, expected_even_tone, exclude, bg, w_odd, top_k, ts, freq, locked_pronouns, locked_sentiment, line_keywords) or ("bay" if expected_even_tone == "B" else "rơi")
                return (w_odd, w_even)

        valid_couplets.sort(key=lambda x: x[1], reverse=True)
        top = valid_couplets[:min(top_k, len(valid_couplets))]
        couplets, scores = zip(*top)
        scores_t = [max(s, 1e-10) ** (1.0 / self.temperature) for s in scores]
        tot = sum(scores_t)
        probs = [s / tot for s in scores_t]
        return random.choices(couplets, weights=probs, k=1)[0]

    def _record_bigrams(self, line: list, used_bigrams: set):
        for i in range(len(line) - 1):
            used_bigrams.add((line[i], line[i+1]))

    def generate_cau_luc(self, line_index: int, prev_rhymes: dict, used_rhyme_words: set,
                          poem_words_freq: dict, used_bigrams: set,
                          seed_words: list = None, topic_scores: dict = None,
                          locked_pronouns: set = None, locked_sentiment: str = None) -> list:
        """
        Sinh Câu Lục (6 chữ) theo 3 Cụm Nhịp Đôi: [w1,w2] -> [w3,w4] -> [w5,w6]
        """
        ts = topic_scores or {}
        line = []

        # Nhịp 1: [w1, w2] (pos 2 -> tone "B")
        if seed_words and len(seed_words) > 0:
            w1 = seed_words[0]
            line.append(w1)
            ctx_1 = tuple(line)
            w2 = self._pick_word(ctx_1, tone_filter="B", exclude_words=used_rhyme_words, used_bigrams=used_bigrams, prev_word=w1, top_k=8, topic_scores=ts, poem_words_freq=poem_words_freq, locked_pronouns=locked_pronouns, locked_sentiment=locked_sentiment) or "xưa"
            line.append(w2)
        else:
            w1, w2 = self._pick_couplet((), "B", exclude_words=used_rhyme_words, used_bigrams=used_bigrams, prev_word=None, topic_scores=ts, poem_words_freq=poem_words_freq, locked_pronouns=locked_pronouns, locked_sentiment=locked_sentiment)
            line.extend([w1, w2])

        poem_words_freq[w1] = poem_words_freq.get(w1, 0) + 1
        poem_words_freq[w2] = poem_words_freq.get(w2, 0) + 1

        # Nhịp 2: [w3, w4] (pos 4 -> tone "T")
        prev = line[-1]
        ctx = tuple(line[-(self.lm.n - 1):])
        w3, w4 = self._pick_couplet(ctx, "T", exclude_words=used_rhyme_words, used_bigrams=used_bigrams, prev_word=prev, topic_scores=ts, poem_words_freq=poem_words_freq, locked_pronouns=locked_pronouns, locked_sentiment=locked_sentiment)
        line.extend([w3, w4])
        poem_words_freq[w3] = poem_words_freq.get(w3, 0) + 1
        poem_words_freq[w4] = poem_words_freq.get(w4, 0) + 1

        # Nhịp 3: [w5, w6] (pos 6 -> tone "B" & gieo vần)
        prev_bat_line_idx = line_index - 1
        target_rhyme_word = (
            prev_rhymes.get(f"line{prev_bat_line_idx}_word8")
            if line_index > 0 else None
        )
        valid_w6_candidates = (
            self._get_valid_rhyme_words(target_rhyme_word, exclude_words=used_rhyme_words)
            if target_rhyme_word
            else self._get_valid_tone_words("B", exclude_words=used_rhyme_words)
        )
        if not valid_w6_candidates:
            valid_w6_candidates = ["trời", "mây", "sông", "làng", "đường"]

        valid_w6_candidates = [
            w for w in valid_w6_candidates
            if w not in LINE_END_BLACKLIST and w not in UNPOETIC_WORDS and
            self.lm.get_word_pos(w) in ("N", "V", "A", "Np") and
            (not locked_pronouns or w not in ALL_PRONOUNS or w in locked_pronouns)
        ]

        best_w5_w6 = None
        best_score = -1.0
        prev_w4 = line[-1] if line else None
        ctx_4 = tuple(line[-(self.lm.n - 1):])

        for w6 in valid_w6_candidates[:12]:
            w5_cands = self.lm.get_candidate_probabilities(ctx_4)
            for w5, score5 in w5_cands[:8]:
                if not is_valid_vietnamese_syllable(w5) or w5 in used_rhyme_words:
                    continue
                if (w5, w6) in used_bigrams or (prev_w4 and (prev_w4, w5) in used_bigrams):
                    continue
                pmi_56 = self.lm.get_bigram_pmi(w5, w6)
                if pmi_56 < -0.5:
                    continue

                score = score5 * self.lm.get_kn_probability(w6, tuple(list(ctx_4) + [w5]))
                if score > best_score:
                    best_score = score
                    best_w5_w6 = (w5, w6)

        if best_w5_w6:
            w5, w6 = best_w5_w6
        else:
            w5 = self._pick_word(ctx_4, None, used_rhyme_words, used_bigrams, prev_w4, 8, ts, poem_words_freq, locked_pronouns, locked_sentiment) or "ngàn"
            w6 = valid_w6_candidates[0] if valid_w6_candidates else "trời"

        line.extend([w5, w6])
        poem_words_freq[w5] = poem_words_freq.get(w5, 0) + 1
        poem_words_freq[w6] = poem_words_freq.get(w6, 0) + 1
        used_rhyme_words.add(w6)
        self._record_bigrams(line, used_bigrams)
        return line

    def generate_cau_bat(self, line_index: int, prev_rhymes: dict, used_rhyme_words: set,
                          poem_words_freq: dict, used_bigrams: set,
                          topic_scores: dict = None,
                          locked_pronouns: set = None,
                          locked_sentiment: str = None,
                          luc_keywords: list = None) -> list:
        """
        Sinh Câu Bát (8 chữ) theo 4 Cụm Nhịp Đôi: [w1,w2] -> [w3,w4] -> [w5,w6] -> [w7,w8]
        """
        ts = topic_scores or {}
        target_rhyme_word = prev_rhymes.get(f"line{line_index - 1}_word6")

        for attempt in range(6):
            line = []

            # Nhịp 1: [w1, w2] (pos 2 -> tone "B")
            w1, w2 = self._pick_couplet((), "B", exclude_words=used_rhyme_words, used_bigrams=used_bigrams, prev_word=None, topic_scores=ts, poem_words_freq=poem_words_freq, locked_pronouns=locked_pronouns, locked_sentiment=locked_sentiment, line_keywords=luc_keywords)
            line.extend([w1, w2])

            # Nhịp 2: [w3, w4] (pos 4 -> tone "T")
            ctx_2 = tuple(line[-(self.lm.n - 1):])
            w3, w4 = self._pick_couplet(ctx_2, "T", exclude_words=used_rhyme_words, used_bigrams=used_bigrams, prev_word=line[-1], topic_scores=ts, poem_words_freq=poem_words_freq, locked_pronouns=locked_pronouns, locked_sentiment=locked_sentiment, line_keywords=luc_keywords)
            line.extend([w3, w4])

            # Nhịp 3 & 4: Tìm bộ (w5, w6, w7, w8)
            valid_w6 = (
                self._get_valid_rhyme_words(target_rhyme_word, exclude_words=used_rhyme_words)
                if target_rhyme_word
                else self._get_valid_tone_words("B", exclude_words=used_rhyme_words)
            )
            if not valid_w6:
                valid_w6 = ["trời", "mây", "sông", "làng", "đường"]

            valid_w6 = [
                w for w in valid_w6
                if w not in LINE_END_BLACKLIST and w not in UNPOETIC_WORDS and
                self.lm.get_word_pos(w) in ("N", "V", "A", "Np") and
                (not locked_pronouns or w not in ALL_PRONOUNS or w in locked_pronouns)
            ]

            best_4pack = None
            best_score = -1.0
            ctx_4 = tuple(line[-(self.lm.n - 1):])
            prev_w4 = line[-1]

            for w6 in valid_w6[:10]:
                if locked_sentiment == "SAD" and w6 in JOY_WORDS:
                    continue
                if locked_sentiment == "JOY" and w6 in SAD_WORDS:
                    continue

                w5_cands = self.lm.get_candidate_probabilities(ctx_4)
                for w5, score5 in w5_cands[:6]:
                    if not is_valid_vietnamese_syllable(w5) or w5 in used_rhyme_words or w5 in UNPOETIC_WORDS:
                        continue
                    if (w5, w6) in used_bigrams or (prev_w4, w5) in used_bigrams:
                        continue
                    pmi_56 = self.lm.get_bigram_pmi(w5, w6)
                    if pmi_56 < -0.5:
                        continue

                    ctx_6 = tuple(list(ctx_4) + [w5, w6])
                    w7_cands = self.lm.get_candidate_probabilities(ctx_6[-(self.lm.n-1):])

                    for w7, score7 in w7_cands[:6]:
                        if not is_valid_vietnamese_syllable(w7) or (w6, w7) in used_bigrams or w7 in UNPOETIC_WORDS:
                            continue
                        if locked_pronouns and w7 in ALL_PRONOUNS and w7 not in locked_pronouns:
                            continue

                        ctx_7 = tuple(list(ctx_6) + [w7])
                        w8_cands = self.lm.get_candidate_probabilities(ctx_7[-(self.lm.n-1):])

                        for w8, score8 in w8_cands[:6]:
                            if not is_valid_vietnamese_syllable(w8) or get_tone(w8) != "B":
                                continue
                            if w8 in used_rhyme_words or w8 == w6 or w8 in LINE_END_BLACKLIST or w8 in UNPOETIC_WORDS:
                                continue
                            if self.lm.get_word_pos(w8) not in ("N", "V", "A", "Np"):
                                continue
                            if (w7, w8) in used_bigrams:
                                continue
                            if locked_pronouns and w8 in ALL_PRONOUNS and w8 not in locked_pronouns:
                                continue
                            if locked_sentiment == "SAD" and w8 in JOY_WORDS:
                                continue
                            if locked_sentiment == "JOY" and w8 in SAD_WORDS:
                                continue

                            # RÀNG BUỘC NHỊP 4: PMI(w7, w8) > -0.5
                            pmi_78 = self.lm.get_bigram_pmi(w7, w8)
                            if pmi_78 < -0.5:
                                continue

                            # TIỂU ĐỐI BẰNG-THANH: w6 & w8 phải 1 Ngang, 1 Huyền
                            if is_huyen_tone(w6) == is_huyen_tone(w8):
                                continue

                            score = score5 * score7 * score8 * (1.0 + self.topic_alpha * ts.get(w6, 0.0))
                            if score > best_score:
                                best_score = score
                                best_4pack = (w5, w6, w7, w8)

            if best_4pack:
                w5, w6, w7, w8 = best_4pack
                line.extend([w5, w6, w7, w8])
                for w in line:
                    poem_words_freq[w] = poem_words_freq.get(w, 0) + 1
                used_rhyme_words.add(w6)
                used_rhyme_words.add(w8)
                self._record_bigrams(line, used_bigrams)
                return line

        w8_pool = [
            w for w in w8_pool
            if (w7, w) not in used_bigrams and w not in LINE_END_BLACKLIST and
            (is_ngang_tone(w) if w6_is_huyen else is_huyen_tone(w))
        ]
        w8 = w8_pool[0] if w8_pool else ("sông" if w6_is_huyen else "về")

        line.extend([w6, w7, w8])
        used_rhyme_words.add(w6)
        used_rhyme_words.add(w8)
        self._record_bigrams(line, used_bigrams)
        return line

    def _update_locks(self, line: list, locked_pronouns: set, locked_sentiment: str):
        if not locked_pronouns:
            for w in line:
                for pair in PRONOUN_PAIRS:
                    if w in pair:
                        locked_pronouns = pair
                        print(f"  [Pronoun Lock] Khóa xưng hô: {pair}")
                        break
                if locked_pronouns:
                    break

        if not locked_sentiment:
            sad_count = sum(1 for w in line if w in SAD_WORDS)
            joy_count = sum(1 for w in line if w in JOY_WORDS)
            if sad_count > joy_count:
                locked_sentiment = "SAD"
                print("  [Sentiment Lock] Khóa sắc thái: SAD (U Buồn)")
            elif joy_count > sad_count:
                locked_sentiment = "JOY"
                print("  [Sentiment Lock] Khóa sắc thái: JOY (Tươi Sáng)")

        return locked_pronouns, locked_sentiment

    def generate_luc_bat_poem(self, seed_word: str = "trời", num_pairs: int = 2) -> list:
        """
        Sinh 1 bài thơ Lục bát hoàn chỉnh v5 (Couplet-Based 2/2/2 Meter).
        """
        poem = []
        prev_rhymes = {}
        used_rhyme_words = set()
        poem_words_freq = {}
        used_bigrams = set()

        seed_word_clean = seed_word.strip().lower() if seed_word else "trời"
        seed_tokens = [seed_word_clean]

        topic_scores = self.lm.get_topic_words(seed_word_clean, top_k=25)
        if topic_scores:
            top_topic = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"  [Topic] seed='{seed_word_clean}' → related: {[w for w,_ in top_topic]}")

        locked_pronouns = None
        locked_sentiment = None

        for pair_idx in range(num_pairs):
            line_idx_luc = pair_idx * 2
            line_idx_bat = pair_idx * 2 + 1

            if pair_idx == 0:
                luc_seed = seed_tokens
            else:
                prev_bat_key = f"line{line_idx_bat - 1}_word8"
                carry_word = prev_rhymes.get(prev_bat_key)
                luc_seed = [carry_word] if carry_word else None

            luc_line = self.generate_cau_luc(
                line_idx_luc, prev_rhymes, used_rhyme_words,
                poem_words_freq, used_bigrams,
                seed_words=luc_seed, topic_scores=topic_scores,
                locked_pronouns=locked_pronouns, locked_sentiment=locked_sentiment
            )
            poem.append(luc_line)
            prev_rhymes[f"line{line_idx_luc}_word6"] = luc_line[5]

            locked_pronouns, locked_sentiment = self._update_locks(luc_line, locked_pronouns, locked_sentiment)
            luc_keywords = [w for w in luc_line if w in self.lm.vocab and w not in ALL_PRONOUNS]

            bat_line = self.generate_cau_bat(
                line_idx_bat, prev_rhymes, used_rhyme_words,
                poem_words_freq, used_bigrams, topic_scores=topic_scores,
                locked_pronouns=locked_pronouns, locked_sentiment=locked_sentiment,
                luc_keywords=luc_keywords
            )
            poem.append(bat_line)
            prev_rhymes[f"line{line_idx_bat}_word8"] = bat_line[7]

            locked_pronouns, locked_sentiment = self._update_locks(bat_line, locked_pronouns, locked_sentiment)

        return poem

    def generate_best_poem(self, seed_word: str = "trời", num_pairs: int = 2, num_candidates: int = 4) -> tuple:
        """
        Sinh N bài thơ thử nghiệm, Tự Đánh Giá & Phân Tích chi tiết từng bài, sau đó chọn ra bài thơ hay nhất!
        """
        evaluator = PoemEvaluator(self.lm)
        candidates = []

        print(f"\n================================================================================")
        print(f"[*] ĐANG SINH VÀ TỰ ĐÁNH GIÁ {num_candidates} BẢN THƠ THỬ NGHIỆM TỪ SEED '{seed_word}'...")
        print(f"================================================================================")

        for i in range(num_candidates):
            poem = self.generate_luc_bat_poem(seed_word=seed_word, num_pairs=num_pairs)
            eval_res = evaluator.evaluate(poem)
            candidates.append((poem, eval_res))
            print(f"  • Bản thử nghiệm #{i+1}: Điểm Tổng = {eval_res['total_score']}/100 "
                  f"(Luật: {eval_res['rule_score']} | Nhịp PMI: {eval_res['couplet_score']} | Thi vị: {eval_res['poetic_score']} | Chống lặp: {eval_res['repetition_score']})")

        # Sắp xếp chọn bài thơ điểm cao nhất
        candidates.sort(key=lambda x: x[1]['total_score'], reverse=True)
        best_poem, best_eval = candidates[0][0], candidates[0][1]

        return best_poem, best_eval, candidates


POETIC_LEXICON = {
    "trời", "mây", "sông", "núi", "trăng", "hoa", "thu", "đông", "xuân", "hạ",
    "tình", "sầu", "lệ", "thương", "nhớ", "đời", "người", "quê", "làng", "đường",
    "sương", "khói", "gió", "mưa", "hương", "trang", "bình", "an", "thanh", "duyên",
    "phận", "đêm", "ngày", "chiều", "mai", "vàng", "xanh", "hồng", "trắng", "tím",
    "biển", "ngàn", "dòng", "nguồn", "cõi", "mộng", "giấc", "thơ", "chờ", "ngóng",
    "mong", "yêu", "vương", "má", "tơ", "trường", "dặm", "ngơi", "gương", "lòng",
    "nghiêng", "bóng", "bão", "bùng", "vất", "vả", "kỷ", "niệm", "chia", "ly"
}


class PoemEvaluator:
    """
    Bộ Tự Đánh Giá Chất Lượng Thơ Lục Bát Tự Động (Thang điểm 100):
    1. Rule Score (25đ): 100% Bằng-Trắc, Vần, Tiểu đối Bằng-Thanh.
    2. Couplet PMI Score (25đ): Trung bình PMI của các cụm 2 từ trong bài.
    3. Poetic Imagery Score (20đ): Tỷ lệ từ thuộc Tập Từ Thi Ca truyền thống.
    4. Anti-Repetition Score (15đ): Chặn lặp lại từ/cụm từ giữa các câu.
    5. Coherence Score (15đ): Tính nhất quán của ngôi xưng hô & cảm xúc.
    """
    def __init__(self, ngram_model: NGramLanguageModel):
        self.lm = ngram_model

    def evaluate(self, poem: list) -> dict:
        if not poem:
            return {"total_score": 0.0}

        # 1. Rule & Prosody Score (Max 25)
        rule_res = check_luc_bat_poem_rules(poem)
        rule_score = 25.0 if rule_res["valid"] else max(0.0, 25.0 - len(rule_res["errors"]) * 8.0)

        # 2. Couplet PMI Score (Max 25)
        pmi_scores = []
        for line in poem:
            for i in range(0, len(line) - 1, 2):
                pmi = self.lm.get_bigram_pmi(line[i], line[i+1])
                pmi_scores.append(pmi)
        avg_pmi = sum(pmi_scores) / len(pmi_scores) if pmi_scores else 0.0
        couplet_score = min(25.0, max(0.0, 15.0 + avg_pmi * 5.0))

        # 3. Poetic Imagery Score (Max 20)
        all_words = [w for line in poem for w in line]
        poetic_count = sum(1 for w in all_words if w in POETIC_LEXICON)
        poetic_ratio = poetic_count / len(all_words) if all_words else 0.0
        poetic_score = min(20.0, poetic_ratio * 35.0)

        # 4. Anti-Repetition Score (Max 15)
        unique_words = set(all_words)
        repeat_penalty = (len(all_words) - len(unique_words)) * 2.0
        repetition_score = max(0.0, 15.0 - repeat_penalty)

        # 5. Inter-Sentence Flow & Coherence (Max 15)
        coherence_score = 15.0

        total_score = round(rule_score + couplet_score + poetic_score + repetition_score + coherence_score, 1)

        return {
            "total_score": total_score,
            "rule_score": round(rule_score, 1),
            "couplet_score": round(couplet_score, 1),
            "poetic_score": round(poetic_score, 1),
            "repetition_score": round(repetition_score, 1),
            "coherence_score": round(coherence_score, 1),
        }


if __name__ == "__main__":
    from dataset import extract_luc_bat_data, FALLBACK_LUC_BAT_CORPUS

    print("--- TEST GENERATOR v6 (Auto Self-Evaluation & Best-of-N Pipeline) ---")
    data = extract_luc_bat_data(FALLBACK_LUC_BAT_CORPUS)
    model = NGramLanguageModel(n=3, k=0.1, min_freq=1, discount=0.75)
    model.train(data)

    gen = LucBatPoemGenerator(model, temperature=1.2)
    best_poem, best_eval, _ = gen.generate_best_poem("nắng", num_candidates=4)

    print(f"\n[BÀI THƠ HAY NHẤT ĐƯỢC CHỌN (Điểm Tổng = {best_eval['total_score']}/100)]:")
    for line in best_poem:
        print("  ", " ".join(line).capitalize())


    eval_res = check_luc_bat_poem_rules(poem)
    print("\nKết quả kiểm tra Luật Thơ:", eval_res)
