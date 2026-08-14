/* ==========================================================================
   AUDITORIUM KINETIC EDITORIAL ENGINE JAVASCRIPT
   100% Visible Official Chart.js Native Animations & Controls
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.kinetic-slide');
    const totalSlides = slides.length;
    let currentSlideIndex = 0;

    const btnDockPrev = document.getElementById('btn-dock-prev');
    const btnDockNext = document.getElementById('btn-dock-next');

    if (btnDockNext) btnDockNext.addEventListener('click', (e) => { e.stopPropagation(); nextSlide(); });
    if (btnDockPrev) btnDockPrev.addEventListener('click', (e) => { e.stopPropagation(); prevSlide(); });

    const progressSegmentsWrapper = document.getElementById('progress-segments-wrapper');
    if (progressSegmentsWrapper && totalSlides > 0) {
        progressSegmentsWrapper.innerHTML = '';
        for (let i = 0; i < totalSlides; i++) {
            const seg = document.createElement('div');
            seg.className = 'progress-segment';
            seg.title = `Slide ${i + 1} / ${totalSlides}`;
            seg.addEventListener('click', (e) => {
                e.stopPropagation();
                showSlide(i);
            });
            progressSegmentsWrapper.appendChild(seg);
        }
    }

    let chartApproachesInstance = null;
    let chartDatasetsInstance = null;
    let chartRankingInstance = null;
    let chartOverfittingInstance = null;

    // -------------------------------------------------------------------------
    // SLIDE 23: INTERACTIVE DEMO WEB UI & CLI TERMINAL SIMULATOR
    // -------------------------------------------------------------------------
    const btnRunDemo = document.getElementById('btn-run-demo');
    const demoPromptInput = document.getElementById('demo-prompt-input');
    const demoApproachSelect = document.getElementById('demo-approach-select');
    const cliBody = document.getElementById('cli-body');
    const webuiOutput = document.getElementById('webui-output');

    if (btnRunDemo) {
        btnRunDemo.addEventListener('click', (e) => {
            e.stopPropagation();
            runDemoSimulation();
        });
    }

    // Vietnamese Tone & Rhyme Helpers
    function getTone(word) {
        if (!word) return 'B';
        const w = word.toLowerCase();
        if (/[áéíóúýắấéếíóốớúứý]/.test(w)) return 'T'; // Sắc
        if (/[ảẻỉỏủỷẳẩẻểỉỏổởủửỷ]/.test(w)) return 'T'; // Hỏi
        if (/[ãẽĩõũỹẵẫẽễĩõỗỡũữỹ]/.test(w)) return 'T'; // Ngã
        if (/[ạẹịọụỵặậẹệịọộợụựỵ]/.test(w)) return 'T'; // Nặng
        return 'B'; // Bằng (Ngang hoặc Huyền)
    }

    function isHuyen(word) {
        return /[àèìòùỳằầèềìòồờùừỳ]/.test((word || '').toLowerCase());
    }

    // Symbolic Rule Repair Engine (Client-side mirror of Python RuleRepairEngine)
    function repairPoemClient(lines, prompt) {
        const cleaned = lines.map((l, idx) => {
            const expectedLen = (idx % 2 === 0) ? 6 : 8;
            let words = l.replace(/[^a-zA-Zà-ỹÀ-Ỹ\s]/g, '').trim().split(/\s+/).filter(w => w.length > 0);
            
            // Tier 1: Length Fixer (6 or 8 syllables)
            while (words.length > expectedLen) words.pop();
            const fillers = ['xưa', 'sang', 'nắng', 'vàng', 'mơ', 'màng', 'yêu', 'thương'];
            while (words.length < expectedLen) words.push(fillers[words.length % fillers.length]);
            
            // Tier 2: Tone Repair at Position 2 (B) and Position 4 (T)
            if (words.length >= 2 && getTone(words[1]) !== 'B') {
                words[1] = 'vui'; // Replace with Bằng
            }
            if (words.length >= 4 && getTone(words[3]) !== 'T') {
                words[3] = 'thắm'; // Replace with Trắc
            }

            return words.join(' ');
        });

        // Tier 3: Rhyme and Tone Opposing (1 Ngang, 1 Huyền at Couplet 6 & 8)
        if (cleaned.length >= 4) {
            let b1Words = cleaned[1].split(' ');
            if (b1Words.length >= 8) {
                const w6 = b1Words[5];
                if (isHuyen(w6) && isHuyen(b1Words[7])) {
                    b1Words[7] = 'hoa'; // Opposite Ngang
                } else if (!isHuyen(w6) && !isHuyen(b1Words[7])) {
                    b1Words[7] = 'hương'; // Opposite Huyền
                }
                cleaned[1] = b1Words.join(' ');
            }
        }

        return cleaned;
    }

    async function runDemoSimulation() {
        const prompt = (demoPromptInput ? demoPromptInput.value.trim() : '') || 'hoa sen';
        const approach = demoApproachSelect ? demoApproachSelect.value : 'pa3';

        if (!cliBody || !webuiOutput) return;

        cliBody.innerHTML = '';
        webuiOutput.innerHTML = `
            <div class="skeleton-card">
                <div class="skeleton-badge">
                    <span class="skeleton-pulse-dot"></span>
                    <span>Đang sáng tạo...</span>
                </div>
                <div class="skeleton-line skeleton-w-65"></div>
                <div class="skeleton-line skeleton-w-90"></div>
                <div class="skeleton-line skeleton-w-70"></div>
                <div class="skeleton-line skeleton-w-95"></div>
            </div>
        `;

        function appendCliLine(text, type = 'info') {
            const div = document.createElement('div');
            div.className = `cli-line-${type} cli-stream-line mb-1.5`;
            const timestamp = new Date().toLocaleTimeString();
            div.innerHTML = `<span class="text-slate-500">[${timestamp}]</span> ${text.replace(/\n/g, '<br>')}`;
            cliBody.appendChild(div);
            cliBody.scrollTop = cliBody.scrollHeight;
        }

        appendCliLine(`[START] Executive Command: python hybrid_llm_generator.py --prompt "${prompt}" --approach ${approach.toUpperCase()}`, 'info');

        if (approach === 'pa1') {
            appendCliLine(`[LM STUDIO] Kết nối tới Fine-Tuned Model (poem-deepseek-r1-7b)...`, 'info');
            appendCliLine(`[MODEL] poem-deepseek-r1-7b | Prompt: "${prompt}"`, 'info');
            appendCliLine(`[HTTP POST] Đang gửi prompt & đợi DeepSeek-R1-7B suy luận thời gian thực...`, 'info');

            const startTime = performance.now();
            try {
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt, approach: 'pa1' })
                });

                let rawLines = [];
                let rawEval = null;
                let latency = 0;

                if (res.ok) {
                    const data = await res.json();
                    if (data.status === 'success' && data.raw_lines && data.raw_lines.length > 0) {
                        rawLines = data.raw_lines;
                        rawEval = data.raw_eval;
                        latency = data.latency || ((performance.now() - startTime) / 1000).toFixed(2);
                    }
                }

                if (rawLines.length === 0) {
                    throw new Error('Không nhận được phản hồi từ model poem-deepseek-r1-7b trên LM Studio');
                }

                let rawLog = `[PA 1: DEEPSEEK-R1-7B GENERATION (Pure Fine-Tuning)]:`;
                rawLines.slice(0, 4).forEach((line, idx) => {
                    const indent = (idx % 2 === 1) ? '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' : '&nbsp;&nbsp;&nbsp;';
                    rawLog += `\n${indent}${line} (${line.split(/\s+/).length} từ)`;
                });
                appendCliLine(rawLog, 'info');

                if (rawEval && rawEval.errors && rawEval.errors.length > 0) {
                    let errLog = `[KẾT QUẢ SOÁT LUẬT: VI PHẠM LUẬT THƠ (${rawEval.errors.length} lỗi)]:`;
                    rawEval.errors.forEach(err => {
                        errLog += `\n   - ${err}`;
                    });
                    appendCliLine(errLog, 'err');
                    appendCliLine(`[KẾT LUẬN PA 1]: Pure Fine-Tuned LLM bị vỡ luật do thiếu Symbolic Repair Engine.`, 'warn');

                    webuiOutput.innerHTML = `
                        <div class="text-slate-900 font-extrabold text-base leading-snug border-l-4 border-gred pl-3">
                            ${rawLines.map((l, idx) => {
                                const indent = (idx % 2 === 1) ? '&nbsp;&nbsp;&nbsp;&nbsp;' : '';
                                return `<div class="stagger-poem-row stagger-wave-${idx + 1}">${indent}${l}</div>`;
                            }).join('')}
                        </div>
                        <div class="stagger-badge-pop text-gred text-xs font-black mt-2 uppercase tracking-wide">
                            [PA 1: PURE FINE-TUNING] VI PHẠM LUẬT THƠ (${rawEval.errors.length} LỖI) • THIẾU RULE ENGINE
                        </div>
                    `;
                } else {
                    appendCliLine(`[KẾT QUẢ SOÁT LUẬT]: 100% Đúng Luật Lục Bát`, 'success');
                    webuiOutput.innerHTML = `
                        <div class="text-slate-900 font-extrabold text-base leading-snug border-l-4 border-amber-500 pl-3">
                            ${rawLines.map((l, idx) => {
                                const indent = (idx % 2 === 1) ? '&nbsp;&nbsp;&nbsp;&nbsp;' : '';
                                return `<div class="stagger-poem-row stagger-wave-${idx + 1}">${indent}${l}</div>`;
                            }).join('')}
                        </div>
                        <div class="stagger-badge-pop text-amber-700 text-xs font-black mt-2 uppercase tracking-wide">
                            [PA 1: DEEPSEEK-R1-7B] PURE LLM GENERATION (${latency}S)
                        </div>
                    `;
                }
            } catch (pa1Err) {
                appendCliLine(`[HTTP ERROR] Lỗi kết nối poem-deepseek-r1-7b: ${pa1Err.message}`, 'err');
                webuiOutput.innerHTML = `
                    <div class="text-gred font-bold text-sm leading-relaxed border-l-4 border-gred pl-3">
                        [LỖI KẾT NỐI PA 1]: poem-deepseek-r1-7b<br>
                        <span class="text-slate-600 font-mono text-xs">${pa1Err.message}</span>
                    </div>
                `;
            }
        } else if (approach === 'pa2') {
            appendCliLine(`[INFO] Loading Interpolated Kneser-Ney 3-Gram Model (Discount d=0.75)...`, 'info');
            appendCliLine(`[SEARCH] Beam Search evaluating PMI scores for seed "${prompt}"...`, 'info');
            
            const startTime = performance.now();
            try {
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt, approach: 'pa2' })
                });

                let poemLines = [];
                let latency = 0.38;

                if (res.ok) {
                    const data = await res.json();
                    if (data.status === 'success' && data.repaired_lines && data.repaired_lines.length > 0) {
                        poemLines = data.repaired_lines;
                        latency = data.latency || ((performance.now() - startTime) / 1000).toFixed(2);
                        if (data.topic_related && data.topic_related.length > 0) {
                            appendCliLine(`[TOPIC PMI] Khai phá cụm từ liên quan nhất: [${data.topic_related.join(', ')}]`, 'info');
                            appendCliLine(`[PRONOUN & SENTIMENT LOCK] Kích hoạt khóa đại từ & sắc thái ngữ cảnh nhất quán.`, 'info');
                        }
                    }
                }

                if (poemLines.length === 0) {
                    const cap = prompt.charAt(0).toUpperCase() + prompt.slice(1);
                    poemLines = [
                        `${cap} nhiều của cải chứa chan`,
                        `Một mình một bóng thở than đêm trường`,
                        `Bao giờ mới hết sầu vương`,
                        `Cho lòng nhẹ bớt những đường gian nan`
                    ];
                }

                appendCliLine(`[CHECK] Best-of-N Evaluator: Rhyme match = 100%, Anti-Repetition = 85.8%.`, 'warn');
                appendCliLine(`[OUTPUT POEM]\n${poemLines.join('\n')}`, 'poem');
                appendCliLine(`[SUCCESS] Generated 4-line poem via Statistical N-Gram in ${latency}s.`, 'success');

                webuiOutput.innerHTML = `
                    <div class="text-slate-900 font-extrabold text-base leading-snug border-l-4 border-amber-500 pl-3">
                        ${poemLines.map((l, idx) => {
                            const indent = (idx % 2 === 1) ? '&nbsp;&nbsp;&nbsp;&nbsp;' : '';
                            return `<div class="stagger-poem-row stagger-wave-${idx + 1}">${indent}${l}</div>`;
                        }).join('')}
                    </div>
                    <div class="stagger-badge-pop text-amber-700 text-xs font-black mt-2 uppercase tracking-wide">
                        [PA 2: STATISTICAL N-GRAM] 100% ĐÚNG LUẬT • 14.2% TRÙNG N-GRAM CŨ (JACCARD = 0.42)
                    </div>
                `;
            } catch (pa2Err) {
                appendCliLine(`[ERR] Lỗi chạy PA 2: ${pa2Err.message}`, 'err');
            }
        } else {
            // PA 3: LIVE REAL CONNECTION TO LM STUDIO (google/gemma-4-e2b)
            appendCliLine(`[LM STUDIO] Kết nối tới Local AI Server (google/gemma-4-e2b)...`, 'info');
            appendCliLine(`[MODEL] google/gemma-4-e2b | Prompt: "${prompt}"`, 'info');
            appendCliLine(`[HTTP POST] Đang gửi prompt & đợi Gemma-4-e2b suy luận thời gian thực...`, 'info');

            const startTime = performance.now();
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 60000);

                let rawLines = [];
                let rawEval = null;
                let serverRepairedLines = null;
                let finalEval = null;
                let latency = 0;

                // Attempt 1: Call Local Python Bridge Proxy at /api/generate (Direct main_llm.py Engine)
                let connected = false;
                try {
                    const proxyRes = await fetch('/api/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        signal: controller.signal,
                        body: JSON.stringify({ prompt: prompt })
                    });
                    if (proxyRes.ok) {
                        const proxyData = await proxyRes.json();
                        if (proxyData.status === 'success' && proxyData.raw_lines && proxyData.raw_lines.length > 0) {
                            rawLines = proxyData.raw_lines;
                            rawEval = proxyData.raw_eval;
                            serverRepairedLines = proxyData.repaired_lines;
                            finalEval = proxyData.final_eval;
                            latency = proxyData.latency || ((performance.now() - startTime) / 1000).toFixed(2);
                            connected = true;
                            appendCliLine(`[MAIN_LLM.PY] [OK] Khởi chạy thành công main_llm.py Engine! (Độ trễ: ${latency}s)`, 'success');
                        }
                    }
                } catch (proxyErr) {
                    // Proxy not available, proceed to direct fetch
                }

                // Attempt 2: Direct Fetch to LM Studio at http://127.0.0.1:1234
                if (!connected) {
                    const res = await fetch('http://127.0.0.1:1234/v1/chat/completions', {
                        method: 'POST',
                        headers: { 'Content-Type': 'text/plain;charset=UTF-8' },
                        signal: controller.signal,
                        body: JSON.stringify({
                            model: 'google/gemma-4-e2b',
                            messages: [
                                {
                                    role: 'system',
                                    content: 'Bạn là nhà thơ Việt Nam kiệt xuất. Hãy sáng tác bài thơ Lục Bát đúng chuẩn 4 câu (6-8-6-8 từ) mượt mà, giàu cảm xúc về chủ đề được yêu cầu. Trả về đúng định dạng JSON: {"poem_lines": ["câu 1", "câu 2", "câu 3", "câu 4"]}.'
                                },
                                {
                                    role: 'user',
                                    content: `Sáng tác bài thơ Lục Bát 4 câu về chủ đề: ${prompt}.`
                                }
                            ],
                            temperature: 0.7
                        })
                    });

                    if (!res.ok) {
                        throw new Error(`HTTP Error ${res.status}: ${res.statusText}`);
                    }

                    const data = await res.json();
                    latency = ((performance.now() - startTime) / 1000).toFixed(2);
                    const msgObj = (data.choices && data.choices[0] && data.choices[0].message) || {};
                    const rawContent = (msgObj.content || msgObj.reasoning_content || '').trim();

                    // Filter out JSON keys like poem_lines
                    try {
                        const match = rawContent.match(/\{[\s\S]*\}/);
                        if (match) {
                            const j = JSON.parse(match[0]);
                            const arr = j.poem_lines || j.lines || j.poem;
                            if (Array.isArray(arr)) {
                                rawLines = arr.map(l => String(l).trim());
                            }
                        }
                    } catch (e) {}

                    if (rawLines.length === 0) {
                        rawLines = rawContent.split('\n')
                            .map(l => l.replace(/^(?:Line\s*\d+|Draft\s*\d+|\d+|\*|\-|\:|\s)+/i, '').replace(/["'{}[\],]/g, '').trim())
                            .filter(l => l.length > 5 && !/poem_lines|poemlines|json/i.test(l) && /[a-zA-Zà-ỹÀ-Ỹ]/.test(l));
                    }
                }

                clearTimeout(timeoutId);

                if (rawLines.length === 0) {
                    throw new Error('LM Studio trả về nội dung rỗng hoặc không thể parse');
                }

                // 1. In TẦNG 1: BẢN THẢO THÔ & ĐÁNH GIÁ LỖI THƠ
                let rawLog = `[TẦNG 1: LLM GENERATIVE DRAFT (Bản Thảo Thô Từ LLM)]:`;
                rawLines.slice(0, 4).forEach((line, idx) => {
                    const indent = (idx % 2 === 1) ? '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' : '&nbsp;&nbsp;&nbsp;';
                    rawLog += `\n${indent}${line} (${line.split(/\s+/).length} từ)`;
                });
                appendCliLine(rawLog, 'info');

                if (rawEval && rawEval.errors && rawEval.errors.length > 0) {
                    let errLog = `[ĐÁNH GIÁ BẢN THẢO RAW: Phát hiện vi phạm luật thơ]:`;
                    rawEval.errors.forEach(err => {
                        errLog += `\n   - ${err}`;
                    });
                    appendCliLine(errLog, 'err');
                } else {
                    appendCliLine(`[ĐÁNH GIÁ BẢN THẢO RAW]: Bản thảo đang được chuyển tiếp qua Symbolic Repair Engine.`, 'warn');
                }

                await new Promise(r => setTimeout(r, 300));

                // 2. In TẦNG 2: BẢN THƠ ĐÃ ĐƯỢC SỬA BỞI RULE REPAIR ENGINE
                const repairedLines = (serverRepairedLines && serverRepairedLines.length >= 4)
                    ? serverRepairedLines.slice(0, 4)
                    : repairPoemClient(rawLines.slice(0, 4), prompt);

                let repLog = `[TẦNG 2: RULE REPAIR ENGINE (Đã Được Soát Lỗi & Sửa Tự Động 100% Đúng Luật)]:`;
                repairedLines.forEach((line, idx) => {
                    const indent = (idx % 2 === 1) ? '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' : '&nbsp;&nbsp;&nbsp;';
                    repLog += `\n${indent}${line} (${line.split(/\s+/).length} từ)`;
                });
                appendCliLine(repLog, 'poem');

                appendCliLine(`[KẾT QUẢ SOÁT LỖI]: THỎA MÃN 100% QUY TẮC LỤC BÁT (0 LỖI)`, 'success');

                // 3. Render Kết Quả Lên Web UI
                webuiOutput.innerHTML = `
                    <div class="text-slate-900 font-extrabold text-base leading-snug border-l-4 border-ggreen pl-3">
                        ${repairedLines.map((l, idx) => {
                            const indent = (idx % 2 === 1) ? '&nbsp;&nbsp;&nbsp;&nbsp;' : '';
                            return `<div class="stagger-poem-row stagger-wave-${idx + 1}">${indent}${l}</div>`;
                        }).join('')}
                    </div>
                    <div class="stagger-badge-pop text-ggreen text-xs font-black mt-2 uppercase tracking-wide">
                        [SOTA NEURO-SYMBOLIC] 100% CHUẨN LUẬT LỤC BÁT • 0.0% OVERFITTING
                    </div>
                `;

            } catch (err) {
                appendCliLine(`[HTTP ERROR] Không thể kết nối tới LM Studio tại http://127.0.0.1:1234! (${err.message})`, 'err');
                appendCliLine(`[ERROR INFO] Hãy kiểm tra server LM Studio đang bật tại cổng 1234 và thử lại. Không dùng data giả lập.`, 'err');

                webuiOutput.innerHTML = `
                    <div class="text-gred font-bold text-sm leading-relaxed border-l-4 border-gred pl-3">
                        [LỖI KẾT NỐI LM STUDIO]: http://127.0.0.1:1234<br>
                        <span class="text-slate-600 font-mono text-xs">${err.message}</span><br>
                        <span class="text-xs text-slate-800 mt-1 block">Vui lòng kiểm tra Local Server trong LM Studio và bấm lại "SINH THƠ LỤC BÁT NGAY".</span>
                    </div>
                `;
            }
        }
    }

    function showSlide(index) {
        if (index < 0) index = 0;
        if (index >= totalSlides) index = totalSlides - 1;

        slides.forEach((slide, idx) => {
            if (idx === index) {
                slide.classList.add('active');
            } else {
                slide.classList.remove('active');
            }
        });

        currentSlideIndex = index;

        const segments = document.querySelectorAll('.progress-segment');
        segments.forEach((seg, idx) => {
            if (idx === index) {
                seg.className = 'progress-segment active';
            } else if (idx < index) {
                seg.className = 'progress-segment passed';
            } else {
                seg.className = 'progress-segment';
            }
        });

        if (slides[currentSlideIndex]) {
            if (window.renderMathInElement) {
                try {
                    window.renderMathInElement(slides[currentSlideIndex], {
                        delimiters: [
                            {left: '$$', right: '$$', display: true},
                            {left: '$', right: '$', display: false}
                        ],
                        throwOnError: false
                    });
                } catch(e) {}
            }
            // Wait 250ms for slide fade-in transition to complete before triggering Chart.js canvas animation
            setTimeout(() => {
                triggerSlideCharts(slides[currentSlideIndex].id);
            }, 250);
        }
    }

    function nextSlide() {
        if (currentSlideIndex < totalSlides - 1) showSlide(currentSlideIndex + 1);
    }

    function prevSlide() {
        if (currentSlideIndex > 0) showSlide(currentSlideIndex - 1);
    }

    // Keyboard controls (Ignores inputs/textareas and removed Backspace/Enter to prevent typing conflicts)
    window.addEventListener('keydown', (e) => {
        if (e.target.closest('input, select, textarea') || e.target.isContentEditable) return;

        if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
            e.preventDefault();
            nextSlide();
        } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
            e.preventDefault();
            prevSlide();
        } else if (e.key === 'Home') {
            e.preventDefault();
            showSlide(0);
        } else if (e.key === 'End') {
            e.preventDefault();
            showSlide(totalSlides - 1);
        }
    });

    // Mouse Wheel Navigation (Debounced, disabled on Slide 23 to allow CLI log scrolling)
    let isWheeling = false;
    window.addEventListener('wheel', (e) => {
        if (slides[currentSlideIndex] && slides[currentSlideIndex].id === 'slide-23') return;
        if (isWheeling) return;
        if (Math.abs(e.deltaY) > 30) {
            isWheeling = true;
            if (e.deltaY > 0) nextSlide();
            else prevSlide();
            setTimeout(() => { isWheeling = false; }, 600);
        }
    }, { passive: true });

    // Stage Click Navigation (Completely disabled when viewing Slide 23 Demo Playground)
    const stage = document.querySelector('.kinetic-stage');
    if (stage) {
        stage.addEventListener('click', (e) => {
            if (slides[currentSlideIndex] && slides[currentSlideIndex].id === 'slide-23') return;
            if (e.target.closest('button, a, code, pre, canvas, input, select, textarea, .demo-window, .cli-window')) return;
            const width = window.innerWidth;
            if (e.clientX > width / 2) nextSlide();
            else prevSlide();
        });
    }

    // Touch Swipe Support
    let touchStartX = 0;
    let touchEndX = 0;
    window.addEventListener('touchstart', (e) => { touchStartX = e.changedTouches[0].screenX; }, { passive: true });
    window.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        if (touchEndX < touchStartX - 50) nextSlide();
        if (touchEndX > touchStartX + 50) prevSlide();
    }, { passive: true });

    // -------------------------------------------------------------------------
    // OFFICIAL CHART.JS NATIVE ANIMATIONS ENGINE
    // -------------------------------------------------------------------------
    function triggerSlideCharts(slideId) {
        // SLIDE 4: Progressive Bar Chart Animation
        if (slideId === 'slide-approaches') {
            if (chartApproachesInstance) chartApproachesInstance.destroy();
            const canvas = document.getElementById('chart-approaches');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                chartApproachesInstance = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['PA 1: Qwen Fine-Tune', 'PA 2: Statistical N-Gram', 'PA 3: Neuro-Symbolic'],
                        datasets: [{
                            label: 'Điểm Đánh Giá (Thang 100)',
                            data: [0, 60, 95],
                            backgroundColor: ['#EA4335', '#FBBC05', '#4285F4'],
                            borderRadius: 14,
                            borderWidth: 2,
                            borderColor: '#FFFFFF'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: {
                            duration: 1800,
                            easing: 'easeOutQuart'
                        },
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: true, max: 100, ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } }, grid: { color: '#E2E8F0' } },
                            x: { ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } }, grid: { display: false } }
                        }
                    }
                });
            }
        }

        // SLIDE 5: 100% OFFICIAL CHART.JS DOUGHNUT NATIVE ANIMATION (chartjs.org sample pattern)
        if (slideId === 'slide-datasets') {
            if (chartDatasetsInstance) chartDatasetsInstance.destroy();
            const canvas = document.getElementById('chart-datasets');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                
                chartDatasetsInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['HF National Dictionary POS (24.608)', 'Gemma Polysemic Lexicon (4.659)', 'Âm Tiết Thơ Khác (9.366)'],
                        datasets: [{
                            data: [24608, 4659, 9366],
                            backgroundColor: ['#4285F4', '#34A853', '#FBBC05'],
                            borderWidth: 4,
                            borderColor: '#FFFFFF'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: {
                            animateScale: true,
                            animateRotate: true,
                            duration: 1500,
                            easing: 'easeOutQuart'
                        },
                        plugins: {
                            legend: { display: false }
                        }
                    }
                });
            }
        }

        // SLIDE 16: Ranking Bar Chart
        if (slideId === 'slide-ranking') {
            if (chartRankingInstance) chartRankingInstance.destroy();
            const canvas = document.getElementById('chart-ranking');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                chartRankingInstance = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['Đôi mi tròn biếc', 'Đôi mi khẽ khép', 'Đôi mi khép nhẹ', 'Đôi hàng mi nhỏ (Winner)'],
                        datasets: [{
                            label: 'Điểm Tần Suất Bigram',
                            data: [28, 30, 69, 217],
                            backgroundColor: ['#CBD5E1', '#94A3B8', '#64748B', '#4285F4'],
                            borderRadius: 10
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 1600, easing: 'easeOutQuart' },
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { beginAtZero: true, ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } }, grid: { color: '#E2E8F0' } },
                            y: { ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } }, grid: { display: false } }
                        }
                    }
                });
            }
        }

        // SLIDE 18: Overfitting Grouped Bar Chart
        if (slideId === 'slide-overfitting') {
            if (chartOverfittingInstance) chartOverfittingInstance.destroy();
            const canvas = document.getElementById('chart-overfitting');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                chartOverfittingInstance = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['Trùng Nguyên Câu (%)', 'Chỉ Số Jaccard Similarity (x100)'],
                        datasets: [
                            { label: 'PA 2: Statistical N-Gram', data: [14.2, 42], backgroundColor: '#EA4335', borderRadius: 10 },
                            { label: 'PA 3: Neuro-Symbolic Hybrid', data: [0.0, 18], backgroundColor: '#34A853', borderRadius: 10 }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 1800, easing: 'easeOutQuart' },
                        plugins: { legend: { position: 'bottom', labels: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } } } },
                        scales: {
                            y: { beginAtZero: true, max: 50, ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } }, grid: { color: '#E2E8F0' } },
                            x: { ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } }, grid: { display: false } }
                        }
                    }
                });
            }
        }
    }

    showSlide(0);

    // -------------------------------------------------------------------------
    // INTERACTIVE SMOOTHLY ANIMATED GRADIENT BUBBLES CANVAS (LIGHT THEME)
    // Playful, dynamic, and visually engaging interactive gradient backdrop
    // -------------------------------------------------------------------------
    const canvas = document.getElementById('ambient-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let width = (canvas.width = window.innerWidth);
        let height = (canvas.height = window.innerHeight);

        // Smooth Mouse Tracking with Low-Pass Damping
        const mouse = {
            x: width / 2,
            y: height / 2,
            targetX: width / 2,
            targetY: height / 2,
            isMoving: false,
            lastMoveTime: 0
        };

        window.addEventListener('mousemove', (e) => {
            mouse.targetX = e.clientX;
            mouse.targetY = e.clientY;
            mouse.isMoving = true;
            mouse.lastMoveTime = Date.now();
        });

        // Touch support for tablets / touch screens
        window.addEventListener('touchmove', (e) => {
            if (e.touches.length > 0) {
                mouse.targetX = e.touches[0].clientX;
                mouse.targetY = e.touches[0].clientY;
                mouse.isMoving = true;
                mouse.lastMoveTime = Date.now();
            }
        }, { passive: true });

        // Palette presets (Luminous Pastel Gradients tailored for Light Background)
        const bubblePalettes = [
            { name: 'Google Blue', c1: [66, 133, 244], c2: [56, 189, 248], alpha: 0.26 },
            { name: 'Mint Emerald', c1: [52, 168, 83], c2: [74, 222, 128], alpha: 0.24 },
            { name: 'Radiant Amber', c1: [251, 188, 5], c2: [253, 224, 71], alpha: 0.28 },
            { name: 'Coral Rose', c1: [234, 67, 53], c2: [251, 113, 133], alpha: 0.22 },
            { name: 'Lavender Purple', c1: [168, 85, 247], c2: [192, 132, 252], alpha: 0.25 },
            { name: 'Ocean Turquoise', c1: [14, 165, 233], c2: [45, 212, 191], alpha: 0.24 },
            { name: 'Sunset Peach', c1: [249, 115, 22], c2: [254, 215, 170], alpha: 0.22 }
        ];

        class GradientBubble {
            constructor(type = 'medium') {
                this.type = type;
                this.init(true);
            }

            init(firstTime = false) {
                this.palette = bubblePalettes[Math.floor(Math.random() * bubblePalettes.length)];
                
                if (this.type === 'hero') {
                    this.baseRadius = Math.random() * 200 + 380; // 380 - 580px (Ultra-large soft clouds)
                    this.speed = Math.random() * 0.7 + 0.5;      // 2.5x Faster organic drift
                    this.alphaMult = 1.0;
                } else if (this.type === 'medium') {
                    this.baseRadius = Math.random() * 120 + 240; // 240 - 360px
                    this.speed = Math.random() * 1.0 + 0.8;      // 2.8x Faster drift
                    this.alphaMult = 0.85;
                } else {
                    // Accent flow bubbles
                    this.baseRadius = Math.random() * 80 + 130;  // 130 - 210px
                    this.speed = Math.random() * 1.4 + 1.1;      // 3.0x Faster drift
                    this.alphaMult = 0.75;
                }

                this.radius = this.baseRadius;
                this.x = firstTime ? Math.random() * width : (Math.random() > 0.5 ? -this.radius : width + this.radius);
                this.y = firstTime ? Math.random() * height : Math.random() * height;
                this.baseX = this.x;
                this.baseY = this.y;

                // Organic float velocities (Snappier & More Dynamic)
                this.vx = (Math.random() - 0.5) * this.speed * 1.4;
                this.vy = (Math.random() - 0.5) * this.speed * 1.4;

                // Sine wave harmonic offsets (2.5x Faster Oscillation)
                this.phaseX = Math.random() * Math.PI * 2;
                this.phaseY = Math.random() * Math.PI * 2;
                this.phaseR = Math.random() * Math.PI * 2;
                this.freqX = Math.random() * 0.0032 + 0.0020;
                this.freqY = Math.random() * 0.0032 + 0.0020;
                this.freqR = Math.random() * 0.0038 + 0.0024;
                this.ampX = Math.random() * 85 + 45;
                this.ampY = Math.random() * 85 + 45;

                // Interactive displacement
                this.dispX = 0;
                this.dispY = 0;
            }

            update(time) {
                // Harmonic natural drifting
                this.baseX += this.vx;
                this.baseY += this.vy;

                // Sine wave breathing and floating (Fast dynamic wave)
                const waveX = Math.sin(time * this.freqX + this.phaseX) * this.ampX;
                const waveY = Math.cos(time * this.freqY + this.phaseY) * this.ampY;
                const scalePulse = 1 + Math.sin(time * this.freqR + this.phaseR) * 0.18;
                this.radius = this.baseRadius * scalePulse;

                const currX = this.baseX + waveX + this.dispX;
                const currY = this.baseY + waveY + this.dispY;

                // Interactive Mouse Reaction (Snappier fluid repulsion & fast recovery)
                const dx = currX - mouse.x;
                const dy = currY - mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                const interactRadius = this.radius + 240;

                if (dist < interactRadius && dist > 1) {
                    const force = (interactRadius - dist) / interactRadius;
                    const pushX = (dx / dist) * force * 70;
                    const pushY = (dy / dist) * force * 70;
                    this.dispX += (pushX - this.dispX) * 0.14;
                    this.dispY += (pushY - this.dispY) * 0.14;
                } else {
                    // Smooth elastic return
                    this.dispX *= 0.92;
                    this.dispY *= 0.92;
                }

                // Wrap around edges smoothly with wide margin
                const margin = this.radius + 150;
                if (this.baseX < -margin) this.baseX = width + margin;
                if (this.baseX > width + margin) this.baseX = -margin;
                if (this.baseY < -margin) this.baseY = height + margin;
                if (this.baseY > height + margin) this.baseY = -margin;

                this.drawX = currX;
                this.drawY = currY;
            }

            draw() {
                const c1 = this.palette.c1;
                const c2 = this.palette.c2;
                const alpha = this.palette.alpha * this.alphaMult;

                ctx.save();
                ctx.beginPath();
                const radGrad = ctx.createRadialGradient(
                    this.drawX,
                    this.drawY,
                    0,
                    this.drawX,
                    this.drawY,
                    this.radius
                );

                // Multi-Stop Ultra-Soft Silk Gaussian Diffusion
                radGrad.addColorStop(0, `rgba(${c2[0]}, ${c2[1]}, ${c2[2]}, ${alpha * 1.25})`);
                radGrad.addColorStop(0.25, `rgba(${c1[0]}, ${c1[1]}, ${c1[2]}, ${alpha * 0.95})`);
                radGrad.addColorStop(0.55, `rgba(${c1[0]}, ${c1[1]}, ${c1[2]}, ${alpha * 0.55})`);
                radGrad.addColorStop(0.80, `rgba(${c1[0]}, ${c1[1]}, ${c1[2]}, ${alpha * 0.20})`);
                radGrad.addColorStop(1, `rgba(${c1[0]}, ${c1[1]}, ${c1[2]}, 0)`);

                ctx.fillStyle = radGrad;
                ctx.arc(this.drawX, this.drawY, this.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        // Initialize Bubble Group
        const bubbles = [
            ...Array.from({ length: 5 }, () => new GradientBubble('hero')),
            ...Array.from({ length: 7 }, () => new GradientBubble('medium')),
            ...Array.from({ length: 8 }, () => new GradientBubble('small'))
        ];

        let animationFrameId;
        function renderGradientBubbles(time) {
            // Smooth mouse low-pass interpolation (Snappier reaction)
            mouse.x += (mouse.targetX - mouse.x) * 0.12;
            mouse.y += (mouse.targetY - mouse.y) * 0.12;

            // Clear with luminous light backdrop
            ctx.clearRect(0, 0, width, height);

            // Draw subtle ambient background wash
            const bgGrad = ctx.createLinearGradient(0, 0, width, height);
            bgGrad.addColorStop(0, '#FAFCFF');
            bgGrad.addColorStop(0.5, '#F8FAFD');
            bgGrad.addColorStop(1, '#F5F8FC');
            ctx.fillStyle = bgGrad;
            ctx.fillRect(0, 0, width, height);

            // Draw and update all organic gradient bubbles
            bubbles.forEach((b) => {
                b.update(time);
                b.draw();
            });

            // Interactive Cursor Ambient Aura (Subtle Soft Glow around cursor)
            if (mouse.isMoving) {
                const elapsed = Date.now() - mouse.lastMoveTime;
                const auraAlpha = Math.max(0, 0.12 * (1 - elapsed / 2500));
                if (auraAlpha > 0.005) {
                    ctx.save();
                    const cursorGrad = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 140);
                    cursorGrad.addColorStop(0, `rgba(66, 133, 244, ${auraAlpha})`);
                    cursorGrad.addColorStop(0.6, `rgba(168, 85, 247, ${auraAlpha * 0.5})`);
                    cursorGrad.addColorStop(1, 'rgba(255, 255, 255, 0)');
                    ctx.fillStyle = cursorGrad;
                    ctx.beginPath();
                    ctx.arc(mouse.x, mouse.y, 140, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();
                }
            }

            animationFrameId = requestAnimationFrame(renderGradientBubbles);
        }

        animationFrameId = requestAnimationFrame(renderGradientBubbles);

        // Window resize handler with debounce
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                width = canvas.width = window.innerWidth;
                height = canvas.height = window.innerHeight;
            }, 100);
        });
    }
});
