// Halaman Experience lewat API Django REST Framework (Tugas 6).
// 1. Template hanya kerangka; data diambil dari /api/v1/experience/ lewat fetch().
// 2. State: skeleton saat memuat, lalu daftar kartu, pesan kosong, atau error + tombol coba lagi.
// 3. Pencarian ?title= dengan debounce 300 ms; permintaan lama dibatalkan dengan AbortController.
// 4. Tambah (POST), ubah (PATCH), hapus (DELETE), dan star (POST) tanpa reload halaman.
//    Setiap permintaan yang mengubah data membawa header X-CSRFToken.
// 5. Error dari API (400 validasi, 403 ditolak, 404 tidak ada) ditampilkan lewat toast.
// 6. Semua teks dari server melewati escapeHtml(), jadi data berisi HTML tampil sebagai teks.
// Butuh: ajax-helpers.js, toast.js, i18n.js, lightbox.js, star-button.js (burstStars).
(function () {
    'use strict';

    const section = document.getElementById('experience');
    if (!section) return;

    // Konfigurasi dari atribut data-* di template
    const config = {
        endpoint: section.dataset.endpoint,           // GET daftar, POST tambah
        detailUrl: section.dataset.detailUrl,         // GET/PATCH/DELETE satu data
        starUrl: section.dataset.starUrl,             // POST star
        loginUrl: section.dataset.loginUrl,
        isAuthenticated: section.dataset.isAuthenticated === 'true',
        canEdit: section.dataset.canEdit === 'true',
        isOwner: section.dataset.isOwner === 'true',
        defaultPhoto: section.dataset.defaultPhoto,
        defaultLogo: section.dataset.defaultLogo,
    };
    const DUMMY_ID = '00000000-0000-0000-0000-000000000000';
    const SEARCH_DEBOUNCE_DELAY = 300;   // ms setelah berhenti mengetik
    const LOADING_DELAY = 120;           // skeleton baru muncul bila server lebih lambat dari ini
    // Field yang dikirim dari form ke API (sama dengan nama field serializer)
    const FORM_FIELDS = [
        'title', 'role', 'role_indo', 'description', 'description_indo', 'category',
        'thumbnail', 'photos', 'logo', 'started_at', 'ended_at',
    ];

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
        addButton: document.getElementById('exp-add-button'),            // hanya untuk pemilik
        modal: document.getElementById('experience-modal'),              // pemilik & Editor
        modalTitle: document.getElementById('experience-modal-title'),
        submitLabel: document.getElementById('experience-submit-label'),
        form: document.getElementById('experience-form'),
    };

    // State
    let experiences = [];        // hasil fetch terakhir
    let loaded = false;          // sudah pernah berhasil memuat?
    let abortController = null;  // untuk membatalkan fetch lama saat pencarian berubah
    let loadingTimer = null;
    let highlightId = null;      // kartu yang baru ditambah/diubah (diberi sorotan)
    let editing = null;          // null = mode tambah; objek Experience = mode ubah

    const tr = (key, fallback) => (window.t ? window.t(key, fallback) : fallback);
    const field = (en, id) => (window.I18N ? window.I18N.field(en, id) : en);
    const urlFor = (template, id) => template.replace(DUMMY_ID, encodeURIComponent(id));
    const autoText = (text) => (window.I18N ? window.I18N.auto(text) : text);   // pesan server -> ID/EN
    const findItem = (id) => experiences.find((item) => item.id === id);

    // Tampilan state: loading / error / kosong / daftar
    function showState(state) {
        el.loading.classList.toggle('hide', state !== 'loading');
        el.error.classList.toggle('hide', state !== 'error');
        el.empty.classList.toggle('hide', state !== 'empty');
        el.grid.classList.toggle('hide', state !== 'grid');
        el.result.classList.toggle('hide', state !== 'grid');
        section.setAttribute('aria-busy', state === 'loading' ? 'true' : 'false');
    }

    // Komunikasi dengan API

    // Pesan error DRF menjadi satu kalimat untuk toast.
    // 400 -> {"field": ["pesan", ...]}, 403/404 -> {"detail": "pesan"}
    function errorSummary(data, status) {
        if (data && typeof data.detail === 'string') return autoText(data.detail);
        const parts = Object.entries(data || {}).map(([name, list]) => {
            const messages = [].concat(list).map((message) => autoText(String(message))).join(' ');
            if (name === 'non_field_errors') return messages;
            const label = el.form && el.form.querySelector(`.form-group[data-field="${CSS.escape(name)}"] label`);
            const labelText = label ? label.textContent.replace('*', '').trim() : name;
            return `${labelText}: ${messages}`;
        });
        return parts.join(' • ') || `${tr('toast.exp.status', 'Request failed with status')} ${status}.`;
    }

    class ApiError extends Error {
        constructor(status, data) {
            super(errorSummary(data, status));
            this.status = status;
            this.data = data;
        }
    }

    // Satu pintu untuk POST/PUT/PATCH/DELETE: JSON, token CSRF di header, error seragam
    async function sendJson(url, method, payload) {
        let response;
        try {
            response = await fetch(url, {
                method,
                headers: {
                    'X-CSRFToken': getCsrfToken(),          // token CSRF lewat header
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: payload === undefined ? undefined : JSON.stringify(payload),
                credentials: 'same-origin',
            });
        } catch (networkError) {
            throw new ApiError(0, { detail: tr('toast.network', 'Could not reach the server. Please try again.') });
        }
        if (response.status === 204) return null;            // DELETE berhasil: body kosong
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new ApiError(response.status, data);
        return data;
    }

    // Membangun kartu (semua teks dari server lewat escapeHtml)

    function periodText(item) {
        const start = formatMonthYear(item.started_at);
        const end = item.is_ongoing ? tr('common.present', 'Present') : formatMonthYear(item.ended_at);
        return `${escapeHtml(start)} &ndash; ${escapeHtml(end)}`;
    }

    function starTitle(item) {
        return item.star_count > 0
            ? `Dibintangi oleh ${item.starred_by_names}`
            : 'Jadilah yang pertama memberi star';
    }

    function starInnerHtml(item) {
        const key = item.is_starred ? 'star.unstar' : 'star.star';
        return `<span aria-hidden="true">&#9733;</span>
                <span data-i18n="${key}">${escapeHtml(tr(key, item.is_starred ? 'Unstar' : 'Star'))}</span>
                <span class="star-count">${Number(item.star_count) || 0}</span>`;
    }

    function starButtonHtml(item) {
        // Belum login: tautan ke halaman login, lalu kembali ke halaman ini
        if (!config.isAuthenticated) {
            const next = encodeURIComponent(window.location.pathname + window.location.search);
            return `<a href="${escapeHtml(config.loginUrl)}?next=${next}" class="button button-star"
                        title="${escapeHtml(starTitle(item))}">${starInnerHtml(item)}</a>`;
        }
        return `<button type="button" class="button button-star${item.is_starred ? ' is-starred' : ''}"
                    data-action="star" data-id="${escapeHtml(item.id)}" title="${escapeHtml(starTitle(item))}">
                    ${starInnerHtml(item)}
                </button>`;
    }

    function actionsHtml(item, title) {
        if (!config.canEdit) return '';
        const deleteButton = config.isOwner
            ? `<button type="button" class="exp-delete-btn" popovertarget="delete-experience-${escapeHtml(item.id)}"
                    aria-label="${escapeHtml(tr('exp.delete.label', 'Delete') + ' ' + title)}" title="${escapeHtml(tr('exp.delete.label', 'Delete'))}">
                    <i class="fa-solid fa-trash" aria-hidden="true"></i>
               </button>`
            : '';
        return `
            <div class="exp-actions">
                <button type="button" class="exp-edit-btn" data-action="edit" data-id="${escapeHtml(item.id)}"
                    aria-label="${escapeHtml(tr('exp.edit.label', 'Edit') + ' ' + title)}" title="${escapeHtml(tr('exp.edit.label', 'Edit'))}">
                    <i class="fa-solid fa-pen" aria-hidden="true"></i>
                </button>
                ${deleteButton}
            </div>`;
    }

    function deleteModalHtml(item, title) {
        if (!config.isOwner) return '';
        const id = escapeHtml(item.id);
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
                    <div class="delete-modal__actions">
                        <button type="button" class="button button-secondary" popovertarget="delete-experience-${id}"
                            popovertargetaction="hide">${escapeHtml(tr('common.cancel', 'Cancel'))}</button>
                        <button type="button" class="button button-danger" data-action="delete" data-id="${id}">
                            ${escapeHtml(tr('common.yes.delete', 'Yes, Delete'))}
                        </button>
                    </div>
                </div>
            </div>`;
    }

    function buildCard(item, index) {
        const title = item.title;
        const photos = Array.isArray(item.all_photos) ? item.all_photos : [];
        const mainPhoto = item.thumbnail || config.defaultPhoto;
        const logo = item.logo || config.defaultLogo;
        const role = field(item.role, item.role_indo);
        const description = field(item.description, item.description_indo);

        const card = document.createElement('article');
        card.className = 'exp-card exp-card--enter';
        card.dataset.id = item.id;
        card.style.setProperty('--i', index);
        card.innerHTML = `
            <div class="exp-meta">
                <span class="exp-category">${escapeHtml(autoText(item.category_display))}</span>
                ${item.is_ongoing
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

                <span class="exp-period">${periodText(item)}</span>
                <p class="exp-desc">${escapeHtml(description)}</p>
                <div class="exp-star">${starButtonHtml(item)}</div>
            </div>
            ${deleteModalHtml(item, title)}`;

        if (item.id === highlightId) card.classList.add('is-new');
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

        // kartu yang baru ditambah/diubah: gulir ke sana sekali, lalu sorotannya hilang sendiri
        if (highlightId) {
            const fresh = el.grid.querySelector('.exp-card.is-new');
            if (fresh) fresh.scrollIntoView({ behavior: 'smooth', block: 'center' });
            highlightId = null;
        }
    }

    // GET /api/v1/experience/?title=...
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

    // Star: POST lalu perbarui tombol di tempat dengan data terbaru dari API

    async function toggleStar(button) {
        const item = await sendJson(urlFor(config.starUrl, button.dataset.id), 'POST');
        const index = experiences.findIndex((entry) => entry.id === item.id);
        if (index !== -1) experiences[index] = item;

        button.classList.toggle('is-starred', item.is_starred);
        button.title = starTitle(item);
        button.innerHTML = starInnerHtml(item);
        button.querySelector('.star-count').classList.add('star-count--bump');
        if (item.is_starred) {
            button.querySelector('span[aria-hidden="true"]').classList.add('star-pop');
            if (typeof burstStars === 'function') burstStars(button);
        }
    }

    // Hapus: DELETE -> 204, lalu muat ulang daftar

    async function deleteExperience(button) {
        await sendJson(urlFor(config.detailUrl, button.dataset.id), 'DELETE');
        const popover = button.closest('[popover]');
        if (popover && popover.matches(':popover-open')) popover.hidePopover();
        showToast(tr('toast.ok', 'Success'), tr('toast.exp.deleted', 'Experience deleted successfully!'), 'success');
        await fetchExperiences();
    }

    // Satu event listener untuk semua tombol di kartu (event delegation),
    // jadi tombol pada kartu yang digambar ulang tetap berfungsi.
    el.grid.addEventListener('click', async (event) => {
        const button = event.target.closest('button[data-action]');
        if (!button || button.disabled) return;
        const action = button.dataset.action;

        if (action === 'edit') {
            const item = findItem(button.dataset.id);
            if (item) openModal(item);
            return;
        }

        button.disabled = true;
        try {
            if (action === 'star') await toggleStar(button);
            if (action === 'delete') await deleteExperience(button);
        } catch (error) {
            if (!(error instanceof ApiError)) console.error(`Error (${action}) experience:`, error);
            const title = action === 'star'
                ? tr('toast.star.fail', 'Failed to change star')
                : tr('toast.exp.delete.fail', 'Failed to delete experience');
            showToast(title, error.message, 'error', 5000);
        } finally {
            button.disabled = false;
        }
    });

    // Modal tambah / ubah (hanya ada untuk pemilik & Editor)

    function clearFieldErrors() {
        el.form.querySelectorAll('.field-error').forEach((p) => { p.hidden = true; p.textContent = ''; });
        el.form.querySelectorAll('[aria-invalid]').forEach((input) => input.removeAttribute('aria-invalid'));
    }

    function showFieldErrors(errors) {
        Object.entries(errors).forEach(([name, list]) => {
            const group = el.form.querySelector(`.form-group[data-field="${CSS.escape(name)}"]`);
            if (!group) return;
            const message = group.querySelector('.field-error');
            message.textContent = [].concat(list).map((e) => autoText(String(e))).join(' ');   // textContent: aman dari XSS
            message.hidden = false;
            const input = group.querySelector('input, textarea, select');
            if (input) input.setAttribute('aria-invalid', 'true');
        });
        const firstInvalid = el.form.querySelector('[aria-invalid="true"]');
        if (firstInvalid) firstInvalid.focus();
    }

    // Judul modal dan tombol mengikuti mode; data-i18n ikut diganti supaya
    // tetap benar saat bahasa diubah ketika modal terbuka.
    function setModalText(titleKey, titleFallback, submitKey, submitFallback) {
        el.modalTitle.dataset.i18n = titleKey;
        el.modalTitle.textContent = tr(titleKey, titleFallback);
        el.submitLabel.dataset.i18n = submitKey;
        el.submitLabel.textContent = tr(submitKey, submitFallback);
    }

    // Nilai form untuk satu Experience (mode ubah), dalam bentuk yang sama dengan isi input
    function formValuesOf(item) {
        const values = {};
        FORM_FIELDS.forEach((name) => { values[name] = item[name] == null ? '' : String(item[name]); });
        return values;
    }

    function readForm() {
        const data = new FormData(el.form);
        const values = {};
        FORM_FIELDS.forEach((name) => { values[name] = (data.get(name) ?? '').toString(); });
        return values;
    }

    // Isi form untuk API: tanggal selesai kosong = masih berlangsung (null)
    function toPayload(values) {
        const payload = { ...values };
        if ('ended_at' in payload && payload.ended_at === '') payload.ended_at = null;
        return payload;
    }

    // show=false dipakai tombol Add yang sudah membuka modal sendiri lewat popovertarget
    function openModal(item, show = true) {
        editing = item || null;
        clearFieldErrors();
        el.form.reset();
        if (editing) {
            const values = formValuesOf(editing);
            FORM_FIELDS.forEach((name) => {
                const input = el.form.elements[name];
                if (input) input.value = values[name];
            });
            setModalText('exp.modal.edit', 'Edit Experience', 'exp.save', 'Save Changes');
        } else {
            setModalText('exp.modal.title', 'Add New Experience', 'exp.add', 'Add Experience');
        }
        if (show && !el.modal.matches(':popover-open')) el.modal.showPopover();
    }

    async function submitExperience(event) {
        event.preventDefault();
        const submitButton = el.form.querySelector('button[type="submit"]');
        const isEdit = Boolean(editing);
        const failTitle = isEdit
            ? tr('toast.exp.update.fail', 'Failed to update experience')
            : tr('toast.exp.fail', 'Failed to add experience');

        // Mode ubah: PATCH hanya field yang benar-benar berubah
        const values = readForm();
        let payload = values;
        if (isEdit) {
            const original = formValuesOf(editing);
            payload = Object.fromEntries(
                Object.entries(values).filter(([name, value]) => value !== original[name])
            );
            if (Object.keys(payload).length === 0) {
                el.modal.hidePopover();
                showToast(tr('toast.info', 'Info'), tr('toast.exp.nochange', 'No changes to save.'), 'normal');
                return;
            }
        }

        submitButton.disabled = true;
        submitButton.classList.add('is-loading');
        clearFieldErrors();
        try {
            const saved = isEdit
                ? await sendJson(urlFor(config.detailUrl, editing.id), 'PATCH', toPayload(payload))
                : await sendJson(config.endpoint, 'POST', toPayload(payload));

            el.form.reset();
            el.modal.hidePopover();
            showToast(
                tr('toast.ok', 'Success'),
                isEdit
                    ? tr('toast.exp.updated', 'Experience updated successfully!')
                    : tr('toast.exp.added', 'New experience added successfully!'),
                'success',
            );
            highlightId = saved.id;
            // Data baru: kosongkan pencarian supaya pasti terlihat
            if (!isEdit && el.searchInput.value) { el.searchInput.value = ''; syncSearchToUrl(); }
            await fetchExperiences();
        } catch (error) {
            // 400/403 adalah jawaban normal dari API (bukan bug), cukup ditampilkan lewat toast
            if (!(error instanceof ApiError)) console.error('Error saving experience:', error);
            if (error.status === 400 && error.data) showFieldErrors(error.data);
            showToast(failTitle, error.message, 'error', 5000);
        } finally {
            submitButton.disabled = false;
            submitButton.classList.remove('is-loading');
        }
    }

    // Modal & form hanya dirender untuk pemilik dan Editor: periksa dulu sebelum memasang listener
    if (el.form && el.modal) {
        el.form.addEventListener('submit', submitExperience);
        // Tombol "Add Experience" membuka modal lewat popovertarget; listener klik
        // berjalan lebih dulu sehingga form sempat disetel ke mode tambah.
        if (el.addButton) el.addButton.addEventListener('click', () => openModal(null, false));
        el.modal.addEventListener('toggle', (event) => {
            if (event.newState === 'open') {
                const first = el.form.querySelector('input:not([type="hidden"]), textarea, select');
                if (first) setTimeout(() => first.focus(), 50);
            } else {
                editing = null;
            }
        });
    }

    // Ganti bahasa: gambar ulang kartu (teks & tanggal ikut bahasa)
    document.addEventListener('langchange', render);

    // Mulai
    fetchExperiences();
})();
