// ИИ-ассистент / AI assistant: панель чата в стиле редактора (палитра #111827/#1f2937/#374151/#3b82f6,
// масштабы --fs/--bs). Самодостаточный файл: сам добавляет кнопку «🤖 AI» в верхнюю панель
// и свои стили. Бэкенд — /api/assistant/* в app.py (любой OpenAI-совместимый провайдер,
// ключ хранится на сервере). Язык (en/ru) берётся из редактора (LANG), иначе из браузера.
(function () {
    'use strict';

    const DICT = {
        en: {
            title: '🤖 Assistant', btn_title: 'AI assistant', settings: 'Settings', clear: 'Clear chat', close: 'Close',
            provider: 'Provider', url_aria: 'API address', url_ph: 'API address (…/v1)',
            key_ph: 'API key (not needed for Ollama)', key_saved_ph: 'Key saved (enter a new one to replace it)',
            model_aria: 'Model', model_ph: 'Model', list: 'List', save: 'Save', clrkey: 'Remove key',
            saved: 'Saved', key_removed: 'Key removed', error: 'Error', no_model: 'no model selected',
            loading_models: 'Loading model list…', models_n: 'Models: {n}. Start typing the name in the “Model” field.',
            models_fail: 'Failed: {msg}', no_server: 'Could not reach the server: {msg}',
            ctx: 'Send the selected object and the open script', input_ph: 'Ask about a script or an object…', send: 'Send',
            empty: 'Ask about the open script or the selected object. The assistant sees them while the checkbox below is on.',
            copy: 'copy', copied: 'copied', err_prefix: 'Error: {msg}', empty_reply: '(empty reply — try another model)', thinking: '💭 thinking…', patch_prep: '⚙ preparing patch…',
            ctx_obj: 'Selected object: ref={ref}, {name} ({cls}), properties: {props}', ctx_script: 'Open script {name} ({cls}):',
            ctx_scene: 'Workspace objects (ref: name, class):',
            auto: 'Apply scene changes automatically', act_title: 'Scene changes', act_prep: '⚙ preparing scene changes…',
            act_apply: 'Apply', act_undo: 'Undo', act_applied: '✓ Applied: {n}', act_reverted: '↩ Reverted', act_failed: '✕ Failed: {msg}',
            act_wait: 'Needs your confirmation (it deletes objects).', act_bad_json: 'Could not read the actions block: {msg}',
            act_no_ref: 'object ref={ref} not found', act_bad: 'invalid action: {what}', act_protected: 'cannot delete a service or system object',
            act_set: '{name} [{ref}]: {prop} → {val}', act_create: '+ {cls} “{name}”', act_delete: '✕ delete {name} [{ref}]',
            custom_addr: 'Custom address', ollama: 'Ollama (local)', lines: 'lines',
            q1: 'Explain the script', q1p: 'Explain what the open script does, step by step.',
            q2: 'Find the bug', q2p: 'Find bugs in the open script and show the fixed code.',
            q3: 'Simplify the code', q3p: 'Simplify and optimize the open script and explain what you changed.'
        },
        ru: {
            title: '🤖 Ассистент', btn_title: 'ИИ-ассистент', settings: 'Настройки', clear: 'Очистить чат', close: 'Закрыть',
            provider: 'Провайдер', url_aria: 'Адрес API', url_ph: 'Адрес API (…/v1)',
            key_ph: 'API-ключ (не нужен для Ollama)', key_saved_ph: 'Ключ сохранён (введи новый, чтобы заменить)',
            model_aria: 'Модель', model_ph: 'Модель', list: 'Список', save: 'Сохранить', clrkey: 'Удалить ключ',
            saved: 'Сохранено', key_removed: 'Ключ удалён', error: 'Ошибка', no_model: 'модель не выбрана',
            loading_models: 'Загружаю список моделей…', models_n: 'Моделей: {n}. Начни вводить название в поле «Модель».',
            models_fail: 'Не получилось: {msg}', no_server: 'Не удалось связаться с сервером: {msg}',
            ctx: 'Передавать выбранный объект и открытый скрипт', input_ph: 'Спроси про скрипт или объект…', send: 'Отправить',
            empty: 'Спроси про открытый скрипт или выбранный объект. Ассистент видит их, пока включена галочка внизу.',
            copy: 'копировать', copied: 'скопировано', err_prefix: 'Ошибка: {msg}', empty_reply: '(пустой ответ — попробуй другую модель)', thinking: '💭 думаю…', patch_prep: '⚙ формирую патч…',
            ctx_obj: 'Выбран объект: ref={ref}, {name} ({cls}), свойства: {props}', ctx_script: 'Открыт скрипт {name} ({cls}):',
            ctx_scene: 'Объекты Workspace (ref: имя, класс):',
            auto: 'Применять изменения сцены автоматически', act_title: 'Изменения сцены', act_prep: '⚙ готовлю изменения сцены…',
            act_apply: 'Применить', act_undo: 'Отменить', act_applied: '✓ Применено: {n}', act_reverted: '↩ Отменено',
            act_failed: '✕ Не получилось: {msg}', act_wait: 'Нужно твоё подтверждение (удаляются объекты).',
            act_bad_json: 'Не удалось прочитать блок действий: {msg}',
            act_no_ref: 'объект ref={ref} не найден', act_bad: 'некорректное действие: {what}', act_protected: 'нельзя удалять сервисы и системные объекты',
            act_set: '{name} [{ref}]: {prop} → {val}', act_create: '+ {cls} «{name}»', act_delete: '✕ удалить {name} [{ref}]',
            custom_addr: 'Свой адрес', ollama: 'Ollama (локально)', lines: 'строк',
            q1: 'Объясни скрипт', q1p: 'Объясни, что делает открытый скрипт, по шагам.',
            q2: 'Найди ошибку', q2p: 'Найди ошибки в открытом скрипте и покажи исправленный код.',
            q3: 'Упрости код', q3p: 'Упрости и оптимизируй открытый скрипт, объясни что изменил.'
        }
    };
    const L = (() => {
        try { if (typeof LANG !== 'undefined' && DICT[LANG]) return LANG; } catch (e) { /* LANG ещё не объявлен */ }
        return /^ru/i.test(navigator.language || '') ? 'ru' : 'en';
    })();
    const T = (k, v) => {
        let s = (DICT[L][k] != null) ? DICT[L][k] : (DICT.en[k] != null ? DICT.en[k] : k);
        if (v) for (const x in v) s = s.split('{' + x + '}').join(v[x]);
        return s;
    };
    const HDR = { 'X-Lang': L };

    const PRESETS = [
        ['OpenRouter', 'https://openrouter.ai/api/v1'],
        ['Groq', 'https://api.groq.com/openai/v1'],
        ['Mistral', 'https://api.mistral.ai/v1'],
        [T('ollama'), 'http://localhost:11434/v1'],
        ['Polza.ai', 'https://polza.ai/api/v1'],
        [T('custom_addr'), '']
    ];
    const QUICK = [[T('q1'), T('q1p')], [T('q2'), T('q2p')], [T('q3'), T('q3p')]];

    const css = `
#ai-panel{--f:calc(13px*var(--fs,1));--b:calc(30px*var(--bs,1));position:fixed;right:12px;bottom:12px;width:400px;max-width:calc(100vw - 24px);
 height:62vh;max-height:calc(100vh - 64px);background:#1f2937;color:#fff;border:1px solid #374151;border-radius:8px;display:none;
 flex-direction:column;z-index:9000;box-shadow:0 8px 28px rgba(0,0,0,.55);font:var(--f)/1.45 system-ui,sans-serif;overflow:hidden}
#ai-panel.open{display:flex}
#ai-panel *{box-sizing:border-box}
#ai-panel button,#ai-panel input,#ai-panel select,#ai-panel textarea{font:inherit;color:#fff}
#ai-panel button{background:#374151;border:none;border-radius:4px;padding:0 10px;min-height:var(--b);cursor:pointer}
#ai-panel button:hover{background:#4b5563}
#ai-panel :focus-visible{outline:2px solid #3b82f6;outline-offset:1px}
#ai-head{display:flex;align-items:center;gap:6px;padding:6px 8px;border-bottom:1px solid #374151;background:#111827}
#ai-head strong{flex:1;font-size:calc(14px*var(--fs,1))}
#ai-chip{font:calc(11px*var(--fs,1)) ui-monospace,Consolas,monospace;background:#1e3a5f;color:#93c5fd;padding:2px 8px;border-radius:99px;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#ai-head button{padding:0 8px}
#ai-settings{display:none;flex-direction:column;gap:6px;padding:8px;border-bottom:1px solid #374151;background:#111827}
#ai-settings.open{display:flex}
#ai-settings{flex:none;max-height:42%;overflow-y:auto}
#ai-settings.open~#ai-chips{display:none!important}
#ai-head,#ai-chips,#ai-foot{flex:none}
#ai-settings input,#ai-settings select{width:100%;background:#374151;border:1px solid #4b5563;border-radius:4px;padding:6px 8px;outline:none;min-height:var(--b)}
#ai-settings .row{display:flex;gap:6px}#ai-settings .row>input{flex:1}
#ai-save{background:#3b82f6!important}#ai-save:hover{background:#2563eb!important}
#ai-note{font-size:calc(11px*var(--fs,1));color:#9ca3af;min-height:1.3em}
#ai-msgs{flex:1;min-height:0;overflow-y:auto;padding:10px;display:flex;flex-direction:column;gap:8px}
.ai-empty{margin:auto;text-align:center;color:#9ca3af;max-width:260px}
.ai-m{padding:7px 10px;border-radius:8px;white-space:pre-wrap;word-break:break-word;user-select:text}
.ai-m.user{background:#1e3a5f;align-self:flex-end;max-width:92%;border-bottom-right-radius:3px}
.ai-m.assistant{background:#111827;border:1px solid #374151;align-self:flex-start;max-width:100%;border-bottom-left-radius:3px}
.ai-m.err{background:#7f1d1d;border-color:#7f1d1d}
.ai-m code{font:calc(12px*var(--fs,1)) 'Fira Code',Consolas,monospace;background:#374151;padding:0 4px;border-radius:3px}
.ai-m pre{position:relative;margin:6px 0 2px;padding:26px 10px 9px;background:#0f172a;border:1px solid #374151;border-radius:6px;overflow-x:auto;white-space:pre;font:calc(12px*var(--fs,1))/1.55 'Fira Code',Consolas,monospace}
.ai-m pre code{background:none;padding:0}\n.ai-modlist{flex:none;min-height:40px;max-height:180px;overflow-y:auto;border:1px solid #374151;border-radius:6px;background:#111827;margin:4px 0}.ai-modlist[hidden]{display:none}.ai-mod{padding:8px 10px;font-size:13px;border-bottom:1px solid #1f2937;word-break:break-all;cursor:pointer}.ai-mod:active{background:#1d4ed8}\n.ai-m .ai-h{display:block;margin-top:4px;color:#93c5fd}.ai-m a{color:#60a5fa}.ai-m hr{border:0;border-top:1px solid #374151;margin:6px 0}
.ai-m pre .ai-copy{position:absolute;top:4px;right:4px;font-size:calc(11px*var(--fs,1));min-height:0;padding:1px 7px}
.ai-caret::after{content:"";display:inline-block;width:7px;height:1em;background:#3b82f6;margin-left:2px;vertical-align:-2px;animation:ai-b 1s steps(2) infinite}
@keyframes ai-b{50%{opacity:0}}
.ai-actmark{color:#9ca3af;font-style:italic;margin:4px 0}
.ai-act{margin-top:8px;padding:8px;background:#0f172a;border:1px solid #374151;border-radius:6px;white-space:normal}
.ai-act h5{margin:0 0 4px;font-size:calc(12px*var(--fs,1));color:#93c5fd}
.ai-act ul{margin:0 0 6px;padding-left:18px}.ai-act li{margin:1px 0;font:calc(12px*var(--fs,1)) 'Fira Code',Consolas,monospace}
.ai-act .row{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.ai-act .st{font-size:calc(11px*var(--fs,1));color:#9ca3af}.ai-act .st.ok{color:#6ee7b7}.ai-act .st.bad{color:#fca5a5}
#ai-chips{display:flex;gap:6px;padding:0 10px 8px;overflow-x:auto}
#ai-chips button{background:#111827;border:1px solid #374151;border-radius:99px;color:#9ca3af;white-space:nowrap;min-height:calc(26px*var(--bs,1))}
#ai-chips button:hover{color:#93c5fd;border-color:#3b82f6;background:#111827}
#ai-foot{display:flex;flex-direction:column;gap:5px;padding:8px;border-top:1px solid #374151;background:#111827}
#ai-foot label{display:flex;gap:6px;align-items:center;font-size:calc(11px*var(--fs,1));color:#9ca3af}
#ai-foot .row{display:flex;gap:6px}
#ai-input{flex:1;background:#374151;border:1px solid #4b5563;border-radius:6px;padding:6px 8px;resize:none;height:calc(50px*var(--bs,1));outline:none}
#ai-input::placeholder{color:#9ca3af}
#ai-send{background:#3b82f6!important;font-weight:700;padding:0 14px!important}#ai-send:hover{background:#2563eb!important}
@media (max-width:700px) and (min-height:561px){
#ai-panel{left:0;right:0;bottom:0;width:auto;max-width:none;height:60vh;max-height:none;border-radius:8px 8px 0 0;border-width:1px 0 0}}
@media (max-height:560px){
#ai-panel{top:44px;bottom:0;right:0;left:auto;height:auto;max-height:none;width:min(48%,420px);border-radius:0;border-width:0 0 0 1px}
#ai-input{height:calc(36px*var(--bs,1))}#ai-foot{padding:6px 8px}#ai-chips{padding-bottom:6px}}
@media (prefers-reduced-motion:reduce){.ai-caret::after{animation:none}}
`;
    const st = document.createElement('style');
    st.textContent = css;
    document.head.appendChild(st);

    const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const $ = id => document.getElementById(id);
    const history = [];
    let busy = false;

    const panel = document.createElement('div');
    panel.id = 'ai-panel';
    panel.setAttribute('aria-label', T('title').replace('🤖 ', ''));
    panel.innerHTML = `
<div id="ai-head"><strong>${esc(T('title'))}</strong><span id="ai-chip"></span><button id="ai-gear" title="${esc(T('settings'))}" aria-expanded="false">⚙</button><button id="ai-clear" title="${esc(T('clear'))}">🗑</button><button id="ai-close" title="${esc(T('close'))}">✕</button></div>
<div id="ai-settings">
  <select id="ai-preset" aria-label="${esc(T('provider'))}">${PRESETS.map((p, i) => `<option value="${i}">${esc(p[0])}</option>`).join('')}</select>
  <input id="ai-url" aria-label="${esc(T('url_aria'))}" placeholder="${esc(T('url_ph'))}">
  <input id="ai-key" type="password" placeholder="${esc(T('key_ph'))}" autocomplete="off">
  <div class="row"><input id="ai-model" autocomplete="off" aria-label="${esc(T('model_aria'))}" placeholder="${esc(T('model_ph'))}"><button id="ai-load">${esc(T('list'))}</button></div>
  <div id="ai-modlist" class="ai-modlist" hidden></div>
  <div class="row"><button id="ai-save">${esc(T('save'))}</button><button id="ai-clrkey">${esc(T('clrkey'))}</button></div>
  <div id="ai-note"></div>
</div>
<div id="ai-msgs" aria-live="polite"></div>
<div id="ai-chips">${QUICK.map((q, i) => `<button type="button" data-q="${i}">${esc(q[0])}</button>`).join('')}</div>
<div id="ai-foot">
  <label><input type="checkbox" id="ai-ctx" checked> ${esc(T('ctx'))}</label>
  <label><input type="checkbox" id="ai-auto" checked> ${esc(T('auto'))}</label>
  <div class="row"><textarea id="ai-input" placeholder="${esc(T('input_ph'))}"></textarea><button id="ai-send" aria-label="${esc(T('send'))}">▶</button></div>
</div>`;
    document.body.appendChild(panel);

    const setNote = t => { $('ai-note').textContent = t || ''; };
    const setChip = m => { $('ai-chip').textContent = m || T('no_model'); };
    const jget = async url => (await fetch(url, { headers: HDR })).json();
    const jpost = async (url, body) => (await fetch(url, { method: 'POST', headers: Object.assign({ 'Content-Type': 'application/json' }, HDR), body: JSON.stringify(body) })).json();

    function showEmpty() {
        $('ai-msgs').innerHTML = '<div class="ai-empty">' + esc(T('empty')) + '</div>';
        $('ai-chips').style.display = '';
    }

    async function loadCfg() {
        try {
            const c = await jget('/api/assistant/config');
            if (!c.ok) { setNote(c.error || T('error')); return; }
            $('ai-url').value = c.base_url;
            $('ai-model').value = c.model;
            setChip(c.model);
            $('ai-key').value = '';
            $('ai-key').placeholder = c.has_key ? T('key_saved_ph') : T('key_ph');
            const idx = PRESETS.findIndex(p => p[1] === c.base_url);
            $('ai-preset').value = String(idx >= 0 ? idx : PRESETS.length - 1);
            if (!c.model) { $('ai-settings').classList.add('open'); $('ai-gear').setAttribute('aria-expanded', 'true'); }
        } catch (e) { setNote(T('no_server', { msg: e })); }
    }

    // Форматирование: ``` блоки -> <pre>, `код` -> <code>, **жирный**, *курсив*, # заголовки, списки, [текст](http…)
    function inline(t) {
        return t.split('`').map((x, i) => {
            if (i % 2) return '<code>' + esc(x) + '</code>';
            return esc(x)
                .replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>')
                .replace(/(^|[\s(])\*([^*\s][^*\n]*?)\*(?=$|[\s).,!?:;])/g, '$1<i>$2</i>')
                .replace(/\[([^\]\n]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
        }).join('');
    }
    function fmtText(p) {
        return p.split('\n').filter(l => !/^\s*(User|Response) Safety:\s*\w+\s*$/i.test(l)).map(line => {
            let m;
            if ((m = /^\s{0,3}#{1,6}\s+(.*)$/.exec(line))) return '<b class="ai-h">' + inline(m[1]) + '</b>';
            if ((m = /^(\s*)[-*•]\s+(.*)$/.exec(line))) return m[1] + '• ' + inline(m[2]);
            if (/^\s*([-*_])\1{2,}\s*$/.test(line)) return '<hr>';
            return inline(line);
        }).join('\n');
    }
    function fmt(text) {
        return String(text).split('```').map((p, i) => {
            if (i % 2 === 0) return fmtText(p);
            if (isActBlock(p)) return '<div class="ai-actmark">' + esc(T('act_prep')) + '</div>';
            const code = p.replace(/^[a-zA-Z0-9_+-]*\n/, '').replace(/\n$/, '');
            return '<pre><button type="button" class="ai-copy">' + esc(T('copy')) + '</button>' + esc(code) + '</pre>';
        }).join('');
    }

    function addMsg(role, text, cls) {
        const e = $('ai-msgs').querySelector('.ai-empty');
        if (e) e.remove();
        const d = document.createElement('div');
        d.className = 'ai-m ' + role + (cls ? ' ' + cls : '');
        if (role === 'assistant' && !cls) d.innerHTML = fmt(text); else d.textContent = text;
        $('ai-msgs').appendChild(d);
        $('ai-msgs').scrollTop = $('ai-msgs').scrollHeight;
        return d;
    }

    const CTX_PROPS = ['Position', 'Rotation', 'Size', 'Transparency', 'Reflectance', 'Anchored', 'CanCollide', 'CastShadow'];
    function ctxProps(props) {
        const o = {};
        CTX_PROPS.forEach(k => { if (props && props[k] !== undefined) o[k] = props[k]; });
        const c8 = props && props.Color3uint8, c = props && (props.Color || props.Color3);
        if (c8 && typeof c8 === 'object' && 'r' in c8) o.Color = { r: Math.round(c8.r), g: Math.round(c8.g), b: Math.round(c8.b) };
        else if (c && typeof c === 'object' && 'r' in c) o.Color = { r: Math.round(c.r * 255), g: Math.round(c.g * 255), b: Math.round(c.b * 255) };
        return JSON.stringify(o);
    }
    function sceneSummary() {
        const out = [];
        try {
            const SKIP = ['Terrain', 'Camera'];
            const walk = (nodes, depth) => {
                let shown = 0;
                for (const n of nodes || []) {
                    if (SKIP.includes(n.cls)) continue;
                    if (out.length >= 150) return;
                    if (shown++ >= 25) { out.push('  '.repeat(depth) + '… (+' + (nodes.length - 25) + ')'); return; }
                    out.push('  '.repeat(depth) + n.ref + ': ' + n.name + ' (' + n.cls + ')');
                    if (depth < 3) walk(n.children, depth + 1);
                }
            };
            for (const root of (typeof treeData !== 'undefined' ? treeData : [])) {
                if (!(root.children || []).length && root.cls !== 'Workspace') continue;
                out.push(root.ref + ': ' + root.name + ' (' + root.cls + ')');
                walk(root.children, 1);
            }
        } catch (e) { /* дерево ещё не загружено */ }
        return out.length ? T('ctx_scene') + '\n' + out.join('\n') : '';
    }

    async function buildContext() {
        if (!$('ai-ctx').checked) return '';
        const out = [];
        try {
            const refs = [];
            if (typeof selectedRefs !== 'undefined' && selectedRefs && selectedRefs.size) refs.push(...Array.from(selectedRefs).slice(0, 5));
            else if (typeof selectedRef !== 'undefined' && selectedRef !== null) refs.push(selectedRef);
            for (const ref of refs) {
                const r = await (await fetch('/api/instance/' + ref)).json();
                if (r.ok) out.push(T('ctx_obj', { ref: ref, name: (r.props && r.props.Name) || '?', cls: r.cls, props: ctxProps(r.props) }));
            }
            if (typeof currentScriptRef !== 'undefined' && currentScriptRef !== null) {
                const r = await (await fetch('/api/instance/' + currentScriptRef)).json();
                if (r.ok && r.props) {
                    let src = r.props.Source || '';
                    if (typeof cmEditor !== 'undefined' && cmEditor && typeof cmEditor.getValue === 'function') src = cmEditor.getValue();
                    out.push(T('ctx_script', { name: r.props.Name || '?', cls: r.cls }) + '\n' + src.slice(0, 12000));
                }
            }
            const sc = sceneSummary();
            if (sc) out.push(sc);
        } catch (e) { /* контекст необязателен */ }
        return out.join('\n\n');
    }

    // ===== Действия над сценой: ассистент присылает блок ```rbx-actions с JSON-массивом =====
    const ACT_PROPS = { Position: 'v3', Rotation: 'v3', Size: 'size', Color: 'color', Transparency: 'unit', Reflectance: 'unit',
        Anchored: 'bool', CanCollide: 'bool', CastShadow: 'bool', Name: 'str', Source: 'src' };
    const SCRIPT_CLASSES = ['Script', 'LocalScript', 'ModuleScript'];
    const ACT_CLASSES = ['Part', 'WedgePart', 'SpherePart', 'CornerWedgePart', 'SpawnLocation', 'Folder', 'Model'].concat(SCRIPT_CLASSES);
    const PROTECTED = ['Terrain', 'Camera'];
    const bad = what => new Error(T('act_bad', { what: what }));
    const num = (x, lo, hi, what) => { const f = Number(x); if (!isFinite(f)) throw bad(what); return Math.max(lo, Math.min(hi, f)); };

    function normVal(kind, v, what) {
        if (kind === 'v3' || kind === 'size') {
            let o = v;
            if (typeof v === 'string') { const m = v.match(/-?\d+(?:\.\d+)?(?:e-?\d+)?/gi); o = (m && m.length >= 3) ? m : null; }
            if (Array.isArray(o)) o = { x: o[0], y: o[1], z: o[2] };
            else if (o && typeof o === 'object' && !('x' in o) && 'X' in o) o = { x: o.X, y: o.Y, z: o.Z };
            if (!o || typeof o !== 'object') throw bad(what);
            const lo = kind === 'size' ? 0.05 : -100000, hi = kind === 'size' ? 2048 : 100000;
            return { x: num(o.x, lo, hi, what), y: num(o.y, lo, hi, what), z: num(o.z, lo, hi, what) };
        }
        if (kind === 'color') {
            if (typeof v === 'string' && /^#?[0-9a-f]{6}$/i.test(v)) {
                const h = v.replace('#', '');
                return { r: parseInt(h.slice(0, 2), 16), g: parseInt(h.slice(2, 4), 16), b: parseInt(h.slice(4, 6), 16) };
            }
            if (!v || typeof v !== 'object') throw bad(what);
            return { r: Math.round(num(v.r, 0, 255, what)), g: Math.round(num(v.g, 0, 255, what)), b: Math.round(num(v.b, 0, 255, what)) };
        }
        if (kind === 'unit') return num(v, 0, 1, what);
        if (kind === 'bool') { if (typeof v !== 'boolean') throw bad(what); return v; }
        if (kind === 'src') { if (typeof v !== 'string') throw bad(what); return v.slice(0, 200000); }
        if (kind === 'str') { if (typeof v !== 'string' || !v.trim()) throw bad(what); return v.slice(0, 100); }
        throw bad(what);
    }
    const aapi = (method, url, body) => (typeof api === 'function') ? api(method, url, body)
        : fetch(url, { method: method, headers: { 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined }).then(r => r.json());
    const postProp = (ref, prop, value) => aapi('POST', '/api/instance/' + ref, { prop: prop, value: value });
    const nodeName = ref => { try { const n = treeByRef[ref]; return (n && n.name) || String(ref); } catch (e) { return String(ref); } };
    const isRoot = ref => { try { return treeData.some(n => n.ref === ref); } catch (e) { return false; } };
    const fmtVal = v => (typeof v === 'string' && v.length > 40) ? v.slice(0, 37).replace(/\n/g, ' ') + '…' : (v && typeof v === 'object') ? Object.keys(v).map(k => +(+v[k]).toFixed(2)).join(', ') : String(v);

    // Бесплатные модели часто забывают метку rbx-actions (пишут ```json, ``` или голый массив) — принимаем всё,
    // что парсится в массив объектов с полем "op".
    function _actList(src) {
        try {
            const j = JSON.parse(src.trim());
            const arr = Array.isArray(j) ? j : [j];
            return arr.length && arr.every(a => a && typeof a === 'object' && typeof a.op === 'string') ? arr : null;
        } catch (e) { return null; }
    }
    function isActBlock(p) {
        if (/^rbx-actions\b/.test(p)) return true;
        return !!_actList(p.replace(/^[a-zA-Z0-9_+-]*[ \t]*\n/, ''));
    }
    function parseActions(text) {
        const list = []; let err = null;
        const parts = String(text).split('```');
        for (let i = 1; i < parts.length; i += 2) {
            const body = parts[i].replace(/^[a-zA-Z0-9_+-]*[ \t]*\n/, '');
            if (/^rbx-actions\b/.test(parts[i])) {
                try { const j = JSON.parse(body); (Array.isArray(j) ? j : [j]).forEach(a => list.push(a)); }
                catch (e) { err = e.message; }
            } else { const l = _actList(body); if (l) l.forEach(a => list.push(a)); }
        }
        if (!list.length && err === null) {   // голый JSON-массив вне fence
            const m = /\[\s*\{\s*"op"[\s\S]*\}\s*\]/.exec(parts.filter((x, i) => i % 2 === 0).join('\n'));
            const l = m && _actList(m[0]); if (l) l.forEach(a => list.push(a));
        }
        return { list: list.slice(0, 30), err: err, found: list.length > 0 || err !== null };
    }

    function describe(a) {
        try {
            if (a.op === 'set') return T('act_set', { name: nodeName(+a.ref), ref: a.ref, prop: a.prop, val: fmtVal(a.value) });
            if (a.op === 'create') return T('act_create', { cls: a.class || 'Part', name: a.name || a.class || 'Part' }) + ((a.source || (a.props && a.props.Source)) ? ' (' + String(a.source || a.props.Source).split('\n').length + ' ' + T('lines') + ')' : '');
            if (a.op === 'move') return '→ ' + nodeName(+a.ref) + ' [' + a.ref + '] ⇒ ' + (a.parent !== undefined ? (isFinite(+a.parent) ? nodeName(+a.parent) : a.parent) : '?');
            if (a.op === 'delete') return T('act_delete', { name: nodeName(+a.ref), ref: a.ref });
        } catch (e) { /* ниже общий вариант */ }
        return JSON.stringify(a).slice(0, 80);
    }

    async function exists(ref) {
        const r = await aapi('GET', '/api/instance/' + ref);
        if (!r || !r.ok || r.cls === '?') throw new Error(T('act_no_ref', { ref: ref }));
        return r;
    }

    async function doSet(a, undo, touched) {
        const ref = parseInt(a.ref, 10);
        if (!(a.prop in ACT_PROPS)) throw bad(String(a.prop));
        const info = await exists(ref);
        const val = normVal(ACT_PROPS[a.prop], a.value, a.prop);
        let prop = a.prop, send = val;
        if (a.prop === 'Color') {
            if (info.props && info.props.Color3uint8 && typeof info.props.Color3uint8 === 'object') prop = 'Color3uint8';
            else send = { r: val.r / 255, g: val.g / 255, b: val.b / 255 };
        }
        const old = info.props ? info.props[prop] : undefined;
        await postProp(ref, prop, send);
        if (old !== undefined) undo.push(() => postProp(ref, prop, old));
        touched.add(ref);
    }

    // имена объектов, созданных в текущем пакете (дерево в браузере обновится только после пакета)
    const batch = { names: {}, last: null };
    function resolveParent(x) {
        const n = parseInt(x, 10);
        if (isFinite(n)) return n;
        if (typeof x !== 'string' || !x.trim()) return NaN;
        const want = x.trim().toLowerCase();
        if (batch.names[want] !== undefined) return batch.names[want];
        let hit = null;
        const walk = ns => { for (const nd of (ns || [])) { if (!hit && (String(nd.name).toLowerCase() === want || String(nd.cls).toLowerCase() === want)) hit = nd; if (!hit) walk(nd.children); } };
        try { walk(treeData); } catch (e) { /* дерево недоступно */ }
        return hit ? hit.ref : NaN;
    }

    async function doMove(a, undo, touched) {
        const ref = resolveParent(a.ref), parent = resolveParent(a.parent);   // ref/parent: число или имя
        if (!isFinite(ref)) throw bad('ref');
        if (!isFinite(parent)) throw bad('parent');
        const info = await exists(ref); await exists(parent);
        if (isRoot(ref) || PROTECTED.includes(info.cls)) throw new Error(T('act_protected'));
        const r = await aapi('POST', '/api/reparent', { refs: [ref], parent: parent });
        if (!r || !r.ok) throw new Error((r && r.error) || 'reparent failed');
        if (isFinite(info.parent) && info.parent >= 0) undo.push(() => aapi('POST', '/api/reparent', { refs: [ref], parent: info.parent }));
        touched.add(ref);
    }

    async function doCreate(a, undo, touched, made) {
        const cls = String(a.class || 'Part');
        if (!ACT_CLASSES.includes(cls)) throw bad(cls);
        const name = (typeof a.name === 'string' && a.name.trim()) ? a.name.slice(0, 100) : cls;
        const p = a.props || {}, body = { class: cls, name: name };
        let parent = resolveParent(a.parent);
        if (!isFinite(parent) && cls === 'Script' && batch.last && /script\.Parent/.test(String(a.source || p.Source || ''))) parent = batch.last;   // скрипт управляет объектом через script.Parent — кладём внутрь
        if (!isFinite(parent)) {
            const roots = (typeof treeData !== 'undefined' ? treeData : []);
            const root = c => roots.find(n => n.cls === c);
            let def = root('Workspace');
            if (SCRIPT_CLASSES.includes(cls)) def = (cls === 'LocalScript' ? root('StarterPlayer') : null) || root('ServerScriptService') || def;
            if (cls === 'LocalScript' && def && def.cls === 'StarterPlayer') def = (def.children || []).find(n => n.cls === 'StarterPlayerScripts') || def;
            parent = def ? def.ref : -1;
        } else await exists(parent);
        body.parent = parent;
        const extra = [];
        if (typeof a.source === 'string' && !('Source' in p)) p.Source = a.source;
        for (const k in p) {
            if (k === 'Name' && typeof p[k] === 'string' && p[k].trim()) { body.name = p[k].slice(0, 100); continue; }
            if (!(k in ACT_PROPS) || k === 'Name') continue;   // неподдерживаемое свойство (Material и т.п.) пропускаем, не валим весь пакет
            const v = normVal(ACT_PROPS[k], p[k], k);
            if (k === 'Position') { body.px = v.x; body.py = v.y; body.pz = v.z; }
            else if (k === 'Size') { body.sx = v.x; body.sy = v.y; body.sz = v.z; }
            else if (k === 'Color') body.color = { r: v.r / 255, g: v.g / 255, b: v.b / 255 };
            else if (k === 'Anchored') body.anchored = v;
            else if (k === 'CanCollide') body.cancollide = v;
            else if (k === 'Source' && !SCRIPT_CLASSES.includes(cls)) continue;
            else extra.push([k, v]);
        }
        const r = await aapi('PUT', '/api/instance', body);
        if (!r || !r.ok) throw new Error((r && r.error) || 'PUT failed');
        for (const [k, v] of extra) await postProp(r.ref, k, v);
        undo.push(() => aapi('DELETE', '/api/instance/' + r.ref));
        made.push(r.ref);
        batch.names[name.toLowerCase()] = r.ref;
        if (!SCRIPT_CLASSES.includes(cls)) batch.last = r.ref;
    }

    async function doDelete(a, touched) {
        const ref = parseInt(a.ref, 10);
        const info = await exists(ref);
        if (isRoot(ref) || PROTECTED.includes(info.cls)) throw new Error(T('act_protected'));
        await aapi('DELETE', '/api/instance/' + ref);
        touched.add(ref);
    }

    async function refreshEditor(made, touched) {
        try {
            if (typeof loadTree === 'function') await loadTree();
            if (made.length && typeof selectRef === 'function') {
                await selectRef(made[0]);
                if (typeof revealRefs === 'function') revealRefs(made, made[0]);
            }
            else if (typeof selectedRef !== 'undefined' && selectedRef !== null && touched.has(selectedRef) && typeof selectRef === 'function') await selectRef(selectedRef);
        } catch (e) { /* интерфейс обновится при следующем действии */ }
    }

    function acc_text_without_block(t) {
        return String(t).replace(/```[a-zA-Z0-9_+-]*[ \t]*\n\s*\[\s*\{\s*"op"[\s\S]*?```/g, '').replace(/\n?\[Патч (применён|отменён)[^\]]*\]/g, '').trim();
    }

    function attachActions(bubble, parsed) {
        const card = document.createElement('div');
        card.className = 'ai-act';
        const acts = parsed.list;
        const hasDelete = acts.some(a => a && a.op === 'delete');
        card.innerHTML = '<h5>' + esc(T('act_title')) + '</h5><ul>' + acts.map(a => '<li>' + esc(describe(a || {})) + '</li>').join('') +
            '</ul><div class="row"><button type="button" class="ai-do"></button><button type="button" class="ai-undo" style="display:none"></button><span class="st"></span></div>';
        const doBtn = card.querySelector('.ai-do'), undoBtn = card.querySelector('.ai-undo'), st = card.querySelector('.st');
        doBtn.textContent = T('act_apply'); undoBtn.textContent = T('act_undo');
        if (parsed.err) { st.textContent = T('act_bad_json', { msg: parsed.err }); st.className = 'st bad'; }
        let undo = [], running = false;

        async function run() {
            if (running) return; running = true; doBtn.disabled = true;
            const touched = new Set(), made = []; let n = 0;
            undo = []; batch.names = {}; batch.last = null;
            try {
                for (const a of acts) {
                    if (!a || typeof a !== 'object') throw bad('?');
                    if (a.op === 'set') await doSet(a, undo, touched);
                    else if (a.op === 'create') await doCreate(a, undo, touched, made);
                    else if (a.op === 'delete') await doDelete(a, touched);
                    else if (a.op === 'move') await doMove(a, undo, touched);
                    else throw bad(String(a.op));
                    n++;
                }
                st.textContent = T('act_applied', { n: n }); st.className = 'st ok';
                if (parsed.entry) parsed.entry.content = acc_text_without_block(parsed.entry.content) + '\n' + patchSummary(acts, made);
            } catch (e) { st.textContent = T('act_failed', { msg: e.message }); st.className = 'st bad'; }
            await refreshEditor(made, touched);
            if (undo.length) undoBtn.style.display = '';
            doBtn.style.display = 'none'; running = false;
            $('ai-msgs').scrollTop = $('ai-msgs').scrollHeight;
        }
        undoBtn.onclick = async () => {
            undoBtn.disabled = true;
            for (const f of undo.reverse()) { try { await f(); } catch (e) { /* пропускаем */ } }
            undo = []; st.textContent = T('act_reverted'); st.className = 'st';
            if (parsed.entry) parsed.entry.content = acc_text_without_block(parsed.entry.content).replace(/\n?\[Патч применён:[^\]]*\]/, '') + '\n[Патч отменён пользователем]';
            undoBtn.style.display = 'none';
            await refreshEditor([], new Set());
        };
        doBtn.onclick = run;
        bubble.querySelectorAll('.ai-actmark').forEach(e => e.remove());
        bubble.appendChild(card);
        if (!acts.length) { doBtn.style.display = 'none'; return; }
        if ($('ai-auto').checked && !hasDelete && !parsed.err) run();
        else if (hasDelete) { st.textContent = T('act_wait'); st.className = 'st'; }
    }

    // Текст для показа во время стрима: убираем пульс \x1f, <think>…</think> и недописанный/сырой блок rbx-actions
    function shown(acc) {
        let t = acc.replace(/\x1f/g, '').replace(/<think>[\s\S]*?(<\/think>|$)/gi, '');
        t = t.replace(/```rbx-actions[\s\S]*?(```|$)/g, '\n' + T('patch_prep') + '\n');
        return t.trim();
    }
    // Сводка выполненного патча для истории: модель видит, что и с какими ref создано
    function patchSummary(acts, made) {
        let mi = 0;
        const parts = acts.map(a => {
            if (!a) return '?';
            if (a.op === 'create') { const r = made[mi++]; return 'create ' + (a.class || 'Part') + ' "' + (a.name || a.class || 'Part') + '"' + (r !== undefined ? ' ref=' + r : ''); }
            if (a.op === 'set') return 'set ref=' + a.ref + ' ' + a.prop;
            if (a.op === 'move') return 'move ref=' + a.ref + ' → ' + a.parent;
            if (a.op === 'delete') return 'delete ref=' + a.ref;
            return String(a.op);
        });
        return '[Патч применён: ' + parts.join('; ').slice(0, 900) + ']';
    }

    async function send(textArg) {
        const text = (textArg != null ? textArg : $('ai-input').value).trim();
        if (!text || busy) return;
        busy = true;
        if (textArg == null) $('ai-input').value = '';
        $('ai-chips').style.display = 'none';
        addMsg('user', text);
        history.push({ role: 'user', content: text });
        const bubble = addMsg('assistant', '');
        bubble.classList.add('ai-caret');
        bubble.textContent = T('thinking');
        let acc = '';
        try {
            for (let attempt = 0; attempt < 2 && !shown(acc); attempt++) {   // бесплатный роутер иногда отдаёт пустой ответ — пробуем ещё раз
                const resp = await fetch('/api/assistant/chat', {
                    method: 'POST', headers: Object.assign({ 'Content-Type': 'application/json' }, HDR),
                    body: JSON.stringify({ messages: history, context: await buildContext() })
                });
                if (!resp.ok || (resp.headers.get('content-type') || '').includes('application/json')) {
                    const j = await resp.json().catch(() => ({}));
                    throw new Error(j.error || ('HTTP ' + resp.status));
                }
                const reader = resp.body.getReader();
                const dec = new TextDecoder('utf-8');
                for (;;) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    acc += dec.decode(value, { stream: true });
                    const vis = shown(acc);
                    bubble.innerHTML = vis ? fmt(vis) : esc(T('thinking'));
                    $('ai-msgs').scrollTop = $('ai-msgs').scrollHeight;
                }
            }
            acc = acc.replace(/\x1f/g, '').replace(/<think>[\s\S]*?(<\/think>|$)/gi, '').trim();
            if (!acc) { bubble.textContent = T('empty_reply'); history.pop(); }
            else {
                bubble.innerHTML = fmt(acc);
                const entry = { role: 'assistant', content: acc };
                history.push(entry);
                const parsed = parseActions(acc);
                parsed.entry = entry;
                if (parsed.found) attachActions(bubble, parsed);
            }
        } catch (e) {
            bubble.className = 'ai-m assistant err';
            bubble.textContent = T('err_prefix', { msg: e.message });
            history.pop();
        } finally { bubble.classList.remove('ai-caret'); busy = false; }
    }

    panel.addEventListener('click', e => {
        if (e.target.classList.contains('ai-copy')) {
            const txt = e.target.parentElement.textContent.slice(e.target.textContent.length);
            if (navigator.clipboard) navigator.clipboard.writeText(txt).catch(() => {});
            e.target.textContent = T('copied');
        }
        const q = e.target.closest('#ai-chips button');
        if (q) send(QUICK[+q.dataset.q][1]);
    });
    // ===== Перетаскивание панели за заголовок (как debug-консоль); позиция запоминается, двойной тап по заголовку — сброс =====
    (function () {
        const head = $('ai-head'), KEY = 'rsw_ai_panel_pos';
        head.style.touchAction = 'none'; head.style.cursor = 'move'; head.title = head.title || '';
        const clamp = (l, t, w, h) => ({
            left: Math.max(0, Math.min(l, window.innerWidth - Math.min(w, window.innerWidth))),
            top: Math.max(0, Math.min(t, window.innerHeight - 40))
        });
        function place(l, t, w, h) {
            const c = clamp(l, t, w, h);
            panel.style.setProperty('left', c.left + 'px'); panel.style.setProperty('top', c.top + 'px');
            panel.style.setProperty('right', 'auto'); panel.style.setProperty('bottom', 'auto');
            panel.style.setProperty('width', Math.min(w, window.innerWidth) + 'px');
            panel.style.setProperty('height', Math.min(h, window.innerHeight - c.top) + 'px');
            panel.style.setProperty('max-width', 'none'); panel.style.setProperty('max-height', 'none');
            return c;
        }
        function reset() {
            ['left', 'top', 'right', 'bottom', 'width', 'height', 'max-width', 'max-height'].forEach(k => panel.style.removeProperty(k));
            try { localStorage.removeItem(KEY); } catch (e) { /* без хранилища */ }
        }
        try {
            const sv = JSON.parse(localStorage.getItem(KEY) || 'null');
            if (sv && [sv.left, sv.top, sv.w, sv.h].every(Number.isFinite)) place(sv.left, sv.top, sv.w, sv.h);
        } catch (e) { /* игнорируем */ }
        let drag = null, lastTap = 0;
        head.addEventListener('pointerdown', e => {
            if (e.target.closest('button, input, select')) return;
            const now = Date.now();
            if (now - lastTap < 350) { reset(); lastTap = 0; return; }
            lastTap = now;
            const r = panel.getBoundingClientRect();
            drag = { x: e.clientX, y: e.clientY, l: r.left, t: r.top, w: r.width, h: r.height, moved: false };
            try { head.setPointerCapture(e.pointerId); } catch (err) { /* не критично */ }
        });
        head.addEventListener('pointermove', e => {
            if (!drag) return;
            const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
            if (!drag.moved && Math.abs(dx) < 4 && Math.abs(dy) < 4) return;
            drag.moved = true;
            place(drag.l + dx, drag.t + dy, drag.w, drag.h);
        });
        const end = () => {
            if (drag && drag.moved) {
                const r = panel.getBoundingClientRect();
                try { localStorage.setItem(KEY, JSON.stringify({ left: r.left, top: r.top, w: r.width, h: r.height })); } catch (e) { /* без хранилища */ }
            }
            drag = null;
        };
        head.addEventListener('pointerup', end); head.addEventListener('pointercancel', end);
        window.addEventListener('resize', () => {
            if (!panel.style.left) return;
            const r = panel.getBoundingClientRect();
            if (r.width) place(r.left, r.top, r.width, r.height);
        });
    })();

    $('ai-close').onclick = () => panel.classList.remove('open');
    $('ai-gear').onclick = () => { const o = $('ai-settings').classList.toggle('open'); $('ai-gear').setAttribute('aria-expanded', o); };
    $('ai-clear').onclick = () => { history.length = 0; showEmpty(); };
    $('ai-send').onclick = () => send();
    $('ai-input').addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
    });
    $('ai-preset').onchange = () => { const p = PRESETS[+$('ai-preset').value]; if (p[1]) $('ai-url').value = p[1]; };
    $('ai-save').onclick = async () => {
        const body = { base_url: $('ai-url').value, model: $('ai-model').value };
        if ($('ai-key').value.trim()) body.api_key = $('ai-key').value;
        const c = await jpost('/api/assistant/config', body);
        setNote(c.ok ? T('saved') : (c.error || T('error')));
        if (c.ok) loadCfg();
    };
    $('ai-clrkey').onclick = async () => {
        const c = await jpost('/api/assistant/config', { clear_key: true });
        setNote(c.ok ? T('key_removed') : (c.error || T('error')));
        if (c.ok) loadCfg();
    };
    // datalist в Android WebView не раскрывается — свой выпадающий список с фильтром по вводу
    let aiModels = [];
    function renderModList(all) {
        const box = $('ai-modlist'), q = $('ai-model').value.trim().toLowerCase();
        const items = aiModels.filter(m => all || !q || m.toLowerCase().includes(q)).slice(0, 200);
        box.innerHTML = items.map(m => '<div class="ai-mod" data-m="' + esc(m) + '">' + esc(m) + '</div>').join('');
        box.hidden = !items.length;
    }
    $('ai-modlist').addEventListener('click', e => {
        const el = e.target.closest('.ai-mod'); if (!el) return;
        $('ai-model').value = el.dataset.m; $('ai-modlist').hidden = true;
    });
    $('ai-model').addEventListener('focus', () => { if (aiModels.length) renderModList(true); });
    $('ai-model').addEventListener('input', () => { if (aiModels.length) renderModList(false); });

    $('ai-load').onclick = async () => {
        setNote(T('loading_models'));
        // сначала сохраняем адрес/ключ, иначе список придёт от прежнего провайдера
        const body = { base_url: $('ai-url').value };
        if ($('ai-key').value.trim()) body.api_key = $('ai-key').value;
        await jpost('/api/assistant/config', body);
        const r = await jget('/api/assistant/models');
        if (!r.ok) { setNote(T('models_fail', { msg: r.error })); return; }
        aiModels = r.models.slice(); renderModList(true);
        setNote(T('models_n', { n: r.models.length }));
    };

    try { if (localStorage.getItem('rsw_ai_auto') === '0') $('ai-auto').checked = false; } catch (e) { /* без хранилища */ }
    $('ai-auto').onchange = () => { try { localStorage.setItem('rsw_ai_auto', $('ai-auto').checked ? '1' : '0'); } catch (e) { /* без хранилища */ } };

    showEmpty();

    // Кнопка в верхней панели (синяя, как «Account»)
    const bar = document.getElementById('toolbar-top');
    if (bar) {
        const b = document.createElement('button');
        b.className = 'purple';
        b.id = 'ai-btn';
        b.textContent = '🤖 AI';
        b.title = T('btn_title');
        b.onclick = () => { panel.classList.toggle('open'); if (panel.classList.contains('open')) loadCfg(); };
        bar.appendChild(b);
    }
})();
