/* ==========================================================================
   ATOTIME CAPSULE CUSTOM PRESENTATION ENGINE JAVASCRIPT
   Pure Responsive Engine | Full Keyboard & Chart Control
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide-item');
    const totalSlides = slides.length;
    let currentSlideIndex = 0;

    const currentSlideNumEl = document.getElementById('current-slide-num');
    const totalSlidesNumEl = document.getElementById('total-slides-num');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    if (totalSlidesNumEl) totalSlidesNumEl.textContent = totalSlides;

    // Chart.js Instances
    let chartApproachesInstance = null;
    let chartDatasetsInstance = null;
    let chartRankingInstance = null;
    let chartOverfittingInstance = null;

    // Show Slide by Index
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

        // Update UI Indicators
        if (currentSlideNumEl) currentSlideNumEl.textContent = currentSlideIndex + 1;
        if (progressBarFill) {
            const percentage = ((currentSlideIndex + 1) / totalSlides) * 100;
            progressBarFill.style.width = `${percentage}%`;
        }

        // Trigger Slide-specific Chart Animations
        triggerSlideCharts(slides[currentSlideIndex].id);
    }

    // Navigation Triggers
    function nextSlide() {
        if (currentSlideIndex < totalSlides - 1) {
            showSlide(currentSlideIndex + 1);
        }
    }

    function prevSlide() {
        if (currentSlideIndex > 0) {
            showSlide(currentSlideIndex - 1);
        }
    }

    if (btnNext) btnNext.addEventListener('click', nextSlide);
    if (btnPrev) btnPrev.addEventListener('click', prevSlide);

    // Keyboard Event Listeners
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

    window.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });

    window.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });

    function handleSwipe() {
        if (touchEndX < touchStartX - 50) nextSlide();
        if (touchEndX > touchStartX + 50) prevSlide();
    }

    // -------------------------------------------------------------------------
    // CHART.JS ANIMATIONS FOR CUSTOM ENGINE
    // -------------------------------------------------------------------------
    function triggerSlideCharts(slideId) {
        // Slide 4 Chart: 3 Approaches
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
                            label: 'Điểm Đánh Giá Tổng Thể (Thang 100)',
                            data: [0, 60, 95],
                            backgroundColor: ['rgba(239, 68, 68, 0.85)', 'rgba(156, 163, 175, 0.85)', 'rgba(255, 255, 255, 0.95)'],
                            borderColor: ['#EF4444', '#9CA3AF', '#FFFFFF'],
                            borderWidth: 1,
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 1200, easing: 'easeOutQuart' },
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: true, max: 100, ticks: { color: '#9CA3AF' }, grid: { color: '#374151' } },
                            x: { ticks: { color: '#9CA3AF' }, grid: { display: false } }
                        }
                    }
                });
            }
        }

        // Slide 5 Chart: Datasets Doughnut
        if (slideId === 'slide-datasets') {
            if (chartDatasetsInstance) chartDatasetsInstance.destroy();
            const canvas = document.getElementById('chart-datasets');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                chartDatasetsInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['HF National Dictionary POS (24.608)', 'Gemma Polysemic Lexicon (4.659)', 'Các Âm Tiết Thơ Khác (9.366)'],
                        datasets: [{
                            data: [24608, 4659, 9366],
                            backgroundColor: ['#FFFFFF', '#D1D5DB', '#6B7280'],
                            borderWidth: 2,
                            borderColor: '#1A1A1A'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 1500, easing: 'easeOutBounce' },
                        plugins: { legend: { position: 'bottom', labels: { color: '#D1D5DB', font: { size: 12 } } } }
                    }
                });
            }
        }

        // Slide 16 Chart: Ranking
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
                            label: 'Điểm Tần Suất 3.4M N-Gram',
                            data: [28, 30, 69, 217],
                            backgroundColor: ['rgba(156, 163, 175, 0.7)', 'rgba(209, 213, 219, 0.8)', 'rgba(243, 244, 246, 0.9)', '#FFFFFF'],
                            borderRadius: 4
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 1400, easing: 'easeOutCubic' },
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { beginAtZero: true, ticks: { color: '#9CA3AF' }, grid: { color: '#374151' } },
                            y: { ticks: { color: '#9CA3AF' }, grid: { display: false } }
                        }
                    }
                });
            }
        }

        // Slide 18 Chart: Overfitting
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
                            { label: 'PA 2: Statistical N-Gram', data: [14.2, 42], backgroundColor: '#9CA3AF', borderRadius: 4 },
                            { label: 'PA 3: Neuro-Symbolic Hybrid', data: [0.0, 18], backgroundColor: '#FFFFFF', borderRadius: 4 }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 1400, easing: 'easeOutQuart' },
                        plugins: { legend: { position: 'bottom', labels: { color: '#D1D5DB' } } },
                        scales: {
                            y: { beginAtZero: true, max: 50, ticks: { color: '#9CA3AF' }, grid: { color: '#374151' } },
                            x: { ticks: { color: '#9CA3AF' }, grid: { display: false } }
                        }
                    }
                });
            }
        }
    }

    // Initialize first slide
    showSlide(0);

    // -------------------------------------------------------------------------
    // ATOTIME ATMOSPHERIC THREE.JS SHADER BACKGROUND
    // -------------------------------------------------------------------------
    const atotimeCanvas = document.getElementById('atotime-canvas');
    if (atotimeCanvas && typeof THREE !== 'undefined') {
        const atotimeScene = new THREE.Scene();
        const atotimeCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

        const atotimeRenderer = new THREE.WebGLRenderer({ canvas: atotimeCanvas, antialias: true, alpha: false });
        atotimeRenderer.setSize(window.innerWidth, window.innerHeight);
        atotimeRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        const atotimeMaterial = new THREE.ShaderMaterial({
            uniforms: {
                u_time: { value: 0 },
                u_resolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
                u_mouse: { value: new THREE.Vector2(0.5, 0.5) }
            },
            vertexShader: `
                varying vec2 vUv;
                void main() { vUv = uv; gl_Position = vec4(position, 1.0); }
            `,
            fragmentShader: `
                uniform float u_time;
                uniform vec2 u_resolution;
                uniform vec2 u_mouse;
                varying vec2 vUv;

                vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
                vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
                vec3 permute(vec3 x) { return mod289(((x*34.0)+1.0)*x); }

                float snoise(vec2 v) {
                    const vec4 C = vec4(0.211324865405187, 0.366025403784439, -0.577350269189626, 0.024390243902439);
                    vec2 i  = floor(v + dot(v, C.yy) );
                    vec2 x0 = v -   i + dot(i, C.xx);
                    vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
                    vec4 x12 = x0.xyxy + C.xxzz;
                    x12.xy -= i1;
                    i = mod289(i);
                    vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 )) + i.x + vec3(0.0, i1.x, 1.0 ));
                    vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
                    m = m*m; m = m*m;
                    vec3 x = 2.0 * fract(p * C.www) - 1.0;
                    vec3 h = abs(x) - 0.5;
                    vec3 ox = floor(x + 0.5);
                    vec3 a0 = x - ox;
                    m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
                    vec3 g;
                    g.x  = a0.x  * x0.x  + h.x  * x0.y;
                    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
                    return 130.0 * dot(m, g);
                }

                void main() {
                    vec2 st = gl_FragCoord.xy / u_resolution.xy;
                    st.x *= u_resolution.x / u_resolution.y;

                    float mouseDist = distance(vUv, u_mouse);
                    float mouseEffect = smoothstep(0.4, 0.0, mouseDist) * 0.1;

                    float t = u_time * 0.15;
                    float n1 = snoise(st * 1.8 + vec2(t * 0.2, t * 0.1) + mouseEffect);
                    float n2 = snoise(st * 3.5 - vec2(t * 0.2, -t * 0.15) + n1);

                    vec3 colorBg = vec3(0.07, 0.07, 0.07);
                    vec3 colorSurface = vec3(0.12, 0.12, 0.12);
                    vec3 colorHighlight = vec3(0.22, 0.22, 0.24);

                    float mix1 = smoothstep(-0.5, 0.5, n1);
                    float mix2 = smoothstep(-0.4, 0.6, n2);

                    vec3 finalColor = mix(colorBg, colorSurface, mix1 * 0.5);
                    finalColor = mix(finalColor, colorHighlight, mix2 * 0.25);

                    float vignette = smoothstep(1.2, 0.2, distance(vUv, vec2(0.5)));
                    finalColor *= vignette;

                    gl_FragColor = vec4(finalColor, 1.0);
                }
            `
        });

        const atotimeQuad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), atotimeMaterial);
        atotimeScene.add(atotimeQuad);

        window.addEventListener('mousemove', (e) => {
            atotimeMaterial.uniforms.u_mouse.value.x = e.clientX / window.innerWidth;
            atotimeMaterial.uniforms.u_mouse.value.y = 1.0 - (e.clientY / window.innerHeight);
        });

        const clock = new THREE.Clock();
        function renderAtotime() {
            requestAnimationFrame(renderAtotime);
            atotimeMaterial.uniforms.u_time.value = clock.getElapsedTime();
            atotimeRenderer.render(atotimeScene, atotimeCamera);
        }
        renderAtotime();

        window.addEventListener('resize', () => {
            atotimeRenderer.setSize(window.innerWidth, window.innerHeight);
            atotimeMaterial.uniforms.u_resolution.value.set(window.innerWidth, window.innerHeight);
        });
    }
});
