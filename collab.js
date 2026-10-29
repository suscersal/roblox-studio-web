/* Совместная работа: хост нажимает «Начать», второй человек открывает тот же
   адрес (http://<ip-хоста>:порт), вводит код комнаты — и оба правят одну карту.
   Самодостаточный файл по образцу assistant.js: сам добавляет кнопку 👥 в
   верхнюю панель и свои стили; серверная часть — блок /api/collab/* в app.py. */
(function () {
    'use strict';

    // ---------- язык ----------
    const DICT = {
        ru: {
            btn_title: 'Совместная работа',
            title: '👥 Совместная работа',
            name: 'Ваше имя',
            start: 'Начать совместную работу',
            stop: 'Закрыть комнату',
            hint_host: 'Второй человек открывает один из адресов в браузере и вводит код.',
            code: 'Код комнаты',
            addr: 'Адрес',
            no_room: 'Комната не запущена. Её начинает хост на своём устройстве.',
            join_title: 'Комната запущена. Введите код от хоста:',
            join: 'Войти',
            bad_code: 'Неверный код комнаты',
            online: 'Сейчас в комнате',
            you: 'вы',
            history: 'История изменений',
            empty: 'Пока без изменений',
            undo: '↩ вернуть до этой точки',
            undo_confirm: 'Откатить все изменения, сделанные после этой точки?',
            reverted: 'Откат выполнен: {n}',
            revert_fail: 'Откат не удался: {msg}',
            joined: '{who} вошёл(а)',
            now: 'сейчас',
            min: '{n} мин',
            h: '{n} ч',
            obj: '{cls} «{name}»',
            op_set: '{who}: {prop} у {obj}',
            op_add: '{who} добавил(а) {obj}',
            op_del: '{who} удалил(а) {obj}',
            op_move: '{who} перенёс(ла) {obj}',
            op_move_n: '{who} перенёс(ла) объектов: {n}',
            op_import: '{who} импортировал(а) объектов: {n}',
            op_revert: '{who} откатил(а) операций: {n}',
            op_reload: 'Открыта другая карта',
            op_script: '{who} изменил(а) скрипт {obj}',
            kept: 'Открыт чужой скрипт был изменён — откройте его заново',
            net: 'Нет связи с сервером',
        },
        en: {
            btn_title: 'Collaboration',
            title: '👥 Collaboration',
            name: 'Your name',
            start: 'Start collaborating',
            stop: 'Close room',
            hint_host: 'The other person opens one of the addresses in a browser and enters the code.',
            code: 'Room code',
            addr: 'Address',
            no_room: 'No room is running. The host starts it on their device.',
            join_title: 'A room is running. Enter the host’s code:',
            join: 'Join',
            bad_code: 'Wrong room code',
            online: 'In the room now',
            you: 'you',
            history: 'Change history',
            empty: 'No changes yet',
            undo: '↩ revert to this point',
            undo_confirm: 'Undo every change made after this point?',
            reverted: 'Reverted: {n}',
            revert_fail: 'Revert failed: {msg}',
            joined: '{who} joined',
            now: 'now',
            min: '{n} min',
            h: '{n} h',
            obj: '{cls} “{name}”',
            op_set: '{who}: {prop} of {obj}',
            op_add: '{who} added {obj}',
            op_del: '{who} deleted {obj}',
            op_move: '{who} moved {obj}',
            op_move_n: '{who} moved {n} objects',
            op_import: '{who} imported {n} objects',
            op_revert: '{who} reverted {n} operations',
            op_reload: 'Another map was opened',
            op_script: '{who} edited script {obj}',
            kept: 'The script you have open was changed — reopen it',
            net: 'No connection to the server',
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
    const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const sleep = ms => new Promise(r => setTimeout(r, ms));

    // ---------- личность: id вкладки, имя, код комнаты ----------
    function store(area, key, val) {
        try {
            const st = window[area];
            if (val === undefined) return st.getItem(key);
            if (val === null) st.removeItem(key); else st.setItem(key, val);
        } catch (e) { /* без хранилища — работаем в памяти вкладки */ }
        return null;
    }
    const myId = store('sessionStorage', 'rsw_co_id') || (Math.random().toString(36).slice(2, 10) + Date.now().toString(36));
    store('sessionStorage', 'rsw_co_id', myId);
    let myName = store('localStorage', 'rsw_co_name') || '';
    let token = store('sessionStorage', 'rsw_co_token') || '';

    // Все запросы к /api/ несут id/имя/код — сервер по ним ведёт журнал и
    // пускает гостя на запись. script.js при этом не трогаем.
    const origFetch = window.fetch.bind(window);
    window.fetch = function (input, init) {
        try {
            const url = typeof input === 'string' ? input : ((input && input.url) || '');
            const path = url.startsWith('/') ? url : (url.startsWith(location.origin) ? url.slice(location.origin.length) : '');
            if (path.startsWith('/api/')) {
                init = Object.assign({}, init);
                const h = new Headers(init.headers || ((typeof Request !== 'undefined' && input instanceof Request) ? input.headers : undefined));
                h.set('X-Collab-Id', myId);
                if (myName) h.set('X-Collab-Name', encodeURIComponent(myName));
                if (token) h.set('X-Collab-Token', token);
                init.headers = h;
            }
        } catch (e) { /* не ломаем чужие запросы */ }
        return origFetch(input, init);
    };
    async function jget(url) { return (await fetch(url)).json(); }
    async function jpost(url, body) {
        const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });
        let d = {}; try { d = await r.json(); } catch (e) { /* не JSON */ }
        d._status = r.status;
        return d;
    }

    // ---------- состояние ----------
    const S = { on: false, local: true, joined: false, rev: 0, base: 0, peers: [], feed: [], token: '', urls: [], net: true };
    let loopId = 0;

    function curSel() {
        try { return (typeof selectedRef !== 'undefined' && selectedRef !== null) ? selectedRef : null; } catch (e) { return null; }
    }
    function ago(t) {
        const s = Math.max(0, Date.now() / 1000 - t);
        if (s < 45) return T('now');
        if (s < 3600) return T('min', { n: Math.round(s / 60) });
        return T('h', { n: Math.round(s / 3600) });
    }
    function objLabel(o) {
        return o.cls ? T('obj', { cls: o.cls, name: o.name || '?' }) : '#' + o.ref;
    }
    function opText(o) {
        const v = { who: o.by, obj: objLabel(o), prop: o.prop, n: o.n };
        switch (o.type) {
            case 'set': return T(o.prop === 'Source' ? 'op_script' : 'op_set', v);
            case 'add': return T('op_add', v);
            case 'del': return T('op_del', v);
            case 'move': return T(o.n > 1 ? 'op_move_n' : 'op_move', v);
            case 'import': return T('op_import', v);
            case 'revert': return T('op_revert', v);
            default: return T('op_reload', v);
        }
    }

    // ---------- обновление редактора после чужих правок ----------
    const STRUCT = { add: 1, del: 1, move: 1, import: 1, revert: 1, reload: 1 };
    let tTree = null, tScene = null, scenePending = false;

    async function refreshTree(reselect) {
        try {
            if (typeof loadTree === 'function') await loadTree();
            const sel = curSel();
            if (reselect && sel !== null && typeof selectRef === 'function') await selectRef(sel);
        } catch (e) { /* интерфейс обновится при следующем действии */ }
        markPeers();
    }
    function refreshScene() {
        try {
            if (typeof isPlaying !== 'undefined' && isPlaying) { scenePending = true; return; }   // в Play сцену не трогаем
            if (typeof reloadScene === 'function') reloadScene();
        } catch (e) { /* ждём следующей правки */ }
    }
    // Сцена перестраивается целиком — не чаще раза в ~1.2 с, как бы быстро ни сыпались правки.
    function applyRemote(ops) {
        const struct = ops.some(o => STRUCT[o.type] || (o.type === 'set' && o.prop === 'Name'));
        const sel = curSel();
        const touchesSel = ops.some(o => o.type === 'revert' || o.type === 'reload' || (o.type === 'set' && o.ref === sel));
        const scene = ops.some(o => !(o.type === 'set' && o.prop === 'Source'));
        if (struct || touchesSel) {
            clearTimeout(tTree);
            tTree = setTimeout(() => refreshTree(touchesSel), 350);
        }
        if (scene) {
            clearTimeout(tScene);
            tScene = setTimeout(refreshScene, 1200);
        }
        try {
            if (typeof notify === 'function') {
                for (const o of ops.filter(x => x.type !== 'set' || x.prop === 'Source').slice(-3)) notify(opText(o));
            }
        } catch (e) { /* без тостов */ }
    }
    function fullRefresh() {
        clearTimeout(tTree); clearTimeout(tScene);
        refreshTree(true).then(refreshScene);
    }
    // вышли из Play — догружаем сцену, которую откладывали
    setInterval(() => {
        try { if (scenePending && !(typeof isPlaying !== 'undefined' && isPlaying)) { scenePending = false; refreshScene(); } } catch (e) { /* ok */ }
    }, 1500);

    // ---------- подсветка объекта, который выбрал другой человек ----------
    function markPeers() {
        const tree = document.getElementById('tree');
        if (!tree) return;
        tree.querySelectorAll('.co-peer').forEach(el => { el.classList.remove('co-peer'); el.removeAttribute('data-co'); });
        for (const p of S.peers) {
            if (p.id === myId || p.sel === null || p.sel === undefined) continue;
            const row = tree.querySelector('[data-ref="' + p.sel + '"]');
            if (row) { row.classList.add('co-peer'); row.setAttribute('data-co', p.name); }
        }
    }
    try {
        const tree = document.getElementById('tree');
        if (tree) new MutationObserver(() => { if (S.joined) markPeers(); }).observe(tree, { childList: true });
    } catch (e) { /* без подсветки */ }

    // ---------- long-poll ----------
    function onPoll(d) {
        S.peers = d.peers || [];
        if (d.reset) {
            S.rev = d.rev;
            loadHistory();
            fullRefresh();
        } else {
            for (const o of d.ops || []) {
                // подряд идущие правки одного свойства сервер склеивает в одну запись — заменяем, а не дублируем
                const f = S.feed[0];
                if (o.type === 'set' && f && f.type === 'set' && f.byId === o.byId && f.ref === o.ref && f.prop === o.prop) S.feed[0] = o;
                else S.feed.unshift(o);
            }
            if (S.feed.length > 300) S.feed.length = 300;
            S.rev = Math.max(S.rev, d.rev);
            const others = (d.ops || []).filter(o => o.byId !== myId);
            if (others.length) applyRemote(others);
        }
        renderPeers(); renderFeed(); markPeers(); updateBadge();
    }
    async function loop(run) {
        while (run === loopId && S.joined) {
            const ctrl = new AbortController();
            const to = setTimeout(() => ctrl.abort(), 32000);
            try {
                const sel = curSel();
                const r = await fetch('/api/collab/poll?since=' + S.rev + '&wait=15' + (sel !== null ? '&sel=' + sel : ''), { signal: ctrl.signal });
                clearTimeout(to);
                if (run !== loopId) return;
                if (r.status === 403) { leave(true); return; }
                const d = await r.json();
                if (!d.on) { S.on = false; leave(false); return; }
                if (!S.net) { S.net = true; renderAll(); }
                onPoll(d);
            } catch (e) {
                clearTimeout(to);
                if (run !== loopId) return;
                if (S.net) { S.net = false; renderAll(); }
                await sleep(2500);
            }
        }
    }
    async function loadHistory() {
        try {
            const h = await jget('/api/collab/history?limit=150');
            if (h.ok) { S.feed = h.ops; S.rev = Math.max(S.rev, h.rev); S.base = h.base; renderFeed(); }
        } catch (e) { /* лента заполнится по poll */ }
    }
    async function join() {
        if (!myName) myName = S.local ? 'Host' : '';
        if (!myName) return false;
        const r = await jpost('/api/collab/join');
        if (r._status === 403) { token = ''; store('sessionStorage', 'rsw_co_token', null); return 'code'; }
        if (!r.ok) return false;
        S.joined = true; S.rev = r.rev; S.peers = r.peers || [];
        await loadHistory();
        loop(++loopId);
        return true;
    }
    function leave(badCode) {
        S.joined = false; loopId++;
        if (badCode) { token = ''; store('sessionStorage', 'rsw_co_token', null); }
        S.peers = []; markPeers();
        renderAll(); updateBadge();
        if (badCode) setMsg(T('bad_code'));
    }

    // ---------- статус комнаты ----------
    async function refreshStatus() {
        try {
            const st = await jget('/api/collab/status');
            if (!st.ok) return;
            S.local = st.local; S.on = st.on; S.token = st.token || ''; S.urls = st.urls || [];
            if (st.on && !S.joined && (S.local || (token && myName))) {
                const j = await join();
                if (j === 'code') setMsg(T('bad_code'));
            } else if (!st.on && S.joined) {
                leave(false);
            }
            renderAll(); updateBadge();
        } catch (e) { /* сервер недоступен — повторим */ }
    }
    setInterval(() => { if (!document.hidden && !S.joined) refreshStatus(); }, 6000);

    // ---------- интерфейс ----------
    const css = document.createElement('style');
    css.textContent = `
#co-panel{--f:calc(13px*var(--fs,1));--b:calc(30px*var(--bs,1));position:fixed;right:12px;top:52px;width:340px;max-width:calc(100vw - 24px);max-height:calc(100vh - 70px);display:none;flex-direction:column;background:#111827;border:1px solid #374151;border-radius:8px;color:#e5e7eb;z-index:9100;box-shadow:0 8px 28px rgba(0,0,0,.55);font:var(--f)/1.45 system-ui,sans-serif;overflow:hidden}
#co-panel.open{display:flex}
#co-panel *{box-sizing:border-box}
#co-panel button,#co-panel input{font:inherit;color:#fff}
#co-panel button{background:#374151;border:none;border-radius:4px;padding:0 10px;min-height:var(--b);cursor:pointer}
#co-panel button:hover{background:#4b5563}
#co-panel button.pri{background:#2563eb}#co-panel button.pri:hover{background:#1d4ed8}
#co-panel button.dng{background:#7f1d1d}
#co-panel input{background:#1f2937;border:1px solid #374151;border-radius:4px;padding:0 8px;min-height:var(--b);width:100%}
#co-panel :focus-visible{outline:2px solid #3b82f6;outline-offset:1px}
#co-head{display:flex;align-items:center;justify-content:space-between;padding:8px 10px;border-bottom:1px solid #374151;font-weight:600}
#co-head button{min-height:calc(24px*var(--bs,1));padding:0 8px}
#co-body{padding:10px;overflow:auto;display:flex;flex-direction:column;gap:10px}
.co-row{display:flex;gap:6px;align-items:center}
.co-sec{font-size:calc(11px*var(--fs,1));text-transform:uppercase;letter-spacing:.04em;color:#9ca3af;margin-bottom:4px}
.co-code{font:700 calc(22px*var(--fs,1))/1 ui-monospace,monospace;letter-spacing:.18em;color:#fbbf24;user-select:all}
.co-url{font:calc(12px*var(--fs,1))/1.4 ui-monospace,monospace;color:#93c5fd;user-select:all;word-break:break-all}
.co-muted{color:#9ca3af}
.co-msg{color:#fca5a5;min-height:1em}
.co-net{background:#78350f;color:#fde68a;border-radius:4px;padding:4px 8px}
.co-peer-i{display:flex;gap:6px;align-items:center;padding:2px 0}
.co-dot{width:8px;height:8px;border-radius:50%;background:#34d399;flex:none}
.co-feed{display:flex;flex-direction:column;gap:2px;max-height:38vh;overflow:auto}
.co-op{padding:4px 6px;border-radius:4px;background:#1f2937}
.co-op:hover{background:#273244}
.co-op small{display:block;color:#9ca3af}
.co-op .co-undo{display:none;margin-top:3px;min-height:calc(22px*var(--bs,1));font-size:.92em}
.co-op:hover .co-undo,.co-op:focus-within .co-undo{display:inline-block}
@media (hover:none){.co-op .co-undo{display:inline-block}}
#toolbar-top button#co-btn{position:relative}
#co-badge{display:none;position:absolute;top:-4px;right:-4px;min-width:16px;height:16px;border-radius:8px;background:#10b981;color:#fff;font:700 10px/16px system-ui,sans-serif;text-align:center;padding:0 3px}
#tree .co-peer{box-shadow:inset 3px 0 0 #f59e0b;background:rgba(245,158,11,.14)}
#tree .co-peer::after{content:attr(data-co);margin-left:8px;font-size:.8em;color:#f59e0b}
@media (max-width:700px){#co-panel{left:8px;right:8px;width:auto;top:48px}}
`;
    document.head.appendChild(css);

    const panel = document.createElement('div');
    panel.id = 'co-panel';
    panel.innerHTML = '<div id="co-head"><span id="co-title"></span><button id="co-x" aria-label="×">×</button></div><div id="co-body"></div>';
    document.body.appendChild(panel);
    const body = panel.querySelector('#co-body');
    panel.querySelector('#co-x').onclick = () => panel.classList.remove('open');

    let msgEl = null;
    function setMsg(t) { if (msgEl) msgEl.textContent = t || ''; else pendingMsg = t; }
    let pendingMsg = '';

    // Каркас перерисовывается только при смене режима; ленту и людей обновляем точечно,
    // чтобы не терять фокус в полях ввода.
    let mode = '';
    function renderAll() {
        document.getElementById('co-title').textContent = T('title');
        const m = S.joined ? 'room' : (S.on ? 'join' : (S.local ? 'host' : 'wait'));
        if (m !== mode || (m === 'room' && !body.querySelector('#co-feed'))) { mode = m; build(m); }
        else if (m === 'room') {
            const net = body.querySelector('#co-net'); if (net) net.style.display = S.net ? 'none' : '';
            const code = body.querySelector('#co-codebox'); if (code) code.innerHTML = codeBox();
        }
        renderPeers(); renderFeed();
    }
    function nameField() {
        return '<div><div class="co-sec">' + T('name') + '</div><input id="co-name" maxlength="32" value="' + esc(myName) + '"></div>';
    }
    function codeBox() {
        if (!S.local || !S.token) return '';
        return '<div class="co-sec">' + T('code') + '</div><div class="co-code">' + esc(S.token) + '</div>'
            + (S.urls.length ? '<div class="co-sec" style="margin-top:8px">' + T('addr') + '</div>' + S.urls.map(u => '<div class="co-url">' + esc(u) + '</div>').join('') : '')
            + '<div class="co-muted" style="margin-top:6px">' + T('hint_host') + '</div>';
    }
    function build(m) {
        msgEl = null;
        let h = '';
        if (m === 'host') {
            h = nameField() + '<button class="pri" id="co-start">' + T('start') + '</button><div class="co-msg" id="co-msg"></div>';
        } else if (m === 'wait') {
            h = '<div class="co-muted">' + T('no_room') + '</div>';
        } else if (m === 'join') {
            h = '<div>' + T('join_title') + '</div>' + nameField()
                + '<div><div class="co-sec">' + T('code') + '</div><input id="co-tok" maxlength="12" autocomplete="off" autocapitalize="characters" value="' + esc(token) + '"></div>'
                + '<button class="pri" id="co-join">' + T('join') + '</button><div class="co-msg" id="co-msg"></div>';
        } else {
            h = '<div class="co-net" id="co-net" style="display:' + (S.net ? 'none' : '') + '">' + T('net') + '</div>'
                + nameField()
                + '<div id="co-codebox">' + codeBox() + '</div>'
                + '<div><div class="co-sec">' + T('online') + '</div><div id="co-peers"></div></div>'
                + '<div><div class="co-sec">' + T('history') + '</div><div class="co-feed" id="co-feed"></div></div>'
                + (S.local ? '<button class="dng" id="co-stop">' + T('stop') + '</button>' : '')
                + '<div class="co-msg" id="co-msg"></div>';
        }
        body.innerHTML = h;
        msgEl = body.querySelector('#co-msg');
        if (msgEl && pendingMsg) { msgEl.textContent = pendingMsg; pendingMsg = ''; }
        wire();
    }
    function saveName() {
        const el = body.querySelector('#co-name');
        if (el) { myName = el.value.trim().slice(0, 32); store('localStorage', 'rsw_co_name', myName); }
        return myName;
    }
    function wire() {
        const nm = body.querySelector('#co-name');
        if (nm) nm.onchange = saveName;
        const st = body.querySelector('#co-start');
        if (st) st.onclick = async () => {
            if (!saveName()) myName = 'Host';
            const r = await jpost('/api/collab/start');
            if (!r.ok) { setMsg(r.error || ''); return; }
            await refreshStatus();
        };
        const jn = body.querySelector('#co-join');
        if (jn) jn.onclick = async () => {
            if (!saveName()) { setMsg(T('name')); return; }
            token = (body.querySelector('#co-tok').value || '').trim().toUpperCase();
            store('sessionStorage', 'rsw_co_token', token);
            const r = await join();
            if (r === 'code' || r === false) { setMsg(T('bad_code')); return; }
            renderAll(); updateBadge();
        };
        const sp = body.querySelector('#co-stop');
        if (sp) sp.onclick = async () => { await jpost('/api/collab/stop'); S.joined = false; loopId++; S.on = false; S.peers = []; markPeers(); await refreshStatus(); };
    }
    function renderPeers() {
        const el = body.querySelector('#co-peers');
        if (!el) return;
        el.innerHTML = S.peers.map(p => '<div class="co-peer-i"><span class="co-dot"></span>' + esc(p.name)
            + (p.id === myId ? ' <span class="co-muted">(' + T('you') + ')</span>' : '') + '</div>').join('');
    }
    function renderFeed() {
        const el = body.querySelector('#co-feed');
        if (!el) return;
        if (!S.feed.length) { el.innerHTML = '<div class="co-muted">' + T('empty') + '</div>'; return; }
        el.innerHTML = S.feed.slice(0, 80).map((o, i) => {
            // «вернуть до этой точки» = вернуть карту к состоянию сразу ПОСЛЕ этой записи;
            // у самой свежей записи откатывать нечего
            const can = i > 0;
            return '<div class="co-op"><div>' + esc(opText(o)) + '</div><small>' + esc(ago(o.t)) + ' · #' + o.rev + '</small>'
                + (can ? '<button class="co-undo" data-rev="' + o.rev + '">' + T('undo') + '</button>' : '') + '</div>';
        }).join('');
        el.querySelectorAll('.co-undo').forEach(b => {
            b.onclick = async () => {
                if (!confirm(T('undo_confirm'))) return;
                const r = await jpost('/api/collab/revert', { rev: parseInt(b.dataset.rev, 10) });
                if (r.ok) {
                    try { if (typeof notify === 'function') notify(T('reverted', { n: r.reverted })); } catch (e) { /* ok */ }
                    fullRefresh();
                } else setMsg(T('revert_fail', { msg: r.error || r._status }));
            };
        });
    }
    // смена выбранного объекта уходит сразу (а не со следующим poll) — другие видят подсветку без задержки
    let lastSel;
    setInterval(() => {
        if (!S.joined) return;
        const s = curSel();
        if (s !== lastSel) { lastSel = s; fetch('/api/collab/ping' + (s !== null ? '?sel=' + s : '')).catch(() => { /* ok */ }); }
    }, 500);
    // время в ленте «тикает» без новых правок
    setInterval(() => { if (panel.classList.contains('open') && S.joined) renderFeed(); }, 30000);

    // ---------- кнопка в верхней панели ----------
    let badge = null;
    function updateBadge() {
        if (!badge) return;
        const n = S.joined ? S.peers.length : 0;
        badge.style.display = n > 1 ? 'block' : 'none';
        badge.textContent = n;
    }
    const bar = document.getElementById('toolbar-top');
    if (bar) {
        const b = document.createElement('button');
        b.className = 'purple';
        b.id = 'co-btn';
        b.textContent = '👥';
        b.title = T('btn_title');
        badge = document.createElement('span');
        badge.id = 'co-badge';
        b.appendChild(badge);
        b.onclick = () => {
            panel.classList.toggle('open');
            if (panel.classList.contains('open')) { mode = ''; refreshStatus(); }
        };
        bar.appendChild(b);
    }

    renderAll();
    refreshStatus();   // если комната уже идёт (страницу перезагрузили) — тихо входим обратно
})();
