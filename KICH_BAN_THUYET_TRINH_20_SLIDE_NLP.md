# KỊCH BẢN THUYẾT TRÌNH CHI TIẾT 20 SLIDE BÁO CÁO ĐỒ ÁN NLP (PHENIKAA UNIVERSITY)

**TÊN DỰ ÁN**: **HỆ THỐNG SINH THƠ LỤC BÁT TIẾNG VIỆT ĐA PHƯƠNG ÁN: TỪ FINE-TUNING/CHƯƠNG CẤT MÔ HÌNH, THỐNG KÊ RULE ENGINE ĐẾN HỆ HYBRID NEURO-SYMBOLIC LLM (GEMMA-4-12B)**

* **Học phần**: Xử Lý Ngôn Ngữ Tự Nhiên và Học Máy (NLP_N01_PKA_2) – Phenikaa University
* **Thời lượng thuyết trình dự kiến**: 15 - 20 Phút (Mỗi slide 45 - 60 giây)

---

## SLIDE 1: TIÊU ĐỀ BÁO CÁO & THÔNG TIN DỰ ÁN
* **Tiêu đề Slide**: HỆ THỐNG SINH THƠ LỤC BÁT TIẾNG VIỆT ĐA PHƯƠNG ÁN (NEURO-SYMBOLIC HYBRID AI)
* **Nội dung hiển thị trên Slide**:
  - Đơn vị: Khoa Công nghệ Thông tin – Trường Đại học Phenikaa (Phenikaa University).
  - Học phần: Xử Lý Ngôn Ngữ Tự Nhiên & Học Máy (NLP_N01_PKA_2).
  - Tên dự án: Hệ thống sinh thơ Lục Bát Tiếng Việt đa phương án.
  - Nhóm thực hiện: PKA NLP Team.
  - Mã nguồn dự án: GitHub Repository `poppykitu/PKA_NLP_N01_VietnamPoetry`.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Kính chào Thầy/Cô và các bạn sinh viên. Hôm nay nhóm PKA NLP Team xin phép được báo cáo đồ án học phần Xử lý Ngôn ngữ Tự nhiên với đề tài: *Hệ thống sinh thơ Lục Bát Tiếng Việt đa phương án: Từ nghiên cứu Fine-Tuning chưng cất mô hình, hệ thống Thống kê Rule Engine đến Kiến trúc SOTA Neuro-Symbolic Hybrid AI*. Bài thuyết trình hôm nay sẽ trình bày chi tiết quy trình nghiên cứu, các thử nghiệm thành công cũng như thất bại, và giải pháp kỹ thuật tối ưu nhất mà nhóm đã triển khai."

---

## SLIDE 2: ĐẶT VẤN ĐỀ & TÍNH CẤP THIẾT CỦA BÀI TOÁN
* **Tiêu đề Slide**: THÁCH THỨC CỦA BÀI TOÁN SINH THƠ LỤC BÁT TIẾNG VIỆT
* **Nội dung hiển thị trên Slide**:
  - Tiếng Việt đơn lập, đa thanh điệu (6 thanh cơ bản).
  - Thơ Lục Bát có 5 ràng buộc thi ca khắt khe:
    1. Cấu trúc số âm tiết: Luân phiên Lục (6) - Bát (8).
    2. Luật Bằng - Trắc bất biến tại vị trí 2-4-6-8.
    3. Quy tắc gieo vần chân và vần lưng.
    4. Quy tắc đối thanh âm vực Ngang - Huyền ở tiếng 6 và tiếng 8 câu Bát.
    5. Cú pháp loại từ POS & Bảo tồn liên kết cụm từ Danh-Tính từ.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Sinh văn bản nghệ thuật luôn là thách thức đỉnh cao trong NLP. Đối với thơ Lục Bát Tiếng Việt, mô hình AI không chỉ cần khả năng sáng tạo ý tưởng mà còn phải tuân thủ tuyệt đối 5 ràng buộc toán học thi ca cực kỳ khắt khe: từ số từ 6-8, luật Bằng-Trắc các vị trí chẵn, gieo vần chân/lưng, đối thanh Ngang-Huyền câu Bát, cho đến tính tự nhiên về ngữ pháp POS."

---

