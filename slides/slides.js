/* ==========================================================================
   AUDITORIUM KINETIC EDITORIAL ENGINE JAVASCRIPT
   100% Visible Official Chart.js Native Animations & Controls
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.kinetic-slide');
    const totalSlides = slides.length;
    let currentSlideIndex = 0;

    const progressBarDock = document.getElementById('progress-bar-dock');
    if (progressBarDock && totalSlides > 0) {
        progressBarDock.innerHTML = '';
        for (let i = 0; i < totalSlides; i++) {
            const seg = document.createElement('div');
            seg.className = 'progress-segment';
            seg.title = `Slide ${i + 1} / ${totalSlides}`;
            seg.addEventListener('click', (e) => {
                e.stopPropagation();
                showSlide(i);
            });
            progressBarDock.appendChild(seg);
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

    function runDemoSimulation() {
        const prompt = (demoPromptInput ? demoPromptInput.value.trim() : '') || 'Mùa thu sang';
        const approach = demoApproachSelect ? demoApproachSelect.value : 'pa3';

        if (!cliBody || !webuiOutput) return;

        cliBody.innerHTML = '';
        webuiOutput.innerHTML = '<div class="animate-pulse text-gblue font-bold text-2xl">⏳ Đang khởi tạo mô hình & sinh thơ...</div>';

        function appendCliLine(text, type = 'info') {
            const div = document.createElement('div');
            div.className = `cli-line-${type} mb-1.5`;
            const timestamp = new Date().toLocaleTimeString();
            div.innerHTML = `<span class="text-slate-500">[${timestamp}]</span> ${text}`;
            cliBody.appendChild(div);
            cliBody.scrollTop = cliBody.scrollHeight;
        }

        appendCliLine(`[START] Executive Command: python generate_poetry.py --prompt "${prompt}" --approach ${approach.toUpperCase()}`, 'info');

        if (approach === 'pa1') {
            setTimeout(() => { appendCliLine(`[INFO] Connecting to Qwen-2.5-7B-Instruct fine-tuned checkpoint...`, 'info'); }, 300);
            setTimeout(() => { appendCliLine(`[WARN] Model generating tokens without constrained tone grammar...`, 'warn'); }, 700);
            setTimeout(() => { appendCliLine(`[ERR] Violation Detected: Tone mismatch at position 4 (Found Trắc instead of Bằng).`, 'err'); }, 1100);
            setTimeout(() => { appendCliLine(`[FAIL] PA 1 Failed (0/100 points). Model hallucinated broken meter.`, 'err'); }, 1500);
            setTimeout(() => {
                webuiOutput.innerHTML = `
                    <div class="text-gred font-bold text-xl leading-relaxed border-l-4 border-gred pl-4">
                        ❌ THẤT BẠI: Qwen 7B Fine-Tune bị vỡ luật thi ca!<br>
                        (Sai 68% luật Bằng-Trắc ở vị trí tiếng 4 & 6 câu Bát)
                    </div>
                `;
            }, 1600);
        } else if (approach === 'pa2') {
            setTimeout(() => { appendCliLine(`[INFO] Loading Interpolated Kneser-Ney 3-Gram Model (Discount d=0.75)...`, 'info'); }, 300);
            setTimeout(() => { appendCliLine(`[SEARCH] Beam Search BeamWidth=10 evaluating PMI scores for "${prompt}"...`, 'info'); }, 700);
            setTimeout(() => { appendCliLine(`[CHECK] Best-of-N Evaluator: Rhyme match = 100%, Anti-Repetition = 85%.`, 'warn'); }, 1100);
            setTimeout(() => { appendCliLine(`[SUCCESS] Generated 4-line poem via Statistical N-Gram in 0.38s.`, 'success'); }, 1400);
            setTimeout(() => {
                webuiOutput.innerHTML = `
                    <div class="text-slate-900 font-bold text-2xl leading-relaxed border-l-4 border-amber-500 pl-4">
                        Thu sang lá rụng bên đình,<br>
                        Gió thu se lạnh cho mình nhớ thương.<br>
                        Mây trôi lặng lẽ dặm trường,<br>
                        Nắng vàng trải nhẹ trên đường xóm xa.
                    </div>
                    <p class="text-amber-700 text-sm font-black mt-3">✓ 100% Đúng luật | ⚠️ 14.2% Trùng n-gram cũ trong dataset</p>
                `;
            }, 1500);
        } else {
            // PA 3: Neuro-Symbolic Hybrid AI (SOTA)
            setTimeout(() => { appendCliLine(`[INFO] Connecting to Local LLM Google Gemma-4-12B-QAT via LM Studio API...`, 'info'); }, 300);
            setTimeout(() => { appendCliLine(`[NEURO] TẦNG 1: RAW Draft generated by Gemma-12B in 0.42s.`, 'info'); }, 700);
            setTimeout(() => { appendCliLine(`[SYMBOLIC] TẦNG 2: Rule Repair Engine Tier 1 (Length Fixer): 6-8 syllables verified.`, 'info'); }, 1100);
            setTimeout(() => { appendCliLine(`[SYMBOLIC] TẦNG 2: Tier 2 (Tone Repair at Pos 6): Repaired syllable with POETIC_SYNONYM_MAP.`, 'warn'); }, 1500);
            setTimeout(() => { appendCliLine(`[SYMBOLIC] TẦNG 2: Tier 3 (Rhyme & Tone Oppositon): Ép đối Bằng (Ngang-Huyền) tiếng 6 & 8.`, 'warn'); }, 1800);
            setTimeout(() => { appendCliLine(`[SUCCESS] Neuro-Symbolic Repair Finished! 100% Rule Valid, 0.0% Overfitting!`, 'success'); }, 2100);
            setTimeout(() => {
                let poemHtml = '';
                if (prompt.toLowerCase().includes('mèo')) {
                    poemHtml = `Nằm nghe nắng đổ chiều mây,<br>Mèo ngoan cuộn bóng bên <strong class="text-ggreen">cây</strong> mơ màng.<br>Lông mềm rủ mượt thu sang,<br>Khẽ khàng bước nhẹ giữa <strong class="text-ggreen">hàng</strong> trút thơ.`;
                } else {
                    poemHtml = `Thu sang rải nắng bên làng,<br>Gió vờn mái tóc mơ màng <strong class="text-ggreen">chiều thu</strong>.<br>Hương hoa thoang thoảng sương mù,<br>Lời ca trầm bổng vi vu <strong class="text-ggreen">gió ngàn</strong>.`;
                }
                webuiOutput.innerHTML = `
                    <div class="text-slate-900 font-black text-2.5xl leading-relaxed border-l-6 border-ggreen pl-5">
                        ${poemHtml}
                    </div>
                    <p class="text-ggreen text-base font-black mt-4">✨ SOTA NEURO-SYMBOLIC: 100% Chuẩn Luật | 0.0% Overfitting | Ý Thơ Thi Vị</p>
                `;
            }, 2200);
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

    // Keyboard controls
    window.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown' || e.key === 'Enter') {
            e.preventDefault();
            nextSlide();
        } else if (e.key === 'ArrowLeft' || e.key === 'PageUp' || e.key === 'Backspace') {
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

    // Mouse Wheel Navigation (Debounced)
    let isWheeling = false;
    window.addEventListener('wheel', (e) => {
        if (isWheeling) return;
        if (Math.abs(e.deltaY) > 30) {
            isWheeling = true;
            if (e.deltaY > 0) nextSlide();
            else prevSlide();
            setTimeout(() => { isWheeling = false; }, 600);
        }
    }, { passive: true });

    // Stage Click Navigation
    const stage = document.querySelector('.kinetic-stage');
    if (stage) {
        stage.addEventListener('click', (e) => {
            if (e.target.closest('button, a, code, pre, canvas')) return;
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
    // AUTOMATIC AMBIENT FLUID PARTICLES CANVAS (60FPS AUTO DRIFT)
    // -------------------------------------------------------------------------
    const canvas = document.getElementById('ambient-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        const colors = ['rgba(66, 133, 244, ', 'rgba(234, 67, 53, ', 'rgba(251, 188, 5, ', 'rgba(52, 168, 83, '];

        class AutoParticle {
            constructor() {
                this.reset();
            }
            reset() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.radius = Math.random() * 120 + 40;
                this.color = colors[Math.floor(Math.random() * colors.length)];
                this.alpha = Math.random() * 0.12 + 0.04;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.5;
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                if (this.x < -150 || this.x > width + 150 || this.y < -150 || this.y > height + 150) {
                    this.reset();
                }
            }
            draw() {
                ctx.beginPath();
                const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius);
                gradient.addColorStop(0, this.color + this.alpha + ')');
                gradient.addColorStop(1, this.color + '0)');
                ctx.fillStyle = gradient;
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        const particles = Array.from({ length: 16 }, () => new AutoParticle());

        function animate() {
            ctx.clearRect(0, 0, width, height);
            particles.forEach(p => {
                p.update();
                p.draw();
            });
            requestAnimationFrame(animate);
        }

        animate();

        window.addEventListener('resize', () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });
    }
});
