/* Open Cloud из редактора: «☁💾» — быстрое сохранение в Roblox (versionType=Saved), «🧰» — Toolbox
   (поиск по Creator Store и вставка моделей в сцену), «⚙» — настройки experience (cloud/v2/universes).
   Самодостаточный файл по образцу collab.js/assistant.js: сам добавляет кнопки в верхнюю панель;
   серверная часть — блок /api/cloud/* в app.py. Ключ API хранится на сервере («Аккаунт»), сюда не приходит. */
(function () {
    'use strict';

    const DICT = {
        ru: {
            save_title: 'Сохранить в Roblox (Saved): игроки версию не увидят, в Studio она откроется',
            tb_title: 'Toolbox (Creator Store)',
            ex_title: 'Настройки experience',
            saving: 'Сохраняю в Roblox…',
            saved: '✅ Сохранено в Roblox (Saved)',
            no_origin: 'Не знаю Universe/Place ID — введите их в окне публикации',
            tb_h: '🧰 Toolbox — Creator Store',
            tb_q: 'Поиск…',
            tb_go: 'Найти',
            tb_more: 'Ещё',
            tb_insert: 'Вставить',
            tb_copy: 'Копировать ID',
            tb_copied: 'ID скопирован',
            tb_empty: 'Ничего не найдено',
            tb_inserted: 'Вставлено из Creator Store',
            tb_hint: 'Вставка работает для категории Model. Сначала используется API-ключ (права creator-store-product:read и legacy-asset:manage), если его нет или он не принят — вход в аккаунт (cookie).',
            ex_h: '⚙ Настройки experience',
            ex_uid: 'Universe ID',
            ex_load: 'Загрузить',
            ex_name: 'Название',
            ex_desc: 'Описание',
            ex_vis: 'Доступ',
            ex_public: 'Публичный',
            ex_private: 'Приватный',
            ex_voice: 'Голосовой чат',
            ex_desktop: 'ПК',
            ex_mobile: 'Телефоны',
            ex_tablet: 'Планшеты',
            ex_console: 'Консоли',
            ex_vr: 'VR',
            ex_ps: 'Цена приватного сервера (Robux, 0 — выкл.)',
            ex_apply: 'Применить',
            ex_restart: 'Перезапустить серверы',
            ex_applied: '✅ Настройки применены',
            ex_restarted: '✅ Серверы перезапускаются',
            ex_private_warn: 'Приватный доступ немедленно выкинет всех игроков с серверов. Продолжить?',
            ex_restart_warn: 'Перезапустить все активные серверы? Это работает, только если опубликована новая версия.',
            ex_hint: 'Сначала API-ключ (права universe:read и universe:write), потом cookie: через неё меняются название, описание, платформы ПК/телефоны/планшеты/консоли и доступ. Перезапуск серверов — только с ключом.',
            close: 'Закрыть',
            err: 'Ошибка',
            via_api: 'через API-ключ',
            via_cookie: 'через вход в аккаунт (cookie)',
            ex_skipped: 'Через cookie не меняются: {list}',
            ex_nochange: 'Нет изменений',
        },
        en: {
            save_title: 'Save to Roblox (Saved): players will not see it, Studio opens it',
            tb_title: 'Toolbox (Creator Store)',
            ex_title: 'Experience settings',
            saving: 'Saving to Roblox…',
            saved: '✅ Saved to Roblox (Saved)',
            no_origin: 'Universe/Place ID unknown — enter them in the Publish dialog',
            tb_h: '🧰 Toolbox — Creator Store',
            tb_q: 'Search…',
            tb_go: 'Search',
            tb_more: 'More',
            tb_insert: 'Insert',
            tb_copy: 'Copy ID',
            tb_copied: 'ID copied',
            tb_empty: 'Nothing found',
            tb_inserted: 'Inserted from Creator Store',
            tb_hint: 'Insert works for the Model category. The API key is tried first (creator-store-product:read and legacy-asset:manage); if there is none or it is rejected, the account login (cookie) is used.',
            ex_h: '⚙ Experience settings',
            ex_uid: 'Universe ID',
            ex_load: 'Load',
            ex_name: 'Name',
            ex_desc: 'Description',
            ex_vis: 'Visibility',
            ex_public: 'Public',
            ex_private: 'Private',
            ex_voice: 'Voice chat',
            ex_desktop: 'Desktop',
            ex_mobile: 'Mobile',
            ex_tablet: 'Tablet',
            ex_console: 'Console',
            ex_vr: 'VR',
            ex_ps: 'Private server price (Robux, 0 = off)',
            ex_apply: 'Apply',
            ex_restart: 'Restart servers',
            ex_applied: '✅ Settings applied',
            ex_restarted: '✅ Servers are restarting',
            ex_private_warn: 'Private visibility immediately removes all players from running servers. Continue?',
            ex_restart_warn: 'Restart all active servers? Works only if a new version has been published.',
            ex_hint: 'The API key is tried first (universe:read and universe:write), then the cookie: it can change name, description, Desktop/Mobile/Tablet/Console and visibility. Restarting servers needs the key.',
            close: 'Close',
            err: 'Error',
            via_api: 'via API key',
            via_cookie: 'via account login (cookie)',
            ex_skipped: 'Not changeable via cookie: {list}',
            ex_nochange: 'No changes',
        },
    };
    function lang() {
        try { if (typeof LANG !== 'undefined' && DICT[LANG]) return LANG; } catch (e) { /* LANG ещё не объявлен */ }
        return /^ru/i.test(navigator.language || '') ? 'ru' : 'en';
    }
    function T(k, v) {
        let s = (DICT[lang()] || DICT.en)[k] || DICT.en[k] || k;
        if (v) for (const x in v) s = s.split('{' + x + '}').join(v[x]);
        return s;
    }
    const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const $ = id => document.getElementById(id);
    function say(msg, type) { try { notify(msg, type); } catch (e) { console.log(msg); } }
    async function call(method, url, body) {
        try {
            const opts = { method: method, headers: { 'Content-Type': 'application/json' } };
            if (body !== undefined) opts.body = JSON.stringify(body);
            const r = await fetch(url, opts);
            return await r.json();
        } catch (e) {
            return { ok: false, error: String(e) };
        }
    }
    const origin = () => window._rbxOrigin || null;
    const viaText = v => v === 'api-key' ? T('via_api') : v === 'cookie' ? T('via_cookie') : '';

    // ---------- быстрое сохранение в Roblox (Saved) ----------
    async function quickSave() {
        const o = origin();
        if (!o || !o.universeId || !o.placeId) {
            say(T('no_origin'), 'warn');
            if (typeof showPublishDialog === 'function') showPublishDialog();
            return;
        }
        say(T('saving'));
        const r = await call('POST', '/api/publish', {
            universe_id: String(o.universeId), place_id: String(o.placeId), version_type: 'Saved',
        });
        if (r.ok) say(T('saved') + (r.via ? ' (' + viaText(r.via) + ')' : ''));
        else say('HTTP ' + (r.status || '') + ': ' + (r.text || r.error || T('err')), 'err');
    }

    // ---------- Toolbox ----------
    const TB = { cat: 'Model', q: '', next: '' };
    const CATS = ['Model', 'Audio', 'Decal', 'Plugin', 'MeshPart', 'Video', 'FontFamily'];

    // Форма ответа toolbox-service не зафиксирована в доках — достаём поля защитно.
    function pickItems(data) {
        if (!data || typeof data !== 'object') return [];
        if (Array.isArray(data)) return data;
        for (const k in data) if (Array.isArray(data[k])) return data[k];
        return [];
    }
    function pickNext(data) {
        if (!data || typeof data !== 'object') return '';
        for (const k in data) if (/pagetoken|cursor/i.test(k) && typeof data[k] === 'string') return data[k];
        return '';
    }
    function itemInfo(it) {
        const a = (it && (it.asset || it.creatorStoreAsset)) || it || {};
        const id = a.id || a.assetId || it.id || it.assetId || '';
        const name = a.displayName || a.name || a.title || it.displayName || it.name || ('#' + id);
        return { id: String(id), name: String(name) };
    }

    function tbShell() {
        return '<h3>' + T('tb_h') + '</h3>' +
            '<div class="modal-row" style="gap:6px;flex-wrap:wrap">' +
            '<select id="cl-cat" style="flex:0 0 auto;width:auto">' + CATS.map(c =>
                '<option value="' + c + '"' + (c === TB.cat ? ' selected' : '') + '>' + c + '</option>').join('') + '</select>' +
            '<input id="cl-q" placeholder="' + esc(T('tb_q')) + '" value="' + esc(TB.q) + '" style="flex:1;min-width:140px">' +
            '<button id="cl-go" style="background:#2563eb">' + T('tb_go') + '</button></div>' +
            '<p id="cl-msg" style="min-height:1.2em;margin:6px 0;font-size:13px;color:#fca5a5"></p>' +
            '<div id="cl-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;max-height:50vh;overflow:auto"></div>' +
            '<div class="modal-row" style="margin-top:8px"><button id="cl-more" style="display:none">' + T('tb_more') + '</button>' +
            '<button id="cl-x">' + T('close') + '</button></div>' +
            '<p style="opacity:.7;font-size:12px;margin:6px 0 0">' + T('tb_hint') + '</p>';
    }
    function tbCard(it) {
        const i = itemInfo(it);
        if (!i.id) return '';
        const thumb = '/api/toolbox/thumb/' + encodeURIComponent(i.id);
        return '<div style="background:#1f2937;border-radius:6px;padding:6px;display:flex;flex-direction:column;gap:4px">' +
            '<img src="' + thumb + '" alt="" data-nolog="1" loading="lazy" style="width:100%;aspect-ratio:1;object-fit:cover;border-radius:4px;background:#111827">' +
            '<div style="font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="' + esc(i.name) + '">' + esc(i.name) + '</div>' +
            (TB.cat === 'Model'
                ? '<button data-ins="' + esc(i.id) + '" style="background:#16a34a">' + T('tb_insert') + '</button>'
                : '<button data-cp="' + esc(i.id) + '">' + T('tb_copy') + '</button>') +
            '</div>';
    }
    async function tbSearch(append) {
        const msg = $('cl-msg'), grid = $('cl-grid'), more = $('cl-more');
        if (!append) { TB.next = ''; grid.innerHTML = ''; }
        msg.textContent = '…';
        const qs = new URLSearchParams({ category: TB.cat, q: TB.q });
        if (append && TB.next) qs.set('pageToken', TB.next);
        msg.style.color = '#fca5a5';
        const r = await call('GET', '/api/cloud/toolbox/search?' + qs.toString());
        if (!r.ok) { msg.textContent = r.error || T('err'); more.style.display = 'none'; return; }
        const items = pickItems(r.data);
        const html = items.map(tbCard).join('');
        if (!html && !append) { msg.textContent = T('tb_empty'); more.style.display = 'none'; return; }
        msg.textContent = '';
        grid.insertAdjacentHTML('beforeend', html);
        msg.style.color = '#9ca3af';
        msg.textContent = viaText(r.via);
        TB.next = pickNext(r.data);
        more.style.display = TB.next ? '' : 'none';
    }
    async function tbInsert(id, btn) {
        btn.disabled = true;
        let parent = null;
        try { if (typeof rbxmImportParent === 'function') parent = rbxmImportParent(); } catch (e) { /* ok */ }
        const r = await call('POST', '/api/cloud/toolbox/insert', { assetId: id, parent: parent });
        btn.disabled = false;
        if (r.ok) {
            if (typeof afterRbxmImport === 'function') await afterRbxmImport(r);
            else say(T('tb_inserted'));
        } else say(r.error || T('err'), 'err');
    }
    function openToolbox() {
        showModal(tbShell());
        $('cl-x').onclick = closeModal;
        $('cl-cat').onchange = e => { TB.cat = e.target.value; tbSearch(false); };
        $('cl-go').onclick = () => { TB.q = $('cl-q').value.trim(); TB.cat = $('cl-cat').value; tbSearch(false); };
        $('cl-q').onkeydown = e => { if (e.key === 'Enter') $('cl-go').click(); };
        $('cl-more').onclick = () => tbSearch(true);
        $('cl-grid').onclick = e => {
            const b = e.target.closest('button');
            if (!b) return;
            if (b.dataset.ins) tbInsert(b.dataset.ins, b);
            else if (b.dataset.cp) {
                try { navigator.clipboard.writeText(b.dataset.cp); } catch (err) { /* ok */ }
                say(T('tb_copied'));
            }
        };
        tbSearch(false);
    }

    // ---------- настройки experience ----------
    const FLAGS = [['voiceChatEnabled', 'ex_voice'], ['desktopEnabled', 'ex_desktop'], ['mobileEnabled', 'ex_mobile'],
        ['tabletEnabled', 'ex_tablet'], ['consoleEnabled', 'ex_console'], ['vrEnabled', 'ex_vr']];

    function exShell() {
        const o = origin();
        return '<h3>' + T('ex_h') + '</h3>' +
            '<div class="modal-row" style="gap:6px"><input id="cx-uid" placeholder="' + esc(T('ex_uid')) + '" value="' + esc(o && o.universeId || '') + '" style="flex:1">' +
            '<button id="cx-load" style="background:#2563eb">' + T('ex_load') + '</button></div>' +
            '<p id="cx-msg" style="min-height:1.2em;margin:6px 0;font-size:13px;color:#fca5a5"></p>' +
            '<div id="cx-form" style="display:none;flex-direction:column;gap:6px">' +
            '<label>' + T('ex_name') + '<input id="cx-name"></label>' +
            '<label>' + T('ex_desc') + '<textarea id="cx-desc" rows="3" style="width:100%;box-sizing:border-box"></textarea></label>' +
            '<label>' + T('ex_vis') + '<select id="cx-vis"><option value="PUBLIC">' + T('ex_public') + '</option>' +
            '<option value="PRIVATE">' + T('ex_private') + '</option></select></label>' +
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px 12px">' + FLAGS.map(f =>
                '<label style="display:flex;gap:6px;align-items:center"><input type="checkbox" id="cx-' + f[0] + '" style="width:auto">' + T(f[1]) + '</label>').join('') + '</div>' +
            '<label>' + T('ex_ps') + '<input id="cx-ps" type="number" min="0"></label>' +
            '<div class="modal-row"><button id="cx-apply" style="background:#2563eb">' + T('ex_apply') + '</button>' +
            '<button id="cx-restart" style="background:#b45309">' + T('ex_restart') + '</button></div></div>' +
            '<div class="modal-row" style="margin-top:8px"><button id="cx-x">' + T('close') + '</button></div>' +
            '<p style="opacity:.7;font-size:12px;margin:6px 0 0">' + T('ex_hint') + '</p>';
    }
    let exLoaded = {};
    function exSay(text, ok) {
        const m = $('cx-msg');
        m.style.color = ok ? '#9ca3af' : '#fca5a5';
        m.textContent = text || '';
    }
    async function exLoad() {
        const id = $('cx-uid').value.trim();
        if (!/^\d+$/.test(id)) { exSay(T('ex_uid') + ': 123…'); return; }
        exSay('…', true);
        const r = await call('GET', '/api/cloud/universe/' + id);
        if (!r.ok) { exSay(r.error || T('err')); return; }
        exSay(viaText(r.via), true);
        const u = r.data || {};
        exLoaded = {};
        $('cx-name').value = exLoaded.displayName = u.displayName || '';
        $('cx-desc').value = exLoaded.description = u.description || '';
        // доступ: если источник его не отдал, показываем «—» и не трогаем, пока пользователь не выберет сам
        const vis = u.visibility === 'PRIVATE' ? 'PRIVATE' : u.visibility === 'PUBLIC' ? 'PUBLIC' : '';
        const sel = $('cx-vis');
        const blank = sel.querySelector('option[value=""]');
        if (!vis && !blank) sel.insertAdjacentHTML('afterbegin', '<option value="">—</option>');
        if (vis && blank) blank.remove();
        sel.value = exLoaded.visibility = vis;
        // флаги и цена, которых источник не знает (cookie-путь), отключаем — иначе «false» ушло бы как изменение
        FLAGS.forEach(f => {
            const el = $('cx-' + f[0]);
            const known = typeof u[f[0]] === 'boolean';
            el.disabled = !known;
            el.indeterminate = !known;
            el.checked = known && u[f[0]];
            exLoaded[f[0]] = known ? u[f[0]] : undefined;
        });
        const psKnown = u.privateServerPriceRobux != null;
        $('cx-ps').disabled = !psKnown;
        $('cx-ps').value = psKnown ? (Number(u.privateServerPriceRobux) || 0) : '';
        exLoaded.privateServerPriceRobux = psKnown ? (Number(u.privateServerPriceRobux) || 0) : undefined;
        $('cx-form').style.display = 'flex';
    }
    async function exApply() {
        const id = $('cx-uid').value.trim();
        // отправляем только то, что пользователь изменил: так не затираются поля, которые мы не смогли прочитать
        const now = { displayName: $('cx-name').value, description: $('cx-desc').value, visibility: $('cx-vis').value };
        FLAGS.forEach(f => { const el = $('cx-' + f[0]); now[f[0]] = el.disabled ? undefined : el.checked; });
        const ps = $('cx-ps');
        now.privateServerPriceRobux = ps.disabled ? undefined : (parseInt(ps.value, 10) || 0);
        const body = {};
        for (const k in now) if (now[k] !== undefined && now[k] !== '' && now[k] !== exLoaded[k]) body[k] = now[k];
        if (!Object.keys(body).length) { exSay(T('ex_nochange'), true); return; }
        if (body.visibility === 'PRIVATE' && !confirm(T('ex_private_warn'))) return;
        exSay('…', true);
        const r = await call('PATCH', '/api/cloud/universe/' + id, body);
        if (!r.ok) { exSay(r.error || T('err')); return; }
        for (const k in body) exLoaded[k] = body[k];
        const sk = r.data && Array.isArray(r.data.skipped) ? r.data.skipped : [];
        exSay(T('ex_applied') + ' (' + viaText(r.via) + ')' + (sk.length ? '. ' + T('ex_skipped', { list: sk.join(', ') }) : ''), true);
    }
    async function exRestart() {
        const id = $('cx-uid').value.trim();
        if (!confirm(T('ex_restart_warn'))) return;
        const r = await call('POST', '/api/cloud/universe/' + id + '/restart');
        if (r.ok) say(T('ex_restarted'));
        else exSay(r.error || T('err'));
    }
    function openExperience() {
        showModal(exShell());
        $('cx-x').onclick = closeModal;
        $('cx-load').onclick = exLoad;
        $('cx-apply').onclick = exApply;
        $('cx-restart').onclick = exRestart;
        if (/^\d+$/.test($('cx-uid').value)) exLoad();
    }

    // ---------- кнопки в верхней панели (после «☁ Публикация») ----------
    const bar = document.getElementById('toolbar-top');
    if (bar) {
        const mk = (label, title, fn, cls) => {
            const b = document.createElement('button');
            if (cls) b.className = cls;
            b.textContent = label;
            b.title = title;
            b.onclick = fn;
            return b;
        };
        const anchor = bar.querySelector('button[onclick^="showPublishDialog"]');
        const btns = [
            mk('☁💾', T('save_title'), quickSave, 'blue'),
            mk('🧰', T('tb_title'), openToolbox),
            mk('⚙', T('ex_title'), openExperience),
        ];
        let ref = anchor;
        for (const b of btns) {
            if (ref && ref.parentNode) { ref.parentNode.insertBefore(b, ref.nextSibling); ref = b; }
            else bar.appendChild(b);
        }
    }
})();