## SLIDE 3: MỤC TIÊU DỰ ÁN & 4 CHUẨN ĐẦU RA (LEARNING OUTCOMES)
* **Tiêu đề Slide**: MỤC TIÊU NGHIÊN CỨU VÀ CHUẨN ĐẦU RA HỌC PHẦN (LOs)
* **Nội dung hiển thị trên Slide**:
  - LO1: Khảo sát & làm chủ kỹ thuật từ NLP Thống kê truyền thống đến Large Language Models (LLM).
  - LO2: Xử lý dữ liệu lớn (84.686 bài thơ Lục Bát, 38.633 từ vựng POS Quốc Gia).
  - LO3: Xây dựng thuật toán Neuro-Symbolic & tối ưu hóa quy trình sửa lỗi tự động.
  - LO4: Đánh giá định lượng đa tiêu chí (Độ đúng luật 100%, Chống overfitting Jaccard = 0.18).
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Dự án được thiết kế nhằm đáp ứng trọn vẹn 4 chuẩn đầu ra môn học của Phenikaa University: nghiên cứu sâu lý thuyết NLP, xử lý tập dữ liệu lớn hàng triệu token, thiết kế thuật toán lai Neuro-Symbolic tiên tiến và thực hiện đánh giá thực nghiệm định lượng minh bạch."

---

## SLIDE 4: TỔNG QUAN 3 PHƯƠNG ÁN TIẾP CẬN TRONG DỰ ÁN
* **Tiêu đề Slide**: KHẢO SÁT & THỬ NGHIỆM 3 PHƯƠNG ÁN KỸ THUẬT
* **Nội dung hiển thị trên Slide**:
  - **Phương án 1**: Fine-Tuning Qwen-2.5-7B (Chưng cất tri thức từ Gemini 3.5 Flash) $\rightarrow$ **THẤT BẠI (0/100)**.
  - **Phương án 2**: Thống kê Rule-Based Engine (N-gram Kneser-Ney 3-Gram + Best-of-N Evaluator) $\rightarrow$ **ĐẠT 60/100 ĐIỂM**.
  - **Phương án 3**: SOTA Neuro-Symbolic Hybrid AI (Local Gemma-4-12B + Rule Repair Engine 3 Tầng) $\rightarrow$ **XUẤT SẮC 90+/100 ĐIỂM**.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Để tìm ra lời giải tốt nhất, nhóm đã thử nghiệm qua 3 phương án: Phương án 1 dùng Fine-tuning Qwen 7B chưng cất từ Gemini 3.5 Flash nhưng thất bại; Phương án 2 dùng mô hình Thống kê Rule-based đạt 60 điểm vì đúng luật nhưng thiếu sáng tạo; và Phương án 3 là mô hình lai Neuro-Symbolic đạt trên 90 điểm hoàn hảo."

---

## SLIDE 5: TẬP DỮ LIỆU THI CA VÀ TỪ ĐIỂN QUỐC GIA
* **Tiêu đề Slide**: TẬP DỮ LIỆU HUẤN LUYỆN VÀ TRI THỨC NGÔN NGỮ
* **Nội dung hiển thị trên Slide**:
  - `phamson02/vietnamese-poetry-corpus`: **84.686 bài thơ Lục Bát** (286.206 câu thơ, 3.4M tokens).
  - `tsdocode/vietnamese-dictionary`: **36.764 mục từ điển Quốc gia** (chiết xuất 24.608 từ loại chuẩn).
  - Từ điển Đa loại từ Gemma AI (4.659 từ thi ca) $\rightarrow$ **Tổng quy mô POS: 38.633 TỪ VỰNG**.
  - Xử lý cache nhị phân `.pkl` giúp nạp dữ liệu < 0.1 giây.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Về dữ liệu, nhóm khai thác tập thơ Lục Bát lớn nhất hiện nay với hơn 84 nghìn bài thơ từ Hugging Face để làm giàu tri thức N-gram. Đồng thời, nhóm tích hợp Từ điển Tiếng Việt Quốc Gia với hơn 38 nghìn từ vựng được dán nhãn loại từ POS để kiểm soát cú pháp Tiếng Việt."

---

