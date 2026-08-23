/**
 * SYNOPTIC - Professional Motion Graphics Auth Controller
 * Features: 3D Kinetic Card Tilt, Specular Light Sheen, Tab Switching & Micro-Animations.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Tab Switcher Logic (Sign In vs Register)
    const tabBtns = document.querySelectorAll('.auth-tab-btn');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const target = btn.getAttribute('data-tab');

            if (target === 'login') {
                if (loginForm) loginForm.style.display = 'flex';
                if (registerForm) registerForm.style.display = 'none';
            } else {
                if (loginForm) loginForm.style.display = 'none';
                if (registerForm) registerForm.style.display = 'flex';
            }
        });
    });

    // 2. Password Visibility Toggles
    document.querySelectorAll('.auth-input-toggle-btn').forEach(toggleBtn => {
        toggleBtn.addEventListener('click', () => {
            const input = toggleBtn.parentElement.querySelector('input');
            const icon = toggleBtn.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'fa-solid fa-eye-slash';
            } else {
                input.type = 'password';
                icon.className = 'fa-solid fa-eye';
            }
        });
    });

    // 3. Interactive 3D Kinetic Tilt & Specular Sheen Physics
    const cardFrame = document.getElementById('interactive-card-frame');
    const card = document.getElementById('interactive-card');

    if (cardFrame && card) {
        let isHovered = false;

        const handleMouseMove = (e) => {
            const rect = cardFrame.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            // Maximum tilt angle in degrees
            const maxTilt = 8;
            const rotateX = ((y - centerY) / centerY) * -maxTilt;
            const rotateY = ((x - centerX) / centerX) * maxTilt;

            // Set specular highlight position
            card.style.setProperty('--mouse-x', `${(x / rect.width) * 100}%`);
            card.style.setProperty('--mouse-y', `${(y / rect.height) * 100}%`);

            // Apply 3D Transform
            cardFrame.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.01, 1.01, 1.01)`;
        };

        const handleMouseLeave = () => {
            cardFrame.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
            card.style.setProperty('--mouse-x', `50%`);
            card.style.setProperty('--mouse-y', `50%`);
        };

        cardFrame.addEventListener('mouseenter', () => isHovered = true);
        cardFrame.addEventListener('mousemove', handleMouseMove);
        cardFrame.addEventListener('mouseleave', handleMouseLeave);
    }

    // 4. Interactive Mouse Cursor Parallax for Floating Background Clouds
    const bgCloud = document.getElementById('cloud-layer-bg');
    const midCloud = document.getElementById('cloud-layer-mid');
    const fgCloud = document.getElementById('cloud-layer-fg');

    if (bgCloud || midCloud || fgCloud) {
        window.addEventListener('mousemove', (e) => {
            const normX = (e.clientX / window.innerWidth) - 0.5;
            const normY = (e.clientY / window.innerHeight) - 0.5;

            requestAnimationFrame(() => {
                if (bgCloud) bgCloud.style.transform = `translate3d(${(normX * 22).toFixed(1)}px, ${(normY * 12).toFixed(1)}px, 0)`;
                if (midCloud) midCloud.style.transform = `translate3d(${(normX * 45).toFixed(1)}px, ${(normY * 24).toFixed(1)}px, 0)`;
                if (fgCloud) fgCloud.style.transform = `translate3d(${(normX * 75).toFixed(1)}px, ${(normY * 40).toFixed(1)}px, 0)`;
            });
        });
    }
});
