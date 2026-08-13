/* ==========================================================================
   MOD LABS x GOOGLE I/O MODICUM ENGINE JAVASCRIPT
   60fps Interactive 3D Magnetic Canvas Physics | Be Vietnam Pro Typography
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.mod-slide-view');
    const totalSlides = slides.length;
    let currentSlideIndex = 0;

    const currentSlideNumEl = document.getElementById('current-slide-num');
    const totalSlidesNumEl = document.getElementById('total-slides-num');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    if (totalSlidesNumEl) totalSlidesNumEl.textContent = totalSlides;

    // Chart Instances
    let chartApproachesInstance = null;
    let chartDatasetsInstance = null;
    let chartRankingInstance = null;
    let chartOverfittingInstance = null;

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
        if (currentSlideNumEl) currentSlideNumEl.textContent = currentSlideIndex + 1;

        triggerSlideCharts(slides[currentSlideIndex].id);
    }

    function nextSlide() {
        if (currentSlideIndex < totalSlides - 1) showSlide(currentSlideIndex + 1);
    }

    function prevSlide() {
        if (currentSlideIndex > 0) showSlide(currentSlideIndex - 1);
    }

    if (btnNext) btnNext.addEventListener('click', nextSlide);
    if (btnPrev) btnPrev.addEventListener('click', prevSlide);

    window.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
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

    // Touch Swipe Support
    let touchStartX = 0;
    let touchEndX = 0;
    window.addEventListener('touchstart', (e) => { touchStartX = e.changedTouches[0].screenX; });
    window.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        if (touchEndX < touchStartX - 50) nextSlide();
        if (touchEndX > touchStartX + 50) prevSlide();
    });

    // -------------------------------------------------------------------------
    // CHART.JS ANIMATIONS (GOOGLE I/O PALETTE & LARGE FONTS)
    // -------------------------------------------------------------------------
    function triggerSlideCharts(slideId) {
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
                            borderRadius: 14
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 1200, easing: 'easeOutQuart' },
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: true, max: 100, ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 14, weight: 'bold' } }, grid: { color: '#E2E8F0' } },
                            x: { ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 14, weight: 'bold' } }, grid: { display: false } }
                        }
                    }
                });
            }
        }

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
                        animation: { duration: 1400, easing: 'easeOutBounce' },
                        plugins: { legend: { position: 'bottom', labels: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 14, weight: 'bold' } } } }
                    }
                });
            }
        }

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
                        animation: { duration: 1200, easing: 'easeOutCubic' },
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { beginAtZero: true, ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 14, weight: 'bold' } }, grid: { color: '#E2E8F0' } },
                            y: { ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 14, weight: 'bold' } }, grid: { display: false } }
                        }
                    }
                });
            }
        }

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
                        animation: { duration: 1400, easing: 'easeOutQuart' },
                        plugins: { legend: { position: 'bottom', labels: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 14, weight: 'bold' } } } },
                        scales: {
                            y: { beginAtZero: true, max: 50, ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 14, weight: 'bold' } }, grid: { color: '#E2E8F0' } },
                            x: { ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 14, weight: 'bold' } }, grid: { display: false } }
                        }
                    }
                });
            }
        }
    }

    showSlide(0);

    // -------------------------------------------------------------------------
    // MOD LABS DYNAMIC MAGNETIC PHYSICS CANVAS (SPHERES & PILL CAPSULES)
    // -------------------------------------------------------------------------
    const canvas = document.getElementById('mod-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        const colors = ['#4285F4', '#EA4335', '#FBBC05', '#34A853'];

        let mouse = { x: width / 2, y: height / 2 };
        window.addEventListener('mousemove', (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        });

        class ModShape {
            constructor() {
                this.reset();
            }
            reset() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.size = Math.random() * 40 + 20;
                this.type = Math.floor(Math.random() * 3); // 0: Sphere, 1: Pill, 2: Cube
                this.color = colors[Math.floor(Math.random() * colors.length)];
                this.alpha = Math.random() * 0.15 + 0.05;
                this.vx = (Math.random() - 0.5) * 0.8;
                this.vy = (Math.random() - 0.5) * 0.8;
                this.angle = Math.random() * Math.PI * 2;
                this.vRot = (Math.random() - 0.5) * 0.02;
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.angle += this.vRot;

                // Magnetic Attraction to Mouse
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 250) {
                    const force = (250 - dist) / 250;
                    this.x += (dx / dist) * force * 1.5;
                    this.y += (dy / dist) * force * 1.5;
                }

                if (this.x < -100 || this.x > width + 100 || this.y < -100 || this.y > height + 100) {
                    this.reset();
                }
            }
            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);
                ctx.fillStyle = this.color;
                ctx.globalAlpha = this.alpha;

                if (this.type === 0) {
                    // Soft Sphere
                    ctx.beginPath();
                    ctx.arc(0, 0, this.size, 0, Math.PI * 2);
                    ctx.fill();
                } else if (this.type === 1) {
                    // Pill Shape
                    const w = this.size * 2;
                    const h = this.size;
                    ctx.beginPath();
                    ctx.roundRect(-w/2, -h/2, w, h, h/2);
                    ctx.fill();
                } else {
                    // Rounded Cube
                    const s = this.size * 1.4;
                    ctx.beginPath();
                    ctx.roundRect(-s/2, -s/2, s, s, 12);
                    ctx.fill();
                }
                ctx.restore();
            }
        }

        const shapes = Array.from({ length: 22 }, () => new ModShape());

        function animate() {
            ctx.clearRect(0, 0, width, height);
            shapes.forEach(shape => {
                shape.update();
                shape.draw();
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
