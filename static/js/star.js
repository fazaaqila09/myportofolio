// Star tanpa reload: mencegat submit form.star-form (Projects dan Experience),
// mengirimnya lewat fetch, lalu memperbarui tombol di tempat.
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

        // Belum login: arahkan ke halaman login seperti sebelumnya
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
        button.innerHTML =
            '<span aria-hidden="true">&#9733;</span> ' +
            (data.is_starred ? 'Unstar' : 'Star') +
            ' <span class="star-count">' + Number(data.star_count) + '</span>';
    } catch (error) {
        console.error('Error toggling star:', error);
        if (typeof showToast === 'function') {
            showToast('Gagal mengubah star', 'Tidak dapat terhubung ke server. Silakan coba lagi.', 'error');
        }
    } finally {
        button.disabled = false;
    }
});