## SLIDE 6: PHƯƠNG ÁN 1 - FINE-TUNING QWEN-2.5-7B BẰNG CHƯƠNG CẤT GEMINI 3.5 FLASH
* **Tiêu đề Slide**: PHƯƠNG ÁN 1: THỬ NGHIỆM FINE-TUNING BẰNG KNOWLEDGE DISTILLATION
* **Nội dung hiển thị trên Slide**:
  - Ý tưởng: Dùng mô hình Gemini 3.5 Flash sinh 10.000 mẫu cặp Prompt-Poem chuẩn Lục Bát (Teacher Model).
  - Huấn luyện Student Model **Qwen-2.5-7B-Instruct** bằng kỹ thuật QLoRA (Rank=16, Alpha=32).
  - Mục tiêu: Ép Qwen 7B tự học thuộc lòng luật Lục Bát để sinh thơ trực tiếp.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Ở Phương án 1, nhóm đặt giả thuyết: Liệu có thể dùng kỹ thuật Chưng cất tri thức (Knowledge Distillation) từ mô hình mạnh Gemini 3.5 Flash để Fine-tune mô hình nhỏ Qwen-2.5-7B sinh thơ Lục Bát trực tiếp được không?"

---

## SLIDE 7: PHÂN TÍCH NGUYÊN NHÂN THẤT BẠI CỦA PHƯƠNG ÁN 1
* **Tiêu đề Slide**: PHÂN TÍCH NGUYÊN NHÂN THẤT BẠI CỦA PHƯƠNG ÁN 1 (0/100 ĐIỂM)
* **Nội dung hiển thị trên Slide**:
  - Qwen-2.5-7B không hội tụ luật thanh Bằng - Trắc (thanh điệu ẩn trong từ Tiếng Việt).
  - Tỷ lệ sai vị trí 2-4-6-8 vẫn lên tới **68%**.
  - Hiện tượng lặp câu (Hallucination) và vỡ vần nghiêm trọng.
  - **Kết luận**: Mô hình Neural pure (LLM thuần túy) không thể tự đảm bảo 100% ràng buộc toán học thi ca cứng nếu không có bộ luật Symbolic kiểm soát.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Tuy nhiên, thử nghiệm này đã THẤT BẠI hoàn toàn. Mô hình Qwen 7B sau fine-tuning vẫn bị sai luật Bằng-Trắc tới 68%, bị lặp từ và vỡ vần. Điều này chứng minh: Các mô hình Neural thuần túy không thể tự học thuộc 100% các luật toán học thi ca cứng nếu không có sự can thiệp của bộ luật Symbol."

---

## SLIDE 8: PHƯƠNG ÁN 2 - MÔ HÌNH THỐNG KÊ RULE-BASED ENGINE (60/100 ĐIỂM)
* **Tiêu đề Slide**: PHƯƠNG ÁN 2: STATISTICAL NLP (KNESER-NEY N-GRAM & PMI)
* **Nội dung hiển thị trên Slide**:
  - Mô hình Interpolated Kneser-Ney 3-Gram ($d=0.75$).
  - Ma trận tương quan ngữ nghĩa PMI giữa Seed Prompt và từ gieo vần.
  - Bộ Tự Đánh Giá Định Lượng Best-of-N Evaluator 5 Tiêu Chí (Luật, PMI, Từ thi ca, Anti-repetition, Mượt mà).
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Chuyển sang Phương án 2, nhóm xây dựng mô hình NLP Thống kê truyền thống dựa trên Kneser-Ney 3-Gram kết hợp ma trận PMI và bộ tự đánh giá Best-of-N sinh 50 bản chọn 1."

---

## SLIDE 9: ĐÁNH GIÁ ƯU & NHƯỢC ĐIỂM PHƯƠNG ÁN 2 (ĐẠT 60/100 ĐIỂM)
* **Tiêu đề Slide**: ĐÁNH GIÁ KẾT QUẢ PHƯƠNG ÁN 2 (60/100 ĐIỂM)
* **Nội dung hiển thị trên Slide**:
  - **Ưu điểm**: Độ chính xác luật thơ đạt **100%**, tốc độ cực nhanh (<0.5 giây).
  - **Nhược điểm lớn**:
    - Thiếu tính sáng tạo ý tưởng nghệ thuật.
    - Dễ bị lặp lại các câu thơ cũ trong dataset (Chỉ số Overfitting Jaccard = 0.42, 14.2% trùng câu).
  - **Đánh giá chung**: Đạt 60/100 điểm.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Phương án 2 đạt 100% độ chính xác luật thơ và chạy cực nhanh, nhưng nhược điểm lớn nhất là thiếu sáng tạo, câu thơ bị khô cứng và dễ lặp lại câu có sẵn trong tập huấn luyện. Phương án này đạt 60 điểm."

---

