// Notifikasi toast (dari Tutorial 05): showToast(judul, pesan, 'success' | 'error' | 'normal', durasiMs).
// Klik toast = tutup, arahkan kursor = jeda hitung mundur, bar di bawah = sisa waktu.

let toastTimer;
let toastHideTimer;
let toastRemaining = 0;
let toastStartedAt = 0;
let toastWired = false;

// Bar progres di dalam toast (dibuat sekali)
function ensureToastProgress(toastComponent) {
    let bar = toastComponent.querySelector('.toast-progress');
    if (!bar) {
        bar = document.createElement('div');
        bar.className = 'toast-progress';
        bar.innerHTML = '<span></span>';
        toastComponent.appendChild(bar);
    }
    return bar;
}

function hideToast() {
    const toastComponent = document.getElementById('toast-component');
    if (!toastComponent) return;
    clearTimeout(toastTimer);
    clearTimeout(toastHideTimer);
    toastComponent.classList.remove('toast-show');
    toastComponent.classList.add('toast-hidden');
    toastHideTimer = setTimeout(() => {
        if (toastComponent.matches(':popover-open')) toastComponent.hidePopover();
    }, 300);
}

function scheduleToastHide(ms) {
    clearTimeout(toastTimer);
    toastRemaining = ms;
    toastStartedAt = Date.now();
    toastTimer = setTimeout(hideToast, ms);
}

function showToast(title, message, type = 'normal', duration = 3000) {
    const toastComponent = document.getElementById('toast-component');
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');
    if (!toastComponent) return;

    toastComponent.classList.remove('toast-success', 'toast-error', 'toast-normal');
    if (type === 'success') {
        toastComponent.classList.add('toast-success');
    } else if (type === 'error') {
        toastComponent.classList.add('toast-error');
    } else {
        toastComponent.classList.add('toast-normal');
    }

    // textContent: teks dari server tidak pernah dijalankan sebagai HTML
    toastTitle.textContent = title;
    toastMessage.textContent = message;

    const bar = ensureToastProgress(toastComponent);

    // Interaksi dipasang sekali saja
    if (!toastWired) {
        toastWired = true;
        toastComponent.setAttribute('role', 'status');
        toastComponent.addEventListener('click', hideToast);
        toastComponent.addEventListener('mouseenter', () => {
            clearTimeout(toastTimer);
            toastRemaining = Math.max(toastRemaining - (Date.now() - toastStartedAt), 400);
            bar.classList.add('paused');
        });
        toastComponent.addEventListener('mouseleave', () => {
            bar.classList.remove('paused');
            scheduleToastHide(toastRemaining);
        });
    }

    clearTimeout(toastTimer);
    clearTimeout(toastHideTimer);

    // Muncul (offsetHeight memaksa browser menghitung style agar transisi berjalan)
    if (!toastComponent.matches(':popover-open')) {
        toastComponent.showPopover();
        void toastComponent.offsetHeight;
    }
    toastComponent.classList.remove('toast-hidden');
    toastComponent.classList.add('toast-show');

    // Mulai ulang animasi bar progres
    bar.style.setProperty('--toast-duration', duration + 'ms');
    bar.classList.remove('run', 'paused');
    void bar.offsetWidth;
    bar.classList.add('run');

    scheduleToastHide(duration);
}
