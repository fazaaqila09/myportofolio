// Halaman Experience dengan AJAX (Tugas 5).
// 1. Template hanya kerangka; data diambil dari /api/experience/ lewat fetch().
// 2. State: skeleton saat memuat, lalu daftar kartu, pesan kosong, atau error + tombol coba lagi.
// 3. Pencarian dengan debounce 300 ms; permintaan lama dibatalkan dengan AbortController.
// 4. Pemilik menambah data lewat modal: fetch() + token CSRF, balasan 201 / 400 / 403 -> toast.
// 5. Semua teks dari server melewati escapeHtml(), jadi data berisi HTML tampil sebagai teks.
// Butuh: ajax-helpers.js, toast.js, language.js, lightbox.js, star-button.js.
(function () {
    'use strict';

    const section = document.getElementById('experience');
    if (!section) return;

    // Konfigurasi dari atribut data-* di template
    const config = {
        endpoint: section.dataset.endpoint,
        createEndpoint: section.dataset.createEndpoint,
        editUrl: section.dataset.editUrl,
        deleteUrl: section.dataset.deleteUrl,
        starUrl: section.dataset.starUrl,
        canEdit: section.dataset.canEdit === 'true',
        isOwner: section.dataset.isOwner === 'true',
        defaultPhoto: section.dataset.defaultPhoto,
        defaultLogo: section.dataset.defaultLogo,
    };
    const DUMMY_ID = '00000000-0000-0000-0000-000000000000';
    const SEARCH_DEBOUNCE_DELAY = 300;   // ms setelah berhenti mengetik
    const LOADING_DELAY = 120;           // skeleton baru muncul bila server lebih lambat dari ini

    // Elemen
    const el = {
        loading: document.getElementById('exp-loading'),
        error: document.getElementById('exp-error'),
        retry: document.getElementById('exp-retry'),
        empty: document.getElementById('exp-empty'),
        emptyMessage: document.getElementById('exp-empty-message'),
        grid: document.getElementById('exp-grid'),
        result: document.getElementById('exp-result'),
        count: document.getElementById('exp-count'),
        searchForm: document.getElementById('exp-search-form'),
        searchInput: document.getElementById('exp-search-input'),
        modal: document.getElementById('add-experience-modal'),     // null bila bukan pemilik
        form: document.getElementById('experience-form'),            // null bila bukan pemilik
    };

    // State
    let experiences = [];        // hasil fetch terakhir
    let loaded = false;          // sudah pernah berhasil memuat?
    let abortController = null;  // untuk membatalkan fetch lama saat pencarian berubah
    let loadingTimer = null;
    let highlightId = null;      // kartu yang baru ditambahkan (diberi sorotan)

    const tr = (key, fallback) => (window.t ? window.t(key, fallback) : fallback);
    const field = (en, id) => (window.I18N ? window.I18N.field(en, id) : en);
    const urlFor = (template, id) => template.replace(DUMMY_ID, encodeURIComponent(id));
    const autoText = (text) => (window.I18N ? window.I18N.auto(text) : text);   // pesan server -> ID/EN

    // Tampilan state: loading / error / kosong / daftar
    function showState(state) {
        el.loading.classList.toggle('hide', state !== 'loading');
        el.error.classList.toggle('hide', state !== 'error');
        el.empty.classList.toggle('hide', state !== 'empty');
        el.grid.classList.toggle('hide', state !== 'grid');
        el.result.classList.toggle('hide', state !== 'grid');
        section.setAttribute('aria-busy', state === 'loading' ? 'true' : 'false');
    }

    // Membangun kartu (semua teks dari server lewat escapeHtml)
    function periodText(f) {
        const start = formatMonthYear(f.started_at);
        const end = f.is_ongoing ? tr('common.present', 'Present') : formatMonthYear(f.ended_at);
        return `${escapeHtml(start)} &ndash; ${escapeHtml(end)}`;
    }

    function starButtonHtml(item) {
        const f = item.fields;
        const key = f.is_starred ? 'star.unstar' : 'star.star';
        const title = f.star_count > 0
            ? `Dibintangi oleh ${f.starred_by_names}`
            : 'Jadilah yang pertama memberi star';
        return `
            <form method="post" action="${escapeHtml(urlFor(config.starUrl, item.pk))}" class="star-form">
                <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(getCsrfToken())}">
                <button type="submit" class="button button-star${f.is_starred ? ' is-starred' : ''}" title="${escapeHtml(title)}">
                    <span aria-hidden="true">&#9733;</span>
                    <span data-i18n="${key}">${escapeHtml(tr(key, f.is_starred ? 'Unstar' : 'Star'))}</span>
                    <span class="star-count">${Number(f.star_count) || 0}</span>
                </button>
            </form>`;
    }

    function actionsHtml(item, title) {
        if (!config.canEdit) return '';
        const deleteButton = config.isOwner
            ? `<button type="button" class="exp-delete-btn" popovertarget="delete-experience-${escapeHtml(item.pk)}"
                    aria-label="${escapeHtml(tr('exp.delete.label', 'Delete') + ' ' + title)}" title="${escapeHtml(tr('exp.delete.label', 'Delete'))}">
                    <i class="fa-solid fa-trash" aria-hidden="true"></i>
               </button>`
            : '';
        return `
            <div class="exp-actions">
                <a href="${escapeHtml(urlFor(config.editUrl, item.pk))}" class="exp-edit-btn"
                    aria-label="${escapeHtml(tr('exp.edit.label', 'Edit') + ' ' + title)}" title="${escapeHtml(tr('exp.edit.label', 'Edit'))}">
                    <i class="fa-solid fa-pen" aria-hidden="true"></i>
                </a>
                ${deleteButton}
            </div>`;
    }

    function deleteModalHtml(item, title) {
        if (!config.isOwner) return '';
        const id = escapeHtml(item.pk);
        return `
            <div id="delete-experience-${id}" class="delete-modal" popover="auto" role="dialog"
                aria-modal="true" aria-labelledby="delete-experience-title-${id}">
                <button type="button" class="delete-modal__backdrop" popovertarget="delete-experience-${id}"
                    popovertargetaction="hide" aria-label="${escapeHtml(tr('lb.close', 'Close'))}"></button>
                <div class="delete-modal__content">
                    <button type="button" class="delete-modal__close" popovertarget="delete-experience-${id}"
                        popovertargetaction="hide" aria-label="${escapeHtml(tr('lb.close', 'Close'))}">&times;</button>
                    <h2 id="delete-experience-title-${id}">${escapeHtml(tr('exp.delete.title', 'Delete Experience?'))}</h2>
                    <p>${escapeHtml(tr('exp.delete.text', 'Are you sure you want to delete'))} <strong>${escapeHtml(title)}</strong>?</p>
                    <form method="post" action="${escapeHtml(urlFor(config.deleteUrl, item.pk))}">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(getCsrfToken())}">
                        <div class="delete-modal__actions">
                            <button type="button" class="button button-secondary" popovertarget="delete-experience-${id}"
                                popovertargetaction="hide">${escapeHtml(tr('common.cancel', 'Cancel'))}</button>
                            <button type="submit" class="button button-danger">${escapeHtml(tr('common.yes.delete', 'Yes, Delete'))}</button>
                        </div>
                    </form>
                </div>
            </div>`;
    }

    function buildCard(item, index) {
        const f = item.fields;
        const title = f.title;
        const photos = Array.isArray(f.photos) ? f.photos : [];
        const mainPhoto = f.thumbnail || config.defaultPhoto;
        const logo = f.logo || config.defaultLogo;
        const role = field(f.role, f.role_indo);
        const description = field(f.description, f.description_indo);

        const card = document.createElement('article');
        card.className = 'exp-card exp-card--enter';
        card.dataset.id = item.pk;
        card.style.setProperty('--i', index);
        card.innerHTML = `
            <div class="exp-meta">
                <span class="exp-category">${escapeHtml(window.I18N ? I18N.auto(f.category_display) : f.category_display)}</span>
                ${f.is_ongoing
                    ? `<span class="exp-status is-ongoing">${escapeHtml(tr('exp.ongoing', 'Ongoing'))}</span>`
                    : `<span class="exp-status">${escapeHtml(tr('exp.completed', 'Completed'))}</span>`}
            </div>

            <div class="exp-photo" data-photos="${escapeHtml(JSON.stringify(photos))}">
                <img src="${escapeHtml(mainPhoto)}" alt="${escapeHtml('Documentation ' + title)}" loading="lazy">
                ${photos.length > 1
                    ? `<span class="exp-photo__count" aria-hidden="true"><i class="fa-regular fa-images"></i> ${photos.length}</span>`
                    : ''}
            </div>

            <div class="exp-body">
                <div class="exp-head">
                    <div class="exp-logo">
                        <img src="${escapeHtml(logo)}" alt="${escapeHtml('Logo ' + title)}" loading="lazy">
                    </div>
                    <div class="exp-heading">
                        <h3 class="exp-org">${escapeHtml(title)}</h3>
                        ${role ? `<p class="exp-role">${escapeHtml(role)}</p>` : ''}
                    </div>
                    ${actionsHtml(item, title)}
                </div>

                <span class="exp-period">${periodText(f)}</span>
                <p class="exp-desc">${escapeHtml(description)}</p>
                <div class="exp-star">${starButtonHtml(item)}</div>
            </div>
            ${deleteModalHtml(item, title)}`;

        if (item.pk === highlightId) card.classList.add('is-new');
        return card;
    }

    function render() {
        if (!loaded) return;

        if (experiences.length === 0) {
            el.emptyMessage.textContent = el.searchInput.value.trim()
                ? tr('exp.none.found', 'No experience found with that name.')
                : tr('exp.none.yet', 'No experience added yet.');
            el.emptyMessage.dataset.i18n = el.searchInput.value.trim() ? 'exp.none.found' : 'exp.none.yet';
            showState('empty');
            return;
        }

        const fragment = document.createDocumentFragment();
        experiences.forEach((item, index) => fragment.appendChild(buildCard(item, index)));
        el.grid.replaceChildren(fragment);
        el.count.textContent = experiences.length;
        showState('grid');

        if (window.ExpLightbox) window.ExpLightbox.decorate(el.grid);

        // kartu yang baru ditambahkan: gulir ke sana sekali, lalu sorotannya hilang sendiri
        if (highlightId) {
            const fresh = el.grid.querySelector('.exp-card.is-new');
            if (fresh) fresh.scrollIntoView({ behavior: 'smooth', block: 'center' });
            highlightId = null;
        }
    }

    // Mengambil data (fetch + await)
    async function fetchExperiences() {
        if (abortController) abortController.abort();     // batalkan pencarian sebelumnya
        abortController = new AbortController();

        clearTimeout(loadingTimer);
        loadingTimer = setTimeout(() => showState('loading'), loaded ? LOADING_DELAY : 0);

        const query = el.searchInput.value.trim();
        const url = query ? `${config.endpoint}?title=${encodeURIComponent(query)}` : config.endpoint;

        try {
            const response = await fetch(url, {
                headers: { 'Accept': 'application/json' },
                signal: abortController.signal,
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            if (!Array.isArray(data)) throw new Error('Unexpected response');

            experiences = data;
            loaded = true;
            clearTimeout(loadingTimer);
            render();
        } catch (error) {
            if (error.name === 'AbortError') return;         // dibatalkan oleh pencarian baru
            clearTimeout(loadingTimer);
            console.error('Error loading experience:', error);
            showState('error');
        }
    }

    // Pencarian dengan debouncing
    function syncSearchToUrl() {
        // ?title= ikut diperbarui supaya hasil pencarian bisa dibagikan/di-refresh
        const params = new URLSearchParams(window.location.search);
        const query = el.searchInput.value.trim();
        if (query) params.set('title', query); else params.delete('title');
        const qs = params.toString();
        window.history.replaceState(null, '', window.location.pathname + (qs ? '?' + qs : ''));
    }

    const debouncedSearch = debounce(() => {
        syncSearchToUrl();
        fetchExperiences();
    }, SEARCH_DEBOUNCE_DELAY);

    el.searchInput.addEventListener('input', debouncedSearch);
    el.searchForm.addEventListener('submit', (event) => {
        event.preventDefault();          // tanpa reload halaman
        debouncedSearch.cancel();
        syncSearchToUrl();
        fetchExperiences();
    });
    el.retry.addEventListener('click', fetchExperiences);

    // Tambah data lewat modal (hanya ada untuk pemilik)
    function clearFieldErrors() {
        if (!el.form) return;
        el.form.querySelectorAll('.field-error').forEach((p) => { p.hidden = true; p.textContent = ''; });
        el.form.querySelectorAll('[aria-invalid]').forEach((input) => input.removeAttribute('aria-invalid'));
    }

    function showFieldErrors(errors) {
        Object.entries(errors).forEach(([name, list]) => {
            const group = el.form.querySelector(`.form-group[data-field="${CSS.escape(name)}"]`);
            if (!group) return;
            const message = group.querySelector('.field-error');
            message.textContent = list.map((e) => autoText(e.message)).join(' ');   // textContent: aman dari XSS
            message.hidden = false;
            const input = group.querySelector('input, textarea, select');
            if (input) input.setAttribute('aria-invalid', 'true');
        });
        const firstInvalid = el.form.querySelector('[aria-invalid="true"]');
        if (firstInvalid) firstInvalid.focus();
    }

    function errorSummary(result, status) {
        if (result.errors) {
            const labels = result.labels || {};
            return Object.entries(result.errors).map(([name, list]) => {
                const label = name === '__all__' ? '' : (labels[name] || name) + ': ';
                return label + list.map((e) => autoText(e.message)).join(' ');
            }).join(' • ');
        }
        return result.message ? autoText(result.message) : `${tr('toast.exp.status', 'Request failed with status')} ${status}.`;
    }

    async function addExperience(event) {
        event.preventDefault();
        const submitButton = el.form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.classList.add('is-loading');
        clearFieldErrors();

        try {
            const response = await fetch(config.createEndpoint, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),          // token CSRF lewat header
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json',
                },
                body: new FormData(el.form),               // juga memuat csrfmiddlewaretoken
                credentials: 'same-origin',
            });
            const result = await response.json().catch(() => ({}));

            if (response.status === 201) {
                el.form.reset();
                el.modal.hidePopover();
                showToast(tr('toast.ok', 'Success'), tr('toast.exp.added', 'New experience added successfully!'), 'success');
                highlightId = result.pk || null;
                // kosongkan pencarian supaya data baru pasti terlihat
                if (el.searchInput.value) { el.searchInput.value = ''; syncSearchToUrl(); }
                await fetchExperiences();
            } else if (response.status === 400) {
                if (result.errors) showFieldErrors(result.errors);
                showToast(tr('toast.exp.fail', 'Failed to add experience'), errorSummary(result, response.status), 'error', 5000);
            } else if (response.status === 403) {
                showToast(tr('toast.exp.fail', 'Failed to add experience'), tr('toast.exp.forbidden', 'Only the portfolio owner can add experience.'), 'error');
            } else {
                showToast(tr('toast.exp.fail', 'Failed to add experience'), errorSummary(result, response.status), 'error');
            }
        } catch (error) {
            console.error('Error adding experience:', error);
            showToast(tr('toast.exp.fail', 'Failed to add experience'), tr('toast.network', 'Could not reach the server. Please try again.'), 'error');
        } finally {
            submitButton.disabled = false;
            submitButton.classList.remove('is-loading');
        }
    }

    // Modal & form hanya dirender untuk pemilik: periksa dulu sebelum memasang listener
    if (el.form && el.modal) {
        el.form.addEventListener('submit', addExperience);
        el.modal.addEventListener('toggle', (event) => {
            if (event.newState === 'open') {
                clearFieldErrors();
                const first = el.form.querySelector('input:not([type="hidden"]), textarea, select');
                if (first) setTimeout(() => first.focus(), 50);
            }
        });
    }

    // Ganti bahasa: gambar ulang kartu (teks & tanggal ikut bahasa)
    document.addEventListener('langchange', render);

    // Mulai
    fetchExperiences();
})();