## SLIDE 10: PHƯƠNG ÁN 3 - SOTA NEURO-SYMBOLIC HYBRID AI (90+/100 ĐIỂM)
* **Tiêu đề Slide**: PHƯƠNG ÁN 3: KIẾN TRÚC SOTA NEURO-SYMBOLIC HYBRID AI
* **Nội dung hiển thị trên Slide**:
  - Triết lý Neuro-Symbolic: Kết hợp trí tuệ sáng tạo Neural với sự chính xác tuyệt đối Symbolic.
  - **Tầng 1 (Neuro Stage)**: Local LLM Gemma-4-12B-QAT sinh bản thảo thô giàu hình ảnh.
  - **Tầng 2 (Symbolic Stage)**: Rule Repair Engine 3 Tầng tự động sửa lỗi cấu trúc, thanh điệu & POS.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Để giải quyết triệt để nhược điểm của 2 phương án trên, nhóm đã sáng tạo kiến trúc SOTA Neuro-Symbolic Hybrid AI ở Phương án 3. Sự kết hợp giữa Tầng 1 (LLM Gemma 12B sinh ý tưởng nghệ thuật) và Tầng 2 (Rule Repair Engine sửa lỗi tự động) đã giúp hệ thống đạt 90+ điểm xuất sắc."

---

## SLIDE 11: TẦNG 1 - LOCAL LLM ENGINE (GEMMA-4-12B VIA LM STUDIO)
* **Tiêu đề Slide**: TẦNG 1: NEURO STAGE - LOCAL LLM GENERATIVE ENGINE
* **Nội dung hiển thị trên Slide**:
  - Host mô hình `google/gemma-4-12b-qat` local trên LM Studio Server cổng `1234`.
  - Kết nối qua REST API HTTP Client.
  - Ép cấu trúc đầu ra bằng **Structured JSON Schema**: Bắt buộc LLM trả về mảng đúng 4 câu thơ Lục Bát.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Ở Tầng 1, mô hình Gemma-4-12B chạy local thông qua LM Studio API. Nhóm đã sử dụng kĩ thuật Structured JSON Schema để ép LLM luôn trả về mảng 4 câu thơ Lục Bát đầy đủ ý tưởng nghệ thuật."

---

## SLIDE 12: TẦNG 2 - SYMBOLIC RULE REPAIR ENGINE 3 TẦNG
* **Tiêu đề Slide**: TẦNG 2: SYMBOLIC STAGE - BỘ SỬA LỖI TỰ ĐỘNG 3 TẦNG
* **Nội dung hiển thị trên Slide**:
  - **Tier 1 (Sửa độ dài câu)**: Cắt hư từ nếu thừa, chèn từ đệm nếu thiếu (đủ 6-8 từ).
  - **Tier 2 (Sửa thanh 2 & 4)**: Tra cứu ma trận Bigram N-gram Corpus sửa tiếng 2 (Bằng) và tiếng 4 (Trắc).
  - **Tier 3 (Sửa vần & đối âm vực)**: Ép đối thanh Bằng Ngang - Huyền ở tiếng 6 & 8 câu Bát và sửa vần chân/lưng.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Tầng 2 là trái tim của hệ thống: Rule Repair Engine 3 tầng. Nếu bản thảo thô từ LLM bị lệch thanh hay sai vần, Tầng 2 sẽ tự động can thiệp, sửa câu thơ đạt 100% chuẩn luật thi ca."

---

## SLIDE 13: VẤN ĐỀ 1 & GIẢI PHÁP - KIỆT TOKEN SUY LUẬN LM STUDIO API
* **Tiêu đề Slide**: VẤN ĐỀ 1: LỖI KIỆT TOKEN SUY LUẬN API VÀ GIẢI PHÁP
* **Nội dung hiển thị trên Slide**:
  - **Vấn đề**: Cấu hình API `max_tokens: 300` làm Gemma-4-12B kiệt ngân sách token vào phần suy luận (`reasoning_content`), trả về chuỗi JSON rỗng.
  - **Nguyên nhân**: Token suy luận nội bộ của LLM tiêu tốn giới hạn token trước khi kịp xuất kết quả.
  - **Biện pháp**: Loại bỏ hoàn toàn `max_tokens` khỏi HTTP Payload để LLM tự do suy luận và sinh JSON đầy đủ.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Trong quá trình phát triển, nhóm đã gặp 5 vấn đề lớn. Vấn đề 1 là LM Studio bị trả về JSON rỗng do cài `max_tokens: 300` làm kiệt token suy luận của Gemma 12B. Giải pháp là loại bỏ hoàn toàn giới hạn max_tokens khỏi payload."

