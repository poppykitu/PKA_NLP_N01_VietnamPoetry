/* ==========================================================================
   AUDITORIUM KINETIC EDITORIAL ENGINE JAVASCRIPT
   Fixed Slide Transitioning | Multi-Input Controls | Large Chart Fonts
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.kinetic-slide');
    const totalSlides = slides.length;
    let currentSlideIndex = 0;

    const currentSlideNumEl = document.getElementById('current-slide-num');
    const totalSlidesNumEl = document.getElementById('total-slides-num');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    if (totalSlidesNumEl) totalSlidesNumEl.textContent = totalSlides;

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

        if (slides[currentSlideIndex]) {
            triggerSlideCharts(slides[currentSlideIndex].id);
        }
    }

    function nextSlide() {
        if (currentSlideIndex < totalSlides - 1) showSlide(currentSlideIndex + 1);
    }

    function prevSlide() {
        if (currentSlideIndex > 0) showSlide(currentSlideIndex - 1);
    }

    if (btnNext) btnNext.addEventListener('click', (e) => { e.stopPropagation(); nextSlide(); });
    if (btnPrev) btnPrev.addEventListener('click', (e) => { e.stopPropagation(); prevSlide(); });

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

    // Stage Click Navigation (Click right half = Next, Click left half = Prev)
    const stage = document.querySelector('.kinetic-stage');
    if (stage) {
        stage.addEventListener('click', (e) => {
            // Ignore click if clicking interactive buttons or links
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
    // CHART.JS ANIMATIONS (GOOGLE PRIMARY PALETTE & LARGE FONTS)
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
                            y: { beginAtZero: true, max: 100, ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } }, grid: { color: '#E2E8F0' } },
                            x: { ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } }, grid: { display: false } }
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
                        plugins: { legend: { position: 'bottom', labels: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } } } }
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
                            x: { beginAtZero: true, ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } }, grid: { color: '#E2E8F0' } },
                            y: { ticks: { color: '#0F172A', font: { family: 'Be Vietnam Pro', size: 16, weight: 'bold' } }, grid: { display: false } }
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
