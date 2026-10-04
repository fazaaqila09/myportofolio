// Tombol star (Projects & Experience) tanpa reload: submit form.star-form dicegat lalu dikirim lewat fetch().

// Ledakan bintang kecil dari tombol saat memberi star
function burstStars(button) {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !button.animate) return;
    for (let i = 0; i < 7; i++) {
        const particle = document.createElement('i');
        particle.className = 'star-particle';
        particle.setAttribute('aria-hidden', 'true');
        particle.innerHTML = '&#9733;';
        button.appendChild(particle);

        const angle = (Math.PI * 2 * i) / 7 + Math.random() * 0.5;
        const distance = 26 + Math.random() * 22;
        const animation = particle.animate([
            { transform: 'translate(-50%, -50%) scale(.4)', opacity: 1 },
            { transform: 'translate(calc(-50% + ' + (Math.cos(angle) * distance).toFixed(1) + 'px), calc(-50% + ' + (Math.sin(angle) * distance).toFixed(1) + 'px)) scale(1.1)', opacity: 0 },
        ], { duration: 650, easing: 'cubic-bezier(.2,.8,.3,1)' });
        animation.onfinish = () => particle.remove();
    }
}

document.addEventListener('submit', async function (event) {
    const form = event.target.closest('form.star-form');
    if (!form) return;
    event.preventDefault();

    const button = form.querySelector('button[type="submit"]');
    if (button.disabled) return;
    button.disabled = true;

    try {
        const response = await fetch(form.action, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' },
            body: new FormData(form),
            credentials: 'same-origin',
        });

        // Belum login: arahkan ke halaman login
        if (response.status === 401) {
            const data = await response.json().catch(() => ({}));
            const next = encodeURIComponent(window.location.pathname + window.location.search);
            window.location.href = (data.login_url || '/login/') + '?next=' + next;
            return;
        }
        if (!response.ok) throw new Error('Gagal mengubah star (status ' + response.status + ')');

        const data = await response.json();
        button.classList.toggle('is-starred', data.is_starred);
        button.title = data.star_count > 0
            ? 'Dibintangi oleh ' + data.starred_by_names
            : 'Jadilah yang pertama memberi star';
        const starKey = data.is_starred ? 'star.unstar' : 'star.star';
        button.innerHTML =
            '<span aria-hidden="true">&#9733;</span> ' +
            '<span data-i18n="' + starKey + '">' + t(starKey) + '</span>' +
            ' <span class="star-count">' + Number(data.star_count) + '</span>';

        // Angka memantul; bintang membesar dan meledak hanya saat memberi star
        button.querySelector('.star-count').classList.add('star-count--bump');
        if (data.is_starred) {
            button.querySelector('span[aria-hidden="true"]').classList.add('star-pop');
            burstStars(button);
        }
    } catch (error) {
        console.error('Error toggling star:', error);
        if (typeof showToast === 'function') {
            showToast(t('toast.star.fail'), t('toast.network'), 'error');
        }
    } finally {
        button.disabled = false;
    }
});