---

## SLIDE 14: VẤN ĐỀ 2 & GIẢI PHÁP - TỰ ĐỘNG KHAI PHÁ N-GRAM CORPUS BIGRAM
* **Tiêu đề Slide**: VẤN ĐỀ 2: TỰ ĐỘNG KHAI PHÁ BIGRAM CORPUS THAY CHO TỪ ĐIỂN CỨNG
* **Nội dung hiển thị trên Slide**:
  - **Vấn đề**: Sử dụng mảng tra cứu cứng `POETIC_COLLOCATIONS` làm câu thơ bị gượng ép và lặp từ.
  - **Biện pháp**: Khai phá tự động **Bigram Followers từ 3.4M N-gram tập thơ** (`ngram_model_hf.pkl`).
  - Hệ thống tự tìm từ $w_2$ có tần suất cao nhất sau $w_1$ thỏa mãn thanh điệu và loại từ POS.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Vấn đề 2 là việc ghép từ thủ công làm câu thơ thiếu tự nhiên. Nhóm đã khắc phục bằng cách xây dựng thuật toán tự động chiết xuất ma trận Bigram từ 3.4 triệu N-gram tập thơ, giúp việc chọn từ thay thế đạt độ mượt mà cao nhất."

---

## SLIDE 15: VẤN ĐỀ 3 & 4 & GIẢI PHÁP - BẢO TỒN MIỀN NGỮ NGHĨA & TỪ TRUNG GIAN
* **Tiêu đề Slide**: VẤN ĐỀ 3 & 4: BẢO TỒN MIỀN NGỮ NGHĨA CỤM TỪ DANH-TÍNH TỪ
* **Nội dung hiển thị trên Slide**:
  - **Vấn đề 3**: Thay `Đôi mắt` (Trắc) $\rightarrow$ `Đôi ta` (Bằng) làm lệch miền ngữ nghĩa tả đôi mắt.
    $\rightarrow$ **Giải pháp**: Ma trận `POETIC_SYNONYM_MAP` đổi `mắt` $\rightarrow$ **`mi`** (trong *"Đôi mi"*).
  - **Vấn đề 4**: Thay ngẫu nhiên 2 vị trí làm vỡ từ ở giữa (`tròn`) thành *"Đôi ta tròn lại"*.
    $\rightarrow$ **Giải pháp**: Thuật toán `repair_phrase_chunk` bảo tồn 100% Tính từ trung gian **`"Đôi mi tròn biếc"`**.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Vấn đề 3 và 4 là lỗi lệch miền ngữ nghĩa và vỡ cụm từ trung gian khi sửa từ `Đôi mắt tròn xoe`. Nhóm đã tạo ma trận POETIC_SYNONYM_MAP đổi `mắt` thành `mi` để giữ nguyên nghĩa tả đôi mắt, đồng thời tinh chỉnh thuật toán repair_phrase_chunk bảo tồn từ `tròn` ở giữa để tạo thành cụm thi vị *Đôi mi tròn biếc*."

---

## SLIDE 16: VẤN ĐỀ 5 & GIẢI PHÁP - BỘ SO SÁNH TẦN SUẤT CORPUS FREQUENCY RANKING
* **Tiêu đề Slide**: VẤN ĐỀ 5: BỘ SO SÁNH TẦN SUẤT N-GRAM CORPUS XẾP HẠNG ỨNG VIÊN
* **Nội dung hiển thị trên Slide**:
  - Băn khoăn: Giữ từ `tròn` (`"Đôi mi tròn biếc"`) hay Bỏ `tròn` thay cụm mới (`"Đôi mi khép nhẹ"`)?
  - **Giải pháp**: Xây dựng `score_segment_corpus_frequency` chấm điểm tần suất thực tế trong 3.4M N-gram:
    - `"Đôi mi tròn biếc"` $\rightarrow$ Điểm Corpus: **28**
    - `"Đôi mi khép nhẹ"` $\rightarrow$ Điểm Corpus: **69** (Phổ biến gấp 2.5 lần)
    - `"Đôi hàng mi nhỏ"` $\rightarrow$ Điểm Corpus: **217** (Phổ biến gấp 7.7 lần)
  - **Kết luận**: Hệ thống tự động chọn phương án có điểm tần suất cao nhất!
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Vấn đề 5 là việc lựa chọn định lượng giữa giữ từ `tròn` hay thay bằng cụm từ phổ biến hơn. Nhóm đã viết thuật toán chấm điểm tần suất N-gram thực tế. Nếu cụm *Đôi mi khép nhẹ* có điểm tần suất 69 cao hơn cụm *Đôi mi tròn biếc* (28 điểm), hệ thống sẽ TỰ ĐỘNG CHỌN cụm phổ biến hơn!"

