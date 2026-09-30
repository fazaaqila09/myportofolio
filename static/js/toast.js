let toastTimer;
let toastHideTimer;
let toastRemaining = 0;
let toastStartedAt = 0;
let toastWired = false;

// Membuat bar progress di dalam toast (sekali saja)
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

  // Hapus class tipe sebelumnya
  toastComponent.classList.remove('toast-success', 'toast-error', 'toast-normal');

  // Terapkan class baru berdasarkan tipe
  if (type === 'success') {
      toastComponent.classList.add('toast-success');
  } else if (type === 'error') {
      toastComponent.classList.add('toast-error');
  } else {
      toastComponent.classList.add('toast-normal');
  }

  // Perbarui konten teks
  toastTitle.textContent = title;
  toastMessage.textContent = message;

  const bar = ensureToastProgress(toastComponent);

  // Pasang interaksi sekali saja: klik = tutup, hover = jeda hitung mundur
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

  // Batalkan timer sebelumnya jika toast masih tampil
  clearTimeout(toastTimer);
  clearTimeout(toastHideTimer);

  // Animasi muncul
  if (!toastComponent.matches(':popover-open')) {
      toastComponent.showPopover();
      void toastComponent.offsetHeight; // paksa browser menghitung style agar transisi berjalan
  }
  toastComponent.classList.remove('toast-hidden');
  toastComponent.classList.add('toast-show');

  // Mulai ulang animasi progress bar
  bar.style.setProperty('--toast-duration', duration + 'ms');
  bar.classList.remove('run', 'paused');
  void bar.offsetWidth;
  bar.classList.add('run');

  // Animasi hilang otomatis
  scheduleToastHide(duration);
}