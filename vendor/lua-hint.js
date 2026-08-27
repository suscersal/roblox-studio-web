/**
 * Roblox Luau autocomplete for CodeMirror 5 + show-hint.
 * Type "pri" → print, pairs, ipairs, ...
 * Triggers on typing (inputRead) and Ctrl-Space.
 */
(function (mod) {
  if (typeof exports === 'object' && typeof module === 'object')
    mod(require('codemirror'));
  else if (typeof define === 'function' && define.amd)
    define(['codemirror'], mod);
  else
    mod(CodeMirror);
})(function (CodeMirror) {
  'use strict';

  var KEYWORDS = [
    // Lua / Luau builtins
    'print', 'warn', 'error', 'assert', 'tick', 'wait', 'require',
    'typeof', 'type', 'pairs', 'ipairs', 'next', 'select', 'unpack',
    'collectgarbage', 'tonumber', 'tostring', 'pcall', 'xpcall',
    'setmetatable', 'getmetatable', 'rawget', 'rawset', 'rawequal',
    'rawlen', 'spawn', 'delay',
    'task', 'task.wait', 'task.spawn', 'task.delay', 'task.cancel', 'task.defer',
    'math', 'math.abs', 'math.ceil', 'math.floor', 'math.max', 'math.min',
    'math.random', 'math.randomseed', 'math.sqrt', 'math.sin', 'math.cos',
    'math.tan', 'math.pi', 'math.huge', 'math.clamp', 'math.sign', 'math.round',
    'math.rad', 'math.deg',
    'table', 'table.insert', 'table.remove', 'table.concat', 'table.sort',
    'table.find', 'table.clear', 'table.clone', 'table.pack', 'table.unpack',
    'string', 'string.find', 'string.format', 'string.gmatch', 'string.gsub',
    'string.len', 'string.lower', 'string.upper', 'string.match', 'string.rep',
    'string.sub', 'string.split', 'string.byte', 'string.char',
    'os', 'os.time', 'os.clock', 'os.date',
    'coroutine', 'coroutine.create', 'coroutine.resume', 'coroutine.yield',
    'coroutine.wrap', 'coroutine.status',

    // keywords
    'and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for', 'function',
    'goto', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat', 'return',
    'then', 'true', 'until', 'while', 'continue',

    // globals
    'game', 'workspace', 'script', 'shared', '_G', 'Enum',

    // services / common
    'Workspace', 'Lighting', 'ReplicatedStorage', 'ReplicatedFirst',
    'ServerScriptService', 'ServerStorage', 'StarterGui', 'StarterPack',
    'StarterPlayer', 'SoundService', 'Players', 'Teams', 'Chat',
    'TextChatService', 'RunService', 'HttpService', 'TweenService',
    'CollectionService', 'UserInputService', 'ContextActionService',
    'MarketplaceService', 'DataStoreService', 'TeleportService',
    'PhysicsService', 'PathfindingService', 'ProximityPromptService',
    'BadgeService', 'InsertService', 'GetService',

    // constructors
    'Instance', 'Instance.new', 'Vector3', 'Vector3.new', 'Vector2', 'Vector2.new',
    'CFrame', 'CFrame.new', 'CFrame.Angles', 'CFrame.lookAt',
    'Color3', 'Color3.new', 'Color3.fromRGB', 'Color3.fromHSV',
    'BrickColor', 'BrickColor.new', 'UDim2', 'UDim2.new', 'UDim2.fromScale',
    'UDim2.fromOffset', 'UDim', 'UDim.new', 'Rect', 'Rect.new', 'Ray', 'Ray.new',
    'Region3', 'Random', 'Random.new', 'NumberSequence', 'ColorSequence',
    'NumberRange', 'TweenInfo', 'TweenInfo.new',

    // classes
    'BasePart', 'Part', 'MeshPart', 'WedgePart', 'CornerWedgePart', 'TrussPart',
    'SpawnLocation', 'Model', 'Folder', 'Humanoid', 'HumanoidDescription',
    'Tool', 'Accessory', 'Weld', 'WeldConstraint', 'Motor6D', 'Attachment',
    'RemoteEvent', 'RemoteFunction', 'BindableEvent', 'BindableFunction',
    'NumberValue', 'StringValue', 'BoolValue', 'IntValue', 'ObjectValue',
    'Vector3Value', 'CFrameValue', 'Color3Value', 'BrickColorValue',
    'ParticleEmitter', 'Fire', 'Smoke', 'Sparkles', 'Explosion', 'Sound',
    'PointLight', 'SpotLight', 'SurfaceLight', 'Camera', 'Animation',
    'ProximityPrompt', 'Highlight', 'SelectionBox',

    // GUI
    'ScreenGui', 'BillboardGui', 'SurfaceGui', 'Frame', 'ScrollingFrame',
    'TextLabel', 'TextButton', 'TextBox', 'ImageLabel', 'ImageButton',
    'UIListLayout', 'UIGridLayout', 'UIPadding', 'UICorner', 'UIStroke',
    'UIGradient',

    // methods / props (часто пишут после точки)
    'FindFirstChild', 'FindFirstChildOfClass', 'FindFirstChildWhichIsA',
    'FindFirstAncestor', 'WaitForChild', 'GetChildren', 'GetDescendants',
    'GetFullName', 'IsA', 'Clone', 'Destroy', 'ClearAllChildren',
    'SetAttribute', 'GetAttribute', 'GetAttributes', 'AddTag', 'RemoveTag',
    'HasTag', 'GetTags', 'GetPropertyChangedSignal', 'GetPivot', 'PivotTo',
    'MoveTo', 'Connect', 'Disconnect', 'Once', 'Wait',
    'Name', 'Parent', 'ClassName', 'Position', 'Orientation', 'Size',
    'Anchored', 'CanCollide', 'Transparency', 'Color', 'BrickColor',
    'Material', 'Text', 'Visible', 'Enabled', 'Value', 'Character', 'UserId',

    // events
    'Changed', 'ChildAdded', 'ChildRemoved', 'Touched', 'TouchEnded',
    'Died', 'MouseButton1Click', 'RenderStepped', 'Stepped', 'Heartbeat',
    'PlayerAdded', 'PlayerRemoving', 'OnServerEvent', 'OnClientEvent',
    'FireServer', 'FireClient', 'FireAllClients', 'InvokeServer'
  ];

  // unique + sorted for stable UI
  var SEEN = Object.create(null);
  var LIST = [];
  for (var i = 0; i < KEYWORDS.length; i++) {
    var k = KEYWORDS[i];
    if (!SEEN[k]) { SEEN[k] = 1; LIST.push(k); }
  }
  LIST.sort();

  function wordBefore(cm) {
    var cur = cm.getCursor();
    var line = cm.getLine(cur.line) || '';
    var before = line.slice(0, cur.ch);
    // слово или цепочка с точками: print / task.wait / Vector3.new
    var m = before.match(/[\w.]+$/);
    if (!m) return { word: '', from: cur, to: cur };
    return {
      word: m[0],
      from: CodeMirror.Pos(cur.line, cur.ch - m[0].length),
      to: cur
    };
  }

  function robloxHint(cm) {
    var w = wordBefore(cm);
    var prefix = w.word.toLowerCase();
    var out = [];
    for (var i = 0; i < LIST.length; i++) {
      var item = LIST[i];
      if (!prefix || item.toLowerCase().indexOf(prefix) !== -1) {
        out.push(item);
        if (out.length >= 50) break;
      }
    }
    // если пусто — не открываем пустой popup
    if (!out.length) return null;
    return { list: out, from: w.from, to: w.to };
  }

  CodeMirror.registerHelper('hint', 'lua', robloxHint);
  CodeMirror.robloxHint = robloxHint;

  /** Вызвать вручную: CodeMirror.showRobloxHint(cmEditor) */
  CodeMirror.showRobloxHint = function (cm) {
    if (!cm || !CodeMirror.showHint) return;
    // Раньше здесь ВСЕГДА использовался встроенный список этого файла
    // (robloxHint/LIST), даже если страница уже настроила cm с более
    // полным словарём через hintOptions.hint (как делает index.html:
    // ROBLOX_LUA_KEYWORDS + robloxSubstringHint). Из-за этого на одном
    // редакторе одновременно жили ДВА независимых источника подсказок —
    // свой inputRead здесь и отдельный ручной обработчик в index.html,
    // каждый со своим списком слов, — и они гонялись друг с другом за
    // каждое нажатие клавиши. На десктопе гонка обычно разрешалась
    // предсказуемо, на телефоне (другой тайминг событий/IME) — нет,
    // поэтому подсказки либо мигали, либо не появлялись вовсе.
    // Используем настроенный на самом cm хинтер, если он есть, и только
    // если нет — свой список по умолчанию (для случаев, когда
    // enableRobloxAutocomplete подключают к редактору без hintOptions).
    var opts = (cm.options && cm.options.hintOptions) || {};
    var hintFn = opts.hint || robloxHint;
    CodeMirror.showHint(cm, hintFn, {
      completeSingle: false,
      closeOnUnfocus: true,
      alignWithWord: true
    });
  };

  /**
   * Подключить авто-показ при наборе букв/точки.
   * Вызвать ОДИН раз после CodeMirror.fromTextArea(...).
   */
  CodeMirror.enableRobloxAutocomplete = function (cm) {
    if (!cm || cm._robloxHintBound) return;
    cm._robloxHintBound = true;

    cm.on('inputRead', function (editor, change) {
      // Раньше здесь была строгая проверка `change.origin !== '+input'` —
      // на Android виртуальная клавиатура (особенно с IME/предиктивным
      // вводом) не всегда помечает событие ровно так же, как обычная
      // клавиатура на десктопе, и проверка молча отфильтровывала ВЕСЬ
      // ввод с телефона — подсказки просто никогда не пытались показаться.
      // Отбрасываем только заведомо не ручной ввод (программную вставку
      // значения через setValue), а не полагаемся на конкретное имя origin.
      if (change.origin === 'setValue') return;
      var t = change.text && change.text.join('');
      if (!t || !/[\w.]/.test(t)) return;
      if (editor.state.completionActive) return;
      CodeMirror.showRobloxHint(editor);
    });

    var map = cm.getOption('extraKeys') || {};
    if (typeof map === 'string') map = {};
    map['Ctrl-Space'] = function (editor) {
      CodeMirror.showRobloxHint(editor);
    };
    cm.setOption('extraKeys', map);
  };
});