---

## SLIDE 17: PHÂN TÍCH THỰC NGHIỆM & CASE STUDY BÀI THƠ "CON MÈO"
* **Tiêu đề Slide**: KẾT QUẢ CHẠY DEMO THỰC TẾ TRÊN TERMINAL (CHỦ ĐỀ: CON MÈO)
* **Nội dung hiển thị trên Slide**:
  - **Bản thảo thô LLM (Tầng 1)**:
    *"Đôi mắt tròn xoe êm đềm dõi nhìn"* (Sai thanh tiếng 2 `mắt` & tiếng 4 `xoe`).
  - **Kết quả sau sửa lỗi (Tầng 2)**:
    *"Nằm nghe nắng đổ bên thềm"*
    *"Đôi mi tròn chữ êm đềm dõi theo"*
    *"Bộ lông mềm mại tựa neo"*
    *"Khẽ khàng bước nhẹ trôi bèo yêu thương"*
  - Đánh giá: **Thỏa mãn 100% luật Lục Bát, hình ảnh thi vị**.
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Đây là kết quả chạy thực tế với chủ đề 'con mèo'. Câu thô từ LLM bị sai thanh ở câu 2 đã được Tầng 2 sửa lại thành 'Đôi mi tròn chữ êm đềm dõi theo', gieo vần chân với 'tựa neo' và vần lưng với 'trôi bèo', tạo nên bài thơ chuẩn luật và giàu cảm xúc."

---

## SLIDE 18: KIỂM THỬ CHỐNG OVERFITTING VÀ ĐỘ SÁNG TẠO
* **Tiêu đề Slide**: ĐÁNH GIÁ ĐỘ SÁNG TẠO VÀ KHẢ NĂNG CHỐNG OVERFITTING
* **Nội dung hiển thị trên Slide**:
  - Phương pháp: So sánh 100 bài thơ sinh ra với 84.686 bài thơ gốc trong dataset bằng chỉ số Jaccard Similarity và Exact String Match.
  - **Phương án 1 & 2**: Trùng câu 14.2%, Jaccard = 0.42 (Dễ học vẹt N-gram).
  - **Phương án 3 (Neuro-Symbolic)**: **TRÙNG CÂU 0.0%**, Jaccard = **0.18**.
  - **Kết luận**: Phương án 3 đạt độ sáng tạo 100% hoàn toàn mới!
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Để chứng minh mô hình không bị học vẹt, nhóm đã đo đạc độ trùng lặp với 84 nghìn bài thơ gốc. Kết quả: Phương án 3 Neuro-Symbolic đạt 0.0% tỷ lệ trùng câu và chỉ số Jaccard cực thấp (0.18), khẳng định các bài thơ sinh ra là hoàn toàn mới."

---

## SLIDE 19: BẢNG TỔNG KẾT SO SÁNH 3 PHƯƠNG ÁN NGHIÊN CỨU
* **Tiêu đề Slide**: BẢNG TỔNG KẾT SO SÁNH ĐÁNH GIÁ 3 PHƯƠNG ÁN

| Tiêu Chí So Sánh | Phương Án 1 (Fine-Tune Qwen 7B) | Phương Án 2 (Statistical N-gram) | Phương Án 3 (Neuro-Symbolic Hybrid) |
| :--- | :--- | :--- | :--- |
| **Kiến trúc Cốt lõi** | Fine-Tuning QLoRA | N-gram 3-Gram + Rules | Gemma-4-12B Local + Rule Engine |
| **Tính Sáng Tạo Ý Tưởng** | Thấp (Bị lặp từ/vỡ câu) | Trung bình (Dựa trên N-gram) | **Cực Cao (Trí tuệ 12B LLM)** |
| **Độ Chính Xác Luật Thơ** | Sai 68% (Thất bại) | **100% (Best-of-N Filter)** | **100% (Rule Repair Engine)** |
| **Chống Overfitting** | Thấp | Trùng câu 14.2% | **Trùng câu 0.0% (Sáng tạo mới)** |
| **ĐIỂM ĐÁNH GIÁ TỔNG THỂ**| **0 / 100 ĐIỂM** | **60 / 100 ĐIỂM** | **90+ / 100 ĐIỂM (XUẤT SẮC)** |

* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Bảng tổng hợp này thể hiện rõ hành trình nghiên cứu: Phương án 1 thất bại (0 điểm), Phương án 2 đạt 60 điểm chuẩn luật nhưng lặp lại, và Phương án 3 Neuro-Symbolic xuất sắc đạt 90+ điểm dung hòa hoàn hảo giữa tính sáng tạo và độ chính xác."

---

## SLIDE 20: KẾT LUẬN, CHUẨN ĐẦU RA (LOs) VÀ HƯỚNG PHÁT TRIỂN
* **Tiêu đề Slide**: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN TRONG TƯƠNG LAI
* **Nội dung hiển thị trên Slide**:
  - **Kết luận**: Đã hoàn thành 100% mục tiêu đề ra và đáp ứng trọn vẹn 4 Chuẩn đầu ra môn học (LO1 - LO4).
  - **Đóng góp**: Xây dựng thành công hệ thống Neuro-Symbolic Hybrid AI sinh thơ Lục Bát chuẩn mực đầu tiên tích hợp 38.633 từ loại POS và 3.4M N-grams.
  - **Hướng phát triển tương lai**:
    1. Fine-tuning LoRA trực tiếp trên các dòng mô hình Qwen-2.5-7B / LLaMA-3.
    2. Xây dựng giao diện Web Application trực quan bằng Next.js / FastAPI.
  - **Lời cảm ơn**: Xin chân thành cảm ơn Thầy/Cô đã lắng nghe!
* **Lời thoại thuyết trình (Speaker Notes)**:
  > "Tóm lại, đồ án đã chứng minh tính hiệu quả vượt trội của giải pháp Neuro-Symbolic Hybrid AI cho bài toán sinh thơ Lục Bát Tiếng Việt. Nhóm xin chân thành cảm ơn Thầy/Cô đã theo dõi. Xin kính mời Thầy/Cô đặt câu hỏi góp ý cho nhóm!"

---

## BỘ CÂU HỎI VÀ GỢI Ý TRẢ LỜI PHẢN BIỆN (Q&A DEFENSE PREPARATION)

### Câu hỏi 1: Tại sao Phương án 1 Fine-tuning Qwen 7B chưng cất từ Gemini 3.5 Flash lại thất bại?
* **Trả lời**: Do đặc thù Tiếng Việt là ngôn ngữ thanh điệu, các thanh Bằng-Trắc nằm ở dấu thanh âm tiết chứ không nằm công khai ở dạng chữ viết không dấu. Khi Fine-tune LLM thuần túy, mô hình Neural chỉ dự đoán token tiếp theo theo xác suất thống kê chuỗi mà không có cơ chế đếm số âm tiết (6-8) hay kiểm tra bảng thanh cứng. Do đó, mô hình bị lặp từ và sai luật Bằng-Trắc tới 68%.

### Câu hỏi 2: Làm thế nào hệ thống đảm bảo liên kết cụm từ không bị lệch nghĩa khi sửa từ?
* **Trả lời**: Hệ thống kết hợp 2 cơ chế: (1) Ma trận `POETIC_SYNONYM_MAP` bảo tồn miền ngữ nghĩa thi ca (chuyển `mắt` Trắc thành `mi` Bằng); và (2) Thuật toán `repair_phrase_chunk` sửa độc lập tiếng 2 và tiếng 4 dựa trên từ đứng trước và từ đứng sau, bảo tồn nguyên vẹn từ trung gian (như từ `tròn` trong *"Đôi mi tròn biếc"*).

### Câu hỏi 3: Chỉ số Overfitting được đo đạc như thế nào?
* **Trả lời**: Nhóm trích xuất toàn bộ câu thơ trong tập dữ liệu 84.686 bài thơ gốc. Sau đó cho mô hình sinh 100 bài thơ mới và so sánh bằng chỉ số Jaccard Similarity cấp n-gram và Exact Match. Phương án 3 đạt 0.0% trùng nguyên câu và Jaccard = 0.18, chứng minh bài thơ tạo ra là sáng tạo hoàn toàn mới.
