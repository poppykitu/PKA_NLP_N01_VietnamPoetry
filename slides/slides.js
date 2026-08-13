/* ==========================================================================
   GOOGLE FLAT GEOMETRIC PROJECTOR LIGHT THEME ENGINE JAVASCRIPT
   Optimized for Classroom & Hall Projectors | Large Fonts | High Contrast
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
    // CHART.JS ANIMATIONS FOR PROJECTOR LIGHT THEME (HIGH CONTRAST)
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
                            backgroundColor: ['#EA4335', '#FBBC04', '#1A73E8'],
                            borderColor: ['#C5221F', '#B06000', '#1557B0'],
                            borderWidth: 2,
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 1200, easing: 'easeOutQuart' },
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: true, max: 100, ticks: { color: '#0F172A', font: { size: 13, weight: 'bold' } }, grid: { color: '#E2E8F0' } },
                            x: { ticks: { color: '#0F172A', font: { size: 13, weight: 'bold' } }, grid: { display: false } }
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
                            backgroundColor: ['#1A73E8', '#34A853', '#FBBC04'],
                            borderWidth: 3,
                            borderColor: '#FFFFFF'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 1500, easing: 'easeOutBounce' },
                        plugins: { legend: { position: 'bottom', labels: { color: '#0F172A', font: { size: 13, weight: 'bold' } } } }
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
                            backgroundColor: ['#CBD5E1', '#94A3B8', '#64748B', '#1A73E8'],
                            borderRadius: 6
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 1400, easing: 'easeOutCubic' },
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { beginAtZero: true, ticks: { color: '#0F172A', font: { size: 13, weight: 'bold' } }, grid: { color: '#E2E8F0' } },
                            y: { ticks: { color: '#0F172A', font: { size: 13, weight: 'bold' } }, grid: { display: false } }
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
                            { label: 'PA 2: Statistical N-Gram', data: [14.2, 42], backgroundColor: '#EA4335', borderRadius: 6 },
                            { label: 'PA 3: Neuro-Symbolic Hybrid', data: [0.0, 18], backgroundColor: '#34A853', borderRadius: 6 }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 1400, easing: 'easeOutQuart' },
                        plugins: { legend: { position: 'bottom', labels: { color: '#0F172A', font: { size: 13, weight: 'bold' } } } },
                        scales: {
                            y: { beginAtZero: true, max: 50, ticks: { color: '#0F172A', font: { size: 13, weight: 'bold' } }, grid: { color: '#E2E8F0' } },
                            x: { ticks: { color: '#0F172A', font: { size: 13, weight: 'bold' } }, grid: { display: false } }
                        }
                    }
                });
            }
        }
    }

    // Initialize first slide
    showSlide(0);

    // -------------------------------------------------------------------------
    // GOOGLE FLAT GEOMETRIC LIGHT THREE.JS SHADER BACKGROUND
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
                    float mouseEffect = smoothstep(0.4, 0.0, mouseDist) * 0.08;

                    float t = u_time * 0.12;
                    float n1 = snoise(st * 1.5 + vec2(t * 0.15, t * 0.1) + mouseEffect);
                    float n2 = snoise(st * 3.0 - vec2(t * 0.15, -t * 0.1) + n1);

                    // Google Light Palette (#FFFFFF base with soft pastel floating geometric aura)
                    vec3 colorBg = vec3(0.99, 0.99, 0.98);      // Soft Pearl White
                    vec3 colorSky = vec3(0.81, 0.92, 1.00);     // ColorHunt Sky Blue (#CFEBFF)
                    vec3 colorPeach = vec3(1.00, 0.75, 0.57);   // ColorHunt Peach (#FFBE91)

                    float mix1 = smoothstep(-0.5, 0.5, n1);
                    float mix2 = smoothstep(-0.4, 0.6, n2);

                    vec3 finalColor = mix(colorBg, colorSky, mix1 * 0.12);
                    finalColor = mix(finalColor, colorPeach, mix2 * 0.08);

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
