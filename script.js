        // ============ МЕТКА СБОРКИ ============
        // Меняйте строку при каждой правке — по ней в Output видно, что WebView
        // загрузил свежий script.js, а не кэш.
        const BUILD_LABEL = '2026-10-29 · door-tween';
        window.BUILD_LABEL = BUILD_LABEL;

        // ============ I18N ============
        const I18N = {
            en: {
                stop_title: 'Stop',
                no_output: '(no output)',
                pub_ver_published: 'Published',
                pub_ver_saved: 'Saved',
                add_search_ph: 'Search class…',
                menu_file: '📁 File',
                menu_new: 'New',
                menu_open_file: 'Open from file…',
                menu_open_roblox: 'Open from Roblox…',
                menu_save: 'Save',
                menu_save_note: 'files only',
                menu_save_as: 'Save as .rbxl…',
                menu_import: 'Import model (.rbxm)…',
                menu_export: 'Export selection (.rbxm)…',
                ui_explorer: 'Explorer',
                ui_properties: 'Properties',
                ui_script_tab: 'Script',
                ui_output: 'Output',
                ui_out_all: 'All',
                ui_out_server: '🖥️ Server',
                ui_out_client: '💻 Client',
                ui_out_filter_title: 'Filter by runtime',
                ui_out_clear: 'Clear',
                tb_view: '👤 View',
                tb_view_title: 'First / third person',
                q_low: 'Low',
                q_med: 'Med',
                q_high: 'High',
                mv_ghost_n: '📦 {n} objects',
                mv_failed: 'Could not move',
                mv_done: 'Moved objects: {n}',
                mv_skipped: ' (skipped {n})',
                mv_none: 'Nothing moved',
                exp_asset_start: 'Exporting {label} {id}…',
                exp_asset_fail: 'Could not fetch asset {id}: {err}',
                exp_asset_fail_http: 'Could not fetch asset {id} (HTTP {status})',
                exp_shared: 'Sent: {name} ({kb} KB)',
                exp_saved: 'Saved: {name} ({kb} KB)',
                exp_error: 'Export error: {msg}',
                exp_generic_err: 'error',
                exp_longpress: 'long press: export file {id}',
                mesh_failed_n: 'Unparsed meshes: {n}',
                mesh_failed_none: 'No unparsed meshes yet (run Play first)',
                exp_assets_start: 'Exporting {n} assets…',
                exp_assets_fail: 'Could not fetch assets: {err}',
                exp_assets_missing: 'Not received: {list}',
                exp_assets_saved: 'Saved: {name} ({kb} KB, assets: {n})',
                av_step_status: 'Asking Roblox for the model status',
                av_step_wait: 'Waiting for Roblox to generate the model',
                av_step_download: 'Downloading obj/mtl/textures',
                av_step_add: 'Adding to the scene',
                av_step_save: 'Choose where to save',
                av_err_empty_geom: 'The model was parsed but the geometry is empty (0 vertices) — Roblox may have changed the OBJ format',
                av_err_scene_not_ready: 'The 3D scene is not ready yet, try again in a second',
                av_err_not_saved: 'The model was added to the viewport only (visually) and was NOT saved as a scene object: no project is open (.rbxl/.rbxlx). Open or create a project file, then import the avatar again.',
                lp_title: 'Sign in to Roblox',
                lp_text: 'Sign in to open your experiences, download places and publish changes right from the app.',
                lp_f1: '📁 All your experiences in one list',
                lp_f2: '⬇ Download places in one tap',
                lp_f3: '☁ Publish from the editor',
                lp_btn: 'Sign in with Roblox',
                lp_later: 'Not now',
                lp_never: 'Don\'t show this again',
                lp_note: 'Your sign-in is stored on this device only.',
                err_3d: '3D: error',
                ui_btn_title: 'Text, button and splitter sizes',
                ui_text: 'Text',
                ui_buttons: 'Buttons and fields',
                ui_splitters: 'Panel splitters',
                ui_scrollbars: 'Scrollbars',
                ui_auto: 'auto',
                ui_reset: 'Reset',
                ui_close: 'Close',
                cam_third: 'Third person',
                cam_first: 'First person (eyes)',
                log_draco_lod0: 'Draco: using LOD0 ({n} of {total} faces)',
                log_play_account: 'Account: {name} (id {id})',
                log_play_guest: 'No Roblox account — default avatar',
                log_play_avatar_ok: 'Player avatar loaded',
                log_play_avatar_fail: 'Could not load player avatar ({msg}) — default avatar',
                log_outfit_applied: 'Costume: {n} item(s) shown on the character',
                warn_sky_failed: 'Could not load the map skybox — using sky color',
                log_mesh_load_failed: 'Mesh {id}: load failed ({msg}), using approximation',
                log_cloth_loaded: 'Clothing: loaded {n} of {total} layer(s)',
                asset_fail_reason: 'Asset {id} did not load: {reason}',
                asset_not_image: 'Asset {id}: the server returned "{type}", not an image',
                asset_decode_failed: 'Asset {id}: the browser could not decode the image ({type})',
                lua_compile_error: 'compile error: ',
                lua_run_aborted: 'Lua run aborted: ',
                lua_scripts_no_reply: '/api/scripts did not respond',
                lua_no_scripts: 'No enabled Script/LocalScript in the map',
                lua_fengari_fail: 'fengari failed to load — check your internet',
                lua_vm_fail_notify: 'Lua VM (fengari) failed to load — check your internet',
                lua_instances_no_reply: '/api/all_instances did not respond',
                notify_editor_unavailable: 'Script editor unavailable (CodeMirror failed to load)',
                confirm_discard_unsaved: 'The current scene (if unsaved) will be replaced with an empty one. Continue?',
                notify_new_scene: 'New Baseplate scene created',
                notify_download_cancelled: 'Download cancelled',
                notify_loading_model: 'Loading model…',
                notify_import_failed: 'Import failed: ',
                notify_import_error: 'Import error',
                notify_import_net: 'Network error during import',
                notify_reading_file: 'Reading file…',
                notify_read_error: 'File read error: ',
                notify_archive_failed: 'Could not read the archive',
                av_net_error: 'Network/server: ',
                av_status_failed: 'Could not request the status',
                av_roblox_failed: 'Roblox could not generate a model for this User ID',
                av_timeout: 'Roblox is taking too long to prepare the model — try again a bit later',
                av_download_error: 'Download error: ',
                av_download_failed: 'Could not download the files',
                av_import_failed: 'Import failed: ',
                av_zip_android: 'Saving .zip is only available in the Android app (in desktop mode the file is already written next to app.py: {path})',
                tb_new: '🆕 New', tb_new_title: 'New scene (Baseplate)',
                tb_open: '📂 Open', tb_open_title: 'Open file (Ctrl+O)',
                tb_save: '💾 Save', tb_save_title: 'Save (Ctrl+S)',
                tb_saveas: '💾 As...', tb_saveas_title: 'Save as',
                tb_import: '📥 Import', tb_import_title: 'Import a model (.rbxm) into the scene',
                tb_export: '📤 Export', tb_export_title: 'Export the selected objects to a model (.rbxm)',
                exp_multisel_title: 'Multi-select mode: tap adds/removes objects (Ctrl+click and Shift+click also work)',
                rbxm_export_title: 'Export {n} object(s) to .rbxm',
                notify_rbxm_exported: '📤 Exported: {n} object(s)',
                notify_rbxm_imported: '📥 Imported: {n} object(s)',
                notify_rbxm_warn: '⚠ {msg}',
                tb_add: '➕ Add', tb_addobj_title: 'Add object',
                tb_delete: '🗑 Delete', tb_delete_title: 'Delete (Delete)',
                tb_refresh: '🔄 Refresh', tb_refresh_title: 'Refresh scene (F5)',
                tb_publish: '☁ Publish', tb_publish_title: 'Publish',
                tb_download: '🏠 Start', tb_download_title: 'Start screen: recent files and your Roblox experiences',
                dl_hint: 'Uses your Roblox sign-in (Account), like Studio. You need edit access to the place or it must be copyable.', cookie_ph: '.ROBLOSECURITY value', cookie_btn: 'Sign in with cookie', cookie_help: 'Desktop sign-in: in your browser, signed in to roblox.com, open DevTools → Application → Cookies → .ROBLOSECURITY and paste the value. Treat it like a password: it gives full account access. It is stored only on this device.', cookie_ok: '✅ Signed in as {name}', cookie_bad: 'Sign-in failed',
                st_new: 'New Experience', st_recents: 'Recents', st_home: 'Home', st_experiences: 'Experiences', st_templates: 'Templates', st_archive: 'Archive', st_recent_h: 'My Recent Experiences', st_tpl_h: 'Open a Template', st_banner_t: 'Pick up where you left off', st_banner_p: 'Open a file, download one of your experiences from Roblox, or start from a template.', st_modified: 'Modified {d}', st_opened: 'Opened {d}', st_local: 'Local', st_refresh: 'Refresh', st_close: 'Close', st_remove: 'Remove from recents?', st_tpl_base: 'Baseplate', st_tpl_empty: 'Empty scene', st_tpl_sub: 'Template', st_menu: 'Remove from recents', st_studio: 'Studio games', st_studio_pill: 'Studio', st_studio_empty: 'The studio game list is empty. Add games to studio_games.json in the repository (groupId or games).', st_studio_group_err: 'Could not load group games: {err}',
                start_title: 'Start', start_welcome: 'Welcome, {name}', start_recent: 'Recent', start_new: 'New scene', start_open: 'Open file…', start_file: 'File', start_roblox: 'Roblox', start_err: 'Could not load your experiences: {err}',
                exp_title: 'My Experiences', exp_loading: 'Loading experiences…', exp_search: 'Search…', exp_empty: 'Nothing found', exp_login_needed: 'Sign in to Roblox first (Account) to see your experiences.', exp_private: 'Private', exp_public: 'Public', exp_by_id: 'By Place ID…', exp_pick_place: 'This experience has several places. Pick one:', pub_origin: 'Opened from Roblox: {name} (Place {id}). IDs are prefilled.',
                dl_title: '⬇ Download place', dl_place: 'Place ID', dl_version: 'Version (optional)', dl_btn: 'Download', dl_discard: 'Unsaved changes in the current scene will be lost. Continue?', dl_ok: '✅ Place loaded: {n} objects', dl_loading: 'Downloading the latest version…',
                tb_account: '👤 Account', tb_account_title: 'Roblox account and Open Cloud API key',
                tb_play: '▶ Play', tb_play_title: 'Run physics simulation',
                tb_resetcam: '🏠 Reset', tb_resetcam_title: 'Reset camera',
                tb_topview: '⬆ Top', tb_topview_title: 'Top view',
                tb_frontview: '📷 Front', tb_frontview_title: 'Front view',
                tb_rightview: '➡ Right', tb_rightview_title: 'Right view',
                tb_teleport: '🎯 Go to', tb_teleport_title: 'Teleport camera to selected object',
                tb_helpers_title: 'Grid and axes',
                tb_resetlayout_title: 'Reset panel sizes',
                exp_collapse_title: 'Collapse all',
                exp_expand_title: 'Expand all',
                exp_search_ph: '🔍 Search...',
                vp_hint: '🖱️ LMB — rotate | 🖱️ RMB — pan | 🖱️ Wheel — render distance<br>⌨️ WASD — move | F — focus | Esc — deselect',
                pad_up_title: 'Up',
                pad_down_title: 'Down',
                pad_jump_title: 'Jump',
                props_placeholder: '← Select an object',
                script_none_selected: 'No script selected',
                script_save_btn: '💾 Save script',
                notify_quality: '🎨 Quality: ',
                notify_layout_reset: '📐 Panel sizes reset',
                notify_camera_reset: '🏠 Camera reset',
                notify_topview: '⬆ Top view',
                notify_frontview: '📷 Front view',
                notify_rightview: '➡ Right view',
                notify_teleport_no_selection: 'Select an object in Explorer first',
                notify_teleported: '🎯 Teleported to selected object',
                notify_stop_play_first: 'Stop Play first, then refresh the scene',
                notify_scene_loaded: '🔄 Scene: {n} objects',
                notify_scene_of: ' (of {total})',
                notify_helpers_on: '📏 Grid and axes: ON',
                notify_helpers_off: '📏 Grid and axes: OFF',
                notify_spawn_not_found: 'SpawnLocation not found in file — spawning near current camera',
                notify_cannon_not_ready: "Cannon.js hasn't loaded yet, wait a second and try again",
                notify_no_geometry: 'No geometry near the spawn — nothing to run',
                notify_play_started: '▶ Play: {n} physics bodies',
                notify_stop: '⏹ Stop',
                notify_script_none: 'No script selected',
                notify_script_saved: '✅ Script saved',
                notify_focus: '🎯 Focused on object',
                notify_loaded_count: '✅ {n} objects',
                notify_error: 'Error',
                fb_saveas_title: '💾 Save as',
                fb_open_title: '📂 Open',
                fb_name_ph: 'file.rbxl',
                btn_save: 'Save',
                btn_cancel: 'Cancel',
                btn_publish: 'Publish',
                notify_saved_simple: '💾 Saved',
                notify_save_cancelled: 'Save cancelled or failed',
                notify_enter_name: 'Enter a name',
                add_name_ph: 'Name',
                add_parent_label: 'Parent:',
                btn_add: 'Add',
                notify_not_selected: 'Nothing selected',
                notify_deleted: '🗑 Deleted',
                notify_published: '✅ Published!',
                notify_saved_original: '💾 Saved to the original file',
                notify_save_original_failed: '⚠️ Could not write to the original file: {err}. Use “Save As”.',
                upd_title: '🚀 New version available',
                upd_text: 'Version {ver} has been released. Update the app to get the latest features and fixes.',
                upd_go: 'Go',
                upd_later: 'Later',
                notify_quickadd: '✅ {cls} added',
                avatar_title: '🧍 3D Avatar',
                avatar_title_uid: '🧍 3D Avatar by User ID',
                avatar_login_needed: 'To download a NEW avatar by User ID, you need to sign in to your Roblox account.',
                avatar_login_btn: 'Sign in via Roblox',
                avatar_login_android_only: 'Sign-in is only available in the Android app.',
                avatar_import_scene: '🎬 Import to scene',
                avatar_download_zip: '💾 Download .zip',
                avatar_import_file: '📁 Import from file (.zip)',
                avatar_logout: 'Log out',
                avatar_uid_ph: 'Roblox User ID',
                avatar_enter_uid: 'Enter a numeric Roblox User ID',
                avatar_added_to_scene: '✅ Avatar added to scene',
                avatar_saved: '✅ Avatar saved',
                avatar_save_cancelled: 'Save cancelled',
                account_title: '👤 Roblox Account',
                acc_asset_title: 'Download asset by ID (mesh, texture, sound)',
                acc_asset_ph: 'MeshId / Asset ID (e.g. 80841113310862)',
                acc_asset_btn: '⬇ Download',
                acc_asset_bad: 'Enter a numeric asset ID',
                acc_asset_failed: '↯ Insert unparsed meshes (IDs can be separated by spaces)',
                account_section_login: 'Roblox login (cookie)',
                account_section_apikey: 'Open Cloud API key',
                apikey_desc: 'Create a key at <a href="https://create.roblox.com/dashboard/credentials" target="_blank">create.roblox.com/dashboard/credentials</a> with read-only Asset Delivery access and paste it here — needed for sounds/images in Play (Roblox requires auth for AssetDelivery since April 2025).',
                apikey_status_set: '✅ Key saved (…{last4})',
                apikey_status_set_env: ' — set via ROBLOX_API_KEY environment variable on the server',
                apikey_status_unset: '⚠️ Key not set — sounds/images from the server won\'t load.',
                apikey_placeholder: 'Paste API key',
                apikey_save: '💾 Save',
                apikey_delete: '🗑 Delete',
                apikey_validate: '🔎 Check',
                apikey_validating: 'Checking…',
                apikey_valid: '✅ Key works',
                apikey_invalid: '❌ Key rejected (401/403) — check it was created with Asset Delivery read access and hasn\'t expired.',
                warn_texture_failed: 'Failed to load part texture (assetId={id})',
                warn_sound_failed: 'Failed to load sound "{name}" ({src})',
                warn_image_failed: 'Failed to load image "{name}" ({src})',
                apikey_empty: 'Key is empty',
                apikey_saved_notify: '✅ Key saved (…{last4})',
                apikey_deleted_notify: 'Key deleted',
                apikey_error: 'Error: {msg}',
                acc_username_ph: 'Roblox nickname',
                acc_get_id_btn: '🔍 Get ID',
                acc_uid_ph: 'Roblox User ID (filled in automatically)',
                acc_enter_username: 'Enter a nickname',
                acc_id_found: '✅ ID found: {id} ({name})',
                acc_user_not_found: 'User not found',
                acc_request_error: 'Request error: {msg}',
                avatar_progress_title: '🧍 Downloading 3D avatar',
                avatar_progress_back: 'Back',
                avatar_progress_cancel: 'Cancel',
                acc_login_done: '✅ Signed in',
                acc_login_failed: 'Sign-in failed',
                preview_listen: 'Listen',
                preview_stop: 'Stop',
            },
            ru: {
                stop_title: 'Стоп',
                no_output: '(нет вывода)',
                pub_ver_published: 'Опубликовать (Published)',
                pub_ver_saved: 'Только сохранить (Saved)',
                add_search_ph: 'Поиск класса…',
                menu_file: '📁 Файл',
                menu_new: 'Новый',
                menu_open_file: 'Открыть из файла…',
                menu_open_roblox: 'Открыть из Roblox…',
                menu_save: 'Сохранить',
                menu_save_note: 'только файлы',
                menu_save_as: 'Сохранить как .rbxl…',
                menu_import: 'Импорт модели (.rbxm)…',
                menu_export: 'Экспорт выделенного (.rbxm)…',
                ui_explorer: 'Проводник',
                ui_properties: 'Свойства',
                ui_script_tab: 'Скрипт',
                ui_output: 'Вывод',
                ui_out_all: 'Все',
                ui_out_server: '🖥️ Сервер',
                ui_out_client: '💻 Клиент',
                ui_out_filter_title: 'Фильтр по среде выполнения',
                ui_out_clear: 'Очистить',
                tb_view: '👤 Вид',
                tb_view_title: 'Вид от 1-го / 3-го лица',
                q_low: 'Низ.',
                q_med: 'Сред.',
                q_high: 'Выс.',
                mv_ghost_n: '📦 {n} объектов',
                mv_failed: 'Не удалось перенести',
                mv_done: 'Перенесено объектов: {n}',
                mv_skipped: ' (пропущено {n})',
                mv_none: 'Ничего не перенесено',
                exp_asset_start: 'Экспорт {label} {id}…',
                exp_asset_fail: 'Не удалось получить ассет {id}: {err}',
                exp_asset_fail_http: 'Не удалось получить ассет {id} (HTTP {status})',
                exp_shared: 'Отправлено: {name} ({kb} КБ)',
                exp_saved: 'Сохранено: {name} ({kb} КБ)',
                exp_error: 'Ошибка экспорта: {msg}',
                exp_generic_err: 'ошибка',
                exp_longpress: 'долгое нажатие: экспорт файла {id}',
                mesh_failed_n: 'Неразобранных мешей: {n}',
                mesh_failed_none: 'Неразобранных мешей пока нет (сначала запусти Play)',
                exp_assets_start: 'Экспорт {n} ассетов…',
                exp_assets_fail: 'Не удалось получить ассеты: {err}',
                exp_assets_missing: 'Не получены: {list}',
                exp_assets_saved: 'Сохранено: {name} ({kb} КБ, ассетов: {n})',
                av_step_status: 'Запрашиваю статус модели у Roblox',
                av_step_wait: 'Жду, пока Roblox сгенерирует модель',
                av_step_download: 'Скачиваю obj/mtl/текстуры',
                av_step_add: 'Добавляю на сцену',
                av_step_save: 'Выберите, куда сохранить',
                av_err_empty_geom: 'Модель распарсилась, но геометрия пустая (0 вершин) — формат OBJ мог измениться на стороне Roblox',
                av_err_scene_not_ready: '3D-сцена ещё не готова, попробуйте через секунду',
                av_err_not_saved: 'Модель добавлена только в вьюпорт (визуально), но НЕ сохранена как объект сцены: нет открытого проекта (.rbxl/.rbxlx). Откройте или создайте файл проекта, затем импортируйте аватар заново.',
                lp_title: 'Войдите в Roblox',
                lp_text: 'Войдите, чтобы открывать свои experiences, скачивать плейсы и публиковать изменения прямо из приложения.',
                lp_f1: '📁 Все твои experiences одним списком',
                lp_f2: '⬇ Скачивание плейсов в одно касание',
                lp_f3: '☁ Публикация из редактора',
                lp_btn: 'Войти через Roblox',
                lp_later: 'Не сейчас',
                lp_never: 'Больше не показывать',
                lp_note: 'Вход хранится только на этом устройстве.',
                err_3d: '3D: ошибка',
                ui_btn_title: 'Размер текста, кнопок и разделителей',
                ui_text: 'Текст',
                ui_buttons: 'Кнопки и поля',
                ui_splitters: 'Разделители панелей',
                ui_scrollbars: 'Полосы прокрутки',
                ui_auto: 'авто',
                ui_reset: 'Сбросить',
                ui_close: 'Закрыть',
                cam_third: '3-е лицо',
                cam_first: '1-е лицо (от глаз)',
                log_draco_lod0: 'Draco: использую LOD0 ({n} из {total} граней)',
                log_play_account: 'Аккаунт: {name} (id {id})',
                log_play_guest: 'Нет входа в Roblox — стандартный аватар',
                log_play_avatar_ok: 'Аватар игрока загружен',
                log_play_avatar_fail: 'Не удалось загрузить аватар игрока ({msg}) — стандартный аватар',
                log_outfit_applied: 'Костюм: на персонаже показано предметов — {n}',
                warn_sky_failed: 'Не удалось загрузить скайбокс карты — оставляю цвет неба',
                log_mesh_load_failed: 'Mesh {id}: загрузка не удалась ({msg}), использую приближение',
                log_cloth_loaded: 'Одежда: загружено слоёв {n} из {total}',
                asset_fail_reason: 'Ассет {id} не загрузился: {reason}',
                asset_not_image: 'Ассет {id}: сервер вернул «{type}», а не картинку',
                asset_decode_failed: 'Ассет {id}: браузер не смог декодировать картинку ({type})',
                lua_compile_error: 'ошибка компиляции: ',
                lua_run_aborted: 'Запуск Lua прерван: ',
                lua_scripts_no_reply: '/api/scripts не ответил',
                lua_no_scripts: 'Нет включённых Script/LocalScript на карте',
                lua_fengari_fail: 'fengari не загрузилась — проверь интернет',
                lua_vm_fail_notify: 'Lua VM (fengari) не загрузилась — проверь интернет',
                lua_instances_no_reply: '/api/all_instances не ответил',
                notify_editor_unavailable: 'Редактор скриптов недоступен (CodeMirror не загрузился)',
                confirm_discard_unsaved: 'Текущая сцена (если не сохранена) будет заменена пустой. Продолжить?',
                notify_new_scene: 'Создана новая сцена Baseplate',
                notify_download_cancelled: 'Скачивание отменено',
                notify_loading_model: 'Загружаю модель…',
                notify_import_failed: 'Не удалось импортировать: ',
                notify_import_error: 'Ошибка импорта',
                notify_import_net: 'Ошибка сети при импорте',
                notify_reading_file: 'Читаю файл…',
                notify_read_error: 'Ошибка чтения файла: ',
                notify_archive_failed: 'Не удалось прочитать архив',
                av_net_error: 'Сеть/сервер: ',
                av_status_failed: 'Не удалось запросить статус',
                av_roblox_failed: 'Roblox не смог сгенерировать модель для этого User ID',
                av_timeout: 'Roblox слишком долго готовит модель — попробуйте ещё раз чуть позже',
                av_download_error: 'Ошибка скачивания: ',
                av_download_failed: 'Не удалось скачать файлы',
                av_import_failed: 'Не удалось импортировать: ',
                av_zip_android: 'Сохранение .zip доступно только в Android-приложении (в десктоп-режиме файл уже записан рядом с app.py: {path})',
                tb_new: '🆕 Новый', tb_new_title: 'Новая сцена (Baseplate)',
                tb_open: '📂 Открыть', tb_open_title: 'Открыть файл (Ctrl+O)',
                tb_save: '💾 Сохранить', tb_save_title: 'Сохранить (Ctrl+S)',
                tb_saveas: '💾 Как...', tb_saveas_title: 'Сохранить как',
                tb_import: '📥 Импорт', tb_import_title: 'Импортировать модель (.rbxm) в сцену',
                tb_export: '📤 Экспорт', tb_export_title: 'Экспортировать выбранные объекты в модель (.rbxm)',
                exp_multisel_title: 'Режим мультивыбора: тап добавляет/убирает объекты (Ctrl+клик и Shift+клик тоже работают)',
                rbxm_export_title: 'Экспорт объектов: {n} → .rbxm',
                notify_rbxm_exported: '📤 Экспортировано объектов: {n}',
                notify_rbxm_imported: '📥 Импортировано объектов: {n}',
                notify_rbxm_warn: '⚠ {msg}',
                tb_add: '➕ Добавить', tb_addobj_title: 'Добавить объект',
                tb_delete: '🗑 Удалить', tb_delete_title: 'Удалить (Delete)',
                tb_refresh: '🔄 Обновить', tb_refresh_title: 'Обновить сцену (F5)',
                tb_publish: '☁ Публикация', tb_publish_title: 'Опубликовать',
                tb_download: '🏠 Старт', tb_download_title: 'Стартовый экран: недавние файлы и твои experiences с Roblox',
                dl_hint: 'Используется твой вход в Roblox (Account), как в Studio. Нужен доступ на редактирование места или оно должно быть копируемым.', cookie_ph: 'Значение .ROBLOSECURITY', cookie_btn: 'Войти по куке', cookie_help: 'Вход на десктопе: в браузере, где ты вошёл на roblox.com, открой DevTools → Application → Cookies → .ROBLOSECURITY и вставь значение. Относись как к паролю: оно даёт полный доступ к аккаунту. Хранится только на этом устройстве.', cookie_ok: '✅ Вход выполнен: {name}', cookie_bad: 'Вход не выполнен',
                st_new: 'Новый experience', st_recents: 'Недавние', st_home: 'Главная', st_experiences: 'Experiences', st_templates: 'Шаблоны', st_archive: 'Архив', st_recent_h: 'Мои недавние Experiences', st_tpl_h: 'Открыть шаблон', st_banner_t: 'Продолжи с того же места', st_banner_p: 'Открой файл, скачай одно из своих experiences с Roblox или начни с шаблона.', st_modified: 'Изменено {d}', st_opened: 'Открыто {d}', st_local: 'Локально', st_refresh: 'Обновить', st_close: 'Закрыть', st_remove: 'Убрать из недавних?', st_tpl_base: 'Baseplate', st_tpl_empty: 'Пустая сцена', st_tpl_sub: 'Шаблон', st_menu: 'Убрать из недавних', st_studio: 'Игры студии', st_studio_pill: 'Студия', st_studio_empty: 'Список игр студии пуст. Добавьте игры в studio_games.json в репозитории (groupId или games).', st_studio_group_err: 'Не удалось загрузить игры группы: {err}',
                start_title: 'Старт', start_welcome: 'Привет, {name}', start_recent: 'Недавние', start_new: 'Новая сцена', start_open: 'Открыть файл…', start_file: 'Файл', start_roblox: 'Roblox', start_err: 'Не удалось загрузить experiences: {err}',
                exp_title: 'Мои Experiences', exp_loading: 'Загружаю список…', exp_search: 'Поиск…', exp_empty: 'Ничего не найдено', exp_login_needed: 'Сначала войди в Roblox (Аккаунт), чтобы увидеть свои experiences.', exp_private: 'Private', exp_public: 'Public', exp_by_id: 'По Place ID…', exp_pick_place: 'В этом experience несколько мест. Выбери:', pub_origin: 'Открыто с Roblox: {name} (Place {id}). ID подставлены.',
                dl_title: '⬇ Скачать место', dl_place: 'Place ID', dl_version: 'Версия (необязательно)', dl_btn: 'Скачать', dl_discard: 'Несохранённые изменения в текущей сцене пропадут. Продолжить?', dl_ok: '✅ Место загружено: {n} объектов', dl_loading: 'Скачиваю свежую версию…',
                tb_account: '👤 Аккаунт', tb_account_title: 'Аккаунт Roblox и Open Cloud API-ключ',
                tb_play: '▶ Play', tb_play_title: 'Запустить симуляцию физики',
                tb_resetcam: '🏠 Сброс', tb_resetcam_title: 'Сбросить камеру',
                tb_topview: '⬆ Верх', tb_topview_title: 'Вид сверху',
                tb_frontview: '📷 Фронт', tb_frontview_title: 'Вид спереди',
                tb_rightview: '➡ Право', tb_rightview_title: 'Вид справа',
                tb_teleport: '🎯 К объекту', tb_teleport_title: 'Телепортировать камеру к выбранному объекту',
                tb_helpers_title: 'Сетка и оси',
                tb_resetlayout_title: 'Сбросить размеры панелей',
                exp_collapse_title: 'Свернуть всё',
                exp_expand_title: 'Развернуть всё',
                exp_search_ph: '🔍 Поиск...',
                vp_hint: '🖱️ ЛКМ — вращение | 🖱️ ПКМ — панорама | 🖱️ Колесо — дальность прорисовки<br>⌨️ WASD — движение | F — фокус | Esc — снять',
                pad_up_title: 'Вверх',
                pad_down_title: 'Вниз',
                pad_jump_title: 'Прыжок',
                props_placeholder: '← Выбери объект',
                script_none_selected: 'Скрипт не выбран',
                script_save_btn: '💾 Сохранить скрипт',
                notify_quality: '🎨 Качество: ',
                notify_layout_reset: '📐 Размеры панелей сброшены',
                notify_camera_reset: '🏠 Камера сброшена',
                notify_topview: '⬆ Вид сверху',
                notify_frontview: '📷 Вид спереди',
                notify_rightview: '➡ Вид справа',
                notify_teleport_no_selection: 'Сначала выберите объект в Explorer',
                notify_teleported: '🎯 Телепортировано к выбранному объекту',
                notify_stop_play_first: 'Сначала останови Play, потом обновляй сцену',
                notify_scene_loaded: '🔄 Сцена: {n} объектов',
                notify_scene_of: ' (из {total})',
                notify_helpers_on: '📏 Сетка и оси: ВКЛ',
                notify_helpers_off: '📏 Сетка и оси: ВЫКЛ',
                notify_spawn_not_found: 'SpawnLocation не найден в файле — спавню у текущей камеры',
                notify_cannon_not_ready: 'Cannon.js ещё не загрузился, подожди секунду и попробуй снова',
                notify_no_geometry: 'Рядом со спавном нет геометрии — нечего запускать',
                notify_play_started: '▶ Play: {n} тел физики',
                notify_stop: '⏹ Stop',
                notify_script_none: 'Скрипт не выбран',
                notify_script_saved: '✅ Скрипт сохранён',
                notify_focus: '🎯 Фокус на объекте',
                notify_loaded_count: '✅ {n} объектов',
                notify_error: 'Ошибка',
                fb_saveas_title: '💾 Сохранить как',
                fb_open_title: '📂 Открыть',
                fb_name_ph: 'файл.rbxl',
                btn_save: 'Сохранить',
                btn_cancel: 'Отмена',
                btn_publish: 'Опубликовать',
                notify_saved_simple: '💾 Сохранено',
                notify_save_cancelled: 'Сохранение отменено или не удалось',
                notify_enter_name: 'Введи имя',
                add_name_ph: 'Имя',
                add_parent_label: 'Родитель:',
                btn_add: 'Добавить',
                notify_not_selected: 'Не выбран',
                notify_deleted: '🗑 Удалён',
                notify_published: '✅ Опубликовано!',
                notify_saved_original: '💾 Сохранено в исходный файл',
                notify_save_original_failed: '⚠️ Не удалось записать в исходный файл: {err}. Сохраните через «Сохранить как».',
                upd_title: '🚀 Вышла новая версия',
                upd_text: 'Вышла версия {ver}. Обновите приложение, чтобы получить новые функции и исправления.',
                upd_go: 'Перейти',
                upd_later: 'Позже',
                notify_quickadd: '✅ {cls} добавлен',
                avatar_title: '🧍 3D-аватар',
                avatar_title_uid: '🧍 3D-аватар по User ID',
                avatar_login_needed: 'Чтобы скачать НОВЫЙ аватар по User ID, нужен вход в аккаунт Roblox.',
                avatar_login_btn: 'Войти через Roblox',
                avatar_login_android_only: 'Вход доступен только в Android-приложении.',
                avatar_import_scene: '🎬 Импортировать на сцену',
                avatar_download_zip: '💾 Скачать .zip',
                avatar_import_file: '📁 Импортировать из файла (.zip)',
                avatar_logout: 'Выйти из аккаунта',
                avatar_uid_ph: 'Roblox User ID',
                avatar_enter_uid: 'Введите числовой Roblox User ID',
                avatar_added_to_scene: '✅ Аватар добавлен на сцену',
                avatar_saved: '✅ Аватар сохранён',
                avatar_save_cancelled: 'Сохранение отменено',
                account_title: '👤 Аккаунт Roblox',
                acc_asset_title: 'Скачать ассет по ID (меш, текстура, звук)',
                acc_asset_ph: 'MeshId / Asset ID (например, 80841113310862)',
                acc_asset_btn: '⬇ Скачать',
                acc_asset_bad: 'Введи числовой ID ассета',
                acc_asset_failed: '↯ Вставить неразобранные меши (ID можно через пробел)',
                account_section_login: 'Вход в Roblox (кука)',
                account_section_apikey: 'Open Cloud API key',
                apikey_desc: 'Создайте ключ на <a href="https://create.roblox.com/dashboard/credentials" target="_blank">create.roblox.com/dashboard/credentials</a> с правом только на чтение ассетов (Asset Delivery) и вставьте сюда — нужен для звуков/картинок в Play (Roblox требует авторизацию на AssetDelivery с апреля 2025).',
                apikey_status_set: '✅ Ключ сохранён (…{last4})',
                apikey_status_set_env: ' — задан через переменную окружения ROBLOX_API_KEY на сервере',
                apikey_status_unset: '⚠️ Ключ не задан — звуки/картинки с сервера грузиться не будут.',
                apikey_placeholder: 'Вставьте API-ключ',
                apikey_save: '💾 Сохранить',
                apikey_delete: '🗑 Удалить',
                apikey_validate: '🔎 Проверить',
                apikey_validating: 'Проверяю…',
                apikey_valid: '✅ Ключ работает',
                apikey_invalid: '❌ Ключ отклонён (401/403) — проверьте, что он создан с правом на чтение Asset Delivery и не истёк.',
                warn_texture_failed: 'Не удалось загрузить текстуру part\'а (assetId={id})',
                warn_sound_failed: 'Не удалось загрузить звук "{name}" ({src})',
                warn_image_failed: 'Не удалось загрузить картинку "{name}" ({src})',
                apikey_empty: 'Ключ пустой',
                apikey_saved_notify: '✅ Ключ сохранён (…{last4})',
                apikey_deleted_notify: 'Ключ удалён',
                apikey_error: 'Ошибка: {msg}',
                acc_username_ph: 'Ник в Roblox',
                acc_get_id_btn: '🔍 Получить ID',
                acc_uid_ph: 'Roblox User ID (заполнится автоматически)',
                acc_enter_username: 'Введите никнейм',
                acc_id_found: '✅ ID найден: {id} ({name})',
                acc_user_not_found: 'Пользователь не найден',
                acc_request_error: 'Ошибка запроса: {msg}',
                avatar_progress_title: '🧍 Скачивание 3D-аватара',
                avatar_progress_back: 'Назад',
                avatar_progress_cancel: 'Отменить',
                acc_login_done: '✅ Вход выполнен',
                acc_login_failed: 'Вход не выполнен',
                preview_listen: 'Прослушать',
                preview_stop: 'Стоп',
            },
        };

        // Language auto-detection:
        function detectLang() {
            try {
                const saved = localStorage.getItem('rbxstudio-lang');
                if (saved && I18N[saved]) return saved;
            } catch (e) { emuWarn('swallow:detectLang:504', 'detectLang: ' + _errText(e) + ''); }
            const langs = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language || 'en'];
            for (const l of langs) {
                const short = (l || '').slice(0, 2).toLowerCase();
                if (I18N[short]) return short;
            }
            return 'en';
        }
        const LANG = detectLang();

        function t(key, vars) {
            let s = (I18N[LANG] && I18N[LANG][key] != null) ? I18N[LANG][key] : (I18N.en[key] != null ? I18N.en[key] : key);
            if (vars) {
                for (const k in vars) s = s.split('{' + k + '}').join(vars[k]);
            }
            return s;
        }

        function applyStaticI18n() {
            document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.getAttribute('data-i18n')); });
            document.querySelectorAll('[data-i18n-title]').forEach(el => { el.title = t(el.getAttribute('data-i18n-title')); });
            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => { el.placeholder = t(el.getAttribute('data-i18n-placeholder')); });
            document.querySelectorAll('[data-i18n-html]').forEach(el => { el.innerHTML = t(el.getAttribute('data-i18n-html')); });
            document.documentElement.lang = LANG;
            const langBtn = document.getElementById('lang-btn');
            if (langBtn) {
                // Кнопка показывает язык, НА КОТОРЫЙ переключит (не текущий) —
                // так интуитивнее, как переключатели языка в большинстве приложений.
                langBtn.textContent = LANG === 'ru' ? '🌐 EN' : '🌐 RU';
            }
        }
        applyStaticI18n();

        // Простой переключатель между двумя языками (en/ru).
        function toggleLang() {
            const next = LANG === 'ru' ? 'en' : 'ru';
            try { localStorage.setItem('rbxstudio-lang', next); } catch (e) { emuWarn('swallow:localStorage.setItem:540', 'localStorage.setItem: ' + _errText(e) + ''); }
            location.reload();
        }

        // Three.js загрузка
        (function () {
            const scripts = [
                'vendor/three.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'
            ];
            let loaded = false;
            function tryLoad(i) {
                if (i >= scripts.length) {
                    console.error('Three.js не загружен');
                    document.getElementById('fps-counter').textContent = t('err_3d');
                    return;
                }
                const s = document.createElement('script');
                s.src = scripts[i];
                s.onload = () => {
                    if (!loaded) {
                        loaded = true;
                        console.log('Three.js загружен из: ' + scripts[i]);
                        initThree();
                    }
                };
                s.onerror = () => {
                    console.warn('Не удалось загрузить: ' + scripts[i]);
                    tryLoad(i + 1);
                };
                document.head.appendChild(s);
            }
            tryLoad(0);
        })();

        // OBJLoader/MTLLoader грузятся ЛЕНИВО, только когда реально нужен
        let _objMtlLoadersPromise = null;
        function ensureObjMtlLoaders() {
            if (_objMtlLoadersPromise) return _objMtlLoadersPromise;
            _objMtlLoadersPromise = new Promise((resolve, reject) => {
                const pairs = [
                    ['vendor/MTLLoader.js', 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/MTLLoader.js'],
                    ['vendor/OBJLoader.js', 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/OBJLoader.js'],
                ];
                let remaining = pairs.length;
                pairs.forEach(([local, cdn]) => {
                    const s = document.createElement('script');
                    s.src = local;
                    s.onload = () => { if (--remaining === 0) resolve(); };
                    s.onerror = () => {
                        const fb = document.createElement('script');
                        fb.src = cdn;
                        fb.onload = () => { if (--remaining === 0) resolve(); };
                        fb.onerror = () => reject(new Error('Не удалось загрузить ' + cdn));
                        document.head.appendChild(fb);
                    };
                    document.head.appendChild(s);
                });
            });
            return _objMtlLoadersPromise;
        }

        // Cannon.js загрузка (физика для Play-режима)
        (function () {
            const scripts = [
                'vendor/cannon.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/cannon.js/0.6.2/cannon.min.js'
            ];
            let loaded = false;
            function tryLoad(i) {
                if (i >= scripts.length) {
                    console.error('Cannon.js не загружен — Play-режим недоступен');
                    return;
                }
                const s = document.createElement('script');
                s.src = scripts[i];
                s.onload = () => {
                    if (!loaded) {
                        loaded = true;
                        console.log('Cannon.js загружен из: ' + scripts[i]);
                    }
                };
                s.onerror = () => tryLoad(i + 1);
                document.head.appendChild(s);
            }
            tryLoad(0);
        })();

        // ============ ANDROID (SAF) ============
        const IS_ANDROID = typeof window.AndroidBridge !== 'undefined';

        // Цвет неба (фон сцены + туман) — единая константа, чтобы оба места
        const SKY_COLOR = 0x87ceeb;

        // ============ CODEMIRROR ============

        const ROBLOX_LUA_KEYWORDS = [
            // Глобальные функции / стандартная библиотека Lua
            'print', 'warn', 'error', 'assert', 'tick', 'wait', 'require',
            'typeof', 'type', 'pairs', 'ipairs', 'next', 'select', 'unpack',
            'collectgarbage', 'tonumber', 'tostring', 'pcall', 'xpcall',
            'setmetatable', 'getmetatable', 'rawget', 'rawset', 'rawequal',
            'rawlen', 'spawn', 'delay',
            'task', 'task.wait', 'task.spawn', 'task.delay', 'task.cancel',
            'task.defer',
            'math', 'math.abs', 'math.ceil', 'math.floor', 'math.max',
            'math.min', 'math.random', 'math.randomseed', 'math.sqrt',
            'math.sin', 'math.cos', 'math.tan', 'math.pi', 'math.huge',
            'math.clamp', 'math.sign', 'math.round', 'math.rad', 'math.deg',
            'table', 'table.insert', 'table.remove', 'table.concat',
            'table.sort', 'table.find', 'table.clear', 'table.clone',
            'table.pack', 'table.unpack',
            'string', 'string.find', 'string.format', 'string.gmatch',
            'string.gsub', 'string.len', 'string.lower', 'string.upper',
            'string.match', 'string.rep', 'string.sub', 'string.split',
            'string.byte', 'string.char',
            'os', 'os.time', 'os.clock', 'os.date',
            'coroutine', 'coroutine.create', 'coroutine.resume',
            'coroutine.yield', 'coroutine.wrap', 'coroutine.status',

            // Глобальные объекты окружения скрипта
            'game', 'workspace', 'script', 'shared', '_G',

            // Сервисы (game:GetService('...'))
            'Workspace', 'Lighting', 'ReplicatedStorage', 'ReplicatedFirst',
            'ServerScriptService', 'ServerStorage', 'StarterGui',
            'StarterPack', 'StarterPlayer', 'SoundService', 'Players',
            'Teams', 'Chat', 'TextChatService', 'RunService', 'HttpService',
            'TweenService', 'CollectionService', 'UserInputService',
            'ContextActionService', 'MarketplaceService', 'DataStoreService',
            'TeleportService', 'PhysicsService', 'PathfindingService',
            'ProximityPromptService', 'BadgeService', 'InsertService',
            'GetService',

            // Конструкторы дататипов
            'Instance', 'Instance.new', 'Vector3', 'Vector3.new', 'Vector2',
            'Vector2.new', 'CFrame', 'CFrame.new', 'CFrame.Angles',
            'CFrame.lookAt', 'Color3', 'Color3.new', 'Color3.fromRGB',
            'Color3.fromHSV', 'BrickColor', 'BrickColor.new', 'UDim2',
            'UDim2.new', 'UDim2.fromScale', 'UDim2.fromOffset', 'UDim',
            'UDim.new', 'Rect', 'Rect.new', 'Ray', 'Ray.new', 'Region3',
            'Random', 'Random.new', 'NumberSequence', 'ColorSequence',
            'NumberRange', 'TweenInfo', 'TweenInfo.new',
            'Enum', 'EnumItem',

            // Классы Instance
            'BasePart', 'Part', 'MeshPart', 'WedgePart', 'CornerWedgePart',
            'TrussPart', 'SpawnLocation', 'Model', 'Folder', 'Humanoid',
            'HumanoidDescription', 'Tool', 'Accessory', 'Weld', 'WeldConstraint',
            'Motor6D', 'Attachment', 'BodyPosition', 'BodyVelocity',
            'BodyGyro', 'BodyForce', 'BodyAngularVelocity', 'AlignPosition',
            'AlignOrientation', 'LinearVelocity', 'VectorForce',
            'RemoteEvent', 'RemoteFunction', 'BindableEvent', 'BindableFunction',
            'NumberValue', 'StringValue', 'BoolValue', 'IntValue', 'ObjectValue',
            'Vector3Value', 'CFrameValue', 'Color3Value', 'BrickColorValue',
            'ParticleEmitter', 'Fire', 'Smoke', 'Sparkles', 'Explosion',
            'Sound', 'SoundGroup', 'PointLight', 'SpotLight', 'SurfaceLight',
            'Camera', 'Animation', 'AnimationController', 'Animator',
            'AnimationTrack', 'Player', 'PlayerGui', 'Backpack',
            'ProximityPrompt', 'Highlight', 'SelectionBox',

            // GUI
            'ScreenGui', 'BillboardGui', 'SurfaceGui', 'Frame',
            'ScrollingFrame', 'CanvasGroup', 'TextLabel', 'TextButton',
            'TextBox', 'ImageLabel', 'ImageButton', 'ViewportFrame',
            'UIListLayout', 'UIGridLayout', 'UIPadding', 'UICorner',
            'UIStroke', 'UIGradient', 'UIAspectRatioConstraint',
            'UISizeConstraint', 'UITextSizeConstraint',

            // Часто используемые методы Instance
            'FindFirstChild', 'FindFirstChildOfClass', 'FindFirstChildWhichIsA',
            'FindFirstAncestor', 'FindFirstAncestorOfClass', 'WaitForChild',
            'GetChildren', 'GetDescendants', 'GetFullName', 'IsA',
            'IsDescendantOf', 'IsAncestorOf', 'Clone', 'Destroy',
            'ClearAllChildren', 'SetAttribute', 'GetAttribute',
            'GetAttributes', 'AddTag', 'RemoveTag', 'HasTag', 'GetTags',
            'GetPropertyChangedSignal', 'GetPivot', 'PivotTo',
            'MoveTo', 'BreakJoints', 'GetMass', 'ApplyImpulse',
            'ToWorldSpace', 'ToObjectSpace', 'PointToWorldSpace',

            // Часто используемые свойства
            'Name', 'Parent', 'ClassName', 'Position', 'Orientation',
            'Rotation', 'Size', 'Anchored', 'CanCollide', 'CanTouch',
            'Transparency', 'Reflectance', 'Color', 'BrickColor', 'Material',
            'Shape', 'Massless', 'Velocity', 'AssemblyLinearVelocity',
            'AssemblyAngularVelocity', 'Mass', 'Health', 'MaxHealth',
            'WalkSpeed', 'JumpPower', 'JumpHeight', 'HipHeight', 'Text',
            'TextColor3', 'TextSize', 'BackgroundColor3', 'BackgroundTransparency',
            'BorderSizePixel', 'Visible', 'Image', 'Enabled', 'Value',
            'PlayerToHideFrom', 'Character', 'CharacterAdded', 'UserId',
            'DisplayName', 'Team',

            // Часто используемые события
            'Changed', 'ChildAdded', 'ChildRemoved', 'DescendantAdded',
            'DescendantRemoving', 'Touched', 'TouchEnded', 'Died',
            'MouseEnter', 'MouseLeave', 'MouseButton1Click',
            'MouseButton1Down', 'MouseButton1Up', 'InputBegan', 'InputEnded',
            'InputChanged', 'RenderStepped', 'Stepped', 'Heartbeat',
            'PlayerAdded', 'PlayerRemoving', 'OnServerEvent', 'OnClientEvent',
            'FireServer', 'FireClient', 'FireAllClients', 'InvokeServer',
            'InvokeClient', 'Connect', 'Disconnect', 'Once', 'Wait',
        ];


        // Раньше здесь была отдельная robloxSubstringHint-функция для

        // ---- CodeMirror 6 вместо CodeMirror 5 ----
        let cmEditor = null;
        window.addEventListener('DOMContentLoaded', function () {
            try {
                if (!window.CM6) {
                    console.error('CM6 не найден — vendor/cm6-bundle.min.js не загрузился (проверьте путь/файл на сервере)');
                    return;
                }
                cmEditor = window.CM6.fromTextArea(document.getElementById('script-editor'), {
                    words: ROBLOX_LUA_KEYWORDS,
                });
            } catch (e) {
                console.error('CodeMirror 6 не загрузился:', e);
            }
        });

        function refreshCM() {
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    if (cmEditor) cmEditor.refresh();
                });
            });
        }

        // ============ КАЧЕСТВО 3D ============
        const QUALITY_PRESETS = {
            low: {
                antialias: false,
                shadows: false,
                resolutionScale: 0.3,
                sphereSegments: 4,
                textures: false,
                helpers: false,
                ambientLight: 1.0,
                dirLight: 0.0,
                fog: true,
                skipSmallObjects: true,
                maxObjects: 1000,
                lodDistance: 50,
                renderDistance: 250,
                playBodies: 500, // потолок Play-объектов один на все пресеты — см. medium/high ниже
                // Раньше здесь была плотность веера лучей (rayGrid) —
                loadRadius: 350,
                // Раньше физика (playBodies) и рендер были одним и тем же
                visualRadius: 2000,
                visualBodies: 3000,
            },
            medium: {
                antialias: false,
                shadows: false,
                resolutionScale: 0.5,
                sphereSegments: 8,
                textures: false,
                helpers: false,
                ambientLight: 0.8,
                dirLight: 0.2,
                fog: true,
                skipSmallObjects: false,
                maxObjects: 3000,
                lodDistance: 100,
                renderDistance: 500,
                playBodies: 500, // было 900 — при 4-6к-парт картах (Castle Warfare)
                // даже это заметно роняло FPS на мобильном GPU; единый
                // потолок 500 держит Play play лёгким на всех пресетах,
                loadRadius: 550,
                visualRadius: 2000,
                visualBodies: 3000,
            },
            high: {
                antialias: true,
                shadows: false,
                resolutionScale: 1.0,
                sphereSegments: 16,
                textures: true,
                helpers: true,
                ambientLight: 0.5,
                dirLight: 0.6,
                fog: false,
                skipSmallObjects: false,
                maxObjects: 99999,
                lodDistance: 200,
                renderDistance: 1200,
                playBodies: 500, // было 1600 — тот самый случай из скриншота
                // (High, 10 FPS, 4000+ обj):
                loadRadius: 900,
                visualRadius: 2000,
                visualBodies: 3000,
            }
        }

        let currentQuality = 'low';
        let currentSkyColor = SKY_COLOR; // меняется applyMapLighting() по ClockTime карты
        let qualitySettings = QUALITY_PRESETS.low;

        function setQuality(level) {
            currentQuality = level;
            qualitySettings = QUALITY_PRESETS[level];
            document.querySelectorAll('#quality-selector button[id^="q-"]').forEach(b => b.classList.remove('active'));
            document.getElementById('q-' + level).classList.add('active');
            if (renderer) {
                renderer.shadowMap.enabled = qualitySettings.shadows;
                applyPixelRatio();
                resize();
            }
            if (scene) {
                // См. комментарий у инициализации scene.fog — при переключении
                const far = isPlaying ? STREAM_PRUNE_DIST : (qualitySettings.fog ? 400 : qualitySettings.renderDistance);
                scene.fog = new THREE.Fog(currentSkyColor, 50, far);
                buildSceneLights(); // свет зависит от пресета (число источников) — пересобираем
            }
            updateHelpers();
            reloadScene();
            notify(t('notify_quality') + level.toUpperCase());
        }

        // ============ РАЗДЕЛИТЕЛИ ПАНЕЛЕЙ ============
        function initResizers() {
            const resizers = document.querySelectorAll('.resizer');
            let currentResizer = null, startX = 0, startWidth = 0, startRightWidth = 0;

            // === Вертикальные ресайзеры (мышь) ===
            resizers.forEach(resizer => {
                resizer.addEventListener('mousedown', (e) => {
                    currentResizer = resizer;
                    resizer.classList.add('active');
                    if (resizer.id === 'resizer-1') {
                        startWidth = document.getElementById('explorer').offsetWidth;
                        startX = e.clientX;
                    } else if (resizer.id === 'resizer-2') {
                        startRightWidth = document.getElementById('rightpanel').offsetWidth;
                        startX = e.clientX;
                    }
                    document.body.style.cursor = 'col-resize';
                    document.body.style.userSelect = 'none';
                });
            });

            // === Горизонтальный ресайзер (мышь) ===
            const hResizer = document.getElementById('resizer-h');
            if (hResizer) {
                let startY = 0, startHeight = 0;
                hResizer.addEventListener('mousedown', (e) => {
                    hResizer.classList.add('active');
                    startY = e.clientY;
                    startHeight = document.getElementById('bottom-panel').offsetHeight;
                    document.body.style.cursor = 'row-resize';
                    document.body.style.userSelect = 'none';
                });

                document.addEventListener('mousemove', (e) => {
                    if (!hResizer.classList.contains('active')) return;
                    const panel = document.getElementById('bottom-panel');
                    let newH = startHeight + (startY - e.clientY);
                    newH = Math.max(80, Math.min(window.innerHeight * 0.6, newH));
                    panel.style.height = newH + 'px';
                });

                document.addEventListener('mouseup', () => {
                    if (hResizer.classList.contains('active')) {
                        hResizer.classList.remove('active');
                        document.body.style.cursor = '';
                        document.body.style.userSelect = '';
                        try {
                            localStorage.setItem('rbxstudio-bottom-height', document.getElementById('bottom-panel').offsetHeight);
                        } catch (e) { emuWarn('swallow:L910', 'блок около script.js:910: ' + _errText(e) + ''); }
                    }
                });

                // === Горизонтальный ресайзер (touch) ===
                hResizer.addEventListener('touchstart', (e) => {
                    hResizer.classList.add('active');
                    startY = e.touches[0].clientY;
                    startHeight = document.getElementById('bottom-panel').offsetHeight;
                    document.body.style.userSelect = 'none';
                }, { passive: true });

                document.addEventListener('touchmove', (e) => {
                    if (!hResizer.classList.contains('active')) return;
                    const panel = document.getElementById('bottom-panel');
                    let newH = startHeight + (startY - e.touches[0].clientY);
                    newH = Math.max(80, Math.min(window.innerHeight * 0.6, newH));
                    panel.style.height = newH + 'px';
                }, { passive: true });

                // touchend ИЛИ touchcancel — браузер иногда шлёт cancel вместо end
                // (жест прерван системой), и без этого userSelect:none навсегда
                // застревал на body — после чего переставали работать ЛЮБЫЕ
                // текстовые поля на странице (промокод, скрипты и т.д.), пока
                // страницу не перезагружали.
                const endHResize = () => {
                    if (hResizer.classList.contains('active')) {
                        hResizer.classList.remove('active');
                        document.body.style.userSelect = '';
                        document.body.style.webkitUserSelect = '';
                        try {
                            localStorage.setItem('rbxstudio-bottom-height', document.getElementById('bottom-panel').offsetHeight);
                        } catch (e) { emuWarn('swallow:L942', 'блок около script.js:942: ' + _errText(e) + ''); }
                    }
                };
                document.addEventListener('touchend', endHResize);
                document.addEventListener('touchcancel', endHResize);
            }

            // === Общие обработчики для вертикальных ресайзеров (mousemove/mouseup) ===
            document.addEventListener('mousemove', (e) => {
                if (!currentResizer) return;
                if (currentResizer.id === 'resizer-1') {
                    let w = Math.max(150, Math.min(window.innerWidth * 0.6, startWidth + e.clientX - startX));
                    document.getElementById('explorer').style.width = w + 'px';
                } else if (currentResizer.id === 'resizer-2') {
                    let w = Math.max(200, Math.min(window.innerWidth * 0.7, startRightWidth + startX - e.clientX));
                    document.getElementById('rightpanel').style.width = w + 'px';
                }
                refreshCM();
                resize();
            });

            const endVResize = () => {
                if (currentResizer) {
                    currentResizer.classList.remove('active');
                    currentResizer = null;
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    document.body.style.webkitUserSelect = '';
                    saveLayout();
                }
            };
            document.addEventListener('mouseup', endVResize);

            // === Touch-поддержка для вертикальных ресайзеров ===
            resizers.forEach(resizer => {
                resizer.addEventListener('touchstart', (e) => {
                    currentResizer = resizer;
                    resizer.classList.add('active');
                    if (resizer.id === 'resizer-1') {
                        startWidth = document.getElementById('explorer').offsetWidth;
                        startX = e.touches[0].clientX;
                    } else if (resizer.id === 'resizer-2') {
                        startRightWidth = document.getElementById('rightpanel').offsetWidth;
                        startX = e.touches[0].clientX;
                    }
                    document.body.style.userSelect = 'none';
                }, { passive: true });
            });

            document.addEventListener('touchmove', (e) => {
                if (!currentResizer) return;
                if (currentResizer.id === 'resizer-1') {
                    let w = Math.max(150, Math.min(window.innerWidth * 0.6, startWidth + e.touches[0].clientX - startX));
                    document.getElementById('explorer').style.width = w + 'px';
                } else if (currentResizer.id === 'resizer-2') {
                    let w = Math.max(200, Math.min(window.innerWidth * 0.7, startRightWidth + startX - e.touches[0].clientX));
                    document.getElementById('rightpanel').style.width = w + 'px';
                }
                refreshCM();
                resize();
            }, { passive: true });

            document.addEventListener('touchend', endVResize);
            document.addEventListener('touchcancel', endVResize);
        }

        // ============ НАСТРОЙКИ ИНТЕРФЕЙСА (размер текста/кнопок, ползунки-разделители) ============
        const UI_DEFAULTS = { fs: 1, bs: 1, rz: 0, sb: 0 }; // rz/sb = 0 → значение по умолчанию из CSS
        let uiCfg = { ...UI_DEFAULTS };
        function applyUiSettings() {
            const st = document.documentElement.style;
            st.setProperty('--fs', uiCfg.fs);
            st.setProperty('--bs', uiCfg.bs);
            if (uiCfg.rz) st.setProperty('--rz', uiCfg.rz + 'px'); else st.removeProperty('--rz');
            if (uiCfg.sb) st.setProperty('--sb', uiCfg.sb + 'px'); else st.removeProperty('--sb');
            try { localStorage.setItem('rbxstudio-ui', JSON.stringify(uiCfg)); } catch (e) { emuWarn('swallow:localStorage.setItem:1017', 'localStorage.setItem: ' + _errText(e) + ''); }
            try { refreshCM(); resize(); } catch (e) { emuWarn('swallow:refreshCM:1018', 'refreshCM: ' + _errText(e) + ''); }
        }
        function initUiSettings() {
            try { uiCfg = { ...UI_DEFAULTS, ...JSON.parse(localStorage.getItem('rbxstudio-ui') || '{}') }; } catch (e) { emuWarn('swallow:uiCfg:1021', 'uiCfg: ' + _errText(e) + ''); }
            applyUiSettings();
            const lang = document.getElementById('lang-btn');
            if (!lang || !lang.parentNode) return;
            const btn = document.createElement('button');
            btn.id = 'ui-btn';
            btn.textContent = '🎚 UI';
            btn.title = t('ui_btn_title');
            lang.parentNode.insertBefore(btn, lang);
            const panel = document.createElement('div');
            panel.id = 'ui-settings';
            panel.style.display = 'none';
            const rows = [
                ['fs', t('ui_text'), 0.7, 2.2, 0.05, '', 1],
                ['bs', t('ui_buttons'), 0.7, 2.2, 0.05, '', 1],
                ['rz', t('ui_splitters'), 4, 40, 1, 'px', 16],
                ['sb', t('ui_scrollbars'), 4, 30, 1, 'px', 10],
            ];
            const syncers = [];
            for (const [key, label, min, max, step, unit, dflt] of rows) {
                const row = document.createElement('label');
                row.className = 'ui-row';
                const cap = document.createElement('span');
                const rng = document.createElement('input');
                rng.type = 'range'; rng.min = min; rng.max = max; rng.step = step;
                const sync = () => {
                    rng.value = uiCfg[key] || dflt;
                    cap.textContent = label + ': ' + (uiCfg[key] ? uiCfg[key] + unit : t('ui_auto'));
                };
                rng.oninput = () => { uiCfg[key] = parseFloat(rng.value); sync(); applyUiSettings(); };
                sync(); syncers.push(sync);
                row.appendChild(cap); row.appendChild(rng);
                panel.appendChild(row);
            }
            const reset = document.createElement('button');
            reset.textContent = t('ui_reset');
            reset.onclick = () => { uiCfg = { ...UI_DEFAULTS }; applyUiSettings(); syncers.forEach(f => f()); };
            const close = document.createElement('button');
            close.textContent = t('ui_close');
            close.onclick = () => { panel.style.display = 'none'; };
            const btns = document.createElement('div');
            btns.className = 'ui-btns';
            btns.appendChild(reset); btns.appendChild(close);
            panel.appendChild(btns);
            document.body.appendChild(panel);
            btn.onclick = () => { panel.style.display = panel.style.display === 'none' ? 'flex' : 'none'; };
        }
        window.addEventListener('load', initUiSettings);

        function saveLayout() {
            const layout = {
                explorer: document.getElementById('explorer').style.width || '220px',
                rightpanel: document.getElementById('rightpanel').style.width || '260px'
            };
            localStorage.setItem('rbxstudio-layout', JSON.stringify(layout));
        }

        function loadLayout() {
            try {
                const saved = localStorage.getItem('rbxstudio-layout');
                if (saved) {
                    const layout = JSON.parse(saved);
                    document.getElementById('explorer').style.width = layout.explorer || '220px';
                    document.getElementById('rightpanel').style.width = layout.rightpanel || '260px';
                }
                // Восстанавливаем высоту нижней панели
                const h = localStorage.getItem('rbxstudio-bottom-height');
                if (h) {
                    document.getElementById('bottom-panel').style.height = h + 'px';
                }
            } catch (e) { emuWarn('swallow:L1091', 'блок около script.js:1091: ' + _errText(e) + ''); }
        }

        function resetLayout() {
            document.getElementById('explorer').style.width = '220px';
            document.getElementById('rightpanel').style.width = '260px';
            // Сбрасываем высоту нижней панели на дефолтную
            document.getElementById('bottom-panel').style.height = '180px';
            localStorage.removeItem('rbxstudio-layout');
            localStorage.removeItem('rbxstudio-bottom-height');
            refreshCM();
            resize();
            notify(t('notify_layout_reset'));
        }

        // ============ THREE.JS ПЕРЕМЕННЫЕ ============
        let selectedRef = null;          // «главный» выбранный объект: его свойства в панели Properties
        let selectedRefs = new Set();     // все выбранные (мультивыделение); selectedRef всегда входит сюда
        let selAnchorRef = null;          // от чего считается диапазон по Shift+клик
        let multiSelectMode = false;      // тап добавляет/убирает из выделения (для экранов без Ctrl/Shift)
        // Ref открытого сейчас в CodeMirror скрипта и его последний
        let currentScriptRef = null;
        let currentScriptOrigSource = null;
        async function saveCurrentScriptIfDirty() {
            if (currentScriptRef === null || !cmEditor) return;
            const src = cmEditor.getValue();
            if (src === currentScriptOrigSource) return; // ничего не поменялось — лишний запрос не нужен
            await api('POST', '/api/instance/' + currentScriptRef, { prop: 'Source', value: src });
            currentScriptOrigSource = src;
        }
        let expanded = new Set();
        let treeData = [];
        let searchText = '';
        let sceneObjs = {};
        let camera;
        let renderer;
        let scene;
        let raycaster;
        let mouse;
        let isDragging = false;
        let prevMouse = { x: 0, y: 0 };
        let spherical = { theta: Math.PI / 4, phi: Math.PI / 3, r: 30 };
        let target = { x: 0, y: 2, z: 0 };
        let keysPressed = {};
        let joyVector = { x: 0, y: 0 }; // аналоговый стик: x — влево/вправо, y — вперёд/назад
        let moveSpeed = 1.0;
        let fpsFrames = 0;
        acseration = 0;
        speed = 0;
        time_move = 0;
        let fpsTime = performance.now();
        let currentFPS = 0;
        let lastCameraUpdate = 0;
        const CAMERA_UPDATE_INTERVAL = 2000;
        let lastReloadTarget = { x: null, y: null, z: null };

        // Раньше подгрузка триггерилась только WASD-движением, да ещё с
        function maybeReloadNearby(now) {
            if (isPlaying) return; // у Play своя отдельная подгрузка вокруг персонажа
            if (now - lastCameraUpdate < CAMERA_UPDATE_INTERVAL) return;
            const moved = lastReloadTarget.x === null
                ? Infinity
                : Math.hypot(target.x - lastReloadTarget.x, target.y - lastReloadTarget.y, target.z - lastReloadTarget.z);
            const threshold = (qualitySettings.renderDistance || 300) * 0.25;
            if (moved < threshold) return;
            reloadScene();
        }

        // Кеш для raycasting
        let raycasterCache = {
            lastUpdate: 0,
            objects: [],
            updateInterval: 100
        };

        // ============ УВЕДОМЛЕНИЯ ============
        function notify(msg, type = 'ok') {
            const d = document.createElement('div');
            d.className = 'notif' + (type === 'err' ? ' err' : type === 'warn' ? ' warn' : '');
            d.textContent = msg;
            document.getElementById('notify').appendChild(d);
            setTimeout(() => d.remove(), 3000);
        }

        async function api(method, url, body) {
            const opts = {
                method: method,
                headers: { 'Content-Type': 'application/json' }
            };
            if (body) {
                opts.body = JSON.stringify(body);
            }
            const r = await fetch(url, opts);
            return r.json();
        }

        // ============ СВЕТ (дёшево по дизайну) ============
        // Почему не лагает: НИКАКИХ теневых карт и НИКАКИХ настоящих точечных
        // источников. MeshLambertMaterial в three r128 считает свет по вершинам,
        // поэтому PointLight на больших боксах всё равно выглядел бы криво, а
        // каждый такой источник — это ещё и пересборка шейдеров всех материалов.
        // Вместо этого: Hemisphere (+Directional «солнце» на medium/high) —
        // число источников зависит только от пресета и не меняется во время игры;
        // свет по настройкам карты (ClockTime, Brightness, Ambient) считается ОДИН
        // раз при загрузке карты, а не каждый кадр; лампы карты (PointLight/SpotLight)
        // рисуются как свечение — ВСЕ одним THREE.Points (1 draw call).
        let hemiLight = null, sunLight = null;
        let mapLighting = null;       // ответ /api/lighting (или null — карта без Lighting)
        let _glowTex = null;
        let _dayFactor = 1;           // 0 ночь .. 1 день — по ClockTime карты

        function _lerpN(a, b, t) { return a + (b - a) * t; }

        function buildSceneLights() {
            if (!scene) return;
            if (hemiLight) scene.remove(hemiLight);
            if (sunLight) scene.remove(sunLight);
            hemiLight = new THREE.HemisphereLight(0xffffff, 0x8a8a8a, qualitySettings.ambientLight);
            scene.add(hemiLight);
            sunLight = null;
            if (qualitySettings.dirLight > 0) {
                sunLight = new THREE.DirectionalLight(0xffffff, qualitySettings.dirLight);
                sunLight.position.set(20, 40, 20);
                scene.add(sunLight);
            }
            applyMapLighting();
            applyMapSky();   // low — без скайбокса, medium/high — с ним
        }

        function applyMapLighting() {
            if (!scene || !hemiLight) return;
            const ml = mapLighting && mapLighting.lighting;
            const sky = new THREE.Color(SKY_COLOR);
            const skyCol = new THREE.Color(0xffffff), gndCol = new THREE.Color(0x8a8a8a);
            const sunCol = new THREE.Color(1, 1, 1);
            const sunDir = new THREE.Vector3(20, 40, 20).normalize();
            let bright = 1;
            _dayFactor = 1;
            if (ml) {
                const ang = (ml.clockTime - 6) / 12 * Math.PI;        // 6ч восход, 12ч зенит, 18ч закат
                const elev = Math.sin(ang);
                let day = Math.max(0, Math.min(1, (elev + 0.1) / 0.4));
                day = day * day * (3 - 2 * day);                       // плавный рассвет/закат
                _dayFactor = day;
                sunDir.set(-Math.cos(ang), Math.max(elev, 0.05), 0.35).normalize();
                const warm = Math.max(0, Math.min(1, 1 - elev / 0.45)); // низкое солнце — тёплое
                sunCol.setRGB(1, _lerpN(1, 0.72, warm), _lerpN(1, 0.5, warm));
                // Ambient в Roblox тёмный (у него ещё есть свет неба) — подтягиваем к белому,
                // но не ниже пола, иначе сцена на телефоне станет чёрной.
                const oa = ml.outdoorAmbient || [0.5, 0.5, 0.5], am = ml.ambient || oa;
                const floorSky = sunLight ? 0.45 : 0.7, floorGnd = sunLight ? 0.25 : 0.4;
                skyCol.setRGB(Math.max(floorSky, _lerpN(oa[0], 1, 0.5)), Math.max(floorSky, _lerpN(oa[1], 1, 0.5)), Math.max(floorSky, _lerpN(oa[2], 1, 0.5)));
                gndCol.setRGB(Math.max(floorGnd, am[0] * 0.9), Math.max(floorGnd, am[1] * 0.9), Math.max(floorGnd, am[2] * 0.9));
                skyCol.lerp(new THREE.Color(0.22, 0.26, 0.42), (1 - day) * 0.8);   // ночью — синий полумрак
                gndCol.lerp(new THREE.Color(0.08, 0.09, 0.15), (1 - day) * 0.8);
                sky.lerp(new THREE.Color(0x0a1030), 1 - day);
                bright = Math.max(0.4, Math.min(1.6, ml.brightness / 2));
            }
            // ColorCorrectionEffect карты — без пост-обработки (она дорогая на телефоне): тон и яркость
            // запекаются в цвета света; контраст/насыщенность не воспроизводим.
            const cc = mapLighting && mapLighting.colorCorrection;
            if (cc) {
                const k = Math.max(0.5, 1 + cc.brightness);
                skyCol.multiply(new THREE.Color(cc.tint[0] * k, cc.tint[1] * k, cc.tint[2] * k));
                gndCol.multiply(new THREE.Color(cc.tint[0] * k, cc.tint[1] * k, cc.tint[2] * k));
                sunCol.multiply(new THREE.Color(cc.tint[0], cc.tint[1], cc.tint[2]));
            }
            hemiLight.color.copy(skyCol);
            hemiLight.groundColor.copy(gndCol);
            hemiLight.intensity = qualitySettings.ambientLight;
            if (sunLight) {
                sunLight.color.copy(sunCol);
                sunLight.position.copy(sunDir).multiplyScalar(100);
                sunLight.intensity = qualitySettings.dirLight * bright * _dayFactor;
            }
            // Небо/туман. Дальность тумана карты применяем только вне Play (в Play fog.far = дальность стриминга).
            currentSkyColor = sky.getHex();
            if (!_skyCube) {   // есть скайбокс карты — фон не трогаем
                if (scene.background && scene.background.isColor) scene.background.copy(sky);
                else scene.background = new THREE.Color(sky);
            }
            if (scene.fog) {
                scene.fog.color.copy(sky);
                if (ml && !isPlaying && ml.fogEnd < 50000 && ml.fogEnd > ml.fogStart) {
                    if (ml.fogColor) scene.fog.color.setRGB(ml.fogColor[0], ml.fogColor[1], ml.fogColor[2]);
                    scene.fog.near = Math.max(0, ml.fogStart);
                    scene.fog.far = Math.max(60, ml.fogEnd);
                }
            }
            rebuildMapGlow();
        }

        // Лампы карты: свечение-спрайт на лампу. Лампы делятся на три корзины по Range (размер пятна),
        // каждая корзина — ОДИН THREE.Points: итого не больше 3 draw call при любом числе ламп.
        let glowObjs = [];
        function rebuildMapGlow() {
            for (const g of glowObjs) { scene.remove(g); g.geometry.dispose(); g.material.dispose(); }
            glowObjs = [];
            const L = mapLighting && mapLighting.lights;
            if (!L || !L.length || currentQuality === 'low') return;
            if (!_glowTex) {
                const c = document.createElement('canvas');
                c.width = c.height = 64;
                const g = c.getContext('2d');
                const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
                grad.addColorStop(0, 'rgba(255,255,255,1)');
                grad.addColorStop(0.35, 'rgba(255,255,255,0.45)');
                grad.addColorStop(1, 'rgba(255,255,255,0)');
                g.fillStyle = grad;
                g.fillRect(0, 0, 64, 64);
                _glowTex = new THREE.CanvasTexture(c);
            }
            const vis = 0.45 + 0.55 * (1 - _dayFactor);   // ночью свечение заметнее
            const buckets = [{ size: 6, items: [] }, { size: 12, items: [] }, { size: 20, items: [] }];
            for (const l of L) buckets[l.range <= 10 ? 0 : (l.range <= 25 ? 1 : 2)].items.push(l);
            for (const bk of buckets) {
                if (!bk.items.length) continue;
                const pos = new Float32Array(bk.items.length * 3), col = new Float32Array(bk.items.length * 3);
                bk.items.forEach((l, i) => {
                    pos[i * 3] = l.x; pos[i * 3 + 1] = l.y; pos[i * 3 + 2] = l.z;
                    const k = Math.max(0.3, Math.min(1, 0.3 + l.b * 0.07)) * vis;
                    col[i * 3] = l.color[0] * k; col[i * 3 + 1] = l.color[1] * k; col[i * 3 + 2] = l.color[2] * k;
                });
                const geo = new THREE.BufferGeometry();
                geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
                geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
                const pts = new THREE.Points(geo, new THREE.PointsMaterial({
                    size: bk.size, sizeAttenuation: true, map: _glowTex, vertexColors: true,
                    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false,
                }));
                pts.renderOrder = 5;
                scene.add(pts);
                glowObjs.push(pts);
            }
        }

        // Скайбокс карты (Sky): куб из шести граней, грузится один раз при открытии карты — на кадр
        // не стоит ничего. Только medium/high. Порядок граней three: +X,-X,+Y,-Y,+Z,-Z = Rt,Lf,Up,Dn,Bk,Ft
        // (в Roblox Front смотрит в -Z, Back — в +Z). Нет сети/не загрузилось — остаётся цвет неба.
        let _skyCube = null, _skySig = '';
        function applyMapSky() {
            const sk = mapLighting && mapLighting.sky;
            const sig = (sk && currentQuality !== 'low') ? [sk.Rt, sk.Lf, sk.Up, sk.Dn, sk.Bk, sk.Ft].join(',') : '';
            if (sig === _skySig) return;
            _skySig = sig;
            if (_skyCube) { _skyCube.dispose(); _skyCube = null; }
            if (!sig) { applyMapLighting(); return; }
            const urls = [sk.Rt, sk.Lf, sk.Up, sk.Dn, sk.Bk, sk.Ft].map(id => '/api/asset-proxy?id=' + id);
            new THREE.CubeTextureLoader().load(urls, (cube) => {
                if (_skySig !== sig) { cube.dispose(); return; }  // за время загрузки карту сменили
                cube.encoding = THREE.sRGBEncoding;
                _skyCube = cube;
                scene.background = cube;
            }, undefined, () => { logLuaOutput('warn', t('warn_sky_failed')); });
        }

        async function refreshMapLighting() {
            let r = null;
            try { r = await api('GET', '/api/lighting'); } catch (e) { emuWarn('swallow:L1349', 'блок около script.js:1349: ' + _errText(e) + ' (без сети/сервера — свет по умолчанию)'); }
            mapLighting = (r && r.ok && r.found) ? r : null;
            applyMapLighting();
            applyMapSky();
        }

        // Круглая «тень» под игроком (вид от 3-го лица) — вместо теневых карт: 1 draw call,
        // 1 луч вниз раз в 2 кадра.
        let blobShadow = null, _blobFrame = 0;
        function _makeBlobShadow() {
            const geo = new THREE.CircleGeometry(1, 24);
            geo.rotateX(-Math.PI / 2);
            const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({
                color: 0x000000, transparent: true, opacity: 0.38, depthWrite: false, fog: false,
                polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
            }));
            m.renderOrder = 2;
            m.visible = false;
            return m;
        }
        function _disposeBlobShadow() {
            if (!blobShadow) return;
            scene.remove(blobShadow);
            blobShadow.geometry.dispose();
            blobShadow.material.dispose();
            blobShadow = null;
        }
        function updateBlobShadow() {
            if (!blobShadow || !charBody || !physicsWorld) return;
            if (!thirdPerson) { blobShadow.visible = false; return; }
            const x = charBody.position.x, y = charBody.position.y, z = charBody.position.z;
            if ((_blobFrame++ & 1) === 0) {
                const res = new CANNON.RaycastResult();
                physicsWorld.raycastClosest(new CANNON.Vec3(x, y, z), new CANNON.Vec3(x, y - 60, z),
                    { collisionFilterMask: _charRayMask(), skipBackfaces: true }, res);
                if (res.hasHit) {
                    const k = Math.max(0.35, 1 - (y - res.hitPointWorld.y) / 25); // выше от земли — меньше и бледнее
                    blobShadow.position.y = res.hitPointWorld.y + 0.06;
                    blobShadow.scale.setScalar(CHAR_RADIUS * 1.5 * k);
                    blobShadow.material.opacity = 0.38 * k;
                    blobShadow.visible = true;
                } else blobShadow.visible = false;
            }
            blobShadow.position.x = x;
            blobShadow.position.z = z;
        }

        // ============ THREE.JS INIT ============
        function initThree() {
            const vp = document.getElementById('viewport');

            renderer = new THREE.WebGLRenderer({
                antialias: qualitySettings.antialias,
                powerPreference: currentQuality === 'high' ? "high-performance" : "low-power",
                // highp на всех пресетах: mediump (16 бит) на мобильных GPU даёт мерцание/«помехи»
                // на моделях с анимацией и текстурами (аватар), а выигрыша по FPS почти нет.
                // Если GPU highp в шейдерах не умеет, three сам откатится на mediump.
                precision: "highp"
            });
            // ФИКС ЧЁТКОСТИ НА ТЕЛЕФОНЕ:
            applyPixelRatio();
            renderer.shadowMap.enabled = qualitySettings.shadows;
            vp.appendChild(renderer.domElement);

            // ВРЕМЕННАЯ ДИАГНОСТИКА:
            try {
                const dbgExt = renderer.getContext().getExtension('WEBGL_debug_renderer_info');
                const gpuInfo = dbgExt
                    ? renderer.getContext().getParameter(dbgExt.UNMASKED_RENDERER_WEBGL)
                    : 'н/д (расширение недоступно)';
                notify('GPU: ' + gpuInfo, 'warn');
                console.log('WebGL renderer:', gpuInfo);
            } catch (e) {
                console.log('Не удалось получить инфо о GPU:', e);
            }

            scene = new THREE.Scene();
            scene.background = new THREE.Color(currentSkyColor); // голубое небо вместо тёмно-синего/чёрного фона
            // qualitySettings.fog отключён на High (fog:false) — это ок для
            scene.fog = new THREE.Fog(currentSkyColor, 50, qualitySettings.fog ? 400 : qualitySettings.renderDistance);

            camera = new THREE.PerspectiveCamera(60, 1, 0.5, 500);

            // Инициализация raycaster с правильными настройками
            raycaster = new THREE.Raycaster();
            raycaster.params.Points.threshold = 0.1;
            raycaster.params.Line.threshold = 0.1;

            mouse = new THREE.Vector2();

            // Освещение
            buildSceneLights();

            updateHelpers();
            window._selBox = null;
            resize();
            window.addEventListener('resize', resize);

            // Мышь
            renderer.domElement.addEventListener('mousedown', onMD);
            renderer.domElement.addEventListener('mousemove', onMM);
            renderer.domElement.addEventListener('mouseup', onMU);
            renderer.domElement.addEventListener('wheel', onWh, { passive: false });
            renderer.domElement.addEventListener('contextmenu', e => e.preventDefault());

            // Тач
            renderer.domElement.addEventListener('touchstart', onTS, { passive: false });
            renderer.domElement.addEventListener('touchmove', onTM, { passive: false });
            renderer.domElement.addEventListener('touchend', onTE);

            updateCamera();
            animate();
            loadTree();

            // Фокус viewport для WASD
            vp.addEventListener('click', () => vp.focus());
            vp.focus();

            // Мобильный геймпад: кнопки вверх/вниз
            document.querySelectorAll('.pad-btn').forEach(btn => {
                const key = btn.dataset.key;
                btn.addEventListener('touchstart', e => {
                    e.preventDefault();
                    e.stopPropagation();
                    keysPressed[key] = true;
                    if (key === 'e') luaSetKeySrc('Space', 'virt', true);
                    if (isPlaying && key === 'e' && !luaControlsDisabled) jumpQueued = true;
                    btn.classList.add('active');
                }, { passive: false });
                ['touchend', 'touchcancel'].forEach(ev =>
                    btn.addEventListener(ev, e => {
                        e.preventDefault();
                        keysPressed[key] = false;
                        if (key === 'e') luaSetKeySrc('Space', 'virt', false);
                        btn.classList.remove('active');
                    }, { passive: false })
                );
            });

            // Мобильный геймпад: аналоговый стик движения
            initJoystick();
        }

        function initJoystick() {
            const zone = document.getElementById('joy-zone');
            const base = document.getElementById('joy-base');
            const thumb = document.getElementById('joy-thumb');
            if (!zone || !base || !thumb) return;
            const maxR = 30;   // px, максимальный вылет ручки стика от центра base
            const deadZone = 6; // px — маленький дрожащий сдвиг пальца не должен давать ход
            let touchId = null;

            function setThumb(dx, dy) {
                thumb.style.transform = 'translate(calc(-50% + ' + dx + 'px), calc(-50% + ' + dy + 'px))';
            }

            // "Всплывающий" стик: на touchstart сам круг базы переезжает
            function placeBase(clientX, clientY) {
                const zr = zone.getBoundingClientRect();
                // база квадратная 112×112, центрируем её на пальце, но не
                const half = 56;
                let localCX = clientX - zr.left;
                let localCY = clientY - zr.top;
                localCX = Math.max(half, Math.min(zr.width - half, localCX));
                localCY = Math.max(half, Math.min(zr.height - half, localCY));
                base.style.left = (localCX - half) + 'px';
                base.style.bottom = (zr.height - localCY - half) + 'px';
            }

            function handleMove(clientX, clientY) {
                const rect = base.getBoundingClientRect();
                const cx = rect.left + rect.width / 2;
                const cy = rect.top + rect.height / 2;
                let dx = clientX - cx;
                let dy = clientY - cy;
                const dist = Math.hypot(dx, dy);
                if (dist < deadZone) {
                    setThumb(0, 0);
                    joyVector.x = 0;
                    joyVector.y = 0;
                    return;
                }
                if (dist > maxR) {
                    dx = dx / dist * maxR;
                    dy = dy / dist * maxR;
                }
                setThumb(dx, dy);
                joyVector.x = dx / maxR;
                joyVector.y = -dy / maxR; // тянем вверх по экрану — едем вперёд
            }

            function resetJoy() {
                touchId = null;
                joyVector.x = 0;
                joyVector.y = 0;
                setThumb(0, 0);
                // возвращаем базу в исходный угол зоны для следующего касания
                base.style.left = '0px';
                base.style.bottom = '0px';
            }

            zone.addEventListener('touchstart', e => {
                e.preventDefault();
                e.stopPropagation();
                const t = e.changedTouches[0];
                touchId = t.identifier;
                placeBase(t.clientX, t.clientY);
                handleMove(t.clientX, t.clientY);
            }, { passive: false });

            zone.addEventListener('touchmove', e => {
                e.preventDefault();
                e.stopPropagation();
                for (const t of e.changedTouches) {
                    if (t.identifier === touchId) {
                        handleMove(t.clientX, t.clientY);
                        break;
                    }
                }
            }, { passive: false });

            ['touchend', 'touchcancel'].forEach(ev => zone.addEventListener(ev, e => {
                for (const t of e.changedTouches) {
                    if (t.identifier === touchId) {
                        resetJoy();
                        break;
                    }
                }
            }));
        }

        function updateHelpers() {
            if (window._gridHelper) {
                scene.remove(window._gridHelper);
                window._gridHelper = null;
            }
            if (window._axesHelper) {
                scene.remove(window._axesHelper);
                window._axesHelper = null;
            }
            if (qualitySettings.helpers) {
                window._gridHelper = new THREE.GridHelper(200, 40, 0x374151, 0x1f2937);
                window._axesHelper = new THREE.AxesHelper(5);
                scene.add(window._gridHelper);
                scene.add(window._axesHelper);
            }
        }

        function toggleHelpers() {
            qualitySettings.helpers = !qualitySettings.helpers;
            updateHelpers();
            notify(qualitySettings.helpers ? t('notify_helpers_on') : t('notify_helpers_off'));
        }

        // Максимальный DPR, который реально используем.
        function applyPixelRatio() {
            if (!renderer) return;
            const cap = currentQuality === 'high' ? 3 : currentQuality === 'medium' ? 1.5 : 1;
            const dpr = Math.min(window.devicePixelRatio || 1, cap);
            renderer.setPixelRatio(dpr);
        }

        function resize() {
            const vp = document.getElementById('viewport');
            const scale = qualitySettings.resolutionScale;
            const guiOverlayEl = document.getElementById('gui-overlay');
            // В Play зажимаем вьюпорт к 16:9 (letterbox чёрными полосами
            let cssW = vp.clientWidth, cssH = vp.clientHeight, offX = 0, offY = 0;
            if (typeof isPlaying !== 'undefined' && isPlaying) {
                const targetAspect = 16 / 9;
                const boxAspect = vp.clientWidth / Math.max(vp.clientHeight, 1);
                if (boxAspect > targetAspect) {
                    cssH = vp.clientHeight;
                    cssW = Math.floor(cssH * targetAspect);
                } else {
                    cssW = vp.clientWidth;
                    cssH = Math.floor(cssW / targetAspect);
                }
                offX = Math.floor((vp.clientWidth - cssW) / 2);
                offY = Math.floor((vp.clientHeight - cssH) / 2);
            }
            const w = Math.floor(cssW * scale);
            const h = Math.floor(cssH * scale);
            // ВАЖНО: setSize принимает CSS-размер (третий аргумент false —
            renderer.setSize(w, h, false);
            renderer.domElement.style.position = 'absolute';
            renderer.domElement.style.left = offX + 'px';
            renderer.domElement.style.top = offY + 'px';
            renderer.domElement.style.width = cssW + 'px';
            renderer.domElement.style.height = cssH + 'px';
            // #gui-overlay обязан покрывать РОВНО ту же область, что и
            if (guiOverlayEl) {
                guiOverlayEl.style.left = offX + 'px';
                guiOverlayEl.style.top = offY + 'px';
                guiOverlayEl.style.width = cssW + 'px';
                guiOverlayEl.style.height = cssH + 'px';
                guiOverlayEl.style.right = '';
                guiOverlayEl.style.bottom = '';
            }
            if (camera) {
                camera.aspect = w / Math.max(h, 1);
                camera.updateProjectionMatrix();
            }
        }

        // ============ АНИМАЦИЯ ============
        function animate() {
            requestAnimationFrame(animate);

            fpsFrames++;
            const now = performance.now();
            if (now - fpsTime >= 1000) {
                currentFPS = Math.round(fpsFrames / ((now - fpsTime) / 1000));
                // ВРЕМЕННАЯ ДИАГНОСТИКА:
                const _dbgPR = renderer ? renderer.getPixelRatio() : '?';
                const _dbgSize = renderer ? renderer.getSize(new THREE.Vector2()) : { x: '?', y: '?' };
                const _dbgAniso = renderer ? renderer.capabilities.getMaxAnisotropy() : '?';
                // Раньше тут был Object.keys(sceneObjs).length — общий
                let _visibleObjCount = 0;
                for (const _m of Object.values(sceneObjs)) {
                    if (_m.visible) _visibleObjCount++;
                }
                document.getElementById('fps-counter').textContent = 'FPS: ' + currentFPS + ' | ' + _visibleObjCount + ' obj' +
                    ' | PR:' + _dbgPR + ' | buf:' + Math.round(_dbgSize.x * _dbgPR) + 'x' + Math.round(_dbgSize.y * _dbgPR) +
                    ' | aniso:' + _dbgAniso + (isPlaying ? (' | loaded:' + Object.keys(physicsBodies).length) : '');
                fpsFrames = 0;
                fpsTime = now;
            }

            // WASD + аналоговый стик — свободный полёт камеры (только в режиме
            // редактирования; во время Play движением управляет 'тело' персонажа)
            if (!isPlaying) {
                const forward = Math.max(-1, Math.min(1,
                    (keysPressed['w'] ? 1 : 0) - (keysPressed['s'] ? 1 : 0) + joyVector.y));
                const strafe = Math.max(-1, Math.min(1,
                    (keysPressed['d'] ? 1 : 0) - (keysPressed['a'] ? 1 : 0) + joyVector.x));
                const vertical = (keysPressed['e'] ? 1 : 0) - (keysPressed['q'] ? 1 : 0);

                const anyMove = forward !== 0 || strafe !== 0 || vertical !== 0;


                if (anyMove) {


                    const direction = new THREE.Vector3();
                    camera.getWorldDirection(direction);
                    const right = new THREE.Vector3();
                    right.crossVectors(direction, new THREE.Vector3(0, 1, 0)).normalize();
                    speed = moveSpeed * (spherical.r / 30) * 0.25;
                    //acseration надо в правильный переменовать;
                    if (forward) {
                        acseration = acseration + 0.1;
                        if (acseration > 1) {
                            speed = speed + acseration / 50
                        }
                    }
                    if (now - time_move > 100) {
                        acseration = 0;
                    }
                    time_move = now



                    target.x += direction.x * speed * forward + right.x * speed * strafe;
                    target.z += direction.z * speed * forward + right.z * speed * strafe;
                    target.y += speed * vertical;

                    updateCamera();
                    maybeReloadNearby(now);
                }
            }

            // Раньше исключение внутри stepPhysics() (например, из-за плохих
            // данных от Lua-скрипта карты) улетало из animate() необработанным.
            // requestAnimationFrame(animate) уже был вызван строкой выше, так
            // что следующий кадр планировался и цикл не останавливался — но
            // если ошибка повторялась КАЖДЫЙ кадр (например, что-то на карте
            // стабильно портит один и тот же объект), физика и рендер той же
            // сцены молча не выполнялись НИ РАЗУ: экран замирал ("не идёт
            // время в игре"), а сама ошибка была видна только в консоли
            // браузера, до которой на телефоне не добраться. Теперь она
            // попадает в Output — и не спамит: одно и то же сообщение
            // печатается не чаще раза в 2 секунды, а рендер всё равно
            // пытаемся сделать отдельно, чтобы падение именно физики не
            // морозило картинку целиком.
            try {
                stepPhysics();
            } catch (e) {
                _reportFrameError('stepPhysics', e);
            }
            try {
                updateParticles(now);
            } catch (e) {
                _reportFrameError('particles', e);
            }
            try {
                renderer.render(scene, camera);
            } catch (e) {
                _reportFrameError('render', e);
            }
            if (isPlaying) {
                try { updateBillboardGuis(); } catch (e) { _reportFrameError('billboard', e); }
            }
        }
        let _lastFrameErrorMsg = null, _lastFrameErrorAt = 0;
        function _reportFrameError(where, e) {
            const msg = where + ': ' + (e && e.message || e);
            const now = performance.now();
            if (msg === _lastFrameErrorMsg && now - _lastFrameErrorAt < 2000) return;
            _lastFrameErrorMsg = msg;
            _lastFrameErrorAt = now;
            logLuaOutput('error', msg, null, e && e.stack || null);
        }

        let thirdPerson = false; // true — камера позади куба-персонажа, не в глазах
        const THIRD_PERSON_DIST = 12;
        // Дистанция камеры в Play — как у Roblox: от 0.5 до 128 студов (CameraMaxZoomDistance по умолчанию).
        let playCamDist = THIRD_PERSON_DIST;
        const PLAY_CAM_MIN = 0.5, PLAY_CAM_MAX = 128;
        // Щипок двумя пальцами: true — растягивать пальцы ПРИБЛИЖАЕТ камеру, сводить — отдаляет;
        // false — наоборот. (Колёсико мыши не затрагивается: вниз — отдаляет.)
        const PINCH_SPREAD_ZOOMS_IN = true;
        function applyPlayZoom(factor) {   // factor > 1 — отдаляем, < 1 — приближаем
            if (!isFinite(factor) || factor <= 0) return;
            if (!thirdPerson) {
                if (factor <= 1) return;               // уже вплотную (первое лицо)
                thirdPerson = true; playCamDist = 1.5; // отдаляем от первого лица — выходим в третье
                if (charMesh) charMesh.visible = true;
            }
            playCamDist = Math.max(PLAY_CAM_MIN, Math.min(PLAY_CAM_MAX, playCamDist * factor));
            if (playCamDist <= 0.8 && factor < 1) {    // вплотную — снова первое лицо, как в Roblox
                thirdPerson = false;
                if (charMesh) charMesh.visible = false;
            }
            updateCamera();
        }

        function updateCamera() {
            const { theta, phi } = spherical;
            const dirX = Math.sin(phi) * Math.sin(theta);
            const dirY = Math.cos(phi);
            const dirZ = Math.sin(phi) * Math.cos(theta);
            if (isPlaying && thirdPerson) {
                // dir — направление "назад" (см.
                camera.position.set(target.x + dirX * playCamDist, target.y + dirY * playCamDist, target.z + dirZ * playCamDist);
                camera.lookAt(target.x, target.y, target.z);
            } else {
                // Камера от первого лица: позиция глаза = target,
                // смотрим в направлении, заданном theta/phi (без отступа на радиус r)
                camera.position.set(target.x, target.y, target.z);
                camera.lookAt(target.x - dirX, target.y - dirY, target.z - dirZ);
            }
            updateCharMeshVisibility();
        }

        function toggleThirdPerson() {
            thirdPerson = !thirdPerson;
            if (thirdPerson && playCamDist < 1) playCamDist = THIRD_PERSON_DIST;
            updateCamera();
            notify(thirdPerson ? t('cam_third') : t('cam_first'));
        }

        // ============ ПРЕСЕТЫ КАМЕРЫ ============
        function resetCamera() {
            spherical = { theta: Math.PI / 4, phi: Math.PI / 3, r: 30 };
            target = { x: 0, y: 2, z: 0 };
            updateCamera();
            notify(t('notify_camera_reset'));
        }

        function topView() {
            spherical = { theta: 0, phi: 0.01, r: spherical.r };
            updateCamera();
            notify(t('notify_topview'));
        }

        function frontView() {
            spherical = { theta: 0, phi: Math.PI / 2, r: spherical.r };
            updateCamera();
            notify(t('notify_frontview'));
        }

        function rightView() {
            spherical = { theta: Math.PI / 2, phi: Math.PI / 2, r: spherical.r };
            updateCamera();
            notify(t('notify_rightview'));
        }

        // Телепорт камеры редактора к выбранному в Explorer объекту —
        function teleportCameraToSelected() {
            if (selectedRef === null || !sceneObjs[selectedRef]) {
                notify(t('notify_teleport_no_selection'), 'warn');
                return;
            }
            const pos = sceneObjs[selectedRef].position;
            target = { x: pos.x, y: pos.y, z: pos.z };
            if (spherical.r > 25) spherical.r = 20;
            updateCamera();
            notify(t('notify_teleported'));
        }

        // ============ МЫШЬ ============
        function onMD(e) {
            isDragging = false;
            prevMouse = { x: e.clientX, y: e.clientY };
        }

        function onMM(e) {
            if (!e.buttons) return;
            if (isPlaying && luaControlsDisabled) return; // PlayerModule:GetControls():Disable() — камера тоже не должна крутиться
            if (isPlaying && cameraIsScriptable) return; // как в Roblox: Scriptable-камеру игрок не крутит — ею управляет скрипт

            const dx = e.clientX - prevMouse.x;
            const dy = e.clientY - prevMouse.y;
            prevMouse = { x: e.clientX, y: e.clientY };

            if (Math.abs(dx) + Math.abs(dy) > 3) {
                isDragging = true;
            }

            if (e.buttons === 1) {
                spherical.theta -= dx * .005;
                spherical.phi = Math.max(.05, Math.min(Math.PI - .05, spherical.phi - dy * .005));
            } else if (e.buttons === 2 || e.buttons === 4) {
                const direction = new THREE.Vector3();
                camera.getWorldDirection(direction);
                const right = new THREE.Vector3();
                right.crossVectors(direction, new THREE.Vector3(0, 1, 0)).normalize();
                const up = new THREE.Vector3();
                up.crossVectors(right, direction).normalize();

                const panSpeed = spherical.r * 0.002;
                target.x -= right.x * dx * panSpeed + up.x * dy * panSpeed;
                target.y -= up.y * dy * panSpeed;
                target.z -= right.z * dx * panSpeed + up.z * dy * panSpeed;
                maybeReloadNearby(performance.now());
            }

            updateCamera();
        }

        // После тапа браузер ещё присылает «синтетические» mousedown/mouseup/click — без этой
        // защиты тот же тап обрабатывался дважды (ClickDetector срабатывал и сразу же выделялся объект).
        let _lastTouchEndT = -1e9;
        function onMU(e) {
            if (performance.now() - _lastTouchEndT < 700) return;
            if (!isDragging && (e.button === 0 || e.button === 2) && isPlaying && luaClickDetectorAt(e.clientX, e.clientY, e.button === 2, false)) return;
            if (!isDragging && e.button === 0) {
                pick(e.clientX, e.clientY, { additive: e.ctrlKey || e.metaKey || multiSelectMode });
            }
        }

        function onWh(e) {
            e.preventDefault();

            if (e.shiftKey) {
                moveSpeed = Math.max(0.1, Math.min(10, moveSpeed - e.deltaY * 0.01));
                const indicator = document.getElementById('speed-indicator');
                indicator.textContent = '🚀 x' + moveSpeed.toFixed(1);
                indicator.style.display = 'block';
                clearTimeout(window._speedTimeout);
                window._speedTimeout = setTimeout(() => {
                    indicator.style.display = 'none';
                }, 1500);
                return;
            }

            if (isPlaying && !luaControlsDisabled && !cameraIsScriptable) {
                applyPlayZoom(Math.pow(1.1, (PINCH_SPREAD_ZOOMS_IN ? 1 : 1) * e.deltaY / 100));
                return;
            }
            // r больше не двигает камеру (вид от 1-го лица), но всё ещё
            // задаёт дальность подгрузки сцены и скорость панорамирования
            spherical.r = Math.max(1, Math.min(500, spherical.r + e.deltaY * .05));
        }

        // ============ ТАЧ ============
        let _tch = [];
        let _td = 0;
        let _ts = null;

        function onTS(e) {
            e.preventDefault();
            // targetTouches — только касания НА ЭТОМ элементе (вьюпорт).
            _tch = Array.from(e.targetTouches);
            _ts = _tch[0] ? { x: _tch[0].clientX, y: _tch[0].clientY } : null;
            if (e.targetTouches.length === 2) {
                const dx = e.targetTouches[0].clientX - e.targetTouches[1].clientX;
                const dy = e.targetTouches[0].clientY - e.targetTouches[1].clientY;
                _td = Math.sqrt(dx * dx + dy * dy);
            }
        }

        function onTM(e) {
            e.preventDefault();
            if (isPlaying && luaControlsDisabled) return; // PlayerModule:GetControls():Disable() — та же блокировка, что и для мыши (onMM)
            if (isPlaying && cameraIsScriptable) return; // то же для касаний (Scriptable-камеру не крутим)
            if (e.targetTouches.length === 1) {
                const t = e.targetTouches[0];
                if (!_tch[0]) { _tch = [t]; return; }
                const dx = t.clientX - _tch[0].clientX;
                const dy = t.clientY - _tch[0].clientY;
                _tch = Array.from(e.targetTouches);
                spherical.theta -= dx * .005;
                spherical.phi = Math.max(.05, Math.min(Math.PI - .05, spherical.phi - dy * .005));
                updateCamera();
            } else if (e.targetTouches.length === 2) {
                const dx = e.targetTouches[0].clientX - e.targetTouches[1].clientX;
                const dy = e.targetTouches[0].clientY - e.targetTouches[1].clientY;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (isPlaying) {
                    if (_td > 0 && dist > 0) applyPlayZoom(PINCH_SPREAD_ZOOMS_IN ? _td / dist : dist / _td);
                    _td = dist;
                    _tch = Array.from(e.targetTouches);
                    return;
                }
                spherical.r = Math.max(1, Math.min(500, spherical.r + (dist - _td) * .05));
                _td = dist;
                _tch = Array.from(e.targetTouches);
                updateCamera();
            }
        }

        function onTE(e) {
            _lastTouchEndT = performance.now();
            if (e.changedTouches.length === 1 && _ts) {
                const t = e.changedTouches[0];
                if (Math.abs(t.clientX - _ts.x) < 8 && Math.abs(t.clientY - _ts.y) < 8) {
                    if (isPlaying && luaClickDetectorAt(t.clientX, t.clientY, false, true)) return;
                    pick(t.clientX, t.clientY, { additive: multiSelectMode });
                }
            }
        }

        // ============ ИСПРАВЛЕННЫЙ PICK ============
        function pick(cx, cy, opts) {
            const vp = document.getElementById('viewport');
            const rect = vp.getBoundingClientRect();
            mouse.x = ((cx - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((cy - rect.top) / rect.height) * 2 + 1;

            // Пересоздаем raycaster если нужно
            if (!raycaster) {
                raycaster = new THREE.Raycaster();
                raycaster.params.Points.threshold = 0.1;
                raycaster.params.Line.threshold = 0.1;
            }

            raycaster.setFromCamera(mouse, camera);

            // Обновляем кеш объектов для raycasting
            const now = performance.now();
            let objectsToCheck;

            if (now - raycasterCache.lastUpdate > raycasterCache.updateInterval) {
                raycasterCache.objects = Object.values(sceneObjs);
                raycasterCache.lastUpdate = now;
            }
            objectsToCheck = raycasterCache.objects;

            // Для low/medium с большим количеством объектов - оптимизация
            if (currentQuality !== 'high' && objectsToCheck.length > 2000) {
                objectsToCheck = objectsToCheck
                    .map(obj => ({
                        obj: obj,
                        dist: obj.position.distanceToSquared(camera.position)
                    }))
                    .sort((a, b) => a.dist - b.dist)
                    .slice(0, 2000)
                    .map(item => item.obj);
            }

            // recursive: true — обычным Mesh'ам без детей это ничего не
            const hits = raycaster.intersectObjects(objectsToCheck, true);

            if (hits.length) {
                // У аватара userData.ref есть только на корневой Group —
                let obj = hits[0].object;
                while (obj && !(obj.userData && obj.userData.ref)) {
                    obj = obj.parent;
                }
                if (obj && obj.userData && obj.userData.ref) {
                    selectRef(parseInt(obj.userData.ref), opts);
                    return;
                }
            }

            // Мимо объекта с зажатым Ctrl / в режиме мультивыбора выделение не сбрасываем.
            if (!(opts && opts.additive)) deselect();
        }

        // Геометрия WedgePart (клин/скат). Конвенция Roblox: BackSurface — это +Z
        // (полная прямоугольная грань), FrontSurface — -Z (высота сходится в ребро).
        function makeWedgeGeometry(sx, sy, sz) {
            const hx = sx / 2, hy = sy / 2, hz = sz / 2;
            const BBL = [-hx, -hy, hz], BBR = [hx, -hy, hz];
            const BTL = [-hx, hy, hz], BTR = [hx, hy, hz];
            const FBL = [-hx, -hy, -hz], FBR = [hx, -hy, -hz];
            const tris = [
                BBL, BTR, BTL,   // задняя грань (полная, +Z)
                BBL, BBR, BTR,
                BBL, FBL, FBR,   // низ
                BBL, FBR, BBR,
                BBL, BTL, FBL,   // левая треугольная грань
                BBR, FBR, BTR,   // правая треугольная грань
                BTL, FBR, FBL,   // скат
                BTL, BTR, FBR,
            ];
            const positions = new Float32Array(tris.length * 3);
            tris.forEach((v, i) => positions.set(v, i * 3));
            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geo.computeVertexNormals();
            return geo;
        }

        // SpecialMesh MeshType.Head — скруглённый цилиндр (голова R6), ось Y.
        function makeHeadGeometry(sx, sy, sz, seg) {
            const R = 0.5, rc = 0.22; // радиус скругления кромок (в долях размера)
            const pts = [new THREE.Vector2(0, -0.5), new THREE.Vector2(R - rc, -0.5)];
            const arcN = 5;
            for (let i = 1; i <= arcN; i++) { // нижнее скругление
                const a = -Math.PI / 2 + (i / arcN) * (Math.PI / 2);
                pts.push(new THREE.Vector2(R - rc + Math.cos(a) * rc, -0.5 + rc + Math.sin(a) * rc));
            }
            for (let i = 0; i <= arcN; i++) { // верхнее скругление
                const a = (i / arcN) * (Math.PI / 2);
                pts.push(new THREE.Vector2(R - rc + Math.cos(a) * rc, 0.5 - rc + Math.sin(a) * rc));
            }
            pts.push(new THREE.Vector2(0, 0.5));
            const geo = new THREE.LatheGeometry(pts, Math.max(8, seg));
            geo.applyMatrix4(new THREE.Matrix4().makeScale(sx, sy, sz)); // applyMatrix4 сам поправит нормали
            return geo;
        }
        // Part.Shape = Cylinder: ось цилиндра вдоль X (а не Y, как у MeshType.Cylinder).
        function makeCylinderXGeometry(sx, sy, sz, seg) {
            const geo = new THREE.CylinderGeometry(0.5, 0.5, 1, Math.max(8, seg));
            geo.rotateZ(Math.PI / 2);
            geo.applyMatrix4(new THREE.Matrix4().makeScale(sx, sy, sz));
            return geo;
        }

        // ============ ЗАГРУЗКА РЕАЛЬНОЙ ГЕОМЕТРИИ MeshPart/SpecialMesh(FileMesh) ============
        const _meshGeometryCache = {}; // meshId -> Promise<{geometry, size}|null>

        function _parseRobloxMeshV1(text) {
            // БАГ, из-за которого валился как минимум 514528468 (старый
            const body = text.replace(/^\s*version[^\n]*\n?/i, '');
            const nums = body.match(/-?[\d.]+(?:[eE][-+]?\d+)?/g);
            if (!nums || nums.length < 2) return null;
            const numFaces = parseInt(nums[0], 10);
            if (!numFaces) return null;
            const coords = nums.slice(1).map(Number);
            const need = numFaces * 3 * 9; // 3 вершины/грань × (pos3+norm3+uv3)
            if (coords.length < need) return null;
            const positions = new Float32Array(numFaces * 9);
            const normals = new Float32Array(numFaces * 9);
            const uvs = new Float32Array(numFaces * 6);
            let ci = 0, pi = 0, ni = 0, ui = 0;
            for (let f = 0; f < numFaces; f++) {
                for (let v = 0; v < 3; v++) {
                    positions[pi++] = coords[ci++]; positions[pi++] = coords[ci++]; positions[pi++] = coords[ci++];
                    normals[ni++] = coords[ci++]; normals[ni++] = coords[ci++]; normals[ni++] = coords[ci++];
                    uvs[ui++] = coords[ci++]; uvs[ui++] = coords[ci++]; ci++; // третье число UV-тройки не используется. V больше НЕ переворачиваем — переворот никогда не был подтверждён на реальном Roblox-файле (проверялся только на моих же синтетических данных), а на реальном меше развёртка легла неверно именно с ним
                }
            }
            return { positions, normals, uvs, indices: null };
        }

        // Точная структура v2.00 (получена из реверс-инжиниринга
        function _tryParseV2At(dv, buf, stub, vertSizeArg, vertOffArg) {
            const numVerts = dv.getUint32(stub, true);
            const numFaces = dv.getUint32(stub + 4, true);
            const vertSize = vertSizeArg || 36, faceSize = 12;
            const vertOff = vertOffArg != null ? vertOffArg : stub + 8;
            if (!numVerts || !numFaces || numVerts > 2_000_000 || numFaces > 2_000_000) return null;
            const needBytes = vertOff + numVerts * vertSize + numFaces * faceSize;
            if (needBytes > buf.byteLength) return null;
            const positions = new Float32Array(numVerts * 3);
            const normals = new Float32Array(numVerts * 3);
            const uvs = new Float32Array(numVerts * 2);
            for (let i = 0; i < numVerts; i++) {
                const base = vertOff + i * vertSize;
                positions[i * 3] = dv.getFloat32(base, true);
                positions[i * 3 + 1] = dv.getFloat32(base + 4, true);
                positions[i * 3 + 2] = dv.getFloat32(base + 8, true);
                normals[i * 3] = dv.getFloat32(base + 12, true);
                normals[i * 3 + 1] = dv.getFloat32(base + 16, true);
                normals[i * 3 + 2] = dv.getFloat32(base + 20, true);
                uvs[i * 2] = dv.getFloat32(base + 24, true);
                uvs[i * 2 + 1] = dv.getFloat32(base + 28, true);
                // base+32..35 — третье число UV-тройки (W), не используется.
            }
            const faceOff = vertOff + numVerts * vertSize;
            const indices = new Uint32Array(numFaces * 3);
            for (let i = 0; i < numFaces; i++) {
                const base = faceOff + i * faceSize;
                indices[i * 3] = dv.getUint32(base, true);
                indices[i * 3 + 1] = dv.getUint32(base + 4, true);
                indices[i * 3 + 2] = dv.getUint32(base + 8, true);
            }
            for (let i = 0; i < indices.length; i++) {
                if (indices[i] >= numVerts) return null;
            }
            return { positions, normals, uvs, indices };
        }
        function _tryParseV3(dv, buf, hdrSize, vertSize, nLod) {
            const numVerts = dv.getUint32(8, true), numFaces = dv.getUint32(12, true);
            if (!numVerts || !numFaces || numVerts > 2_000_000 || numFaces > 2_000_000) return null;
            const faceOff = hdrSize + numVerts * vertSize;
            const lodOff = faceOff + numFaces * 12;
            if (lodOff + nLod * 4 > buf.byteLength) return null;
            const positions = new Float32Array(numVerts * 3);
            const normals = new Float32Array(numVerts * 3);
            const uvs = new Float32Array(numVerts * 2);
            for (let i = 0; i < numVerts; i++) {
                const base = hdrSize + i * vertSize;
                for (let k = 0; k < 3; k++) {
                    positions[i * 3 + k] = dv.getFloat32(base + k * 4, true);
                    normals[i * 3 + k] = dv.getFloat32(base + 12 + k * 4, true);
                }
                uvs[i * 2] = dv.getFloat32(base + 24, true);
                uvs[i * 2 + 1] = dv.getFloat32(base + 28, true);
            }
            let f0 = 0, f1 = numFaces;
            if (nLod >= 2) {
                const a = dv.getUint32(lodOff, true), b = dv.getUint32(lodOff + 4, true);
                if (a < b && b <= numFaces) { f0 = a; f1 = b; }
            }
            const indices = new Uint32Array((f1 - f0) * 3);
            for (let i = 0; i < indices.length; i++) {
                indices[i] = dv.getUint32(faceOff + f0 * 12 + i * 4, true);
                if (indices[i] >= numVerts) return null;
            }
            return { positions, normals, uvs, indices };
        }
        function _parseRobloxMeshBinary(buf) {
            const dv = new DataView(buf);
            // 5 байт — подтверждённый реальной документацией размер
            const dbg = 'bufLen=' + buf.byteLength;
            if (buf.byteLength < 13) { _lastMeshParseFailReason = 'буфер короче минимального заголовка v2.00 (' + dbg + ')'; return null; }
            // Заголовок v2.00: u16 sizeof_Header (=12), u8 sizeof_Vertex (36, либо 40 — с цветом вершины),
            // u8 sizeof_Face (=12), u32 numVerts, u32 numFaces; данные вершин начинаются с sizeof_Header.
            if (buf.byteLength >= 16) {
                // Заголовок v3.00 (16 байт): u16 sizeof_Header, u8 sizeof_Vertex (40), u8 sizeof_Face (12),
                // u16 sizeof_LodOffset (4), u16 numLodOffsets, u32 numVerts, u32 numFaces. Счётчики лежат со смещения 8,
                // а не 4, как в v2 — раньше v3 шёл через v2-разбор и падал «ни один вариант заглушки не подошёл».
                // После граней идут numLodOffsets смещений LOD (индексы граней): рисуем только LOD0 = [lod[0], lod[1]).
                const hs = dv.getUint16(0, true), vs = dv.getUint8(2), fs = dv.getUint8(3);
                const lodSz = dv.getUint16(4, true), nLod = dv.getUint16(6, true);
                if (hs === 16 && vs >= 32 && vs <= 64 && fs === 12 && lodSz === 4) {
                    const r3 = _tryParseV3(dv, buf, hs, vs, nLod);
                    if (r3) return r3;
                }
            }
            if (buf.byteLength >= 12) {
                const hdrSize = dv.getUint16(0, true), vSize = dv.getUint8(2), fSize = dv.getUint8(3);
                if (hdrSize >= 12 && hdrSize <= 64 && vSize >= 32 && vSize <= 64 && fSize === 12) {
                    const result = _tryParseV2At(dv, buf, 4, vSize, hdrSize);
                    if (result) return result;
                }
            }
            for (const stub of [5, 0, 4, 6]) {
                if (stub + 8 > buf.byteLength) continue;
                const result = _tryParseV2At(dv, buf, stub);
                if (result) return result;
            }
            _lastMeshParseFailReason = 'ни один вариант заглушки (5/0/4/6 байт) не подошёл (' + dbg + ')';
            return null;
        }

        // Форматы 4.00/4.01 (и, по той же структуре, 5.00/6.00) — с этой
        let _lastMeshParseFailReason = '';
        const failedMeshIds = new Set();   // меши, которые не удалось разобрать (для кнопки в Account)
        function _tryParseV4Layout(dv, buf, vertOff, vertSize, numVerts, numFaces, dbg) {
            const faceOff = vertOff + numVerts * vertSize;
            const needBytes = faceOff + numFaces * 12;
            if (needBytes > buf.byteLength) return null; // не влезает — точно не тот вариант
            const positions = new Float32Array(numVerts * 3);
            const normals = new Float32Array(numVerts * 3);
            const uvs = new Float32Array(numVerts * 2);
            for (let i = 0; i < numVerts; i++) {
                const base = vertOff + i * vertSize;
                positions[i * 3] = dv.getFloat32(base, true);
                positions[i * 3 + 1] = dv.getFloat32(base + 4, true);
                positions[i * 3 + 2] = dv.getFloat32(base + 8, true);
                normals[i * 3] = dv.getFloat32(base + 12, true);
                normals[i * 3 + 1] = dv.getFloat32(base + 16, true);
                normals[i * 3 + 2] = dv.getFloat32(base + 20, true);
                uvs[i * 2] = dv.getFloat32(base + 24, true);
                // ТОЛЬКО для v4.00+ переворот V возвращён обратно:
                uvs[i * 2 + 1] = 1 - dv.getFloat32(base + 28, true);
            }
            const indices = new Uint32Array(numFaces * 3);
            for (let i = 0; i < numFaces; i++) {
                const base = faceOff + i * 12;
                indices[i * 3] = dv.getUint32(base, true);
                indices[i * 3 + 1] = dv.getUint32(base + 4, true);
                indices[i * 3 + 2] = dv.getUint32(base + 8, true);
            }
            // Проверка непротиворечивости:
            for (let i = 0; i < indices.length; i++) {
                if (indices[i] >= numVerts) return null;
            }
            // Этой проверки одной оказалось МАЛО:
            let normalOk = 0, uvOk = 0;
            for (let i = 0; i < numVerts; i++) {
                const nx = normals[i * 3], ny = normals[i * 3 + 1], nz = normals[i * 3 + 2];
                const nlen = Math.sqrt(nx * nx + ny * ny + nz * nz);
                if (nlen > 0.5 && nlen < 1.5) normalOk++;
                const u = uvs[i * 2], v = uvs[i * 2 + 1];
                if (u > -0.5 && u < 1.5 && v > -0.5 && v < 1.5) uvOk++;
            }
            if (normalOk / numVerts < 0.7 || uvOk / numVerts < 0.7) return null;
            return { positions, normals, uvs, indices };
        }
        // Точная раскладка v4.00/v4.01 (проверена на реальных файлах):
        //   header(24) | vertices numVerts*40 | [envelope numVerts*8, если есть кости] |
        //   faces numFaces*12 | LOD-офсеты numLODs*u32 | ...
        // Вершина = 40 байт: pos(12) norm(12) uv(8) tangent(4) color(4).
        // ВАЖНО: numFaces — это грани ВСЕХ уровней детализации подряд, а
        // lods[i]..lods[i+1] — диапазон граней i-го LOD. Раньше рисовались
        // все LOD сразу (грубые копии поверх LOD0) — отсюда «рваные»
        // головы/шапки с полосами и наслоением текстуры.
        function _tryParseV4Exact(dv, buf, sizeofHeader, numVerts, numFaces, numLODs, numBones) {
            const vertSize = 40;
            const vertOff = sizeofHeader;
            const faceOff = vertOff + numVerts * vertSize + (numBones > 0 ? numVerts * 8 : 0);
            const lodOff = faceOff + numFaces * 12;
            if (lodOff > buf.byteLength) return null;
            let faceStart = 0, faceEnd = numFaces;
            if (numLODs >= 2 && lodOff + numLODs * 4 <= buf.byteLength) {
                const l0 = dv.getUint32(lodOff, true), l1 = dv.getUint32(lodOff + 4, true);
                if (l0 === 0 && l1 > 0 && l1 <= numFaces) { faceStart = l0; faceEnd = l1; }
            }
            const positions = new Float32Array(numVerts * 3);
            const normals = new Float32Array(numVerts * 3);
            const uvs = new Float32Array(numVerts * 2);
            for (let i = 0; i < numVerts; i++) {
                const base = vertOff + i * vertSize;
                positions[i * 3] = dv.getFloat32(base, true);
                positions[i * 3 + 1] = dv.getFloat32(base + 4, true);
                positions[i * 3 + 2] = dv.getFloat32(base + 8, true);
                normals[i * 3] = dv.getFloat32(base + 12, true);
                normals[i * 3 + 1] = dv.getFloat32(base + 16, true);
                normals[i * 3 + 2] = dv.getFloat32(base + 20, true);
                uvs[i * 2] = dv.getFloat32(base + 24, true);
                uvs[i * 2 + 1] = 1 - dv.getFloat32(base + 28, true);
            }
            const n = faceEnd - faceStart;
            const indices = new Uint32Array(n * 3);
            for (let i = 0; i < n; i++) {
                const base = faceOff + (faceStart + i) * 12;
                indices[i * 3] = dv.getUint32(base, true);
                indices[i * 3 + 1] = dv.getUint32(base + 4, true);
                indices[i * 3 + 2] = dv.getUint32(base + 8, true);
            }
            for (let i = 0; i < indices.length; i++) if (indices[i] >= numVerts) return null;
            return { positions, normals, uvs, indices };
        }
        function _parseRobloxMeshV4(buf) {
            if (buf.byteLength < 24) { _lastMeshParseFailReason = 'буфер короче 24 байт (' + buf.byteLength + ')'; return null; }
            const dv = new DataView(buf);
            const sizeofHeader = dv.getUint16(0, true);
            const lodType = dv.getUint16(2, true);
            const numVerts = dv.getUint32(4, true);
            const numFaces = dv.getUint32(8, true);
            const numLODs = dv.getUint16(12, true);
            const numBones = dv.getUint16(14, true);
            const dbg = 'sizeofHeader=' + sizeofHeader + ' lodType=' + lodType + ' numVerts=' + numVerts +
                ' numFaces=' + numFaces + ' numLODs=' + numLODs + ' numBones=' + numBones + ' bufLen=' + buf.byteLength;
            if (sizeofHeader < 24 || sizeofHeader > 64) { _lastMeshParseFailReason = 'sizeofHeader вне диапазона 24-64 (' + dbg + ')'; return null; }
            if (!numVerts || !numFaces || numVerts > 2_000_000 || numFaces > 2_000_000) { _lastMeshParseFailReason = 'numVerts/numFaces нулевые или огромные (' + dbg + ')'; return null; }
            const exact = _tryParseV4Exact(dv, buf, sizeofHeader, numVerts, numFaces, numLODs, numBones);
            if (exact) return exact;
            // Точная раскладка не подошла — старый перебор вариантов как запасной путь.
            // Реальные диагностические данные с телефона (см.
            const vertOffCandidates = numLODs > 0
                ? [sizeofHeader + numLODs * 4, sizeofHeader + numLODs * 8, sizeofHeader]
                : [sizeofHeader];
            const vertSizeCandidates = numBones > 0 ? [44, 48] : [36, 40];
            for (const vertOff of vertOffCandidates) {
                for (const vertSize of vertSizeCandidates) {
                    const result = _tryParseV4Layout(dv, buf, vertOff, vertSize, numVerts, numFaces, dbg);
                    if (result) return result;
                }
            }
            _lastMeshParseFailReason = 'ни один из вариантов офсета/размера вершины не сошёлся (' + dbg +
                ' испробованы vertOff=[' + vertOffCandidates.join(',') + '] vertSize=[' + vertSizeCandidates.join(',') + '])';
            return null;
        }

        function _buildGeometryFromParsed(parsed) {
            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', new THREE.BufferAttribute(parsed.positions, 3));
            geo.setAttribute('normal', new THREE.BufferAttribute(parsed.normals, 3));
            geo.setAttribute('uv', new THREE.BufferAttribute(parsed.uvs, 2));
            if (parsed.indices) geo.setIndex(new THREE.BufferAttribute(parsed.indices, 1));
            if (!parsed.normals.some(n => n !== 0)) geo.computeVertexNormals();
            geo.computeBoundingBox();
            const bb = geo.boundingBox;
            const size = {
                x: Math.max(0.001, bb.max.x - bb.min.x),
                y: Math.max(0.001, bb.max.y - bb.min.y),
                z: Math.max(0.001, bb.max.z - bb.min.z),
            };
            // Помечаем как разделяемую между несколькими частями с одним
            geo.userData.sharedMesh = true;
            return { geometry: geo, size };
        }

        // ============ v7.00 — Draco-компрессия ============
        let _dracoModulePromise = null;
        function _loadDracoModule() {
            if (!_dracoModulePromise) {
                _dracoModulePromise = new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.src = 'https://www.gstatic.com/draco/versioned/decoders/1.5.6/draco_decoder.js';
                    script.onload = () => {
                        if (typeof DracoDecoderModule !== 'function') { reject(new Error('DracoDecoderModule не появился после загрузки скрипта')); return; }
                        DracoDecoderModule().then(resolve).catch(reject);
                    };
                    script.onerror = () => reject(new Error('не удалось загрузить draco_decoder.js с CDN'));
                    document.head.appendChild(script);
                });
            }
            return _dracoModulePromise;
        }
        function _tryDecodeDracoAt(decoderModule, bytes, offset, length) {
            const decoder = new decoderModule.Decoder();
            const dracoBuffer = new decoderModule.DecoderBuffer();
            try {
                // length — точная длина Draco-потока из заголовка COREMESH
                // (см. _parseRobloxMeshDraco), если известна: раньше сюда
                // всегда уходил "остаток буфера", то есть Draco читал и
                // байты следующего чанка (LODS) как будто они ещё часть
                // потока — теперь передаём ровно столько, сколько указано.
                const end = length != null ? offset + length : bytes.length;
                dracoBuffer.Init(bytes.subarray(offset, end), end - offset);
                const geomType = decoder.GetEncodedGeometryType(dracoBuffer);
                if (geomType !== decoderModule.TRIANGULAR_MESH) return null;
                const mesh = new decoderModule.Mesh();
                const status = decoder.DecodeBufferToMesh(dracoBuffer, mesh);
                if (!status.ok() || mesh.num_faces() <= 0 || mesh.num_points() <= 0) {
                    decoderModule.destroy(mesh);
                    return null;
                }
                const numPoints = mesh.num_points();
                const numFaces = mesh.num_faces();
                function readAttr(attrType, numComponents) {
                    const attrId = decoder.GetAttributeId(mesh, attrType);
                    if (attrId < 0) return null;
                    const attr = decoder.GetAttribute(mesh, attrId);
                    const out = new decoderModule.DracoFloat32Array();
                    decoder.GetAttributeFloatForAllPoints(mesh, attr, out);
                    const arr = new Float32Array(numPoints * numComponents);
                    for (let i = 0; i < arr.length; i++) arr[i] = out.GetValue(i);
                    decoderModule.destroy(out);
                    return arr;
                }
                const positions = readAttr(decoderModule.POSITION, 3);
                const normalsRaw = readAttr(decoderModule.NORMAL, 3);
                const uvsRaw = readAttr(decoderModule.TEX_COORD, 2);
                if (!positions) { decoderModule.destroy(mesh); return null; }
                const normals = normalsRaw || new Float32Array(numPoints * 3);
                const uvs = uvsRaw || new Float32Array(numPoints * 2);
                // Как и в v4.x: у Roblox начало V сверху, а у three.js (flipY=true
                // у TextureLoader) — снизу. В v4 переворот был, в Draco (v7)
                // его не было — отсюда неправильная развёртка на v7-мешах.
                if (uvsRaw) for (let i = 1; i < uvs.length; i += 2) uvs[i] = 1 - uvs[i];
                const faceBuf = new decoderModule.DracoInt32Array();
                const indices = new Uint32Array(numFaces * 3);
                for (let i = 0; i < numFaces; i++) {
                    decoder.GetFaceFromMesh(mesh, i, faceBuf);
                    indices[i * 3] = faceBuf.GetValue(0);
                    indices[i * 3 + 1] = faceBuf.GetValue(1);
                    indices[i * 3 + 2] = faceBuf.GetValue(2);
                }
                decoderModule.destroy(faceBuf);
                decoderModule.destroy(mesh);
                return { positions, normals, uvs, indices };
            } finally {
                decoderModule.destroy(decoder);
                decoderModule.destroy(dracoBuffer);
            }
        }
        // v7.00 — НЕ просто "заголовок + чистый Draco-поток", как я раньше
        // угадывал: это чанковый формат (как и другие бинарные форматы
        // Roblox), Draco-данные лежат внутри чанка COREMESH, а отдельный
        // чанк LODS задаёт диапазон граней конкретного уровня детализации.
        // Рёбра "рваной" геометрии на скриншотах скорее всего от того, что
        // без учёта LODS декодируются и рисуются ВСЕ уровни детализации
        // сразу, наложенные друг на друга — а не от порядка обхода вершин
        // (DoubleSide в предыдущей правке маскировал часть симптома, не
        // причину). Точная структура чанков не подтверждена — ищем
        // настоящую сигнатуру "DRACO" и имена чанков по байтам вместо
        // слепого перебора отступов, и логируем найденное в Output: этого
        // достаточно, чтобы через одно сообщение получить точные цифры для
        // следующего шага (разбор LODS), вместо гадания вслепую.
        function _findBytes(haystack, needle, from) {
            outer: for (let i = from || 0; i <= haystack.length - needle.length; i++) {
                for (let j = 0; j < needle.length; j++) if (haystack[i + j] !== needle[j]) continue outer;
                return i;
            }
            return -1;
        }
        function _findAllBytes(haystack, needle) {
            const out = [];
            let from = 0;
            while (true) {
                const i = _findBytes(haystack, needle, from);
                if (i < 0) break;
                out.push(i);
                from = i + 1;
            }
            return out;
        }
        // Чанк LODS идёт сразу за COREMESH: 8 байт имя, u32 версия, u32 размер,
        // дальше данные. Точный формат не подтверждён, поэтому ищем в данных
        // возрастающую последовательность u32, начинающуюся с 0 и
        // заканчивающуюся числом граней меша — это офсеты LOD. Возвращает
        // число граней LOD0 или null (тогда рисуются все грани, как раньше).
        function _findLod0FaceCount(bytes, chunkStart, numFaces) {
            if (chunkStart < 0 || chunkStart + 16 > bytes.length) return null;
            const name = new TextDecoder('latin1').decode(bytes.subarray(chunkStart, chunkStart + 4));
            if (name !== 'LODS') return null;
            const dv = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
            const size = dv.getUint32(chunkStart + 12, true);
            const dataStart = chunkStart + 16;
            const dataEnd = Math.min(bytes.length, dataStart + size);
            for (let p = dataStart; p + 8 <= dataEnd; p++) {
                if (dv.getUint32(p, true) !== 0) continue;
                const seq = [0];
                let q = p + 4, prev = 0;
                while (q + 4 <= dataEnd && seq.length < 16) {
                    const v = dv.getUint32(q, true);
                    if (v < prev || v > numFaces) break;
                    seq.push(v); prev = v; q += 4;
                    if (v === numFaces) break;
                }
                if (seq.length >= 2 && seq[seq.length - 1] === numFaces && seq[1] > 0) return seq[1];
            }
            return null;
        }
        // v7.00, COREMESH версии 1 — НЕСЖАТЫЙ чанк (Draco — версия 2).
        // Раскладка (подтверждена на реальном файле): "COREMESH"(8) +
        // u32 версия + u32 размер + u32 numVerts, затем numVerts вершин по 40 байт
        // (pos f32x3, normal f32x3, uv f32x2, tangent 4 байта, color 4 байта),
        // затем u32 numFaces и numFaces*3 u32 индексов. Размер чанка =
        // 4 + numVerts*40 + 4 + numFaces*12. Дальше идёт чанк LODS.
        function _parseRobloxMeshV7Raw(bodyBytes) {
            const dv = new DataView(bodyBytes.buffer, bodyBytes.byteOffset, bodyBytes.byteLength);
            const chunkSize = dv.getUint32(12, true);
            const numVerts = dv.getUint32(16, true);
            const vertStart = 20;
            const facesStart = vertStart + numVerts * 40;
            if (!numVerts || numVerts > 2_000_000 || facesStart + 4 > bodyBytes.length) {
                _lastMeshParseFailReason = 'v7 raw: некорректный numVerts=' + numVerts + ' (bufLen=' + bodyBytes.length + ')';
                return null;
            }
            const numFaces = dv.getUint32(facesStart, true);
            const idxStart = facesStart + 4;
            if (!numFaces || numFaces > 2_000_000 || idxStart + numFaces * 12 > bodyBytes.length) {
                _lastMeshParseFailReason = 'v7 raw: некорректный numFaces=' + numFaces + ' (bufLen=' + bodyBytes.length + ')';
                return null;
            }
            const positions = new Float32Array(numVerts * 3);
            const normals = new Float32Array(numVerts * 3);
            const uvs = new Float32Array(numVerts * 2);
            for (let i = 0; i < numVerts; i++) {
                const o = vertStart + i * 40;
                positions[i * 3] = dv.getFloat32(o, true);
                positions[i * 3 + 1] = dv.getFloat32(o + 4, true);
                positions[i * 3 + 2] = dv.getFloat32(o + 8, true);
                normals[i * 3] = dv.getFloat32(o + 12, true);
                normals[i * 3 + 1] = dv.getFloat32(o + 16, true);
                normals[i * 3 + 2] = dv.getFloat32(o + 20, true);
                uvs[i * 2] = dv.getFloat32(o + 24, true);
                // Как в v4/Draco: V у Roblox сверху, у three.js снизу.
                uvs[i * 2 + 1] = 1 - dv.getFloat32(o + 28, true);
            }
            const indices = new Uint32Array(numFaces * 3);
            for (let i = 0; i < indices.length; i++) {
                const v = dv.getUint32(idxStart + i * 4, true);
                if (v >= numVerts) { _lastMeshParseFailReason = 'v7 raw: индекс ' + v + ' >= numVerts ' + numVerts; return null; }
                indices[i] = v;
            }
            const lod0 = _findLod0FaceCount(bodyBytes, 16 + chunkSize, numFaces);
            const out = (lod0 && lod0 < numFaces) ? indices.subarray(0, lod0 * 3) : indices;
            return { positions, normals, uvs, indices: out };
        }
        async function _parseRobloxMeshDraco(bodyBytes) {
            if (bodyBytes.length >= 20 && new TextDecoder('latin1').decode(bodyBytes.subarray(0, 8)) === 'COREMESH' &&
                new DataView(bodyBytes.buffer, bodyBytes.byteOffset, bodyBytes.byteLength).getUint32(8, true) === 1) {
                return _parseRobloxMeshV7Raw(bodyBytes);
            }
            let decoderModule;
            try {
                decoderModule = await _loadDracoModule();
            } catch (e) {
                _lastMeshParseFailReason = 'не удалось загрузить Draco-декодер (' + e.message + ')';
                return null;
            }
            const dv = new DataView(bodyBytes.buffer, bodyBytes.byteOffset, bodyBytes.byteLength);
            // Заголовок чанка COREMESH — подтверждено вживую на двух
            // реальных файлах (см. диагностику): 8 байт имя "COREMESH",
            // затем 3×uint32 — [флаг/версия=2, длина_Draco+4, длина_Draco].
            // Сам Draco-поток начинается СРАЗУ после этого 20-байтного
            // заголовка и длится ровно третье поле байт — раньше этой
            // точной длины не было, декодер получал "остаток буфера" и мог
            // читать байты уже следующего чанка (LODS) как часть потока.
            const ascii = new TextDecoder('latin1').decode(bodyBytes.subarray(0, Math.min(64, bodyBytes.length)));
            let dracoOffset = 20, dracoLength = null;
            if (ascii.startsWith('COREMESH') && bodyBytes.length >= 20) {
                dracoLength = dv.getUint32(16, true);
            } else {
                // Структура не подтвердилась для этого конкретного файла —
                // ищем сигнатуру "DRACO" по байтам как запасной вариант,
                // без точной длины (декодер получит "остаток буфера").
                const found = _findBytes(bodyBytes, [0x44, 0x52, 0x41, 0x43, 0x4F], 0);
                if (found < 0) {
                    _lastMeshParseFailReason = 'не нашёл ни заголовок COREMESH, ни сигнатуру DRACO';
                    return null;
                }
                dracoOffset = found;
            }
            try {
                const result = _tryDecodeDracoAt(decoderModule, bodyBytes, dracoOffset, dracoLength);
                if (result) {
                    // Оставляем только грани LOD0 — иначе грубые LOD рисуются поверх.
                    if (dracoLength != null) {
                        const totalFaces = result.indices.length / 3;
                        const lod0 = _findLod0FaceCount(bodyBytes, dracoOffset + dracoLength, totalFaces);
                        if (lod0 && lod0 < totalFaces) {
                            result.indices = result.indices.subarray(0, lod0 * 3);
                            logLuaOutput('info', t('log_draco_lod0', { n: lod0, total: totalFaces }));
                        }
                    }
                    return result;
                }
            } catch (e) {
                _lastMeshParseFailReason = 'Draco-декодер бросил исключение: ' + e.message;
                return null;
            }
            // Заявленная длина/офсет не подошли (например, длина 4 у служебного чанка) — ищем сигнатуру
            // "DRACO" в теле и пробуем декодировать от неё, без точной длины.
            try {
                let from = 0;
                for (;;) {
                    const found = _findBytes(bodyBytes, [0x44, 0x52, 0x41, 0x43, 0x4F], from);
                    if (found < 0) break;
                    if (found !== dracoOffset) {
                        const result = _tryDecodeDracoAt(decoderModule, bodyBytes, found, null);
                        if (result) return result;
                    }
                    from = found + 1;
                }
            } catch (e) { emuWarn('swallow:L2558', 'блок около script.js:2558: ' + _errText(e) + ' (падаем в сообщение ниже)'); }
            _lastMeshParseFailReason = 'Draco-декодер не смог разобрать поток по офсету ' + dracoOffset +
                (dracoLength != null ? (', длина ' + dracoLength) : '') + ' (поиск сигнатуры DRACO тоже не помог)';
            return null;
        }

        async function loadRealMeshGeometry(meshId) {
            if (_meshGeometryCache[meshId]) return _meshGeometryCache[meshId];
            const p = (async () => {
                try {
                    const resp = await fetch('/api/asset-proxy?id=' + meshId);
                    if (!resp.ok) throw new Error('HTTP ' + resp.status);
                    const buf = await resp.arrayBuffer();
                    const head = new TextDecoder('ascii').decode(buf.slice(0, 16));
                    const m = /version[ ]?([\d.]+)/i.exec(head);
                    const version = m ? m[1] : null;
                    let parsed = null;
                    if (version === '1.00') {
                        parsed = _parseRobloxMeshV1(new TextDecoder('utf-8').decode(buf));
                    } else if (version === '2.00' || version === '3.00' || version === '4.00' || version === '4.01' || version === '5.00' || version === '6.00') {
                        // Текстовый заголовок "version X.XX\n" (или "\r\n")
                        const bytes = new Uint8Array(buf);
                        let nl = bytes.indexOf(10);
                        let bodyStart = nl + 1;
                        const body = buf.slice(bodyStart);
                        parsed = (version === '2.00' || version === '3.00')
                            ? _parseRobloxMeshBinary(body)
                            : _parseRobloxMeshV4(body);
                    } else if (version === '7.00') {
                        const bytes = new Uint8Array(buf);
                        const nl = bytes.indexOf(10);
                        parsed = await _parseRobloxMeshDraco(bytes.subarray(nl + 1));
                    } else {
                        failedMeshIds.add(String(meshId));
                        logLuaOutput('warn', 'Mesh ' + meshId + ': формат "' + (version || '?') + '" пока не поддержан, использую приближение');
                        return null;
                    }
                    if (!parsed) {
                        failedMeshIds.add(String(meshId));
                        logLuaOutput('warn', 'Mesh ' + meshId + ' (версия "' + version + '"): не удалось разобрать — ' + (_lastMeshParseFailReason || 'причина неизвестна') + ', использую приближение');
                        return null;
                    }
                    return _buildGeometryFromParsed(parsed);
                } catch (e) {
                    logLuaOutput('warn', t('log_mesh_load_failed', { id: meshId, msg: e.message }));
                    return null;
                }
            })();
            _meshGeometryCache[meshId] = p;
            return p;
        }

        // Асинхронно подменяет box-приближение на реальную геометрию, когда
        // Сколько реальных мешей/текстур сейчас грузится по сети — Play
        // ждёт, пока счётчик не опустеет (см. waitForPendingModelLoads),
        // чтобы модель игрока (и остальная сцена) появлялась сразу целиком,
        // как при скачивании аватара, а не проявлялась кусками уже во время
        // игры.
        let _pendingModelLoads = 0;
        function _trackLoad(promiseLike) {
            _pendingModelLoads++;
            const done = () => { _pendingModelLoads = Math.max(0, _pendingModelLoads - 1); };
            promiseLike.then(done, done);
        }
        function waitForPendingModelLoads(maxMs) {
            const start = performance.now();
            return new Promise((resolve) => {
                (function poll() {
                    if (_pendingModelLoads <= 0 || performance.now() - start > maxMs) { resolve(); return; }
                    setTimeout(poll, 50);
                })();
            });
        }
        // ============ UnionOperation: реальная геометрия (деталь минус Negate) ============
        // Сервер отдаёт готовый меш из SolidMeshHolder (см. /api/union_mesh);
        // координаты локальные, в настоящем размере (Size уже "вшит"), поэтому
        // масштабировать не нужно — просто подменяем geometry у box-приближения.
        // Нет меша / формат не разобран (404) — остаётся box по Size.
        function applyUnionTrimesh(body, mesh) {
            const verts = mesh && mesh.userData && mesh.userData.unionTrimeshVerts;
            if (!verts || !body || body.__unionTrimesh || body.mass !== 0 || !body.shapes.length) return;
            const inds = new Array(verts.length / 3);
            for (let q = 0; q < inds.length; q++) inds[q] = q;
            body.shapes.length = 0; body.shapeOffsets.length = 0; body.shapeOrientations.length = 0;
            body.addShape(new CANNON.Trimesh(verts, inds));
            body.updateBoundingRadius();
            body.aabbNeedsUpdate = true;
            body.__unionTrimesh = true;
        }
        let _unionGeoCache = {}; // ref -> Promise<BufferGeometry|null>; сбрасывается в reloadScene
        function loadUnionGeometry(ref) {
            if (_unionGeoCache[ref]) return _unionGeoCache[ref];
            const p = (async () => {
                try {
                    const resp = await fetch('/api/union_mesh?ref=' + ref);
                    if (!resp.ok) return null;
                    const d = await resp.json();
                    const geo = new THREE.BufferGeometry();
                    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(d.position), 3));
                    geo.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(d.normal), 3));
                    geo.computeBoundingBox();
                    geo.computeBoundingSphere();
                    geo.userData.sharedMesh = true; // не dispose при очистке сцены (общий кэш)
                    return geo;
                } catch (e) {
                    return null;
                }
            })();
            _unionGeoCache[ref] = p;
            return p;
        }
        function scheduleUnionMeshSwap(o, mesh) {
            const p = loadUnionGeometry(o.ref).then((geo) => {
                if (!geo) return;
                if (sceneObjs[o.ref] !== mesh) return; // объект уже заменён/удалён
                mesh.geometry = geo;
                // Материал-массив (Decal на одной грани бокса) без групп у union-геометрии не нарисуется:
                // треугольники, смотрящие в сторону грани декали, получают планарные UV и текстурный
                // материал (группа 1), остальные — базовый (группа 0).
                if (Array.isArray(mesh.material) && mesh.material.length === 6) {
                    const mats = mesh.material;
                    const ti = mats.findIndex(m => m && m.map);
                    const base = mats.find(m => m && !m.map) || mats[0];
                    if (ti < 0) {
                        mesh.material = base;
                    } else {
                        const AX = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]][ti];
                        const src = geo.attributes.position.array, nsrc = geo.attributes.normal ? geo.attributes.normal.array : null;
                        const triN = src.length / 9, hit = [], rest = [];
                        for (let t = 0; t < triN; t++) {
                            const o9 = t * 9;
                            const ux = src[o9 + 3] - src[o9], uy = src[o9 + 4] - src[o9 + 1], uz = src[o9 + 5] - src[o9 + 2];
                            const vx = src[o9 + 6] - src[o9], vy = src[o9 + 7] - src[o9 + 1], vz = src[o9 + 8] - src[o9 + 2];
                            let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
                            const ln = Math.hypot(nx, ny, nz) || 1;
                            (((nx * AX[0] + ny * AX[1] + nz * AX[2]) / ln) > 0.9 ? hit : rest).push(t);
                        }
                        const order = hit.concat(rest);
                        const P = new Float32Array(src.length), N = new Float32Array(src.length), UV = new Float32Array(triN * 6);
                        const sx = o.sx || 1, sy = o.sy || 1, sz = o.sz || 1;
                        order.forEach((t, k) => {
                            for (let c = 0; c < 3; c++) {
                                const si = t * 9 + c * 3, di = k * 9 + c * 3;
                                P[di] = src[si]; P[di + 1] = src[si + 1]; P[di + 2] = src[si + 2];
                                if (nsrc) { N[di] = nsrc[si]; N[di + 1] = nsrc[si + 1]; N[di + 2] = nsrc[si + 2]; }
                                const x = P[di], y = P[di + 1], z = P[di + 2];
                                let u, v;   // как у THREE.BoxGeometry для соответствующей грани
                                if (ti === 0) { u = -z / sz + 0.5; v = y / sy + 0.5; }
                                else if (ti === 1) { u = z / sz + 0.5; v = y / sy + 0.5; }
                                else if (ti === 2) { u = x / sx + 0.5; v = -z / sz + 0.5; }
                                else if (ti === 3) { u = x / sx + 0.5; v = z / sz + 0.5; }
                                else if (ti === 4) { u = x / sx + 0.5; v = y / sy + 0.5; }
                                else { u = -x / sx + 0.5; v = y / sy + 0.5; }
                                UV[k * 6 + c * 2] = u; UV[k * 6 + c * 2 + 1] = v;
                            }
                        });
                        const g2 = new THREE.BufferGeometry();
                        g2.setAttribute('position', new THREE.BufferAttribute(P, 3));
                        g2.setAttribute('normal', new THREE.BufferAttribute(nsrc ? N : P.slice(), 3));
                        g2.setAttribute('uv', new THREE.BufferAttribute(UV, 2));
                        if (hit.length) g2.addGroup(0, hit.length * 3, 1);
                        if (rest.length) g2.addGroup(hit.length * 3, rest.length * 3, 0);
                        if (!nsrc) g2.computeVertexNormals();
                        mesh.geometry = g2;
                        mesh.material = [base, mats[ti]];
                    }
                }
                // Внутренняя поверхность выреза (та, что "смотрит" внутрь
                // полости) видна ТОЛЬКО если материал рисует обе стороны —
                // материал box-заглушки общий (matCache) и по умолчанию
                // однобокий: снаружи выемка/дырка не читалась (сплошная
                // деталь), хотя геометрия внутри уже правильная. Клонируем
                // материал (общий кэш трогать нельзя) и включаем DoubleSide
                // только для реальных union-мешей.
                const applyDoubleSide = (m) => {
                    if (m.side === THREE.DoubleSide) return m;
                    const c = m.clone();
                    c.side = THREE.DoubleSide;
                    return c;
                };
                mesh.material = Array.isArray(mesh.material)
                    ? mesh.material.map(applyDoubleSide)
                    : applyDoubleSide(mesh.material);
                // Полый ли юнион (холодильник, шкаф, комната): объём меша заметно меньше
                // объёма габаритного бокса. Физика у юниона — сплошной бокс, и игрока,
                // телепортированного внутрь, выталкивало наружу.
                try {
                    const pa = geo.attributes && geo.attributes.position;
                    if (pa && pa.count >= 12) {
                        let vol = 0;
                        const idx = geo.index;
                        const tri = idx ? idx.count / 3 : pa.count / 3;
                        for (let t = 0; t < tri; t++) {
                            const ia = idx ? idx.getX(t * 3) : t * 3, ib = idx ? idx.getX(t * 3 + 1) : t * 3 + 1, ic = idx ? idx.getX(t * 3 + 2) : t * 3 + 2;
                            const ax = pa.getX(ia), ay = pa.getY(ia), az = pa.getZ(ia);
                            const bx = pa.getX(ib), by = pa.getY(ib), bz = pa.getZ(ib);
                            const cx = pa.getX(ic), cy = pa.getY(ic), cz = pa.getZ(ic);
                            vol += (ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx)) / 6;
                        }
                        geo.computeBoundingBox();
                        const bb = geo.boundingBox;
                        const boxVol = (bb.max.x - bb.min.x) * (bb.max.y - bb.min.y) * (bb.max.z - bb.min.z);
                        const ratio = boxVol > 0 ? Math.abs(vol) / boxVol : 1;
                        // Любой вырез (проём в стене, комната): сплошной бокс не даёт пройти в дырку —
                        // коллайдером становится настоящая геометрия (см. applyUnionTrimesh).
                        // Trimesh в cannon.js хранит индексы в Int16, отсюда лимит ~10 000 треугольников.
                        if (ratio < 0.98 && tri <= 10000 && !idx) {
                            mesh.userData.unionTrimeshVerts = Array.from(pa.array);
                            applyUnionTrimesh(physicsBodies[o.ref], mesh);
                        } else if (ratio < 0.75) luaHollowUnions.add(o.ref);
                    }
                } catch (e) { emuWarn('swallow:L2769', 'блок около script.js:2769: ' + _errText(e) + ''); }
            });
            _trackLoad(p);
        }

        // ref полых юнионов + «призрак»: пока центр игрока внутри габаритов юниона,
        // его тело не сталкивается с персонажем (иначе сфера игрока вылетает из полости).
        const luaHollowUnions = new Set();
        const luaGhostedUnions = new Set();
        function updateHollowUnionGhosts() {
            if (!charBody || !luaHollowUnions.size) return;
            for (const ref of luaHollowUnions) {
                const body = physicsBodies[ref], sz = loadedObjSize[ref];
                if (!body || !sz) continue;
                const dx = charBody.position.x - body.position.x, dy = charBody.position.y - body.position.y, dz = charBody.position.z - body.position.z;
                const v = new CANNON.Vec3(dx, dy, dz);
                const inv = new CANNON.Quaternion(-body.quaternion.x, -body.quaternion.y, -body.quaternion.z, body.quaternion.w);
                const l = inv.vmult(v);
                const m = 0.8;
                const inside = Math.abs(l.x) <= sz.x * 0.5 + m && Math.abs(l.y) <= sz.y * 0.5 + m && Math.abs(l.z) <= sz.z * 0.5 + m;
                if (inside && !luaGhostedUnions.has(ref)) {
                    luaGhostedUnions.add(ref);
                    body.__savedMask = body.collisionFilterMask;
                    body.collisionFilterMask = 0;
                } else if (!inside && luaGhostedUnions.has(ref)) {
                    luaGhostedUnions.delete(ref);
                    body.collisionFilterMask = body.__savedMask === undefined ? 1 : body.__savedMask;
                }
            }
        }

        function scheduleRealMeshSwap(o, mesh) {
            const p = loadRealMeshGeometry(o.meshId).then((result) => {
                if (!result) return;
                if (sceneObjs[o.ref] !== mesh) return; // объект уже заменён/удалён
                mesh.geometry = result.geometry;
                // DoubleSide — реальная геометрия (особенно из Draco, v7.00)
                // могла прийти с порядком обхода вершин граней (winding),
                // обратным тому, что ожидает three.js по умолчанию;
                // FrontSide-материал в этом случае отбрасывает примерно
                // половину треугольников (backface culling) — именно так
                // выглядел рваный/дырявый силуэт на скриншотах. DoubleSide
                // рисует обе стороны независимо от направления обхода —
                // чуть дороже по рендеру, но гарантированно не "дырявое".
                if (mesh.material) mesh.material.side = THREE.DoubleSide;
                const pos = new THREE.Vector3(), quat = new THREE.Quaternion(), scale = new THREE.Vector3();
                mesh.matrix.decompose(pos, quat, scale);
                if (o.meshScale) {
                    // SpecialMesh(FileMesh): размер = родной размер меша * Scale,
                    // Size самой детали не участвует (как в Roblox).
                    scale.set(o.meshScale[0], o.meshScale[1], o.meshScale[2]);
                } else {
                    // MeshPart: меш вписывается в Size детали.
                    const cur = loadedObjSize[o.ref] || { x: o.sx || 1, y: o.sy || 1, z: o.sz || 1 };
                    scale.set(cur.x / result.size.x, cur.y / result.size.y, cur.z / result.size.z);
                    // исходный масштаб (по размеру из файла) — к нему возвращаемся после Stop
                    mesh.userData.partScale0 = new THREE.Vector3((o.sx || 1) / result.size.x, (o.sy || 1) / result.size.y, (o.sz || 1) / result.size.z);
                }
                mesh.matrix.compose(pos, quat, scale);
                // Масштаб меша (вписывание в Size у MeshPart / Scale у SpecialMesh) запоминаем: цикл синхронизации
                // с физикой пересобирает матрицу каждый кадр и раньше сбрасывал его в (1,1,1), из-за чего меши
                // с родным размером != Size (торс, шляпы и прочие аксессуары) рисовались «очень большими».
                mesh.userData.partScale = scale.clone();
                // matrixAutoUpdate=false → three.js сам НЕ пересчитает
                // matrixWorld после первого кадра; без этого флага новый
                // масштаб (и вообще любая правка mesh.matrix) не применялась.
                mesh.matrixWorldNeedsUpdate = true;
            });
            _trackLoad(p);
        }

        // ============ ТЕКСТУРЫ ОБЫЧНЫХ ЧАСТЕЙ (Decal/MeshPart/SpecialMesh) ============
        // Decal лежит НА поверхности детали — часто вплотную к стене/другой детали. polygonOffset сдвигает его
        // к камере в буфере глубины, чтобы он не мерцал и не пропадал под углом (z-fighting); visible=true
        // перекрывает visible:false у «невидимой» детали, на которой висит постер.
        const DECAL_FACE_OPTS = { visible: true, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 };
        // polygonOffset при near=0.5/far=500 даёт сдвиг в доли тысячных стада — стена, стоящая вплотную спереди
        // (постер «утоплен» в стену на 0.02–0.1), всё равно закрывает Decal. Поэтому дополнительно сдвигаем
        // вершины грани с Decal К КАМЕРЕ на фиксированные DECAL_BIAS студов (в view-space, от дистанции не зависит):
        // как в Roblox, Decal рисуется поверх соседней геометрии, лежащей почти в той же плоскости.
        const DECAL_BIAS = 0.12;
        function _applyDecalBias(mat) {
            mat.customProgramCacheKey = () => 'decal-bias';
            mat.onBeforeCompile = (shader) => {
                shader.vertexShader = shader.vertexShader.replace('#include <project_vertex>',
                    '#include <project_vertex>\n mvPosition.z += ' + DECAL_BIAS.toFixed(3) + ';\n gl_Position = projectionMatrix * mvPosition;');
            };
            return mat;
        }
        const _partTexCache = {};
        // Раньше THREE.TextureLoader создавался здесь же, на верхнем уровне
        let _partTexLoader = null;
        // Почему ассет не загрузился: TextureLoader/Image не говорят причину, поэтому
        // повторно спрашиваем прокси и показываем его ответ (401/403, XML вместо картинки...).
        const _assetReported = new Set();
        function reportAssetFailure(id) {
            if (_assetReported.has(id)) return;
            _assetReported.add(id);
            fetch('/api/asset-proxy?id=' + id).then(async r => {
                if (!r.ok) {
                    const txt = (await r.text()).replace(/\s+/g, ' ').slice(0, 300);
                    logLuaOutput('warn', t('asset_fail_reason', { id, reason: r.status + ' ' + txt }));
                } else {
                    const ct = r.headers.get('content-type') || '?';
                    logLuaOutput('warn', t(ct.startsWith('image/') ? 'asset_decode_failed' : 'asset_not_image', { id, type: ct }));
                }
            }).catch(e => logLuaOutput('warn', t('asset_fail_reason', { id, reason: e.message })));
        }
        // Overlay-режим SurfaceAppearance: итог = mix(Color детали, ColorMap.rgb, ColorMap.a). Правим один фрагмент
        // стандартного шейдера (map_fragment), отдельная программа — по customProgramCacheKey.
        function _applyOverlayAlpha(mat) {
            mat.customProgramCacheKey = () => 'overlay-alpha';
            mat.onBeforeCompile = (shader) => {
                shader.fragmentShader = shader.fragmentShader.replace('#include <map_fragment>',
                    `#ifdef USE_MAP
                        vec4 texelColor = mapTexelToLinear( texture2D( map, vUv ) );
                        diffuseColor.rgb = mix( diffuse, texelColor.rgb, texelColor.a );
                    #endif`);
            };
        }

        function getOrLoadPartTexture(assetId) {
            if (_partTexCache[assetId]) return _partTexCache[assetId];
            if (!_partTexLoader) _partTexLoader = new THREE.TextureLoader();
            let resolveLoad;
            _trackLoad(new Promise((res) => { resolveLoad = res; }));
            const tex = _partTexLoader.load('/api/asset-proxy?id=' + assetId, (loaded) => {
                // Тот же r128-фикс насыщенности, что и у аватаров (см.
                // importAvatarIntoScene) — иначе текстура выглядит блёкло.
                loaded.encoding = THREE.sRGBEncoding;
                loaded.anisotropy = renderer.capabilities.getMaxAnisotropy();
                loaded.needsUpdate = true;
                resolveLoad();
            }, undefined, () => {
                // 3-й колбэк TextureLoader.load — onError, раньше не
                logLuaOutput('warn', t('warn_texture_failed', { id: assetId }));
                reportAssetFailure(assetId);
                resolveLoad();
            });
            _partTexCache[assetId] = tex;
            return tex;
        }

        // ============ МАТЕРИАЛЫ (Enum.Material + MaterialVariant) ============
        // Phong вместо Lambert даёт блик без карты окружения (для three r128
        // без RoomEnvironment metalness выглядел бы чёрным).
        const MATERIAL_STYLE = {
            272: { shininess: 40, specular: 0x444444 },   // SmoothPlastic
            288: { neon: true },                          // Neon
            1040: { shininess: 30, specular: 0x666666 },  // CorrodedMetal
            1056: { shininess: 90, specular: 0xaaaaaa },  // DiamondPlate
            1072: { shininess: 120, specular: 0xffffff }, // Foil
            1088: { shininess: 80, specular: 0xbbbbbb },  // Metal
        };
        const _tiledTexCache = {};
        function getTiledTexture(id, rx, ry, srgb) {
            const key = id + '_' + rx.toFixed(2) + '_' + ry.toFixed(2) + (srgb ? 's' : 'l');
            if (_tiledTexCache[key]) return _tiledTexCache[key];
            let resolveTiled;
            _trackLoad(new Promise((res) => { resolveTiled = res; }));
            const tex = new THREE.TextureLoader().load('/api/asset-proxy?id=' + id, (l) => {
                l.wrapS = l.wrapT = THREE.RepeatWrapping;
                l.repeat.set(rx, ry);
                if (srgb) l.encoding = THREE.sRGBEncoding;
                l.anisotropy = renderer.capabilities.getMaxAnisotropy();
                l.needsUpdate = true;
                resolveTiled();
            }, undefined, () => { logLuaOutput('warn', t('warn_texture_failed', { id })); reportAssetFailure(id); resolveTiled(); });
            _tiledTexCache[key] = tex;
            return tex;
        }
        function makeStyledMaterial(o, op) {
            const st = MATERIAL_STYLE[o.material] || {};
            const mv = o.mvar;
            const base = {
                transparent: op < 1.0, opacity: op,
                color: (mv && mv.colorMap) ? '#ffffff' : (o.color || '#a0a0a0'),
                shininess: st.shininess || 20,
                specular: st.specular !== undefined ? st.specular : 0x222222,
            };
            if (st.neon) { base.emissive = new THREE.Color(o.color || '#ffffff'); }
            if (mv && qualitySettings.textures) {
                // Плитка MaterialVariant задаётся в студах (StudsPerTile), а у меша
                // UV на всю деталь — берём приближённо по среднему размеру.
                const tiles = Math.max(1, ((o.sx || 1) + (o.sz || 1)) / 2 / (mv.studsPerTile || 10));
                if (mv.colorMap) base.map = getTiledTexture(mv.colorMap, tiles, tiles, true);
                if (mv.normalMap) base.normalMap = getTiledTexture(mv.normalMap, tiles, tiles, false);
                if (mv.metalnessMap) base.specularMap = getTiledTexture(mv.metalnessMap, tiles, tiles, false);
            }
            return new THREE.MeshPhongMaterial(base);
        }

        // ============ ОДЕЖДА R6 (Shirt/Pants) ============
        // Классический шаблон 585x559: прямоугольники [x, y, w, h] граней.
        // Порядок граней BoxGeometry: +x, -x, +y, -y, +z, -z
        // (Roblox: Right, Left, Top, Bottom, Back, Front). Координаты
        // торса известны точно; для рук/ног боковые грани — по симметричной
        // раскладке шаблона (лицевая грань и верх/низ — точные).
        const CLOTH_W = 585, CLOTH_H = 559;
        const CLOTH_FACES = ['px', 'nx', 'py', 'ny', 'pz', 'nz'];
        const CLOTH_REGIONS = {
            'Torso': { px: [165, 74, 64, 128], nx: [361, 74, 64, 128], py: [231, 8, 128, 64], ny: [231, 204, 128, 64], pz: [427, 74, 128, 128], nz: [231, 74, 128, 128] },
            'Right Arm': { px: [151, 355, 64, 128], nx: [19, 355, 64, 128], py: [217, 289, 64, 64], ny: [217, 483, 64, 64], pz: [85, 355, 64, 128], nz: [217, 355, 64, 128] },
            'Left Arm': { px: [506, 355, 64, 128], nx: [374, 355, 64, 128], py: [308, 289, 64, 64], ny: [308, 483, 64, 64], pz: [440, 355, 64, 128], nz: [308, 355, 64, 128] },
        };
        CLOTH_REGIONS['Right Leg'] = CLOTH_REGIONS['Right Arm'];
        CLOTH_REGIONS['Left Leg'] = CLOTH_REGIONS['Left Arm'];

        function makeClothGeometry(o, baseGeo) {
            const reg = CLOTH_REGIONS[o.cloth.limb];
            if (!reg) return baseGeo;
            const g = baseGeo.clone(); // UV свои у каждой части, общий кэш геометрий трогать нельзя
            const uv = g.attributes.uv;
            CLOTH_FACES.forEach((f, gi) => {
                const [x, y, w, h] = reg[f];
                const u0 = x / CLOTH_W, u1 = (x + w) / CLOTH_W;
                const vt = 1 - y / CLOTH_H, vb = 1 - (y + h) / CLOTH_H;
                const b = gi * 4;
                uv.setXY(b, u0, vt); uv.setXY(b + 1, u1, vt);
                uv.setXY(b + 2, u0, vb); uv.setXY(b + 3, u1, vb);
            });
            uv.needsUpdate = true;
            return g;
        }

        const _clothTexCache = {};
        function getClothTexture(color, shirtId, pantsId) {
            const key = (color || '') + '_' + (shirtId || '') + '_' + (pantsId || '');
            if (_clothTexCache[key]) return _clothTexCache[key];
            const c = document.createElement('canvas');
            c.width = CLOTH_W; c.height = CLOTH_H;
            const ctx = c.getContext('2d');
            ctx.fillStyle = color || '#ffcc99';
            ctx.fillRect(0, 0, CLOTH_W, CLOTH_H);
            const tex = new THREE.CanvasTexture(c);
            tex.encoding = THREE.sRGBEncoding;
            tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
            // штаны под рубашкой; порядок отрисовки не зависит от порядка загрузки
            const layers = [pantsId, shirtId].filter(Boolean);
            const p = Promise.all(layers.map(id => new Promise(res => {
                const im = new Image();
                im.onload = () => res(im);
                im.onerror = () => { logLuaOutput('warn', t('warn_texture_failed', { id })); reportAssetFailure(id); res(null); };
                im.src = '/api/asset-proxy?id=' + id;
            }))).then(imgs => {
                imgs.forEach(im => { if (im) ctx.drawImage(im, 0, 0, CLOTH_W, CLOTH_H); });
                tex.needsUpdate = true;
                logLuaOutput('info', t('log_cloth_loaded', { n: imgs.filter(Boolean).length, total: layers.length }));
            });
            _trackLoad(p);
            _clothTexCache[key] = tex;
            return tex;
        }

        // ============ ИСПРАВЛЕННАЯ СЦЕНА ============
        function buildMeshFromObj(o, geoCache, matCache) {
            const geoKey = o.shape + '_' + (o.sx || 1).toFixed(2) + '_' + (o.sy || 1).toFixed(2) + '_' + (o.sz || 1).toFixed(2);
            if (!geoCache[geoKey]) {
                if (o.shape === 'sphere') {
                    const seg = Math.max(4, qualitySettings.sphereSegments);
                    const radius = Math.max(o.sx || 1, o.sy || 1, o.sz || 1) * 0.5;
                    geoCache[geoKey] = new THREE.SphereGeometry(radius, seg, Math.round(seg * 0.75));
                } else if (o.shape === 'cylinder') {
                    const seg = Math.max(6, qualitySettings.sphereSegments);
                    geoCache[geoKey] = new THREE.CylinderGeometry((o.sx || 1) * 0.5, (o.sz || 1) * 0.5, o.sy || 1, seg);
                } else if (o.shape === 'cone') {
                    const seg = Math.max(6, qualitySettings.sphereSegments);
                    const radius = Math.max(o.sx || 1, o.sz || 1) * 0.5;
                    geoCache[geoKey] = new THREE.ConeGeometry(radius, o.sy || 1, seg);
                } else if (o.shape === 'wedge') {
                    geoCache[geoKey] = makeWedgeGeometry(o.sx || 1, o.sy || 1, o.sz || 1);
                } else if (o.shape === 'head') {
                    geoCache[geoKey] = makeHeadGeometry(o.sx || 1, o.sy || 1, o.sz || 1, Math.max(8, qualitySettings.sphereSegments));
                } else if (o.shape === 'cylinderx') {
                    geoCache[geoKey] = makeCylinderXGeometry(o.sx || 1, o.sy || 1, o.sz || 1, Math.max(8, qualitySettings.sphereSegments));
                } else {
                    geoCache[geoKey] = new THREE.BoxGeometry(o.sx || 1, o.sy || 1, o.sz || 1, 1, 1, 1);
                }
            }
            const geo = geoCache[geoKey];
            // opacity=0 (Transparency=1) — валидное значение; раньше `o.opacity || 1`
            // превращал его в 1, и невидимые детали рисовались непрозрачными.
            const op = (o.opacity === undefined || o.opacity === null) ? 1 : o.opacity;

            // Текстура — только на "high", как и остальные quality-флаги
            const texId = qualitySettings.textures ? o.texture : null;

            // Decal накладывается РОВНО на одну грань (o.textureFace —
            const FACE_TO_BOX_GROUP = {
                Right: 0, Left: 1, Top: 2, Bottom: 3, Back: 4, Front: 5,
            };
            // meshId (реальная кастомная геометрия, см.
            const isBoxShape = !o.meshId && (!o.shape || o.shape === 'block' || o.shape === 'box');
            // Все Decal детали (o.decals, по одному на грань) — только для боксов и только с текстурами
            const decalList = (qualitySettings.textures && isBoxShape && Array.isArray(o.decals) && o.decals.length) ? o.decals : null;
            // Decal — своя явная грань (Face), уже вычислена корректно
            let implicitFaceIdx = null;
            if (texId && (o.textureFace === null || o.textureFace === undefined || o.textureFace === '') && isBoxShape) {
                const sx = o.sx || 1, sy = o.sy || 1, sz = o.sz || 1;
                const areaX = sy * sz, areaY = sx * sz, areaZ = sx * sy;
                implicitFaceIdx = (areaX >= areaY && areaX >= areaZ) ? 0
                    : (areaY >= areaZ) ? 2 : 4;
            }
            // Face у Decal в файле — число NormalId (Right=0, Top=1, Back=2, Left=3, Bottom=4, Front=5),
            // а не имя: раньше число не находилось в таблице и ВСЕГДА превращалось в Front.
            const _faceName = (typeof o.textureFace === 'number')
                ? ['Right', 'Top', 'Back', 'Left', 'Bottom', 'Front'][o.textureFace]
                : o.textureFace;
            const faceIdx = (texId && o.textureFace !== null && o.textureFace !== undefined && o.textureFace !== '' && isBoxShape)
                ? (FACE_TO_BOX_GROUP[_faceName] ?? FACE_TO_BOX_GROUP.Front)
                : implicitFaceIdx;

            // SurfaceAppearance с AlphaMode=Overlay (o.alphaMode===0): цвет детали просвечивает там, где альфа текстуры
            // мала. Раньше такие пиксели вырезались alphaTest'ом (остаются «только линии» на High) или были чёрными.
            const overlayAlpha = !!(texId && o.meshId && faceIdx === null && o.alphaMode === 0);
            const baseColor = (texId && faceIdx === null && !overlayAlpha) ? '#ffffff' : (o.color || '#a0a0a0');
            // Decal на грани: свой уровень непрозрачности (см. textureOpacity на сервере), а не
            // прозрачность детали — иначе постер на невидимой детали (Transparency=1) пропадает.
            const decalOp = (faceIdx !== null && o.textureFace !== null && o.textureFace !== undefined && typeof o.textureOpacity === 'number') ? o.textureOpacity : op;
            const matKey = (o.color || '#a0a0a0') + '_' + op.toFixed(1) + '_' + decalOp.toFixed(1) + '_' +
                (faceIdx === null ? (texId || '') : (texId + '_face' + faceIdx)) + (overlayAlpha ? '_ovl' : '');
            if (!decalList && !matCache[matKey]) {
                // Прозрачные материалы НЕ пишут глубину, а полностью невидимые (Transparency=1) не рисуются вовсе:
                // иначе такая деталь (сортировка идёт по центру объекта, а не по поверхности) под одними
                // углами закрывала Decal и всё остальное позади себя.
                const baseOpts = {
                    transparent: op < 1.0,
                    opacity: op,
                    depthWrite: op >= 1.0,
                    visible: op > 0.01,
                    flatShading: currentQuality === 'low',
                };
                if (faceIdx !== null) {
                    // Массив материалов по группам граней BoxGeometry:
                    const plain = new THREE.MeshLambertMaterial({ ...baseOpts, color: o.color || '#a0a0a0' });
                    const textured = _applyDecalBias(new THREE.MeshLambertMaterial({
                        ...baseOpts, ...DECAL_FACE_OPTS, transparent: true, opacity: decalOp, depthWrite: decalOp >= 0.99,
                        color: '#ffffff', map: getOrLoadPartTexture(texId),
                    }));
                    const arr = [plain, plain, plain, plain, plain, plain];
                    arr[faceIdx] = textured;
                    matCache[matKey] = arr;
                } else {
                    matCache[matKey] = new THREE.MeshLambertMaterial({
                        ...baseOpts,
                        // Текстуру красим в тон o.color — она бы почти всегда
                        color: baseColor,
                        map: texId ? getOrLoadPartTexture(texId) : null,
                        // alphaTest — реальные меши (o.meshId) часто используют
                        // текстуру-атлас с прозрачными областями (PNG alpha);
                        // без него прозрачные пиксели рисуются непрозрачным
                        // чёрным (RGB под alpha=0 у большинства PNG — (0,0,0)),
                        // а не прозрачными, поэтому там, где в развёртке
                        // должна быть "дырка"/незанятая часть атласа, был
                        // виден сплошной чёрный кусок. Не влияет на полностью
                        // непрозрачные текстуры — alpha=1 везде проходит
                        // проверку тривиально.
                        alphaTest: (texId && o.meshId && !overlayAlpha) ? 0.5 : 0,
                    });
                    if (overlayAlpha) _applyOverlayAlpha(matCache[matKey]);
                }
            }
            let mat = matCache[matKey];
            if (decalList) {
                const dk = 'decals_' + (o.color || '#a0a0a0') + '_' + op.toFixed(1) + '_' +
                    decalList.map(d => d.face + ':' + d.tex + ':' + d.op.toFixed(1)).join('|');
                if (!matCache[dk]) {
                    const dBase = { transparent: op < 1.0, opacity: op, depthWrite: op >= 1.0, visible: op > 0.01, flatShading: currentQuality === 'low' };
                    const plainM = new THREE.MeshLambertMaterial({ ...dBase, color: o.color || '#a0a0a0' });
                    const arrM = [plainM, plainM, plainM, plainM, plainM, plainM];
                    const NAMES = ['Right', 'Top', 'Back', 'Left', 'Bottom', 'Front'];
                    for (const d of decalList) {
                        const g = FACE_TO_BOX_GROUP[typeof d.face === 'number' ? NAMES[d.face] : d.face];
                        if (g === undefined) continue;
                        // свой opacity у Decal (Transparency Decal), а не прозрачность детали — постер на невидимой детали виден
                        arrM[g] = _applyDecalBias(new THREE.MeshLambertMaterial({ ...dBase, ...DECAL_FACE_OPTS, transparent: true, opacity: d.op, depthWrite: d.op >= 0.99, color: '#ffffff', map: getOrLoadPartTexture(d.tex) }));
                    }
                    matCache[dk] = arrM;
                }
                mat = matCache[dk];
            }
            // Особые материалы (металлы, Neon) и MaterialVariant — только для сплошных мешей
            if (!Array.isArray(mat) && !texId && (o.mvar || MATERIAL_STYLE[o.material])) {
                const mk = 'mat_' + o.material + '_' + (o.mvar ? o.mvar.name : '') + '_' + (o.color || '') + '_' + op.toFixed(1)
                    + '_' + Math.round(((o.sx || 1) + (o.sz || 1)) * 4);
                if (!matCache[mk]) matCache[mk] = makeStyledMaterial(o, op);
                mat = matCache[mk];
            }

            let meshGeo = geo, meshMat = mat;
            if (o.cloth && qualitySettings.textures && isBoxShape && CLOTH_REGIONS[o.cloth.limb]) {
                meshGeo = makeClothGeometry(o, geo);
                const ck = 'cloth_' + (o.color || '') + '_' + (o.cloth.shirt || '') + '_' + (o.cloth.pants || '') + '_' + op.toFixed(1);
                if (!matCache[ck]) {
                    matCache[ck] = new THREE.MeshLambertMaterial({
                        color: '#ffffff', transparent: op < 1.0, opacity: op,
                        map: getClothTexture(o.color, o.cloth.shirt, o.cloth.pants),
                    });
                }
                meshMat = matCache[ck];
            }
            const mesh = new THREE.Mesh(meshGeo, meshMat);
            // SpecialMesh.Offset — сдвиг меша в ЛОКАЛЬНЫХ осях детали
            let bpx = o.px || 0, bpy = o.py || 0, bpz = o.pz || 0;
            if (o.meshOffset) {
                const [ox, oy, oz] = o.meshOffset;
                if (o.rot && o.rot.length >= 9) {
                    bpx += o.rot[0] * ox + o.rot[1] * oy + o.rot[2] * oz;
                    bpy += o.rot[3] * ox + o.rot[4] * oy + o.rot[5] * oz;
                    bpz += o.rot[6] * ox + o.rot[7] * oy + o.rot[8] * oz;
                } else { bpx += ox; bpy += oy; bpz += oz; }
            }
            mesh.position.set(bpx, bpy, bpz);

            if (o.rot && o.rot.length >= 9) {
                const rm = new THREE.Matrix4();
                // o.rot — row-major [R00,R01,R02, R10,R11,R12, R20,R21,R22],
                rm.set(
                    o.rot[0], o.rot[1], o.rot[2], bpx,
                    o.rot[3], o.rot[4], o.rot[5], bpy,
                    o.rot[6], o.rot[7], o.rot[8], bpz,
                    0, 0, 0, 1
                );
                mesh.matrix.copy(rm);
                mesh.matrixAutoUpdate = false;
            } else {
                mesh.matrixAutoUpdate = false;
                mesh.updateMatrix();
            }

            mesh.castShadow = qualitySettings.shadows;
            mesh.receiveShadow = qualitySettings.shadows;
            mesh.userData.ref = o.ref;
            mesh.userData.cls = o.class;
            mesh.userData.shape = o.shape;
            mesh.userData.pivotOffset = o.pivotOffset || null; // PivotOffset детали (GetPivot/PivotTo)
            mesh.userData.sx = o.sx || 1;
            mesh.userData.sy = o.sy || 1;
            mesh.userData.sz = o.sz || 1;
            mesh.userData.anchoredFlag = !!o.anchored;
            mesh.userData.cancollideFlag = o.cancollide !== false;
            mesh.frustumCulled = true;

            if (op < 1.0) {
                const dw = op > 0.7;
                if (Array.isArray(mesh.material)) mesh.material.forEach(m => { m.depthWrite = dw; });
                else mesh.material.depthWrite = dw;
            }
            if (o.meshId) scheduleRealMeshSwap(o, mesh);
            if (o.unionMesh) scheduleUnionMeshSwap(o, mesh);
            return mesh;
        }

        // ============ ЧАСТИЦЫ (ParticleEmitter) ============
        // Сервер отдаёт эмиттеры (/api/particles), здесь они симулируются на CPU
        // и рисуются одним THREE.Points на эмиттер (свой ShaderMaterial: размер в
        // студах, поворот, цвет/прозрачность по времени жизни).
        const PS = { list: [], key: '', texCache: {}, soft: null, lastT: 0, timer: null, loading: false };
        const PS_MAX_PER = 1500;
        const PS_MAX_TOTAL = 8000;
        const PS_AXES = { 0: [1, 0, 0], 1: [0, 1, 0], 2: [0, 0, 1], 3: [0, -1, 0], 4: [0, 0, -1], 5: [-1, 0, 0] };

        function _psSoftTexture() {
            if (PS.soft) return PS.soft;
            const c = document.createElement('canvas');
            c.width = c.height = 64;
            const g = c.getContext('2d');
            const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
            gr.addColorStop(0, 'rgba(255,255,255,1)');
            gr.addColorStop(0.4, 'rgba(255,255,255,.55)');
            gr.addColorStop(1, 'rgba(255,255,255,0)');
            g.fillStyle = gr;
            g.fillRect(0, 0, 64, 64);
            PS.soft = new THREE.CanvasTexture(c);
            return PS.soft;
        }

        // Текстура эмиттера: rbxassetid://N / ссылка с id= / число -> через asset-proxy,
        // всё остальное (rbxasset://... встроенные .dds) -> мягкий круглый спрайт.
        function _psLoadTexture(uniforms, url) {
            const m = /(?:id=|rbxassetid:\/\/|^)(\d{3,})/.exec(String(url || ''));
            if (!m) { uniforms.map.value = _psSoftTexture(); return; }
            const id = m[1];
            if (PS.texCache[id]) {
                const c = PS.texCache[id];
                uniforms.map.value = c.tex || _psSoftTexture();
                if (!c.tex && !c.failed) c.waiters.push(uniforms);
                return;
            }
            const entry = PS.texCache[id] = { tex: null, failed: false, waiters: [uniforms] };
            uniforms.map.value = _psSoftTexture();
            new THREE.TextureLoader().load('/api/asset-proxy?id=' + id, (tex) => {
                entry.tex = tex;
                entry.waiters.forEach(u => { u.map.value = tex; });
                entry.waiters = [];
            }, undefined, () => {
                entry.failed = true;
                console.warn('Particle texture ' + id + ' не загрузилась — мягкий спрайт вместо неё');
            });
        }

        function _psSeqNum(seq, t, dflt) {
            // В файле значение может быть обычным числом (константа) или вообще
            // отсутствовать (тогда парсер подставляет число-дефолт) — это не «пустая»
            // последовательность: раньше 0 принимался за «нет данных» и частицы были
            // полностью прозрачными.
            if (typeof seq === 'number') return [seq, 0];
            if (!seq || !seq.length) return [dflt === undefined ? 1 : dflt, 0];
            if (t <= seq[0].time) return [seq[0].value, seq[0].envelope || 0];
            for (let i = 1; i < seq.length; i++) {
                if (t <= seq[i].time) {
                    const a = seq[i - 1], b = seq[i];
                    const k = (t - a.time) / Math.max(1e-6, b.time - a.time);
                    return [a.value + (b.value - a.value) * k, (a.envelope || 0) + ((b.envelope || 0) - (a.envelope || 0)) * k];
                }
            }
            const l = seq[seq.length - 1];
            return [l.value, l.envelope || 0];
        }

        function _psSeqColor(seq, t, out) {
            if (!seq || !seq.length) { out[0] = out[1] = out[2] = 1; return; }
            if (t <= seq[0].time) { out[0] = seq[0].r; out[1] = seq[0].g; out[2] = seq[0].b; return; }
            for (let i = 1; i < seq.length; i++) {
                if (t <= seq[i].time) {
                    const a = seq[i - 1], b = seq[i];
                    const k = (t - a.time) / Math.max(1e-6, b.time - a.time);
                    out[0] = a.r + (b.r - a.r) * k; out[1] = a.g + (b.g - a.g) * k; out[2] = a.b + (b.b - a.b) * k;
                    return;
                }
            }
            const l = seq[seq.length - 1];
            out[0] = l.r; out[1] = l.g; out[2] = l.b;
        }

        function _psRange(r, dmin, dmax) {
            const lo = (r && typeof r.min === 'number') ? r.min : dmin;
            const hi = (r && typeof r.max === 'number') ? r.max : dmax;
            return lo + Math.random() * (hi - lo);
        }

        function _psMat4(r, p) {
            const m = new THREE.Matrix4();
            m.set(r[0], r[1], r[2], p[0], r[3], r[4], r[5], p[1], r[6], r[7], r[8], p[2], 0, 0, 0, 1);
            return m;
        }

        function _psDispose() {
            for (const e of PS.list) {
                if (scene) scene.remove(e.points);
                e.geo.dispose();
                e.mat.dispose();
            }
            PS.list = [];
        }

        function _psBuild(d) {
            const p = d.p || {};
            const rate = typeof p.Rate === 'number' ? p.Rate : 20;
            const life = p.Lifetime || { min: 5, max: 5 };
            const ts = typeof p.TimeScale === 'number' ? p.TimeScale : 1;
            const n = Math.max(8, Math.min(PS_MAX_PER, Math.ceil(rate * Math.max(life.max || 0, life.min || 0) * Math.max(ts, 0.1) * 1.25) + 8));
            const geo = new THREE.BufferGeometry();
            const pos = new Float32Array(n * 3), size = new Float32Array(n), rot = new Float32Array(n), col = new Float32Array(n * 4);
            geo.setAttribute('position', new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage));
            geo.setAttribute('aSize', new THREE.BufferAttribute(size, 1).setUsage(THREE.DynamicDrawUsage));
            geo.setAttribute('aRot', new THREE.BufferAttribute(rot, 1).setUsage(THREE.DynamicDrawUsage));
            geo.setAttribute('aColor', new THREE.BufferAttribute(col, 4).setUsage(THREE.DynamicDrawUsage));
            geo.setDrawRange(0, 0);
            const additive = (typeof p.LightEmission === 'number' ? p.LightEmission : 0) >= 0.5;
            const uniforms = { map: { value: null }, uScale: { value: 600 } };
            _psLoadTexture(uniforms, p.Texture);
            const mat = new THREE.ShaderMaterial({
                uniforms: uniforms,
                vertexShader:
                    'attribute float aSize; attribute float aRot; attribute vec4 aColor;' +
                    'varying vec4 vColor; varying float vRot; uniform float uScale;' +
                    'void main(){ vColor = aColor; vRot = aRot;' +
                    ' vec4 mv = modelViewMatrix * vec4(position, 1.0);' +
                    ' gl_PointSize = clamp(aSize * uScale / max(0.001, -mv.z), 0.0, 512.0);' +
                    ' gl_Position = projectionMatrix * mv; }',
                fragmentShader:
                    'uniform sampler2D map; varying vec4 vColor; varying float vRot;' +
                    'void main(){ vec2 c = gl_PointCoord - 0.5; float s = sin(vRot), co = cos(vRot);' +
                    ' c = vec2(co * c.x - s * c.y, s * c.x + co * c.y) + 0.5;' +
                    ' if (c.x < 0.0 || c.x > 1.0 || c.y < 0.0 || c.y > 1.0) discard;' +
                    ' vec4 col = texture2D(map, c) * vColor; if (col.a < 0.01) discard; gl_FragColor = col; }',
                transparent: true, depthWrite: false,
                blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending,
            });
            const points = new THREE.Points(geo, mat);
            points.frustumCulled = false;
            points.renderOrder = 10;
            scene.add(points);
            const att = d.att || { p: [0, 0, 0], r: [1, 0, 0, 0, 1, 0, 0, 0, 1] };
            const w = d.world || att;
            return {
                d: d, p: p, n: n, count: 0, acc: 0, geo: geo, mat: mat, points: points,
                pos: pos, size: size, rot: rot, col: col,
                vel: new Float32Array(n * 3), age: new Float32Array(n), life: new Float32Array(n),
                rnd: new Float32Array(n * 2), spin: new Float32Array(n), rot0: new Float32Array(n),
                attMat: _psMat4(att.r, att.p), staticMat: _psMat4(w.r, w.p), mat4: new THREE.Matrix4(),
                dir: PS_AXES[p.EmissionDirection !== undefined ? p.EmissionDirection : 1] || PS_AXES[1],
            };
        }

        async function loadParticles() {
            if (typeof scene === 'undefined' || !scene || typeof THREE === 'undefined') return;
            if (PS.loading) return;
            PS.loading = true;
            try {
                const r = await api('GET', '/api/particles');
                if (!r || !r.ok) return;
                const key = JSON.stringify(r.emitters);
                if (key === PS.key) return;       // ничего не изменилось — не сбрасываем живые частицы
                PS.key = key;
                _psDispose();
                for (const d of r.emitters) {
                    try { PS.list.push(_psBuild(d)); } catch (e) { console.error('particle build:', e); }
                }
                const _msg = 'Particles: эмиттеров ' + PS.list.length +
                    PS.list.map(e => '\n  • ' + e.d.name + ' @ ' + e.d.world.p.map(v => v.toFixed(1)).join(', ') +
                        ' | Enabled=' + (e.p.Enabled !== false) + ' Rate=' + e.p.Rate + ' tex=' + (e.p.Texture || '—')).join('');
                console.log(_msg);
                try { logLuaOutput('info', _msg); } catch (e) { /* Output ещё не готов */ }
                setTimeout(() => {
                    const m2 = 'Particles alive: ' + PS.list.map(e => e.d.name + '=' + e.count + (e.points.visible ? '' : '(скрыт: далеко)')).join(', ');
                    console.log(m2);
                    try { logLuaOutput('info', m2); } catch (e) { /* Output ещё не готов */ }
                }, 1500);
            } catch (e) {
                console.error('loadParticles:', e);
            } finally {
                PS.loading = false;
            }
        }

        function _psSchedule() {
            clearTimeout(PS.timer);
            PS.timer = setTimeout(loadParticles, 300);
        }

        function _psSpawn(e, mat) {
            if (e.count >= e.n) return;
            const p = e.p, i = e.count++;
            const o = e.d.onPart ? 1 : 0;
            // точка появления: в Attachment — точка; в детали — внутри объёма (Box/Sphere)
            let lx = 0, ly = 0, lz = 0;
            if (o) {
                const sz = e.d.partSize || [1, 1, 1];
                if (p.Shape === 1) {           // Sphere
                    let x, y, z;
                    do { x = Math.random() * 2 - 1; y = Math.random() * 2 - 1; z = Math.random() * 2 - 1; } while (x * x + y * y + z * z > 1);
                    lx = x * sz[0] / 2; ly = y * sz[1] / 2; lz = z * sz[2] / 2;
                } else {
                    lx = (Math.random() - 0.5) * sz[0]; ly = (Math.random() - 0.5) * sz[1]; lz = (Math.random() - 0.5) * sz[2];
                }
            }
            // направление: ось эмиттера + случайное отклонение SpreadAngle (градусы)
            const sa = p.SpreadAngle || { x: 0, y: 0 };
            const ax = Math.abs(sa.x || 0), ay = Math.abs(sa.y || 0);
            let dx, dy, dz;
            const A = e.dir;
            if (Math.max(ax, ay) >= 180) {
                let x, y, z, l;
                do { x = Math.random() * 2 - 1; y = Math.random() * 2 - 1; z = Math.random() * 2 - 1; l = x * x + y * y + z * z; } while (l > 1 || l < 1e-4);
                l = Math.sqrt(l); dx = x / l; dy = y / l; dz = z / l;
            } else {
                const u = Math.abs(A[1]) > 0.9 ? [1, 0, 0] : [0, 1, 0];
                // v1 = A x u, v2 = A x v1
                let v1 = [A[1] * u[2] - A[2] * u[1], A[2] * u[0] - A[0] * u[2], A[0] * u[1] - A[1] * u[0]];
                const l1 = Math.hypot(v1[0], v1[1], v1[2]) || 1; v1 = [v1[0] / l1, v1[1] / l1, v1[2] / l1];
                const v2 = [A[1] * v1[2] - A[2] * v1[1], A[2] * v1[0] - A[0] * v1[2], A[0] * v1[1] - A[1] * v1[0]];
                const t1 = (Math.random() * 2 - 1) * ax * Math.PI / 180, t2 = (Math.random() * 2 - 1) * ay * Math.PI / 180;
                const s1 = Math.sin(t1), c1 = Math.cos(t1), s2 = Math.sin(t2), c2 = Math.cos(t2);
                // сначала поворот вокруг v1 (в плоскости A-v2), затем вокруг v2
                const bx = A[0] * c1 + v2[0] * s1, by = A[1] * c1 + v2[1] * s1, bz = A[2] * c1 + v2[2] * s1;
                dx = bx * c2 + v1[0] * s2; dy = by * c2 + v1[1] * s2; dz = bz * c2 + v1[2] * s2;
                const l = Math.hypot(dx, dy, dz) || 1; dx /= l; dy /= l; dz /= l;
            }
            const speed = _psRange(p.Speed, 5, 5);
            const k = i * 3;
            const m = mat.elements;       // column-major
            const locked = !!p.LockedToPart;
            // локальные -> мировые координаты (если не LockedToPart); LockedToPart хранит локальные
            if (locked) {
                e.pos[k] = lx; e.pos[k + 1] = ly; e.pos[k + 2] = lz;
                e.vel[k] = dx * speed; e.vel[k + 1] = dy * speed; e.vel[k + 2] = dz * speed;
            } else {
                e.pos[k] = m[0] * lx + m[4] * ly + m[8] * lz + m[12];
                e.pos[k + 1] = m[1] * lx + m[5] * ly + m[9] * lz + m[13];
                e.pos[k + 2] = m[2] * lx + m[6] * ly + m[10] * lz + m[14];
                e.vel[k] = (m[0] * dx + m[4] * dy + m[8] * dz) * speed;
                e.vel[k + 1] = (m[1] * dx + m[5] * dy + m[9] * dz) * speed;
                e.vel[k + 2] = (m[2] * dx + m[6] * dy + m[10] * dz) * speed;
            }
            e.age[i] = 0;
            e.life[i] = Math.max(0.02, _psRange(p.Lifetime, 5, 5));
            e.rnd[i * 2] = Math.random() * 2 - 1;
            e.rnd[i * 2 + 1] = Math.random() * 2 - 1;
            e.rot0[i] = _psRange(p.Rotation, 0, 0) * Math.PI / 180;
            e.spin[i] = _psRange(p.RotSpeed, 0, 0) * Math.PI / 180;
        }

        function psEmit(ref, count) {
            for (const e of PS.list) {
                if (e.d.ref !== ref) continue;
                const mat = _psWorldMat(e);
                for (let i = 0; i < count; i++) _psSpawn(e, mat);
            }
        }

        function _psWorldMat(e) {
            const part = sceneObjs[e.d.part];
            if (part) {
                e.mat4.compose(part.position, part.quaternion, new THREE.Vector3(1, 1, 1));
                return e.mat4.multiply(e.attMat);
            }
            return e.staticMat;
        }

        const _psTmpC = [1, 1, 1];

        function updateParticles(nowMs) {
            if (!PS.list.length) { PS.lastT = nowMs; return; }
            let dt = (nowMs - PS.lastT) / 1000;
            PS.lastT = nowMs;
            if (!(dt > 0)) return;
            dt = Math.min(dt, 0.05);
            // перевод размера в студах -> пиксели точки
            let scale = 600;
            if (renderer && camera) {
                const hpx = renderer.getDrawingBufferSize(new THREE.Vector2()).y;
                scale = hpx / (2 * Math.tan(camera.fov * Math.PI / 360));
            }
            const qf = currentQuality === 'low' ? 0.5 : (currentQuality === 'medium' ? 0.8 : 1);
            const maxDist = (qualitySettings && qualitySettings.renderDistance ? qualitySettings.renderDistance : 300) * 1.5;
            let total = 0;
            for (const e of PS.list) total += e.count;
            for (const e of PS.list) {
                const p = e.p;
                const mat = _psWorldMat(e);
                const me = mat.elements;
                // дальние эмиттеры не считаем (и не рисуем)
                const ddx = me[12] - camera.position.x, ddy = me[13] - camera.position.y, ddz = me[14] - camera.position.z;
                if (ddx * ddx + ddy * ddy + ddz * ddz > maxDist * maxDist) { e.points.visible = false; e.count = 0; continue; }
                e.points.visible = true;
                e.mat.uniforms.uScale.value = scale;
                const ts = (typeof p.TimeScale === 'number' ? p.TimeScale : 1);
                const sdt = dt * ts;
                // эмиссия
                if (p.Enabled !== false && total < PS_MAX_TOTAL) {
                    e.acc += (typeof p.Rate === 'number' ? p.Rate : 20) * sdt * qf;
                    let n = Math.floor(e.acc);
                    e.acc -= n;
                    if (n > 200) n = 200;
                    for (let i = 0; i < n; i++) _psSpawn(e, mat);
                } else {
                    e.acc = 0;
                }
                // симуляция
                const acc = p.Acceleration || { x: 0, y: 0, z: 0 };
                const drag = Math.max(0, p.Drag || 0);
                const dk = drag > 0 ? Math.exp(-drag * sdt) : 1;
                const locked = !!p.LockedToPart;
                const bright = typeof p.Brightness === 'number' ? p.Brightness : 1;
                let i = 0;
                while (i < e.count) {
                    e.age[i] += sdt;
                    if (e.age[i] >= e.life[i]) {
                        // swap-remove: последний встаёт на место умершего
                        const last = --e.count;
                        if (i !== last) {
                            const a = i * 3, b = last * 3;
                            e.pos[a] = e.pos[b]; e.pos[a + 1] = e.pos[b + 1]; e.pos[a + 2] = e.pos[b + 2];
                            e.vel[a] = e.vel[b]; e.vel[a + 1] = e.vel[b + 1]; e.vel[a + 2] = e.vel[b + 2];
                            e.age[i] = e.age[last]; e.life[i] = e.life[last];
                            e.rnd[i * 2] = e.rnd[last * 2]; e.rnd[i * 2 + 1] = e.rnd[last * 2 + 1];
                            e.rot0[i] = e.rot0[last]; e.spin[i] = e.spin[last];
                        }
                        continue;
                    }
                    const k = i * 3;
                    e.vel[k] += acc.x * sdt; e.vel[k + 1] += acc.y * sdt; e.vel[k + 2] += acc.z * sdt;
                    if (dk !== 1) { e.vel[k] *= dk; e.vel[k + 1] *= dk; e.vel[k + 2] *= dk; }
                    e.pos[k] += e.vel[k] * sdt; e.pos[k + 1] += e.vel[k + 1] * sdt; e.pos[k + 2] += e.vel[k + 2] * sdt;
                    i++;
                }
                // выгрузка в атрибуты
                const P = e.geo.attributes.position.array;
                for (let j = 0; j < e.count; j++) {
                    const t = e.age[j] / e.life[j];
                    const k = j * 3;
                    if (locked) {
                        const x = e.pos[k], y = e.pos[k + 1], z = e.pos[k + 2];
                        P[k] = me[0] * x + me[4] * y + me[8] * z + me[12];
                        P[k + 1] = me[1] * x + me[5] * y + me[9] * z + me[13];
                        P[k + 2] = me[2] * x + me[6] * y + me[10] * z + me[14];
                    } else { P[k] = e.pos[k]; P[k + 1] = e.pos[k + 1]; P[k + 2] = e.pos[k + 2]; }
                    const sv = _psSeqNum(p.Size, t, 1);
                    e.size[j] = Math.max(0, sv[0] + sv[1] * e.rnd[j * 2]);
                    const tv = _psSeqNum(p.Transparency, t, 0);
                    const alpha = 1 - Math.min(1, Math.max(0, tv[0] + tv[1] * e.rnd[j * 2 + 1]));
                    _psSeqColor(p.Color, t, _psTmpC);
                    const c4 = j * 4;
                    e.col[c4] = _psTmpC[0] * bright; e.col[c4 + 1] = _psTmpC[1] * bright; e.col[c4 + 2] = _psTmpC[2] * bright;
                    e.col[c4 + 3] = alpha;
                    e.rot[j] = e.rot0[j] + e.spin[j] * e.age[j];
                }
                e.geo.setDrawRange(0, e.count);
                e.geo.attributes.position.needsUpdate = true;
                e.geo.attributes.aSize.needsUpdate = true;
                e.geo.attributes.aRot.needsUpdate = true;
                e.geo.attributes.aColor.needsUpdate = true;
            }
        }

        async function reloadScene() {
            if (isPlaying) {
                notify(t('notify_stop_play_first'), 'warn');
                return;
            }
            lastCameraUpdate = performance.now();
            lastReloadTarget = { x: target.x, y: target.y, z: target.z };
            const params = new URLSearchParams({
                cx: Math.round(target.x),
                cy: Math.round(target.y),
                cz: Math.round(target.z),
                r: qualitySettings.renderDistance,
                quality: currentQuality
            });

            const r = await api('GET', '/api/scene?' + params.toString());
            if (!r.ok) return;

            // Очистка старых объектов
            for (const mesh of Object.values(sceneObjs)) {
                scene.remove(mesh);
                // sharedMesh (см. loadRealMeshGeometry/_buildGeometryFromParsed)
                if (mesh.geometry && !mesh.geometry.userData.sharedMesh) mesh.geometry.dispose();
                if (mesh.material) {
                    if (Array.isArray(mesh.material)) {
                        mesh.material.forEach(m => {
                            if (m.map) m.map.dispose();
                            m.dispose();
                        });
                    } else {
                        if (mesh.material.map) mesh.material.map.dispose();
                        mesh.material.dispose();
                    }
                }
            }
            sceneObjs = {};
            _unionGeoCache = {}; // другой файл — те же ref, другая геометрия

            // Сбрасываем кеш raycasting
            raycasterCache.objects = [];
            raycasterCache.lastUpdate = 0;

            if (window._selBox) {
                scene.remove(window._selBox);
                window._selBox = null;
            }

            // Кеши геометрий и материалов
            const geoCache = {};
            const matCache = {};

            let objects = r.objects;
            let totalAvailable = r.total || objects.length;

            // Применяем лимиты качества
            if (qualitySettings.maxObjects && objects.length > qualitySettings.maxObjects) {
                if (currentQuality === 'high') {
                    const maxHighObjects = Math.min(objects.length, 10000);
                    objects = objects.slice(0, maxHighObjects);
                } else {
                    objects = objects.slice(0, qualitySettings.maxObjects);
                }
            }

            for (const o of objects) {
                // Импортированные 3D-аватары — не обычные Part/MeshPart,
                const cached = window._avatarMeshCache && window._avatarMeshCache[o.ref];
                const mesh = cached ? cached.object : buildMeshFromObj(o, geoCache, matCache);
                if (cached) {
                    // Геометрия закэширована и не перестраивается, но
                    mesh.position.set(o.px || 0, o.py || 0, o.pz || 0);
                    if (o.rot && o.rot.length >= 9) {
                        const rm = new THREE.Matrix4();
                        rm.set(
                            o.rot[0], o.rot[1], o.rot[2], 0,
                            o.rot[3], o.rot[4], o.rot[5], 0,
                            o.rot[6], o.rot[7], o.rot[8], 0,
                            0, 0, 0, 1
                        );
                        mesh.quaternion.setFromRotationMatrix(rm);
                    }
                    mesh.userData.ref = o.ref;
                }
                scene.add(mesh);
                sceneObjs[o.ref] = mesh;
            }

            // Чистим кэш от аватаров, чьи Instance удалили через обычный
            // Explorer/Delete — сервер уже не пришлёт такой ref в objects.
            if (window._avatarMeshCache) {
                const liveRefs = new Set(objects.map(o => o.ref));
                for (const ref of Object.keys(window._avatarMeshCache)) {
                    if (!liveRefs.has(Number(ref))) {
                        const entry = window._avatarMeshCache[ref];
                        entry.object.traverse(n => {
                            if (n.isMesh) {
                                if (n.geometry) n.geometry.dispose();
                                const mats = Array.isArray(n.material) ? n.material : [n.material];
                                mats.forEach(m => { if (m) { if (m.map) m.map.dispose(); m.dispose(); } });
                            }
                        });
                        delete window._avatarMeshCache[ref];
                    }
                }
            }

            const shown = Object.keys(sceneObjs).length;
            notify(t('notify_scene_loaded', { n: shown }) + (totalAvailable > shown ? t('notify_scene_of', { total: totalAvailable }) : ''));
            updateInventoryCount();

            // Обновляем выделение если было
            if (selectedRefs.size || (selectedRef && sceneObjs[selectedRef])) {
                highlightSelected(selectedRef);
            }
            loadParticles();
        }

        function highlightSelected(ref) {
            const selSet = new Set(selectedRefs);
            if (ref) selSet.add(ref);
            for (const [r, mesh] of Object.entries(sceneObjs)) {
                // ФИКС: импортированные 3D-аватары (importAvatarIntoScene)
                const isSelected = selSet.has(parseInt(r));
                const applyEmissive = (m) => {
                    if (!m || !m.material) return;
                    const mats = Array.isArray(m.material) ? m.material : [m.material];
                    mats.forEach(mat => {
                        if (!mat) return;
                        mat.emissive = new THREE.Color(isSelected ? 0xff6600 : 0);
                        mat.emissiveIntensity = isSelected ? 0.4 : 0;
                    });
                };
                if (mesh.isMesh) {
                    applyEmissive(mesh);
                } else if (typeof mesh.traverse === 'function') {
                    mesh.traverse(n => { if (n.isMesh) applyEmissive(n); });
                }
            }
            if (window._selBox) {
                scene.remove(window._selBox);
                window._selBox = null;
            }
            // Рамки — только у первых 100 выбранных, иначе выделение целой карты тормозит.
            const boxRefs = [...selSet].filter(r => sceneObjs[r]).slice(0, 100);
            if (boxRefs.length) {
                const group = new THREE.Group();
                boxRefs.forEach(r => group.add(new THREE.BoxHelper(sceneObjs[r], 0xff6600)));
                scene.add(group);
                window._selBox = group;
            }
        }

        // ============ PLAY-РЕЖИМ (ФИЗИКА + ПЕРСОНАЖ) ============
        let isPlaying = false;
        let prevFogFar = null; // scene.fog.far на момент старта Play — восстанавливается в stopPlay()
        let physicsWorld = null;
        let physicsBodies = {};   // ref -> CANNON.Body
        let playSnapshot = {};    // ref -> THREE.Matrix4 до запуска
        let playOnlyRefs = new Set(); // ref-ы мешей, подгруженных только для Play
        // Позиция каждого загруженного (в Play) объекта — независимо от
        let loadedObjPos = {}; // ref -> {x,y,z}
        // Раньше part.Size для ОБЫЧНОГО (не GUI) BasePart в Lua-скриптах
        // не читался НИОТКУДА и всегда был nil — .Size вообще не был
        // особым случаем в мосте (в отличие от Position/CFrame), а общий
        // "мусорный ящик" свойств (luaGenericPropsByRef) заполняется только
        // ЗАПИСЯМИ, никогда из данных файла. Любой скрипт вида
        // "part.Size.Z" на детали, которую сам ни разу не трогал, падал
        // с ошибкой (в MenuCamera.lua это останавливало enableSongCamera
        // ДО строки camera.CFrame = ... — камера песни вообще никогда не
        // переставлялась). См. __get_size ниже.
        let loadedObjSize = {}; // ref -> {x,y,z}
        let charPushX = 0, charPushZ = 0, charPushT = 0;
        let charBody = null;
        let charMesh = null; // куб для вида от третьего лица, см. toggleThirdPerson

        function updateCharMeshVisibility() {
            if (charMesh) charMesh.visible = isPlaying && thirdPerson;
        }
        let jumpQueued = false;
        let canJump = false;
        let prevCameraState = null;
        const GRAVITY_STUDS = -196.2; // workspace.Gravity в настоящем Roblox
        // Размеры настоящего Roblox R15 — сняты с content/avatar/characterR15.rbxm:
        // HumanoidRootPart 2x2x1, Humanoid.HipHeight 1.35 (ступни на 2.35 ниже центра HRP),
        // макушка на 2.65 выше центра HRP => рост 5.0 стада, ширина торса 2.0.
        // Глаза (центр головы) — на 4.5 над землёй.
        const R15_HEIGHT = 5.0;
        const R15_EYE_ABOVE_GROUND = 4.5;
        const R15_HRP_ABOVE_GROUND = 2.35;   // HipHeight 1.35 + половина высоты HRP (1.0): центр HRP в настоящем Roblox
        const CHAR_RADIUS = 1.0;      // половина ширины R15 (2 стада); коллайдер — сфера, центр на CHAR_RADIUS над землёй
        // (было 2.2 — со стандартным Roblox-персонажем шириной ~2 стада
        const CHAR_SPEED = 16;        // стадов/сек — дефолтный Humanoid.WalkSpeed
        // Реальный WalkSpeed/JumpPower виртуального Humanoid (см.
        // bootstrapClientPlayer) — карта может их менять (например,
        // MenuCamera.lua ставит WalkSpeed=0 на время камеры песни); раньше
        // Humanoid у игрока не существовал вообще, и такие вызовы были
        // no-op'ами — игрок продолжал ходить, пока шла сценарная камера.
        let charWalkSpeed = CHAR_SPEED;
        const STEP_HEIGHT = 3.2;      // студов — низкий бордюр перешагиваем автоматически
        const JUMP_VELOCITY = 50;     // Humanoid.JumpPower (как видят скрипты)
        // В Roblox JumpPower 50 == JumpHeight 7.2; чистая v=50 при g=196.2 даёт лишь 6.37,
        // поэтому реальную начальную скорость берём из высоты: v = sqrt(2*g*7.2) ≈ 53.15.
        const JUMP_POWER_TO_VELOCITY = Math.sqrt(2 * -GRAVITY_STUDS * 7.2) / 50;
        let charJumpPower = JUMP_VELOCITY;
        const EYE_HEIGHT = R15_EYE_ABOVE_GROUND - CHAR_RADIUS; // от центра сферы-коллайдера до глаз
        // Физику считаем не для всей загруженной сцены (при Quality=High это
        function maxStreamedBodies() { return qualitySettings.playBodies; }
        function maxVisualBodies() { return qualitySettings.visualBodies || qualitySettings.playBodies; }
        // Раньше геометрия для физики запрашивалась ОДИН раз при старте
        let lastStreamPos = { x: null, y: null, z: null };
        let streamInFlight = false;
        let fallingSinceMs = null; // когда персонаж начал падать без опоры под ногами
        const STREAM_REFRESH_DIST = 20;   // студов сместились — пора подгрузить ещё
        const STREAM_REFRESH_MS = 600;    // не чаще этого, даже если стоим на месте
        const STREAM_PRUNE_DIST = 5000;    // общий "дальний" предел (fog/начальный вид) — НЕ радиус подгрузки, см. qualitySettings.loadRadius
        const UNLOAD_MARGIN = 150;   // студов сверх loadRadius — гистерезис, чтобы объект
        // на самой границе загрузки/выгрузки не мигал каждый refresh-цикл
        // Радиус описанной сферы объекта: расстояния для стриминга/отсечения считаем до БЛИЖАЙШЕГО края,
        // иначе длинные стены (центр далеко, один конец рядом) пропадают и теряют физику.
        function objRadiusOfRef(ref) {
            const sz = loadedObjSize[ref];
            return sz ? 0.5 * Math.hypot(sz.x || 0, sz.y || 0, sz.z || 0) : 0;
        }
        function playRenderCutoff() {
            const loadMargin = 100;
            const visualRadius = qualitySettings.visualRadius || qualitySettings.loadRadius || 350;
            return Math.min(qualitySettings.renderDistance, STREAM_PRUNE_DIST * 0.6, visualRadius - loadMargin);
        }

        function togglePlay() {
            if (isPlaying) stopPlay(); else startPlay();
        }

        // Раньше спавн искался среди уже подгруженных в редакторе мешей —
        async function findSpawnPoint() {
            const r = await api('GET', '/api/spawn?team=auto');
            if (r && r.ok) {
                return { x: r.x, y: r.y + CHAR_RADIUS + 1, z: r.z };
            }
            notify(t('notify_spawn_not_found'), 'warn');
            return { x: target.x, y: target.y + 10, z: target.z };
        }

        // Кэши геометрии/материалов для мешей, которые Play подгружает по
        let playGeoCache = {}, playMatCache = {};

        // Последний CFrame, который СКРИПТ выставил детали (PivotTo/CFrame/Position/твин). Стриминг выгружает и
        // заново строит детали из исходных данных карты — без этого сдвинутый босс «откатывался» на старое
        // место, а дистанции отсечения считались от исходной точки, а не от текущей.
        let luaPartXform = {};   // ref -> {p:[x,y,z], q:[x,y,z,w]}
        function objPosFor(o) {
            const t = luaPartXform[o.ref];
            return t ? { x: t.p[0], y: t.p[1], z: t.p[2] } : { x: o.px, y: o.py, z: o.pz };
        }
        function applyMovedXform(ref, mesh) {
            const t = luaPartXform[ref];
            if (!t || !mesh) return;
            const p0 = new THREE.Vector3(), q0 = new THREE.Quaternion(), s0 = new THREE.Vector3();
            mesh.matrix.decompose(p0, q0, s0);
            mesh.matrix.compose(new THREE.Vector3(t.p[0], t.p[1], t.p[2]), new THREE.Quaternion(t.q[0], t.q[1], t.q[2], t.q[3]), s0);
        }
        // Данные деталей карты (ответы /api/scene) по ref — нужны, чтобы Instance:Clone() детали из файла
        // получал меш и физику (см. luaRealizeClonedParts): у виртуального клона своей геометрии нет.
        let playObjData = {};
        function addPhysicsBodyForObj(o) {
            playObjData[o.ref] = o;
            if (physicsBodies[o.ref]) return; // уже физически представлен
            let mesh = sceneObjs[o.ref];
            if (!mesh) {
                // Этого объекта не было в текущем виде редактора —
                // подгружаем именно для физики и добавляем в сцену.
                mesh = buildMeshFromObj(o, playGeoCache, playMatCache);
                if (!(o.ref in playSnapshot)) playSnapshot[o.ref] = mesh.matrix.clone();   // снимок — ИСХОДНОЕ положение
                applyMovedXform(o.ref, mesh);
                scene.add(mesh);
                sceneObjs[o.ref] = mesh;
                playOnlyRefs.add(o.ref);
            }
            if (!(o.ref in playSnapshot)) {
                playSnapshot[o.ref] = mesh.matrix.clone();
            }
            loadedObjPos[o.ref] = objPosFor(o);
            loadedObjSize[o.ref] = { x: o.sx, y: o.sy, z: o.sz };

            const pos = new THREE.Vector3();
            const quat = new THREE.Quaternion();
            mesh.matrix.decompose(pos, quat, new THREE.Vector3());

            const shape = buildCannonShape(mesh);
            if (!shape) return;

            const canCollide = mesh.userData.cancollideFlag !== false;

            // По умолчанию вся загруженная геометрия статична (mass=0),
            const body = new CANNON.Body({
                mass: 0,
                shape: shape,
                position: new CANNON.Vec3(pos.x, pos.y, pos.z),
                quaternion: new CANNON.Quaternion(quat.x, quat.y, quat.z, quat.w),
                allowSleep: true,
            });

            if (!canCollide) {
                body.collisionFilterGroup = 2;
                body.collisionFilterMask = 0;
                body.__noCollide = true;
            } else {
                if (luaPartGroup[o.ref]) body.__rbxGroup = luaPartGroup[o.ref];
                luaApplyGroup(body);
            }

            applyUnionTrimesh(body, mesh);
            physicsWorld.addBody(body);
            physicsBodies[o.ref] = body;
            body.__ref = o.ref; // для Touched-события (см. beginContact ниже) — по-другому
            // из cannon.js колбэка контакта не узнать, какому игровому
            // объекту принадлежит столкнувшееся тело.
        }

        // Только меш, без CANNON.Body — для объектов, которые видно, но до
        function addVisualMeshForObj(o) {
            playObjData[o.ref] = o;
            if (sceneObjs[o.ref]) {
                loadedObjPos[o.ref] = objPosFor(o);
                loadedObjSize[o.ref] = { x: o.sx, y: o.sy, z: o.sz };
                return; // уже загружен (визуально или физически) — трогать не нужно
            }
            const mesh = buildMeshFromObj(o, playGeoCache, playMatCache);
            if (!(o.ref in playSnapshot)) {
                playSnapshot[o.ref] = mesh.matrix.clone();
            }
            applyMovedXform(o.ref, mesh);
            scene.add(mesh);
            sceneObjs[o.ref] = mesh;
            playOnlyRefs.add(o.ref);
            loadedObjPos[o.ref] = objPosFor(o);
            loadedObjSize[o.ref] = { x: o.sx, y: o.sy, z: o.sz };
        }

        // Разжалование из физики в чисто визуальный меш:
        function demoteToVisualOnly(ref) {
            const body = physicsBodies[ref];
            // Тело игрока (оно же physicsBodies[HumanoidRootPart]) нельзя выгружать:
            // раньше при подгрузке геометрии оно вылетало из физмира, и персонаж
            // не мог двигаться (скорость есть, позиция стоит).
            if (body && body === charBody) return;
            if (body) {
                physicsWorld.removeBody(body);
                delete physicsBodies[ref];
            }
        }

        // Убирает физическое тело (если было) и, если меш был подгружен
        function removePhysicsBodyForRef(ref) {
            const body = physicsBodies[ref];
            if (body && body === charBody) return;
            if (body) {
                physicsWorld.removeBody(body);
                delete physicsBodies[ref];
            }
            delete loadedObjPos[ref];
            delete loadedObjSize[ref];
            if (playOnlyRefs.has(ref)) {
                const mesh = sceneObjs[ref];
                if (mesh) {
                    scene.remove(mesh);
                }
                delete sceneObjs[ref];
                delete playSnapshot[ref];
                playOnlyRefs.delete(ref);
            } else {
                // Объект был в сцене ещё до Play (подгружен редактором,
                const mesh = sceneObjs[ref];
                if (mesh) mesh.visible = false;
            }
        }

        // Подгружает геометрию вокруг позиции персонажа, выгружает то, что
        async function refreshStreamedGeometry() {
            if (!isPlaying || !charBody || streamInFlight) return;
            const cx = charBody.position.x, cy = charBody.position.y, cz = charBody.position.z;
            streamInFlight = true;
            try {
                const loadRadius = qualitySettings.loadRadius || 350;     // физика — до этой дистанции
                const visualRadius = qualitySettings.visualRadius || 2000; // рендер — до этой (без физики)
                const visualCap = maxVisualBodies(); // аварийный потолок на количество, см. пресеты
                const sceneResp = await api('POST', '/api/scene', {
                    cx: Math.round(cx), cy: Math.round(cy), cz: Math.round(cz),
                    load_radius: visualRadius,
                    limit: visualCap, chunk: true
                });
                if (!isPlaying || !sceneResp || !sceneResp.ok) return; // Play могли остановить, пока шёл запрос

                // Сервер сортирует ответ с поправкой на размер объекта
                const physicsCap = maxStreamedBodies();
                for (const o of sceneResp.objects) { if (o.nw) playObjData[o.ref] = o; }
                sceneResp.objects = sceneResp.objects.filter(o => !o.nw);   // шаблоны ServerStorage: данные сохранены, меша/физики нет
                const withDist = sceneResp.objects.map(o => { const op = objPosFor(o); return [o, Math.max(0, Math.hypot(op.x - cx, op.y - cy, op.z - cz) - 0.5 * Math.hypot(o.sx || 0, o.sy || 0, o.sz || 0))]; });
                withDist.sort((a, b) => a[1] - b[1]);

                const nearRefs = new Set();
                let physicsAssigned = 0;
                for (let i = 0; i < withDist.length; i++) {
                    const [o, d] = withDist[i];
                    if (physicsAssigned < physicsCap && d <= loadRadius) {
                        nearRefs.add(o.ref);
                        physicsAssigned++;
                        addPhysicsBodyForObj(o);
                    } else {
                        // Видно, но физически ещё далеко (или бюджет
                        addVisualMeshForObj(o);
                    }
                }
                // Объект раньше был среди ближайших physicsCap, а теперь
                for (const refStr of Object.keys(physicsBodies)) {
                    if (!nearRefs.has(parseInt(refStr)) && luaCloneOrigin[refStr] === undefined) {
                        demoteToVisualOnly(parseInt(refStr));
                    }
                }

                // Полная выгрузка (и физика, и меш) — с запасом
                const unloadDist = visualRadius + UNLOAD_MARGIN;
                for (const ref of Array.from(playOnlyRefs)) {
                    const p = loadedObjPos[ref];
                    if (!p || luaCloneOrigin[ref] !== undefined) continue;
                    const d = Math.hypot(p.x - cx, p.y - cy, p.z - cz) - objRadiusOfRef(ref);
                    if (d > unloadDist) {
                        removePhysicsBodyForRef(ref);
                    }
                }

                // Тело физически держит пол/стены на месте и дальше этой
                const renderCutoff = playRenderCutoff();
                for (const ref of Object.keys(loadedObjPos)) {
                    const mesh = sceneObjs[ref];
                    if (!mesh) continue;
                    const p = loadedObjPos[ref];
                    const d = Math.hypot(p.x - cx, p.y - cy, p.z - cz) - objRadiusOfRef(ref);
                    mesh.visible = d <= renderCutoff;
                }
            } finally {
                streamInFlight = false;
            }
        }

        function maybeStreamGeometry() {
            // ВАЖНО: streamInFlight проверяем ДО таймера, а не внутри
            if (!isPlaying || !charBody || streamInFlight) return;
            const now = performance.now();
            const moved = lastStreamPos.x === null ? Infinity :
                Math.hypot(charBody.position.x - lastStreamPos.x,
                    charBody.position.y - lastStreamPos.y,
                    charBody.position.z - lastStreamPos.z);
            if (moved < STREAM_REFRESH_DIST && now - (lastStreamPos.time || 0) < STREAM_REFRESH_MS) return;
            lastStreamPos = { x: charBody.position.x, y: charBody.position.y, z: charBody.position.z, time: now };
            refreshStreamedGeometry();
        }

        // Explorer/Properties занимают заметную часть ширины экрана (по
        let _savedExplorerWidth = null;
        let _savedRightpanelWidth = null;
        let _savedBottomPanelStyle = null;
        let _outputDragInited = false;
        // Таскание Output за заголовок, когда он "плавающий" (Play, см.
        function initOutputDrag() {
            if (_outputDragInited) return;
            _outputDragInited = true;
            const header = document.getElementById('output-header');
            const panel = document.getElementById('bottom-panel');
            if (!header || !panel) return;
            let dragging = false, startX = 0, startY = 0, startLeft = 0, startTop = 0;
            function onDown(e) {
                if (!panel.classList.contains('output-floating')) return;
                // Не перетаскивать, если тап пришёлся на сами кнопки
                if (e.target.closest('button, select')) return;
                dragging = true;
                const p = e.touches ? e.touches[0] : e;
                startX = p.clientX; startY = p.clientY;
                const r = panel.getBoundingClientRect();
                startLeft = r.left; startTop = r.top;
                e.preventDefault();
            }
            function onMove(e) {
                if (!dragging) return;
                const p = e.touches ? e.touches[0] : e;
                const dx = p.clientX - startX, dy = p.clientY - startY;
                const w = panel.offsetWidth, h = panel.offsetHeight;
                let nl = startLeft + dx, nt = startTop + dy;
                // Не даём утащить целиком за пределы экрана — иначе
                nl = Math.max(-w + 40, Math.min(window.innerWidth - 40, nl));
                nt = Math.max(0, Math.min(window.innerHeight - 40, nt));
                panel.style.left = nl + 'px';
                panel.style.top = nt + 'px';
            }
            function onUp() { dragging = false; }
            header.addEventListener('mousedown', onDown);
            document.addEventListener('mousemove', onMove);
            document.addEventListener('mouseup', onUp);
            header.addEventListener('touchstart', onDown, { passive: false });
            document.addEventListener('touchmove', onMove, { passive: true });
            document.addEventListener('touchend', onUp);
        }

        function setEditorPanelsCollapsedForPlay(collapsed) {
            const explorerEl = document.getElementById('explorer');
            const rightpanelEl = document.getElementById('rightpanel');
            const bottomPanelEl = document.getElementById('bottom-panel');
            const toolbarTopEl = document.getElementById('toolbar-top');
            const viewportEl = document.getElementById('viewport');
            const playStopFab = document.getElementById('play-stop-fab');
            const resizer1 = document.getElementById('resizer-1') || document.querySelector('#explorer + .resizer');
            const resizer2 = document.getElementById('resizer-2');
            const resizerH = document.getElementById('resizer-h');
            if (!explorerEl || !rightpanelEl) return;
            // Раньше панели прятались ПОЛНОСТЬЮ (display:none) — вьюпорт
            const FLOAT_WIDTH = '360px';
            const FLOAT_HEIGHT = '200px';
            const COLLAPSED_WIDTH = '42px';
            if (collapsed) {
                _savedExplorerWidth = explorerEl.style.width || getComputedStyle(explorerEl).width;
                _savedRightpanelWidth = rightpanelEl.style.width || getComputedStyle(rightpanelEl).width;
                explorerEl.style.width = COLLAPSED_WIDTH;
                explorerEl.style.minWidth = COLLAPSED_WIDTH;
                rightpanelEl.style.width = COLLAPSED_WIDTH;
                rightpanelEl.style.minWidth = COLLAPSED_WIDTH;
                if (resizer1) resizer1.style.display = 'none';
                if (resizer2) resizer2.style.display = 'none';
                if (bottomPanelEl) {
                    _savedBottomPanelStyle = bottomPanelEl.getAttribute('style') || '';
                    bottomPanelEl.style.position = 'fixed';
                    bottomPanelEl.style.left = '';
                    bottomPanelEl.style.right = '8px';
                    bottomPanelEl.style.bottom = '8px';
                    bottomPanelEl.style.top = '';
                    bottomPanelEl.style.width = FLOAT_WIDTH;
                    bottomPanelEl.style.height = FLOAT_HEIGHT;
                    bottomPanelEl.style.maxHeight = FLOAT_HEIGHT;
                    bottomPanelEl.style.zIndex = '50';
                    bottomPanelEl.style.boxShadow = '0 4px 18px rgba(0,0,0,.5)';
                    bottomPanelEl.style.borderRadius = '8px';
                    bottomPanelEl.classList.add('output-floating');
                    initOutputDrag();
                }
                if (resizerH) resizerH.style.display = 'none';
                // Верхний тулбар (New/Open/Save/Add/Delete/...) в Play не
                if (toolbarTopEl) toolbarTopEl.style.display = 'none';
                if (playStopFab) playStopFab.classList.add('visible');
                if (viewportEl) viewportEl.classList.add('play-active');
            } else {
                explorerEl.style.minWidth = '';
                rightpanelEl.style.minWidth = '';
                if (_savedExplorerWidth) explorerEl.style.width = _savedExplorerWidth;
                if (_savedRightpanelWidth) rightpanelEl.style.width = _savedRightpanelWidth;
                if (resizer1) resizer1.style.display = '';
                if (resizer2) resizer2.style.display = '';
                if (bottomPanelEl) {
                    bottomPanelEl.classList.remove('output-floating');
                    bottomPanelEl.setAttribute('style', _savedBottomPanelStyle || '');
                }
                if (resizerH) resizerH.style.display = '';
                if (toolbarTopEl) toolbarTopEl.style.display = '';
                if (playStopFab) playStopFab.classList.remove('visible');
                if (viewportEl) viewportEl.classList.remove('play-active');
            }
            // renderer.setSize зависит от фактических размеров DOM
            requestAnimationFrame(() => { if (typeof resize === 'function') resize(); });
        }

        // ============ АВАТАР ИГРОКА В PLAY ============
        // Нет куки Roblox — стандартный «нуб» (рисуется кодом, без сети).
        // Есть кука — ник аккаунта (/api/roblox/me) и 3D-аватар
        // (/api/roblox/play-avatar, кэш на диске) вместо куба.
        // Если аватар смотрит спиной — поставьте PLAY_AVATAR_YAW_OFFSET = Math.PI;
        // если стоит выше/ниже земли — подправьте PLAY_AVATAR_Y_OFFSET.
        const PLAY_AVATAR_YAW_OFFSET = 0;
        const PLAY_AVATAR_Y_OFFSET = R15_HEIGHT / 2 - CHAR_RADIUS; // ступни на земле (центр сферы — на CHAR_RADIUS над ней)
        let playerAccount = null; // {userId, name, displayName} или null (гость)
        const _playAvatarTemplates = {};

        function _applyPlayerAccountToLua() {
            if (!playerAccount || luaPlayerRef === -1 || !luaByRef[luaPlayerRef]) return;
            // Внутреннее имя инстанса ОСТАЁТСЯ 'LocalPlayer': по нему скрипты находят Players.LocalPlayer (раньше здесь
            // стояло переименование в ник — и у всех вошедших в аккаунт LocalPlayer становился nil). Ник отдаёт __get_name.
            const pr = virtualInstanceProps[luaPlayerRef] || (virtualInstanceProps[luaPlayerRef] = {});
            pr.UserId = playerAccount.userId;
            pr.DisplayName = playerAccount.displayName || playerAccount.name;
        }

        function _disposeObj(o) {
            if (o.userData && o.userData.shared) return; // общий шаблон аватара — не трогаем
            o.children.slice().forEach(_disposeObj);
            if (o.geometry) o.geometry.dispose();
            if (o.material) {
                (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => {
                    if (m.map) m.map.dispose();
                    m.dispose();
                });
            }
        }
        function _disposeCharMesh() {
            if (!charMesh) return;
            _clearOutfit(charMesh);
            scene.remove(charMesh);
            _disposeObj(charMesh);
            charMesh = null;
        }
        function _setCharBody(group, body) {
            const old = group.userData.body;
            if (old) { group.remove(old); _disposeObj(old); }
            group.userData.body = body;
            group.add(body);
        }

        // Классический R6-«нуб» в студах (5 высотой): жёлтые голова и руки,
        // синий торс, зелёные ноги. Лицо — на -Z (туда же, куда идёт персонаж).
        function _buildNoobAvatar() {
            const g = new THREE.Group();
            const box = (w, h, d, color, x, y, z, basic, limb) => {
                const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d),
                    basic ? new THREE.MeshBasicMaterial({ color }) : new THREE.MeshLambertMaterial({ color }));
                m.position.set(x, y, z);
                if (limb) { m.userData.limb = limb; m.userData.baseColor = color; } // для BodyColors костюма
                g.add(m);
            };
            const Y = 0xF5CD30, B = 0x0D69AC, G = 0xA4BD47;
            box(1, 2, 1, G, -0.5, 1, 0, false, 'LeftLeg'); box(1, 2, 1, G, 0.5, 1, 0, false, 'RightLeg'); // ноги
            box(2, 2, 1, B, 0, 3, 0, false, 'Torso');                                                    // торс
            box(1, 2, 1, Y, -1.5, 3, 0, false, 'LeftArm'); box(1, 2, 1, Y, 1.5, 3, 0, false, 'RightArm'); // руки
            box(2, 1, 1, Y, 0, 4.5, 0, false, 'Head');                                                   // голова
            box(0.2, 0.3, 0.02, 0x000000, -0.4, 4.6, -0.51, true);         // глаза
            box(0.2, 0.3, 0.02, 0x000000, 0.4, 4.6, -0.51, true);
            box(0.9, 0.1, 0.02, 0x000000, 0, 4.25, -0.51, true);           // рот
            return _fitToCharHeight(g);
        }

        // Центрирует объект и масштабирует до роста R15 (5 стадов).
        function _fitToCharHeight(obj) {
            const box = new THREE.Box3().setFromObject(obj);
            const c = box.getCenter(new THREE.Vector3());
            const s = box.getSize(new THREE.Vector3());
            obj.position.sub(c);
            const inner = new THREE.Group();
            inner.add(obj);
            inner.scale.setScalar(R15_HEIGHT / Math.max(s.y, 1e-3));
            const outer = new THREE.Group();
            outer.add(inner);
            outer.rotation.y = PLAY_AVATAR_YAW_OFFSET;
            outer.position.y = PLAY_AVATAR_Y_OFFSET;
            return outer;
        }

        function _makeNameTag(text) {
            const c = document.createElement('canvas');
            c.width = 256; c.height = 64;
            const g = c.getContext('2d');
            g.font = 'bold 30px sans-serif';
            g.textAlign = 'center'; g.textBaseline = 'middle';
            g.lineWidth = 6; g.strokeStyle = 'rgba(0,0,0,.8)';
            g.strokeText(text, 128, 32);
            g.fillStyle = '#fff';
            g.fillText(text, 128, 32);
            const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthTest: false }));
            sp.scale.set(4, 1, 1);
            sp.position.y = R15_HEIGHT - CHAR_RADIUS + 0.9; // над макушкой
            sp.renderOrder = 10;
            return sp;
        }

        // OBJ+MTL → THREE-объект (те же фиксы Roblox-формата, что в importAvatarIntoScene)
        async function _buildPlayAvatarFromAssets(data) {
            await ensureObjMtlLoaders();
            const fixedObjText = data.obj_text.replace(
                /^v(\s+-?[\d.eE+-]+\s+-?[\d.eE+-]+\s+-?[\d.eE+-]+)(?:\s+-?[\d.eE+-]+)*\s*$/gm,
                'v$1'
            );
            const texByName = {};
            (data.textures || []).forEach(x => { texByName[x.name] = x.data_url; });
            const manager = new THREE.LoadingManager();
            manager.setURLModifier((url) => texByName[url.split('/').pop()] || url);
            const mtlLoader = new THREE.MTLLoader(manager);
            mtlLoader.setMaterialOptions({ invertTrProperty: true });
            const materials = mtlLoader.parse(data.mtl_text, '');
            materials.preload();
            for (const key in materials.materials) {
                const m = materials.materials[key];
                m.side = THREE.DoubleSide;
                m.transparent = false; m.opacity = 1; m.alphaTest = 0;
                m.needsUpdate = true;
            }
            const objLoader = new THREE.OBJLoader(manager);
            objLoader.setMaterials(materials);
            const object = objLoader.parse(fixedObjText);
            let verts = 0;
            object.traverse(n => {
                if (!n.isMesh) return;
                if (n.geometry) { n.geometry.computeVertexNormals(); if (n.geometry.attributes.position) verts += n.geometry.attributes.position.count; }
                (Array.isArray(n.material) ? n.material : [n.material]).forEach(m => {
                    if (m && m.map) {
                        m.map.encoding = THREE.sRGBEncoding;
                        m.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
                        m.map.needsUpdate = true;
                    }
                });
            });
            if (!verts) throw new Error('пустая геометрия аватара');
            const fitted = _fitToCharHeight(object);
            fitted.userData.shared = true; // шаблон общий для всех Play-сессий — не dispose'им
            return fitted;
        }

        function _loadPlayAvatarTemplate(userId) {
            if (_playAvatarTemplates[userId]) return _playAvatarTemplates[userId];
            const p = (async () => {
                let r = await api('GET', '/api/roblox/play-avatar?userId=' + userId);
                if (!r || !r.ok) throw new Error((r && (r.message || r.error)) || 'play-avatar');
                if (!r.cached) {
                    let bundleUrl = null;
                    for (let i = 0; i < 45 && isPlaying; i++) { // Roblox генерирует модель асинхронно
                        const st = await api('GET', '/api/roblox/avatar3d/status?userId=' + userId);
                        if (!st || !st.ok) throw new Error((st && (st.message || st.error)) || 'status');
                        if (st.ready) { bundleUrl = st.bundleUrl; break; }
                        if (st.state === 'Error') throw new Error('Roblox: ошибка генерации');
                        await new Promise(res => setTimeout(res, 1500));
                    }
                    if (!bundleUrl) throw new Error('таймаут генерации');
                    r = await api('GET', '/api/roblox/play-avatar?userId=' + userId + '&bundleUrl=' + encodeURIComponent(bundleUrl));
                    if (!r || !r.ok) throw new Error((r && (r.message || r.error)) || 'play-avatar');
                }
                return _buildPlayAvatarFromAssets(r);
            })();
            _playAvatarTemplates[userId] = p;
            p.catch(() => { delete _playAvatarTemplates[userId]; });
            return p;
        }

        // ============ КОСТЮМ ПЕРСОНАЖА (Accessory / BodyColors в Character) ============
        // Скрипт карты (морф хазмата) клонирует Accessory и BodyColors в Character — раньше
        // приложение это не рисовало, и надетый костюм был невидим. Теперь по ref ОРИГИНАЛА
        // (luaCloneOrigin) берём данные с сервера (/api/outfit_item) и рисуем меш аксессуара
        // на «якоре» тела (R6-раскладка: голова 4.5, торс 3.0 над землёй, спереди -Z; рост 5
        // у нуба и у аватара одинаков, так что якоря подходят обоим). BodyColors красит
        // только нуба (у OBJ-аватара цвет кожи — в текстуре). Shirt/Pants пока не рисуются.
        const OUTFIT_ANCHORS = {
            'Head': [0, 4.5, 0], 'Torso': [0, 3, 0], 'UpperTorso': [0, 3.2, 0], 'LowerTorso': [0, 2.4, 0],
            'HumanoidRootPart': [0, 3, 0], 'Left Arm': [-1.5, 3, 0], 'Right Arm': [1.5, 3, 0],
            'Left Leg': [-0.5, 1, 0], 'Right Leg': [0.5, 1, 0],
        };
        const OUTFIT_ATTACH_TO_PART = {
            HatAttachment: 'Head', HairAttachment: 'Head', FaceFrontAttachment: 'Head', FaceCenterAttachment: 'Head',
            NeckAttachment: 'Torso', BodyFrontAttachment: 'Torso', BodyBackAttachment: 'Torso',
            LeftCollarAttachment: 'Torso', RightCollarAttachment: 'Torso', WaistFrontAttachment: 'Torso',
            WaistBackAttachment: 'Torso', WaistCenterAttachment: 'Torso',
            LeftShoulderAttachment: 'Left Arm', RightShoulderAttachment: 'Right Arm',
        };
        const _outfitInfoCache = {};
        let _outfitTimer = null;

        function _cf12ToMatrix(a) { // [x,y,z, r00..r22 по строкам] -> Matrix4
            const m = new THREE.Matrix4();
            m.set(a[3], a[4], a[5], a[0],
                  a[6], a[7], a[8], a[1],
                  a[9], a[10], a[11], a[2],
                  0, 0, 0, 1);
            return m;
        }
        function _fetchOutfitInfo(originRef) {
            if (!_outfitInfoCache[originRef]) {
                _outfitInfoCache[originRef] = api('GET', '/api/outfit_item/' + originRef).catch(() => null);
            }
            return _outfitInfoCache[originRef];
        }
        function scheduleCharacterOutfit() {
            if (_outfitTimer) return;
            _outfitTimer = setTimeout(() => { _outfitTimer = null; refreshCharacterOutfit(); }, 0);
        }
        function _clearOutfit(group) {
            const root = group && group.userData.outfitRoot;
            if (!root) return;
            // геометрия и текстуры общие (кэши мешей/текстур) — освобождаем только материалы
            root.traverse(n => { if (n.material) n.material.dispose(); });
            group.remove(root);
            group.userData.outfitRoot = null;
        }
        function _applyBodyColors(group, colors) {
            const body = group.userData.body;
            if (!body) return;
            body.traverse(n => {
                const limb = n.userData && n.userData.limb;
                if (!limb || !n.material) return;
                if (colors && colors[limb]) n.material.color.set(colors[limb]);
                else n.material.color.set(n.userData.baseColor);
            });
        }

        async function refreshCharacterOutfit() {
            const group = charMesh;
            if (!isPlaying || !group || luaCharacterRef === -1) return;
            const acc = [], bcs = [];
            for (const k of (luaChildrenByRef[luaCharacterRef] || [])) {
                const cls = luaByRef[k] && luaByRef[k].cls;
                const origin = luaCloneOrigin[k] !== undefined ? luaCloneOrigin[k] : k;
                if (origin < 0) continue;              // создано скриптом (не из файла) — данных на сервере нет
                if (cls === 'Accessory') acc.push(origin);
                else if (cls === 'BodyColors') bcs.push(origin);
            }
            const sig = acc.join(',') + '|' + bcs.join(',');
            if (sig === group.userData.outfitSig) return;
            group.userData.outfitSig = sig;
            const token = group.userData.outfitToken = (group.userData.outfitToken || 0) + 1;
            const [accInfos, bcInfos] = await Promise.all([
                Promise.all(acc.map(_fetchOutfitInfo)), Promise.all(bcs.map(_fetchOutfitInfo))]);
            if (charMesh !== group || group.userData.outfitToken !== token) return; // Play остановили / состав уже сменился
            const bc = bcInfos.find(i => i && i.ok && i.cls === 'BodyColors');
            _applyBodyColors(group, bc ? bc.colors : null);
            _clearOutfit(group);
            const root = new THREE.Group();
            root.position.y = -CHAR_RADIUS;            // земля: центр сферы-коллайдера на CHAR_RADIUS выше
            root.rotation.y = PLAY_AVATAR_YAW_OFFSET;
            group.add(root);
            group.userData.outfitRoot = root;
            for (const info of accInfos) {
                if (!info || !info.ok || info.cls !== 'Accessory') continue;
                try {
                    const mesh = await _buildAccessoryMesh(info);
                    if (charMesh !== group || group.userData.outfitToken !== token) { mesh && mesh.material.dispose(); return; }
                    if (mesh) root.add(mesh);
                } catch (e) { logLuaOutput('warn', 'Costume: ' + (info.name || '?') + ' — ' + (e && e.message || e)); }
            }
            if (root.children.length) logLuaOutput('info', t('log_outfit_applied', { n: root.children.length }));
        }

        async function _buildAccessoryMesh(info) {
            const m = info.mesh || { kind: 'box' };
            let geo, scale = new THREE.Vector3(1, 1, 1), mat;
            const off = new THREE.Matrix4();
            if (m.kind === 'special' || m.kind === 'meshpart') {
                const res = await loadRealMeshGeometry(m.meshId);
                if (!res) return null;                   // меш не разобрался — не рисуем кубик вместо шлема
                geo = res.geometry;
                if (m.kind === 'special') {
                    scale.set(m.scale[0], m.scale[1], m.scale[2]);       // родной размер * Scale
                    off.makeTranslation(m.offset[0], m.offset[1], m.offset[2]);
                } else {
                    scale.set(info.size[0] / res.size.x, info.size[1] / res.size.y, info.size[2] / res.size.z);
                }
                mat = new THREE.MeshLambertMaterial({
                    color: m.textureId ? '#ffffff' : (info.color || '#a3a2a5'),
                    map: m.textureId ? getOrLoadPartTexture(m.textureId) : null,
                    side: THREE.DoubleSide, alphaTest: m.textureId ? 0.5 : 0,
                });
            } else {
                geo = new THREE.BoxGeometry(info.size[0], info.size[1], info.size[2]);
                mat = new THREE.MeshLambertMaterial({ color: info.color || '#a3a2a5' });
            }
            // Handle = Part0(тело) * C0 * C1^-1 (как AccessoryWeld); нет сварки — по имени Attachment
            let H;
            if (info.weld && info.weld.c0 && info.weld.c1) {
                const a = OUTFIT_ANCHORS[info.weld.part0] || OUTFIT_ANCHORS.Torso;
                H = new THREE.Matrix4().makeTranslation(a[0], a[1], a[2])
                    .multiply(_cf12ToMatrix(info.weld.c0)).multiply(_cf12ToMatrix(info.weld.c1).invert());
            } else {
                const a = OUTFIT_ANCHORS[OUTFIT_ATTACH_TO_PART[info.attachment && info.attachment.name] || 'Torso'];
                H = new THREE.Matrix4().makeTranslation(a[0], a[1], a[2]);
                if (info.attachment && info.attachment.cf) H.multiply(_cf12ToMatrix(info.attachment.cf).invert());
            }
            const mesh = new THREE.Mesh(geo, mat);
            mesh.matrixAutoUpdate = false;
            mesh.matrix.copy(H).multiply(off).multiply(new THREE.Matrix4().makeScale(scale.x, scale.y, scale.z));
            mesh.matrixWorldNeedsUpdate = true;
            mesh.userData.shared = true;
            return mesh;
        }

        async function setupPlayerAvatar(group) {
            let acc = null;
            try {
                const r = await api('GET', '/api/roblox/me');
                if (r && r.ok && r.loggedIn) acc = r;
            } catch (e) { emuWarn('swallow:setupPlayerAvatar:4457', 'setupPlayerAvatar: ' + _errText(e) + ' (без сети — гость)'); }
            if (charMesh !== group) return; // Play уже остановили
            if (!acc) { logLuaOutput('info', t('log_play_guest')); return; }
            playerAccount = { userId: acc.userId, name: acc.name, displayName: acc.displayName };
            _applyPlayerAccountToLua();
            group.add(_makeNameTag(acc.displayName || acc.name));
            logLuaOutput('info', t('log_play_account', { name: acc.name, id: acc.userId }));
            try {
                const tpl = await _loadPlayAvatarTemplate(acc.userId);
                if (charMesh !== group) return;
                _setCharBody(group, tpl.clone(true));
                logLuaOutput('info', t('log_play_avatar_ok'));
            } catch (e) {
                if (charMesh === group) logLuaOutput('warn', t('log_play_avatar_fail', { msg: e && e.message || e }));
            }
        }

        async function startPlay() {
            if (typeof CANNON === 'undefined') {
                notify(t('notify_cannon_not_ready'), 'err');
                return;
            }

            // Иначе Play запускал бы Lua-скрипты по последней СОХРАНЁННОЙ
            await saveCurrentScriptIfDirty();

            const spawn = await findSpawnPoint();
            playSpawnPos = { x: spawn.x, y: spawn.y, z: spawn.z };
            loadProximityPrompts(); // не блокирует старт — подтянется чуть позже, если не успеет

            // Геометрия для физики запрашивается заново, центрированная на
            const params = new URLSearchParams({
                cx: Math.round(spawn.x), cy: Math.round(spawn.y), cz: Math.round(spawn.z),
                limit: maxStreamedBodies(), chunk: 1
            });
            const sceneResp = await api('GET', '/api/scene?' + params.toString());
            if (!sceneResp.ok || !sceneResp.objects.length) {
                notify(t('notify_no_geometry'), 'err');
                return;
            }

            physicsWorld = new CANNON.World();
            // cannon.js 0.6.2: ArrayCollisionMatrix.reset() на КАЖДОМ шаге обнуляет N²/2 ячеек (N = все тела мира, а у нас в мир
            // кладётся вся статичная геометрия). После спавна комнат (612 -> 1200+ объектов) шаг физики дорожал в разы
            // и FPS проваливался. Разреженная матрица держит только реально соприкасающиеся пары: reset = clear().
            {
                const mkSparse = () => {
                    const set = new Set();
                    const key = (a, b) => { let i = a.index, j = b.index; if (j > i) { const t = j; j = i; i = t; } return i * 1048576 + j; };
                    return {
                        matrix: set,
                        get(a, b) { return set.has(key(a, b)) ? 1 : 0; },
                        set(a, b, v) { if (v) set.add(key(a, b)); else set.delete(key(a, b)); },
                        reset() { set.clear(); },
                        setNumObjects() { /* размер не зависит от числа тел */ },
                    };
                };
                physicsWorld.collisionMatrix = mkSparse();
                physicsWorld.collisionMatrixPrevious = mkSparse();
            }
            physicsWorld.gravity.set(0, GRAVITY_STUDS, 0);
            // SAPBroadphase сортирует и прогоняет ВСЕ тела мира каждый шаг — а почти все они статичные (карта), друг с другом
            // не сталкиваются. Шаг физики стоил 2.9 мс на 481 теле и 7–9 мс на 943 (после спавна комнат), а за кадр их до 20
            // (PHYSICS_MAX_TICKS × PHYSICS_SUBSTEPS) — FPS падал с 60 до ~9. Здесь пары строятся только от подвижных тел
            // (персонаж, динамические детали) к остальным: стоимость ~ (число подвижных) × (число тел), в 5–8 раз дешевле.
            {
                const STATIC = CANNON.Body.STATIC;
                const DynStaticBroadphase = function (world) { CANNON.Broadphase.call(this); this.world = world; this.useBoundingBoxes = false; };
                DynStaticBroadphase.prototype = Object.create(CANNON.Broadphase.prototype);
                DynStaticBroadphase.prototype.constructor = DynStaticBroadphase;
                DynStaticBroadphase.prototype.collisionPairs = function (world, p1, p2) {
                    const bs = world.bodies, n = bs.length;
                    for (let i = 0; i < n; i++) {
                        const bi = bs[i];
                        if (bi.type === STATIC) continue;
                        for (let j = 0; j < n; j++) {
                            const bj = bs[j];
                            if (bj === bi) continue;
                            if (j < i && bj.type !== STATIC) continue;   // пара подвижных тел — один раз
                            if (!this.needBroadphaseCollision(bi, bj)) continue;
                            this.intersectionTest(bi, bj, p1, p2);
                        }
                    }
                };
                DynStaticBroadphase.prototype.aabbQuery = function (world, aabb, result) {
                    result = result || [];
                    for (const b of world.bodies) {
                        if (b.aabbNeedsUpdate) b.computeAABB();
                        if (b.aabb.overlaps(aabb)) result.push(b);
                    }
                    return result;
                };
                physicsWorld.broadphase = CANNON.Broadphase ? new DynStaticBroadphase(physicsWorld) : new CANNON.SAPBroadphase(physicsWorld);
            }
            physicsWorld.solver.iterations = 10;
            physicsWorld.allowSleep = true;
            // friction = 0 обязательно:
            physicsWorld.defaultContactMaterial.friction = 0;
            physicsWorld.defaultContactMaterial.restitution = 0.05;

            // Touched — настоящее срабатывание по факту контакта в cannon.js
            // (события beginContact в cannon.js 0.6 нет — см. updateContactTouches)
            touchContacts = new Map();

            physicsBodies = {};
            playSnapshot = {};
            playOnlyRefs = new Set();
            playObjData = {};

            // Меши, оставшиеся в сцене от редактора (загружены раньше,
            for (const mesh of Object.values(sceneObjs)) {
                mesh.visible = false;
            }

            for (const o of sceneResp.objects) {
                if (o.nw) { playObjData[o.ref] = o; continue; }   // шаблон из ServerStorage: только данные для Clone()
                addPhysicsBodyForObj(o);
            }
            // Данные ВСЕХ шаблонов (а не только тех, что попали в лимит по дистанции) — для Clone() комнат/врагов/лифтов
            fetch('/api/scene?nw=1').then(r => r.json()).then(tr => {
                if (!tr || !tr.ok || !isPlaying) return;
                for (const o of tr.objects) if (!playObjData[o.ref]) playObjData[o.ref] = o;
            }).catch(e => console.warn('template data:', e));

            {
                const cutoff = playRenderCutoff();
                for (const refStr of Object.keys(physicsBodies)) {
                    const mesh = sceneObjs[refStr];
                    if (!mesh) continue;
                    const body = physicsBodies[refStr];
                    const d = Math.hypot(body.position.x - spawn.x, body.position.y - spawn.y, body.position.z - spawn.z) - objRadiusOfRef(refStr);
                    mesh.visible = d <= cutoff;
                }
            }

            // Персонаж — сфера (без вращения, чтобы камера не крутило),
            charBody = new CANNON.Body({
                mass: 5,
                shape: new CANNON.Sphere(CHAR_RADIUS),
                position: new CANNON.Vec3(spawn.x, spawn.y, spawn.z),
                fixedRotation: true,
                linearDamping: 0,      // в Roblox у персонажа нет «сопротивления воздуха»: прыжок/падение без торможения
                allowSleep: false,
            });
            // Верх тела — колонна сфер того же радиуса, поставленных друг на друга (капсула «из сфер»),
            // от центра первой сферы до макушки R15. Одна сфера закрывала только нижние ~2 стада от земли,
            // и всё выше (стены, балки, юнионы на уровне груди/головы) игрок проходил насквозь.
            // Именно сферы, а не бокс: в cannon.js 0.6 нет столкновения «бокс — trimesh», а юнионы здесь
            // как раз trimesh (applyUnionTrimesh) — бокс сквозь них проходил бы; сфера сталкивается со всем.
            for (let y = CHAR_RADIUS; y + CHAR_RADIUS <= R15_HEIGHT - CHAR_RADIUS + 1e-6; y += CHAR_RADIUS) {
                charBody.addShape(new CANNON.Sphere(CHAR_RADIUS), new CANNON.Vec3(0, y, 0));
            }
            // Группу/маску тела НЕ меняем: у тел в cannon 0.6 mask по умолчанию = 1, и любая другая группа
            // у персонажа отключила бы его столкновения со всем миром. Лучи персонажа стартуют изнутри
            // его сфер, но с skipBackfaces=true выходные грани (нормаль по ходу луча) отбрасываются.
            physicsWorld.addBody(charBody);

            // Куб-персонаж для вида от третьего лица — виден только когда
            _disposeCharMesh();
            charMesh = new THREE.Group();
            _setCharBody(charMesh, _buildNoobAvatar()); // сразу — стандартный «нуб»; аватар аккаунта подменит его, когда загрузится
            charMesh.visible = false;
            scene.add(charMesh);
            _disposeBlobShadow();
            blobShadow = _makeBlobShadow();
            scene.add(blobShadow);
            setupPlayerAvatar(charMesh);

            prevCameraState = {
                spherical: { ...spherical },
                target: { ...target },
            };
            spherical.phi = Math.PI / 2; // смотрим ровно вперёд, а не в пол/потолок
            target = { x: spawn.x, y: spawn.y + EYE_HEIGHT, z: spawn.z };
            updateCamera();

            isPlaying = true;
            setEditorPanelsCollapsedForPlay(true);
            jumpQueued = false;
            lastStreamPos = { x: spawn.x, y: spawn.y, z: spawn.z, time: performance.now() };
            fallingSinceMs = null;
            streamInFlight = false;
            playGeoCache = {};
            playMatCache = {};
            // Реальная дальность отрисовки в Play — playRenderCutoff()
            prevFogFar = scene.fog ? scene.fog.far : null;
            if (scene.fog) scene.fog.far = STREAM_PRUNE_DIST;
            document.getElementById('play-btn').textContent = t('notify_stop');
            document.getElementById('play-btn').classList.add('red');
            document.getElementById('play-btn').classList.remove('green');
            const padE = document.getElementById('pad-e'), padQ = document.getElementById('pad-q');
            if (padE) { padE.textContent = '⤴'; padE.title = t('pad_jump_title'); }
            if (padQ) { padQ.style.visibility = 'hidden'; }
            _updateTouchControlsVisibility(); // luaControlsDisabled сбрасывается в stopLuaScripts/startLuaScriptsInner — на старте контролы должны быть видны, если скрипт не решит иначе
            // Модель игрока (голова/торс/руки/ноги/одежда — обычные MeshPart
            // рядом со спавном) уже перечислена выше и начала грузить
            // реальную геометрию и текстуры по сети
            // (scheduleRealMeshSwap/getOrLoadPartTexture/getClothTexture —
            // каждый асинхронный запрос сам регистрируется в
            // _pendingModelLoads). Раньше рендер уже шёл (requestAnimationFrame
            // не ждёт этот await), поэтому первые секунды игрок ВИДЕЛ, как
            // персонаж доснашивает текстуры и меши прямо во время игры —
            // "доскачивался" по кускам. Закрываем экран модалкой (как при
            // скачивании аватара через "Импорт аватара") на время ожидания
            // — тогда модель появляется сразу целиком; не дольше 2.5 сек,
            // чтобы не превращать это в зависание на тяжёлой карте.
            if (_pendingModelLoads > 0) {
                showModal('<h3>' + t('notify_loading_model') + '</h3>');
                await waitForPendingModelLoads(2500);
                closeModal();
            }
            if (!isPlaying) return; // Stop нажали, пока ждали загрузку
            notify(t('notify_play_started', { n: Object.keys(physicsBodies).length }));
            startLuaScripts(); // асинхронно — не блокирует появление игрока на спавне
        }

        // Реальный Roblox прячет тач-контролы (джойстик, кнопку прыжка)
        function _updateTouchControlsVisibility() {
            const pad = document.getElementById('mobile-pad');
            if (!pad) return;
            pad.style.display = (isPlaying && luaControlsDisabled) ? 'none' : '';
        }

        function stopPlay() {
            isPlaying = false;
            _updateTouchControlsVisibility(); // возвращаем джойстик/кнопку — она могла остаться скрытой, если скрипт вызвал Disable() и не успел/не стал явно включать обратно
            cameraIsScriptable = false;
            _scriptCam = null;
            setEditorPanelsCollapsedForPlay(false);
            stopLuaScripts();
            physicsWorld = null;
            physicsBodies = {};
            charBody = null;
            _camReturnToCharT = null;
            luaHumanoidRootPartRef = -1;
            luaHumanoidRef = -1;
            charWalkSpeed = CHAR_SPEED;
            charJumpPower = JUMP_VELOCITY;
            _promptRegistry = {};
            _activePromptRef = null;
            _activePrompt = null;
            _promptHoldStart = null; _promptShownRef = null; _promptHeldRef = null; _promptTriggered = false; _ppsRefCache = null;
            _activatedTool = null; _hotbarSig = ''; if (_hotbarEl) _hotbarEl.style.display = 'none'; for (const k in _coreGuiOff) delete _coreGuiOff[k];
            const _promptEl = document.getElementById('proximity-prompt');
            if (_promptEl) _promptEl.style.display = 'none';
            _disposeCharMesh();
            _disposeBlobShadow();
            playerAccount = null;
            canJump = false;
            jumpQueued = false;
            if (scene.fog && prevFogFar !== null) scene.fog.far = prevFogFar;
            prevFogFar = null;

            for (const [refStr, mesh] of Object.entries(sceneObjs)) {
                const ref = parseInt(refStr);
                if (!(ref in playSnapshot)) {
                    // Не был подгружен стримингом за время Play вообще
                    mesh.visible = true;
                    continue;
                }
                if (playOnlyRefs.has(ref)) {
                    // Загружен только ради Play — убираем совсем, иначе
                    scene.remove(mesh);
                    if (mesh.geometry && !mesh.geometry.userData.sharedMesh) mesh.geometry.dispose();
                    delete sceneObjs[ref];
                } else {
                    mesh.matrix.copy(playSnapshot[ref]);
                    // Size, выставленный скриптом во время Play, после Stop откатывается (как в Studio)
                    if (mesh.userData.partScale0 !== undefined) {
                        if (mesh.userData.partScale0) mesh.userData.partScale = mesh.userData.partScale0.clone();
                        else delete mesh.userData.partScale;
                    }
                    if (mesh.userData.partScale) {   // геометрия уже настоящая (меш заменён) — масштаб не терять
                        const rp = new THREE.Vector3(), rq = new THREE.Quaternion(), rs = new THREE.Vector3();
                        mesh.matrix.decompose(rp, rq, rs);
                        mesh.matrix.compose(rp, rq, mesh.userData.partScale);
                    } else {
                        const rp = new THREE.Vector3(), rq = new THREE.Quaternion(), rs = new THREE.Vector3();
                        mesh.matrix.decompose(rp, rq, rs);
                        mesh.matrix.compose(rp, rq, new THREE.Vector3(1, 1, 1));
                    }
                    mesh.visible = true; // сняли дальнюю обрезку рендера, введённую во время Play
                }
            }
            playSnapshot = {};
            playOnlyRefs = new Set();
            loadedObjPos = {};
            loadedObjSize = {};

            if (prevCameraState) {
                spherical = prevCameraState.spherical;
                target = prevCameraState.target;
                updateCamera();
                prevCameraState = null;
            }

            document.getElementById('play-btn').textContent = t('tb_play');
            document.getElementById('play-btn').classList.add('green');
            document.getElementById('play-btn').classList.remove('red');
            const padE = document.getElementById('pad-e'), padQ = document.getElementById('pad-q');
            if (padE) { padE.textContent = '⬆'; padE.title = t('pad_up_title'); }
            if (padQ) { padQ.style.visibility = 'visible'; }
            notify(t('notify_stop'));
        }

        // ============ LUA (Script/LocalScript в Play) ============
        let fengariLoadPromise = null;
        function ensureFengariLoaded() {
            if (window.fengari) return Promise.resolve(true);
            if (fengariLoadPromise) return fengariLoadPromise;
            fengariLoadPromise = new Promise((resolve) => {
                // Пробуем по очереди: локальная копия (с cache-bust, чтобы
                // WebView не отдал закэшированный 404/сбой прошлой попытки),
                // затем CDN-зеркала. Причина каждого сбоя пишется в Output.
                const urls = [
                    'vendor/fengari-web.js?_=' + Date.now(),
                    'https://cdn.jsdelivr.net/npm/fengari-web@0.1.4/dist/fengari-web.js',
                    'https://raw.githubusercontent.com/suscersal/roblox-studio-web/main/vendor/fengari-web.js',
                ];
                const tryNext = (i) => {
                    if (i >= urls.length) {
                        console.error('[Lua] fengari не загрузился ни с одного адреса');
                        resolve(false);
                        return;
                    }
                    const s = document.createElement('script');
                    s.src = urls[i];
                    s.onload = () => {
                        if (window.fengari) { resolve(true); return; }
                        logLuaOutput('warn', 'fengari: ' + urls[i] + ' загрузился, но window.fengari не появился');
                        s.remove(); tryNext(i + 1);
                    };
                    s.onerror = () => {
                        logLuaOutput('warn', 'fengari: не загрузился ' + urls[i]);
                        s.remove(); tryNext(i + 1);
                    };
                    document.head.appendChild(s);
                };
                tryNext(0);
            });
            return fengariLoadPromise;
        }

        // Два НЕЗАВИСИМЫХ lua_State — как сервер и клиент в настоящем
        let luaServerL = null;
        let luaClientL = null;
        let luaWaits = [];       // [{co, resumeAt}] — корутины, спящие в wait() (общий шедулер на обе VM)
        let activeTweens = [];   // [{ref, propName, from, to, duration, startTime, composite, completedKey}] — см. TweenService ниже
        let luaSignalWaits = []; // [{co, ref, evName}] — корутины, спящие в Event:Wait()/:wait(), см. __wait_signal
        let luaModuleSourceByRef = {}; // ModuleScript ref -> Source (для require(), см. __compile_module)
        let luaModuleNameByRef = {};   // ModuleScript ref -> имя (для сообщений об ошибках/имени чанка)
        let luaOutputLines = []; // {level, text} — для панели #lua-output

        const LUA_PRELUDE = `
Vector3 = {}
Vector3.__index = Vector3
function Vector3.new(x, y, z)
    return setmetatable({X = x or 0, Y = y or 0, Z = z or 0}, Vector3)
end
Vector3.__add = function(a, b) return Vector3.new(a.X + b.X, a.Y + b.Y, a.Z + b.Z) end
Vector3.__sub = function(a, b) return Vector3.new(a.X - b.X, a.Y - b.Y, a.Z - b.Z) end
Vector3.__mul = function(a, b)
    if type(a) == "number" then return Vector3.new(a * b.X, a * b.Y, a * b.Z) end  -- 2 * v (раньше падало на a.X у числа)
    if type(b) == "number" then return Vector3.new(a.X * b, a.Y * b, a.Z * b) end
    return Vector3.new(a.X * b.X, a.Y * b.Y, a.Z * b.Z)
end
Vector3.__unm = function(a) return Vector3.new(-a.X, -a.Y, -a.Z) end
Vector3.__tostring = function(v) return v.X .. ", " .. v.Y .. ", " .. v.Z end
function Vector3.new_magnitude(v) return math.sqrt(v.X*v.X + v.Y*v.Y + v.Z*v.Z) end
-- Magnitude/Unit/Dot/Cross/Lerp и деление — раньше были только + - * и
-- new_magnitude, из-за чего v.Magnitude/v.Unit давали nil.
function Vector3.Dot(a, b) return a.X*b.X + a.Y*b.Y + a.Z*b.Z end
function Vector3.Cross(a, b)
    return Vector3.new(a.Y*b.Z - a.Z*b.Y, a.Z*b.X - a.X*b.Z, a.X*b.Y - a.Y*b.X)
end
function Vector3.Lerp(a, b, t)
    return Vector3.new(a.X + (b.X-a.X)*t, a.Y + (b.Y-a.Y)*t, a.Z + (b.Z-a.Z)*t)
end
Vector3.__div = function(a, b)
    if type(a) == "number" then return Vector3.new(a / b.X, a / b.Y, a / b.Z) end
    if type(b) == "number" then return Vector3.new(a.X / b, a.Y / b, a.Z / b) end
    return Vector3.new(a.X / b.X, a.Y / b.Y, a.Z / b.Z)
end
Vector3.__eq = function(a, b) return a.X == b.X and a.Y == b.Y and a.Z == b.Z end
Vector3.__index = function(t, k)
    if k == "Magnitude" or k == "magnitude" then
        return math.sqrt(t.X*t.X + t.Y*t.Y + t.Z*t.Z)
    end
    if k == "Unit" or k == "unit" then
        local m = math.sqrt(t.X*t.X + t.Y*t.Y + t.Z*t.Z)
        if m == 0 then return Vector3.new(0, 0, 0) end
        return Vector3.new(t.X/m, t.Y/m, t.Z/m)
    end
    return rawget(Vector3, k)
end
Vector3.zero = Vector3.new(0, 0, 0)
Vector3.one = Vector3.new(1, 1, 1)
Vector3.xAxis = Vector3.new(1, 0, 0)
Vector3.yAxis = Vector3.new(0, 1, 0)
Vector3.zAxis = Vector3.new(0, 0, 1)

-- BrickColor: палитра частых цветов Roblox (номер, имя, sRGB). Неизвестное имя/номер -> Medium stone grey (как в Roblox).
local __BC_PALETTE = {
    {1, "White", 242, 243, 243}, {5, "Brick yellow", 215, 197, 154}, {9, "Light reddish violet", 232, 186, 200},
    {21, "Bright red", 196, 40, 28}, {23, "Bright blue", 13, 105, 172}, {24, "Bright yellow", 245, 205, 48},
    {26, "Black", 27, 42, 53}, {28, "Dark green", 40, 127, 71}, {37, "Bright green", 75, 151, 75},
    {38, "Dark orange", 160, 95, 53}, {45, "Light blue", 180, 210, 228}, {101, "Medium red", 218, 134, 122},
    {102, "Medium blue", 110, 153, 202}, {104, "Bright violet", 107, 50, 124}, {105, "Br. yellowish orange", 226, 155, 64},
    {106, "Bright orange", 218, 133, 65}, {119, "Br. yellowish green", 164, 189, 71}, {124, "Bright reddish violet", 146, 57, 120},
    {125, "Light orange", 234, 184, 146}, {133, "Neon orange", 213, 115, 61}, {141, "Earth green", 39, 70, 45},
    {192, "Reddish brown", 105, 64, 40}, {194, "Medium stone grey", 163, 162, 165}, {199, "Dark stone grey", 99, 95, 98},
    {208, "Light stone grey", 229, 228, 223}, {217, "Brown", 124, 92, 70}, {226, "Cool yellow", 253, 234, 141},
    {1001, "Institutional white", 248, 248, 248}, {1002, "Mid gray", 205, 205, 205}, {1003, "Really black", 17, 17, 17},
    {1004, "Really red", 255, 0, 0}, {1005, "Deep orange", 255, 175, 0}, {1006, "Alder", 180, 128, 255},
    {1007, "Dusty Rose", 163, 75, 75}, {1008, "Olive", 193, 190, 66}, {1009, "New Yeller", 255, 255, 0},
    {1010, "Really blue", 0, 0, 255}, {1011, "Navy blue", 0, 32, 96}, {1012, "Deep blue", 33, 84, 185},
    {1013, "Cyan", 4, 175, 236}, {1014, "CGA brown", 170, 85, 0}, {1015, "Magenta", 170, 0, 170},
    {1016, "Pink", 255, 102, 204}, {1017, "Deep orange", 255, 175, 0}, {1018, "Teal", 18, 238, 212},
    {1019, "Toothpaste", 0, 255, 255}, {1020, "Lime green", 0, 255, 0}, {1025, "Pastel orange", 255, 201, 201},
    {1026, "Pastel violet", 177, 167, 255}, {1028, "Pastel green", 204, 255, 204}, {1029, "Pastel yellow", 255, 255, 204},
    {1030, "Pastel brown", 255, 204, 153}, {1031, "Royal purple", 98, 37, 209}, {1032, "Hot pink", 255, 0, 191},
}
BrickColor = {}
BrickColor.__index = BrickColor
local function __bc_make(entry)
    local c = Color3.fromRGB(entry[3], entry[4], entry[5])
    return setmetatable({Number = entry[1], Name = entry[2], Color = c, r = c.R, g = c.G, b = c.B}, BrickColor)
end
local function __bc_by_number(n)
    for i = 1, #__BC_PALETTE do local e = __BC_PALETTE[i]; if e[1] == n then return __bc_make(e) end end
    return __bc_make({194, "Medium stone grey", 163, 162, 165})
end
local function __bc_by_name(name)
    local want = string.lower(tostring(name))
    for i = 1, #__BC_PALETTE do local e = __BC_PALETTE[i]; if string.lower(e[2]) == want then return __bc_make(e) end end
    return __bc_make({194, "Medium stone grey", 163, 162, 165})
end
local function __bc_nearest(r, g, b)   -- r,g,b в 0..1
    local best, bd = nil, math.huge
    for i = 1, #__BC_PALETTE do
        local e = __BC_PALETTE[i]
        local dr, dg, db = e[3] / 255 - r, e[4] / 255 - g, e[5] / 255 - b
        local d = dr * dr + dg * dg + db * db
        if d < bd then bd = d; best = e end
    end
    return __bc_make(best)
end
function BrickColor.new(a, g, b)
    if type(a) == "number" and g == nil then return __bc_by_number(a) end
    if type(a) == "string" then return __bc_by_name(a) end
    if type(a) == "table" and rawget(a, "R") ~= nil then return __bc_nearest(a.R, a.G, a.B) end
    if type(a) == "table" and rawget(a, "Number") ~= nil then return a end
    if type(a) == "number" and type(g) == "number" and type(b) == "number" then return __bc_nearest(a, g, b) end
    return __bc_by_number(194)
end
function BrickColor.Random() return __bc_make(__BC_PALETTE[math.random(1, #__BC_PALETTE)]) end
BrickColor.random = BrickColor.Random
function BrickColor.palette(i) return __bc_make(__BC_PALETTE[((tonumber(i) or 0) % #__BC_PALETTE) + 1]) end
-- BrickColor.Red(), BrickColor.White() ... — по имени без пробелов
for i = 1, #__BC_PALETTE do
    local e = __BC_PALETTE[i]
    local key = string.gsub(e[2], "[^%w]", "")
    if rawget(BrickColor, key) == nil then BrickColor[key] = function() return __bc_make(e) end end
end
BrickColor.Red = function() return __bc_by_name("Bright red") end
BrickColor.Blue = function() return __bc_by_name("Bright blue") end
BrickColor.Yellow = function() return __bc_by_name("Bright yellow") end
BrickColor.Green = function() return __bc_by_name("Dark green") end
BrickColor.Gray = function() return __bc_by_name("Medium stone grey") end
BrickColor.Orange = function() return __bc_by_name("Bright orange") end
BrickColor.__eq = function(x, y) return rawget(x, "Number") == rawget(y, "Number") end
BrickColor.__tostring = function(x) return rawget(x, "Name") end

Color3 = {}
Color3.__index = Color3
function Color3.new(r, g, b) return setmetatable({R = r or 0, G = g or 0, B = b or 0}, Color3) end
function Color3.fromRGB(r, g, b) return Color3.new((r or 0)/255, (g or 0)/255, (b or 0)/255) end
function Color3.fromHSV(h, s, v)
    -- Стандартная формула HSV->RGB (h,s,v в диапазоне 0..1, как и в Roblox).
    local i = math.floor(h * 6)
    local f = h * 6 - i
    local p = v * (1 - s)
    local q = v * (1 - f * s)
    local t = v * (1 - (1 - f) * s)
    i = i % 6
    if i == 0 then return Color3.new(v, t, p)
    elseif i == 1 then return Color3.new(q, v, p)
    elseif i == 2 then return Color3.new(p, v, t)
    elseif i == 3 then return Color3.new(p, q, v)
    elseif i == 4 then return Color3.new(t, p, v)
    else return Color3.new(v, p, q) end
end
Color3.__tostring = function(c) return c.R .. ", " .. c.G .. ", " .. c.B end
Color3.__eq = function(a, b) return a.R == b.R and a.G == b.G and a.B == b.B end

-- UDim/UDim2 — только конструкторы и арифметика (+/-), достаточно для
-- Position/Size любого GUI-скрипта. Само визуальное применение — через
-- __set_prop -> luaTableToJsPropValue на JS-стороне (см. installLuaBridge):
-- он узнаёт UDim2 по форме {X={Scale,Offset}, Y={Scale,Offset}}, поэтому
-- поля здесь называются РОВНО так (не scale/offset).
UDim = {}
UDim.__index = UDim
function UDim.new(scale, offset) return setmetatable({Scale = scale or 0, Offset = offset or 0}, UDim) end
UDim.__add = function(a, b) return UDim.new(a.Scale + b.Scale, a.Offset + b.Offset) end
UDim.__sub = function(a, b) return UDim.new(a.Scale - b.Scale, a.Offset - b.Offset) end
UDim.__tostring = function(u) return u.Scale .. ", " .. u.Offset end

UDim2 = {}
UDim2.__index = UDim2
function UDim2.new(xs, xo, ys, yo)
    return setmetatable({X = UDim.new(xs or 0, xo or 0), Y = UDim.new(ys or 0, yo or 0)}, UDim2)
end
function UDim2.fromScale(xs, ys) return UDim2.new(xs, 0, ys, 0) end
function UDim2.fromOffset(xo, yo) return UDim2.new(0, xo, 0, yo) end
UDim2.__add = function(a, b) return UDim2.new(a.X.Scale + b.X.Scale, a.X.Offset + b.X.Offset, a.Y.Scale + b.Y.Scale, a.Y.Offset + b.Y.Offset) end
UDim2.__sub = function(a, b) return UDim2.new(a.X.Scale - b.X.Scale, a.X.Offset - b.X.Offset, a.Y.Scale - b.Y.Scale, a.Y.Offset - b.Y.Offset) end
UDim2.__tostring = function(u) return "{" .. tostring(u.X) .. "}, {" .. tostring(u.Y) .. "}" end

-- typeof(v) — глобальная функция Roblox: Lua-тип для простых значений, а для Roblox-типов — их имя
-- ("Instance", "Vector3", "CFrame", "EnumItem"...). Раньше её не было вовсе: любой скрипт с typeof() падал
-- на attempt to call a nil value (global 'typeof').
function typeof(v)
    local t = type(v)
    if t ~= "table" then return t end
    local mt = getmetatable(v)
    if mt ~= nil then
        if mt == Vector3 then return "Vector3" end
        if mt == Vector2 then return "Vector2" end
        if mt == CFrame then return "CFrame" end
        if mt == Color3 then return "Color3" end
        if mt == UDim2 then return "UDim2" end
        if mt == UDim then return "UDim" end
        if mt == BrickColor then return "BrickColor" end
        if mt == TweenInfo then return "TweenInfo" end
        if mt == Random then return "Random" end
    end
    if rawget(v, "__ref") ~= nil then return "Instance" end
    if rawget(v, "EnumType") ~= nil then return "EnumItem" end
    return "table"
end
-- RunService:BindToRenderStep хранит свои подключения здесь (по имени привязки)
__render_binds = {}
-- RaycastParams.new() — только контейнер полей (FilterDescendantsInstances/FilterType/...): workspace:Raycast в
-- приложении пока нет, но скрипты создают параметры до вызова — без глобала падали на RaycastParams.new
RaycastParams = {}
function RaycastParams.new()
    return {FilterDescendantsInstances = {}, FilterType = "Exclude", IgnoreWater = false,
            RespectCanCollide = false, CollisionGroup = "Default", BruteForceAllSlow = false}
end
-- OverlapParams.new() — контейнер полей для workspace:GetPartBoundsInBox/GetPartsInPart/GetPartBoundsInRadius
-- (без глобала скрипты падали: attempt to index a nil value (global 'OverlapParams')).
OverlapParams = {}
function OverlapParams.new()
    return {FilterDescendantsInstances = {}, FilterType = "Exclude", MaxParts = 0, CollisionGroup = "Default",
            RespectCanCollide = false, BruteForceAllSlow = false}
end
-- Random — класс Luau: Random.new(seed) + NextNumber/NextInteger/NextUnitVector/Shuffle/Clone.
-- Свой генератор (xorshift32): один и тот же seed даёт одну и ту же последовательность, как в Roblox.
-- Целые в fengari 32-битные со знаком, поэтому никаких 64-битных множителей и масок 0xFFFFFFFF:
-- работаем в знаковом int32 (сдвиги влево сами «обрезаются»), результат берём без знакового бита.
-- Раньше глобала Random не было вовсе: attempt to index a nil value (global 'Random').
Random = {}
Random.__index = Random
local function __rnd_step(self)
    local x = self._s
    x = x ~ (x << 13)
    x = x ~ (x >> 17)
    x = x ~ (x << 5)
    self._s = x
    return (x & 0x7FFFFFFF) / 2147483648
end
function Random.new(seed)
    seed = math.floor(tonumber(seed) or (os.time() + math.random(0, 999999)))
    local st = seed % 2147483647
    if st == 0 then st = 1 end
    local self = setmetatable({_s = math.tointeger(st) or 1}, Random)
    for _ = 1, 4 do __rnd_step(self) end   -- прогрев: близкие seed не должны давать близкие первые числа
    return self
end
function Random:NextNumber(min, max)
    local r = __rnd_step(self)
    if min == nil then return r end
    return min + r * (max - min)
end
function Random:NextInteger(min, max)
    return min + math.floor(__rnd_step(self) * (max - min + 1))
end
function Random:NextUnitVector()
    local z = self:NextNumber(-1, 1)
    local a = self:NextNumber(0, 2 * math.pi)
    local r = math.sqrt(1 - z * z)
    return Vector3.new(r * math.cos(a), r * math.sin(a), z)
end
function Random:Shuffle(t)
    for i = #t, 2, -1 do
        local j = self:NextInteger(1, i)
        t[i], t[j] = t[j], t[i]
    end
end
function Random:Clone() return setmetatable({_s = self._s}, Random) end

-- Обобщённый for из Luau: "for k, v in tbl do" (без pairs/ipairs).
-- В Lua 5.3 такая запись пыталась ВЫЗВАТЬ таблицу как итератор —
-- "attempt to call a table value". Препроцессор (expandGenericFor)
-- оборачивает выражение после "in" в __geniter(...): таблица без
-- __call превращается в next-итерацию, всё остальное (pairs(t),
-- ipairs(t), функции-итераторы) проходит как есть.
function __geniter(f, s, c)
    if type(f) == "table" and s == nil and c == nil then
        local mt = getmetatable(f)
        if not (mt and mt.__call) then
            if #f > 0 then
                local n = #f
                return function(_, i)
                    i = i + 1
                    if i <= n then return i, f[i] end
                end, f, 0
            end
            return next, f, nil
        end
    end
    return f, s, c
end

-- math.clamp/round/sign — расширения Luau, которых нет в обычной Lua 5.3
-- (см. math в fengari, стандартная библиотека). Были только в списке
-- подсветки синтаксиса, реально не существовали — "attempt to call a nil
-- value (field 'clamp')" на первой же строке любого обработчика слайдера/
-- промокода/чего угодно, что их использует (а их используют ОЧЕНЬ часто —
-- в этой карте минимум в SettingsMenuScript и Plugin.lua).
function math.clamp(x, min, max)
    if x < min then return min end
    if x > max then return max end
    return x
end
function math.round(x) return math.floor(x + 0.5) end
function math.sign(x)
    if x > 0 then return 1 elseif x < 0 then return -1 else return 0 end
end

-- Расширения стандартной библиотеки Luau, которых нет в Lua 5.3 (fengari). В списке известных имён они
-- значились, но реализованы не были: table.find(...) падал с "attempt to call a nil value (field 'find')"
-- прямо в обработчике Touched лифта — поэтому лобби не открывалось и UI не показывался.
function table.find(t, value, init)
    for i = init or 1, #t do
        if t[i] == value then return i end
    end
    return nil
end
function table.clone(t)
    local c = {}
    for k, v in pairs(t) do c[k] = v end
    return setmetatable(c, getmetatable(t))
end
function table.clear(t)
    for k in pairs(t) do t[k] = nil end
end
function table.create(n, value)
    local t = {}
    if value ~= nil then for i = 1, n do t[i] = value end end
    return t
end
-- freeze только помечает таблицу (запрет записи не эмулируется — для этого пришлось бы подменять таблицу)
local __frozenTables = setmetatable({}, { __mode = "k" })
function table.freeze(t) __frozenTables[t] = true return t end
function table.isfrozen(t) return __frozenTables[t] == true end
-- string.split(s, sep): разделитель по умолчанию ",", как в Luau (разделитель — обычная строка, не паттерн)
function string.split(s, sep)
    sep = sep or ","
    local out, pos = {}, 1
    if sep == "" then
        for i = 1, #s do out[i] = s:sub(i, i) end
        return out
    end
    while true do
        local a, b = s:find(sep, pos, true)
        if not a then out[#out + 1] = s:sub(pos) break end
        out[#out + 1] = s:sub(pos, a - 1)
        pos = b + 1
    end
    return out
end
-- bit32 (в Lua 5.3 есть операторы, но не библиотека). Целые в fengari 32-битные со знаком, а bit32 Roblox работает
-- с беззнаковыми 0..2^32-1: входы приводим к знаковым 32 бит (s32), результат — обратно к беззнаковому (u32).
local function __s32(x)
    x = x % 4294967296
    if x >= 2147483648 then x = x - 4294967296 end
    return math.tointeger(x) or x
end
local function __u32(x) x = x % 4294967296 return math.tointeger(x) or x end
bit32 = bit32 or {
    band = function(a, b, ...) local r = __s32(a) & __s32(b) for _, v in ipairs({...}) do r = r & __s32(v) end return __u32(r) end,
    bor = function(a, b, ...) local r = __s32(a) | __s32(b) for _, v in ipairs({...}) do r = r | __s32(v) end return __u32(r) end,
    bxor = function(a, b, ...) local r = __s32(a) ~ __s32(b) for _, v in ipairs({...}) do r = r ~ __s32(v) end return __u32(r) end,
    bnot = function(a) return __u32(~__s32(a)) end,
    lshift = function(a, n) if n >= 32 or n <= -32 then return 0 end if n < 0 then return __u32(__s32(a) >> -n) end return __u32(__s32(a) << n) end,
    rshift = function(a, n) if n >= 32 or n <= -32 then return 0 end if n < 0 then return __u32(__s32(a) << -n) end return __u32(__s32(a) >> n) end,
    arshift = function(a, n)
        a = __s32(a)
        if n <= 0 then return __u32(a << -n) end
        if n >= 32 then return a < 0 and 4294967295 or 0 end
        local r = a >> n                               -- логический сдвиг
        if a < 0 then r = r | ~(-1 >> n) end           -- дописываем старшие единицы
        return __u32(r)
    end,
    btest = function(a, b) return (__s32(a) & __s32(b)) ~= 0 end,
    extract = function(n, f, w) w = w or 1 return __u32((__s32(n) >> f) & ((1 << w) - 1)) end,
    replace = function(n, v, f, w)
        w = w or 1
        local mask = ((1 << w) - 1) << f
        return __u32((__s32(n) & ~mask) | ((__s32(v) << f) & mask))
    end,
}

-- CFrame.new(...) — только конструктор + позиция, БЕЗ полноценной алгебры
-- поворота (нет "*", нет CFrame.Angles с реальным эффектом) — как и у
-- чтения part.CFrame выше (см. __get_cframe_vecs), это осознанное
-- ограничение. camera.CFrame/part.CFrame = CFrame.new(pos) хотя бы
-- переносит позицию (см. __set_prop), CFrame.new(pos, lookAt) поворот не
-- считает вообще (для этого нужна честная матрица взгляда, которой тут
-- нет) — известное ограничение, не притворяемся, что его нет.
-- В Lua 5.3 (fengari) нет math.atan2 — а в Roblox/Luau он есть.
if not math.atan2 then math.atan2 = function(y, x) return math.atan(y, x) end end
CFrame = {}
-- Полноценный CFrame: позиция + матрица поворота 3x3 (R00..R22, строки),
-- как в Roblox: RightVector = столбец 0, UpVector = столбец 1,
-- LookVector = -столбец 2. Поля X/Y/Z/Position/lookVector/... оставлены
-- «плоскими», потому что JS-мост (камера, твины) читает их напрямую.
local function _cfNew(x, y, z, a, b, c, d, e, f, g, h, i)
    local p = Vector3.new(x, y, z)
    local lv = Vector3.new(-c, -f, -i)
    local rv = Vector3.new(a, d, g)
    local uv = Vector3.new(b, e, h)
    return setmetatable({
        X = x, Y = y, Z = z,
        R00 = a, R01 = b, R02 = c, R10 = d, R11 = e, R12 = f, R20 = g, R21 = h, R22 = i,
        Position = p, p = p,
        lookVector = lv, LookVector = lv,
        rightVector = rv, RightVector = rv,
        upVector = uv, UpVector = uv,
    }, CFrame)
end
local function _m3(A, B)
    return {
        A[1]*B[1] + A[2]*B[4] + A[3]*B[7], A[1]*B[2] + A[2]*B[5] + A[3]*B[8], A[1]*B[3] + A[2]*B[6] + A[3]*B[9],
        A[4]*B[1] + A[5]*B[4] + A[6]*B[7], A[4]*B[2] + A[5]*B[5] + A[6]*B[8], A[4]*B[3] + A[5]*B[6] + A[6]*B[9],
        A[7]*B[1] + A[8]*B[4] + A[9]*B[7], A[7]*B[2] + A[8]*B[5] + A[9]*B[8], A[7]*B[3] + A[8]*B[6] + A[9]*B[9],
    }
end
local function _rx(a) local c, s = math.cos(a), math.sin(a) return { 1, 0, 0, 0, c, -s, 0, s, c } end
local function _ry(a) local c, s = math.cos(a), math.sin(a) return { c, 0, s, 0, 1, 0, -s, 0, c } end
local function _rz(a) local c, s = math.cos(a), math.sin(a) return { c, -s, 0, s, c, 0, 0, 0, 1 } end
local function _fromR(x, y, z, M)
    return _cfNew(x, y, z, M[1], M[2], M[3], M[4], M[5], M[6], M[7], M[8], M[9])
end
local function _lookAt(at, tg, up)
    local lx, ly, lz = tg.X - at.X, tg.Y - at.Y, tg.Z - at.Z
    local len = math.sqrt(lx*lx + ly*ly + lz*lz)
    if len < 1e-9 then return _cfNew(at.X, at.Y, at.Z, 1, 0, 0, 0, 1, 0, 0, 0, 1) end
    lx, ly, lz = lx/len, ly/len, lz/len
    local bx, by, bz = -lx, -ly, -lz
    local ux, uy, uz = 0, 1, 0
    if up then ux, uy, uz = up.X, up.Y, up.Z end
    local rx, ry, rz = uy*bz - uz*by, uz*bx - ux*bz, ux*by - uy*bx
    local rl = math.sqrt(rx*rx + ry*ry + rz*rz)
    if rl < 1e-6 then rx, ry, rz = 1, 0, 0 else rx, ry, rz = rx/rl, ry/rl, rz/rl end
    local vx, vy, vz = by*rz - bz*ry, bz*rx - bx*rz, bx*ry - by*rx
    return _cfNew(at.X, at.Y, at.Z, rx, vx, bx, ry, vy, by, rz, vz, bz)
end
local function _isCF(v) return type(v) == "table" and rawget(v, "R00") ~= nil end
function CFrame.new(a, b, c, qx, qy, qz, qw, ...)
    if a == nil then return _cfNew(0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1) end
    if type(a) == "table" then
        if type(b) == "table" then return _lookAt(a, b) end
        return _cfNew(a.X, a.Y, a.Z, 1, 0, 0, 0, 1, 0, 0, 0, 1)
    end
    local rest = { ... }
    if qx ~= nil and qy == nil then -- (на всякий случай) неполный набор
        return _cfNew(a, b or 0, c or 0, 1, 0, 0, 0, 1, 0, 0, 0, 1)
    end
    if qw ~= nil and rest[1] == nil then -- x,y,z, qx,qy,qz,qw
        local n = math.sqrt(qx*qx + qy*qy + qz*qz + qw*qw)
        if n > 0 then qx, qy, qz, qw = qx/n, qy/n, qz/n, qw/n end
        return _cfNew(a, b, c,
            1 - 2*(qy*qy + qz*qz), 2*(qx*qy - qz*qw), 2*(qx*qz + qy*qw),
            2*(qx*qy + qz*qw), 1 - 2*(qx*qx + qz*qz), 2*(qy*qz - qx*qw),
            2*(qx*qz - qy*qw), 2*(qy*qz + qx*qw), 1 - 2*(qx*qx + qy*qy))
    end
    if rest[1] ~= nil then -- 12 компонент: x,y,z,R00,R01,R02,R10,R11,R12,R20,R21,R22
        return _cfNew(a, b, c, qx, qy, qz, qw, rest[1], rest[2], rest[3], rest[4], rest[5])
    end
    return _cfNew(a, b or 0, c or 0, 1, 0, 0, 0, 1, 0, 0, 0, 1)
end
CFrame.identity = _cfNew(0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1)
function CFrame.Angles(rx, ry, rz)
    return _fromR(0, 0, 0, _m3(_m3(_rx(rx or 0), _ry(ry or 0)), _rz(rz or 0)))
end
CFrame.fromEulerAnglesXYZ = CFrame.Angles
function CFrame.fromOrientation(rx, ry, rz)
    return _fromR(0, 0, 0, _m3(_m3(_ry(ry or 0), _rx(rx or 0)), _rz(rz or 0)))
end
CFrame.fromEulerAnglesYXZ = CFrame.fromOrientation
function CFrame.fromAxisAngle(axis, angle)
    local l = math.sqrt(axis.X*axis.X + axis.Y*axis.Y + axis.Z*axis.Z)
    if l < 1e-9 then return CFrame.identity end
    local x, y, z = axis.X/l, axis.Y/l, axis.Z/l
    local c, s = math.cos(angle), math.sin(angle)
    local t = 1 - c
    return _fromR(0, 0, 0, {
        t*x*x + c,   t*x*y - s*z, t*x*z + s*y,
        t*x*y + s*z, t*y*y + c,   t*y*z - s*x,
        t*x*z - s*y, t*y*z + s*x, t*z*z + c })
end
function CFrame.lookAt(at, target, up) return _lookAt(at, target, up) end
function CFrame.fromMatrix(pos, vx, vy, vz)
    vz = vz or vx:Cross(vy)
    return _cfNew(pos.X, pos.Y, pos.Z, vx.X, vy.X, vz.X, vx.Y, vy.Y, vz.Y, vx.Z, vy.Z, vz.Z)
end
CFrame.__index = function(t, k)
    local v = rawget(CFrame, k)
    if v ~= nil then return v end
    if k == "Rotation" then
        return _cfNew(0, 0, 0, t.R00, t.R01, t.R02, t.R10, t.R11, t.R12, t.R20, t.R21, t.R22)
    end
    return nil
end
CFrame.__mul = function(a, b)
    if _isCF(b) then
        local R = _m3({ a.R00, a.R01, a.R02, a.R10, a.R11, a.R12, a.R20, a.R21, a.R22 },
                      { b.R00, b.R01, b.R02, b.R10, b.R11, b.R12, b.R20, b.R21, b.R22 })
        return _fromR(
            a.R00*b.X + a.R01*b.Y + a.R02*b.Z + a.X,
            a.R10*b.X + a.R11*b.Y + a.R12*b.Z + a.Y,
            a.R20*b.X + a.R21*b.Y + a.R22*b.Z + a.Z, R)
    end
    return Vector3.new(
        a.R00*b.X + a.R01*b.Y + a.R02*b.Z + a.X,
        a.R10*b.X + a.R11*b.Y + a.R12*b.Z + a.Y,
        a.R20*b.X + a.R21*b.Y + a.R22*b.Z + a.Z)
end
CFrame.__add = function(a, b)
    return _cfNew(a.X + b.X, a.Y + b.Y, a.Z + b.Z, a.R00, a.R01, a.R02, a.R10, a.R11, a.R12, a.R20, a.R21, a.R22)
end
CFrame.__sub = function(a, b)
    return _cfNew(a.X - b.X, a.Y - b.Y, a.Z - b.Z, a.R00, a.R01, a.R02, a.R10, a.R11, a.R12, a.R20, a.R21, a.R22)
end
CFrame.__eq = function(a, b)
    return a.X == b.X and a.Y == b.Y and a.Z == b.Z and a.R00 == b.R00 and a.R01 == b.R01
        and a.R02 == b.R02 and a.R10 == b.R10 and a.R11 == b.R11 and a.R12 == b.R12
        and a.R20 == b.R20 and a.R21 == b.R21 and a.R22 == b.R22
end
CFrame.__tostring = function(c)
    return c.X .. ", " .. c.Y .. ", " .. c.Z .. ", " .. c.R00 .. ", " .. c.R01 .. ", " .. c.R02 .. ", "
        .. c.R10 .. ", " .. c.R11 .. ", " .. c.R12 .. ", " .. c.R20 .. ", " .. c.R21 .. ", " .. c.R22
end
function CFrame.Inverse(self)
    return _cfNew(
        -(self.R00*self.X + self.R10*self.Y + self.R20*self.Z),
        -(self.R01*self.X + self.R11*self.Y + self.R21*self.Z),
        -(self.R02*self.X + self.R12*self.Y + self.R22*self.Z),
        self.R00, self.R10, self.R20, self.R01, self.R11, self.R21, self.R02, self.R12, self.R22)
end
function CFrame.GetComponents(self)
    return self.X, self.Y, self.Z, self.R00, self.R01, self.R02, self.R10, self.R11, self.R12, self.R20, self.R21, self.R22
end
CFrame.components = CFrame.GetComponents
function CFrame.ToWorldSpace(self, cf) return self * cf end
function CFrame.ToObjectSpace(self, cf) return self:Inverse() * cf end
function CFrame.PointToWorldSpace(self, v) return self * v end
function CFrame.PointToObjectSpace(self, v) return self:Inverse() * v end
function CFrame.VectorToWorldSpace(self, v)
    return Vector3.new(self.R00*v.X + self.R01*v.Y + self.R02*v.Z,
                       self.R10*v.X + self.R11*v.Y + self.R12*v.Z,
                       self.R20*v.X + self.R21*v.Y + self.R22*v.Z)
end
function CFrame.VectorToObjectSpace(self, v)
    return Vector3.new(self.R00*v.X + self.R10*v.Y + self.R20*v.Z,
                       self.R01*v.X + self.R11*v.Y + self.R21*v.Z,
                       self.R02*v.X + self.R12*v.Y + self.R22*v.Z)
end
function CFrame.ToEulerAnglesXYZ(self)
    local s = math.max(-1, math.min(1, self.R02))
    local ry = math.asin(s)
    if math.abs(s) < 0.99999 then
        return math.atan2(-self.R12, self.R22), ry, math.atan2(-self.R01, self.R00)
    end
    return math.atan2(self.R21, self.R11), ry, 0
end
function CFrame.ToOrientation(self)
    local s = math.max(-1, math.min(1, -self.R12))
    local rx = math.asin(s)
    if math.abs(s) < 0.99999 then
        return rx, math.atan2(self.R02, self.R22), math.atan2(self.R10, self.R11)
    end
    return rx, math.atan2(-self.R20, self.R00), 0
end
CFrame.ToEulerAnglesYXZ = CFrame.ToOrientation
function CFrame.Orthonormalize(self) return self end
function CFrame.FuzzyEq(self, o, eps)
    eps = eps or 1e-5
    local a = { self:GetComponents() }
    local b = { o:GetComponents() }
    for i = 1, 12 do if math.abs(a[i] - b[i]) > eps then return false end end
    return true
end
local function _toQuat(M)
    local tr = M[1] + M[5] + M[9]
    local w, x, y, z
    if tr > 0 then
        local s = math.sqrt(tr + 1) * 2
        w = s / 4; x = (M[8] - M[6]) / s; y = (M[3] - M[7]) / s; z = (M[4] - M[2]) / s
    elseif M[1] > M[5] and M[1] > M[9] then
        local s = math.sqrt(1 + M[1] - M[5] - M[9]) * 2
        w = (M[8] - M[6]) / s; x = s / 4; y = (M[2] + M[4]) / s; z = (M[3] + M[7]) / s
    elseif M[5] > M[9] then
        local s = math.sqrt(1 + M[5] - M[1] - M[9]) * 2
        w = (M[3] - M[7]) / s; x = (M[2] + M[4]) / s; y = s / 4; z = (M[6] + M[8]) / s
    else
        local s = math.sqrt(1 + M[9] - M[1] - M[5]) * 2
        w = (M[4] - M[2]) / s; x = (M[3] + M[7]) / s; y = (M[6] + M[8]) / s; z = s / 4
    end
    return x, y, z, w
end
-- cf:Lerp(goal, alpha) — позиция линейно, поворот сферически (slerp)
function CFrame.Lerp(self, goal, alpha)
    local x = self.X + (goal.X - self.X) * alpha
    local y = self.Y + (goal.Y - self.Y) * alpha
    local z = self.Z + (goal.Z - self.Z) * alpha
    local ax, ay, az, aw = _toQuat({ self.R00, self.R01, self.R02, self.R10, self.R11, self.R12, self.R20, self.R21, self.R22 })
    local bx, by, bz, bw = _toQuat({ goal.R00, goal.R01, goal.R02, goal.R10, goal.R11, goal.R12, goal.R20, goal.R21, goal.R22 })
    local dot = ax*bx + ay*by + az*bz + aw*bw
    if dot < 0 then bx, by, bz, bw, dot = -bx, -by, -bz, -bw, -dot end
    local k0, k1
    if dot > 0.9995 then
        k0, k1 = 1 - alpha, alpha
    else
        local th = math.acos(dot)
        local sn = math.sin(th)
        k0, k1 = math.sin((1 - alpha) * th) / sn, math.sin(alpha * th) / sn
    end
    return CFrame.new(x, y, z, k0*ax + k1*bx, k0*ay + k1*by, k0*az + k1*bz, k0*aw + k1*bw)
end

-- NumberSequence/NumberSequenceKeypoint/ColorSequence(Keypoint) — просто
-- данные (чаще всего для UIGradient/ParticleEmitter). Визуального градиента
-- у UIGradient в этом движке нет — эти конструкторы нужны только чтобы
-- скрипт не падал НА СТРОКЕ ИХ СОЗДАНИЯ, а не чтобы градиент реально
-- был виден.
function NumberSequenceKeypoint_new(time, value, envelope) return { Time = time, Value = value, Envelope = envelope or 0 } end
NumberSequenceKeypoint = { new = NumberSequenceKeypoint_new }
function NumberSequence_new(a, b)
    if type(a) == "table" then return { Keypoints = a } end
    if b ~= nil then return { Keypoints = { NumberSequenceKeypoint_new(0, a), NumberSequenceKeypoint_new(1, b) } } end
    return { Keypoints = { NumberSequenceKeypoint_new(0, a), NumberSequenceKeypoint_new(1, a) } }
end
NumberSequence = { new = NumberSequence_new }
function ColorSequenceKeypoint_new(time, value) return { Time = time, Value = value } end
ColorSequenceKeypoint = { new = ColorSequenceKeypoint_new }
function ColorSequence_new(a, b)
    if type(a) == "table" then return { Keypoints = a } end
    if b ~= nil then return { Keypoints = { ColorSequenceKeypoint_new(0, a), ColorSequenceKeypoint_new(1, b) } } end
    return { Keypoints = { ColorSequenceKeypoint_new(0, a), ColorSequenceKeypoint_new(1, a) } }
end
ColorSequence = { new = ColorSequence_new }
-- NumberRange.new(min[, max]) — Min/Max (ParticleEmitter.Lifetime/Speed/..., без эффекта в эмуляторе)
function NumberRange_new(min, max) return { Min = min or 0, Max = max or min or 0 } end
NumberRange = { new = NumberRange_new }

Vector2 = {}
-- Magnitude/Unit — свойства (считаются на лету), остальное — методы из таблицы Vector2.
-- Раньше был только new/+/-: v:Lerp(...) в CameraRecoiler (Blaster) падал каждый кадр.
Vector2.__index = function(t, k)
    if k == "Magnitude" or k == "magnitude" then return math.sqrt(t.X * t.X + t.Y * t.Y) end
    if k == "Unit" or k == "unit" then
        local m = math.sqrt(t.X * t.X + t.Y * t.Y)
        if m == 0 then return Vector2.new(0, 0) end
        return Vector2.new(t.X / m, t.Y / m)
    end
    return rawget(Vector2, k)
end
function Vector2.new(x, y) return setmetatable({X = x or 0, Y = y or 0}, Vector2) end
Vector2.__add = function(a, b) return Vector2.new(a.X + b.X, a.Y + b.Y) end
Vector2.__sub = function(a, b) return Vector2.new(a.X - b.X, a.Y - b.Y) end
Vector2.__mul = function(a, b)
    if type(a) == "number" then return Vector2.new(a * b.X, a * b.Y) end
    if type(b) == "number" then return Vector2.new(a.X * b, a.Y * b) end
    return Vector2.new(a.X * b.X, a.Y * b.Y)
end
Vector2.__div = function(a, b)
    if type(a) == "number" then return Vector2.new(a / b.X, a / b.Y) end
    if type(b) == "number" then return Vector2.new(a.X / b, a.Y / b) end
    return Vector2.new(a.X / b.X, a.Y / b.Y)
end
Vector2.__unm = function(a) return Vector2.new(-a.X, -a.Y) end
Vector2.__eq = function(a, b) return a.X == b.X and a.Y == b.Y end
Vector2.__tostring = function(v) return v.X .. ", " .. v.Y end
function Vector2.Dot(a, b) return a.X * b.X + a.Y * b.Y end
function Vector2.Cross(a, b) return a.X * b.Y - a.Y * b.X end      -- как в Roblox: скаляр (z-компонента)
function Vector2.Lerp(a, b, t) return Vector2.new(a.X + (b.X - a.X) * t, a.Y + (b.Y - a.Y) * t) end
function Vector2.Max(a, b) return Vector2.new(math.max(a.X, b.X), math.max(a.Y, b.Y)) end
function Vector2.Min(a, b) return Vector2.new(math.min(a.X, b.X), math.min(a.Y, b.Y)) end
function Vector2.Abs(a) return Vector2.new(math.abs(a.X), math.abs(a.Y)) end
function Vector2.Floor(a) return Vector2.new(math.floor(a.X), math.floor(a.Y)) end
function Vector2.Ceil(a) return Vector2.new(math.ceil(a.X), math.ceil(a.Y)) end
function Vector2.FuzzyEq(a, b, eps) eps = eps or 1e-5 return math.abs(a.X - b.X) <= eps and math.abs(a.Y - b.Y) <= eps end
Vector2.zero = Vector2.new(0, 0)
Vector2.one = Vector2.new(1, 1)
Vector2.xAxis = Vector2.new(1, 0)
Vector2.yAxis = Vector2.new(0, 1)

-- Enum.* — ленивый и кэширующий: Enum.UserInputType.MouseButton1 создаётся
-- один раз при первом обращении и потом отдаётся ИЗ КЭША тем же объектом,
-- поэтому "input.UserInputType == Enum.UserInputType.MouseButton1" в
-- скриптах сравнивает две ссылки на одну и ту же таблицу (обычное Lua "==",
-- без __eq) — раньше Enum не существовал вовсе (только в списке подсветки
-- синтаксиса), и любое обращение к Enum.* падало "attempt to index a nil
-- value (global 'Enum')".
local __enumCache = {}
-- EnumItem.Value: числа из настоящего Roblox для самых используемых перечислений (раньше .Value не было вовсе:
-- Enum.RenderPriority.Camera.Value + 2 в CameraRecoiler давало 'arithmetic on a nil value (field Value)').
-- Для остальных перечислений Value остаётся nil — выдумывать числа нельзя.
local __ENUM_VALUES = {
    RenderPriority = { First = 0, Input = 100, Camera = 200, Character = 300, Last = 2000 },
    MouseBehavior = { Default = 0, LockCenter = 1, LockCurrentPosition = 2 },
    ProximityPromptInputType = { Keyboard = 1, Mouse = 2, Gamepad = 3, Touch = 4 },
    ProximityPromptStyle = { Default = 0, Custom = 1 },
    ProximityPromptExclusivity = { OnePerButton = 0, OneGlobally = 1, AlwaysShow = 2 },
    CameraType = { Fixed = 0, Watch = 1, Attach = 2, Track = 3, Follow = 4, Custom = 5, Scriptable = 6, Orbital = 7 },
    UserInputType = { MouseButton1 = 0, MouseButton2 = 1, MouseButton3 = 2, MouseWheel = 3, MouseMovement = 4,
        Touch = 7, Keyboard = 8, Focus = 9, Accelerometer = 10, Gyro = 11, Gamepad1 = 12, Gamepad2 = 13,
        Gamepad3 = 14, Gamepad4 = 15, Gamepad5 = 16, Gamepad6 = 17, Gamepad7 = 18, Gamepad8 = 19,
        TextInput = 20, None = 21 },
}
Enum = setmetatable({}, { __index = function(t, enumType)
    if not __enumCache[enumType] then
        __enumCache[enumType] = setmetatable({}, { __index = function(t2, name)
            local key = enumType .. "." .. name
            if not __enumCache[key] then
                __enumCache[key] = setmetatable({ Name = name, EnumType = enumType, Value = (__ENUM_VALUES[enumType] or {})[name] }, {
                    __tostring = function(e) return "Enum." .. e.EnumType .. "." .. e.Name end,
                })
            end
            return __enumCache[key]
        end })
    end
    return __enumCache[enumType]
end })

local InstanceMT = {}
-- свойство -> тип Enum (значения хранятся на JS-стороне строкой)
local __ENUM_PROPS = { CameraType = "CameraType", MouseBehavior = "MouseBehavior", Material = "Material" }

-- Event:Connect(fn) — функция-колбэк хранится ЦЕЛИКОМ на Lua-стороне (в
-- обычной Lua-таблице __conns), а не через luaL_ref в JS-реестр — так
-- проще проверить (тестируется напрямую в lua5.4, без fengari) и не
-- зависит от того, как именно fengari реализует работу с LUA_REGISTRYINDEX
-- изнутри JS-биндинга. JS-стороне (__register_conn/__unregister_conn)
-- нужен только id для маршрутизации: "по этому (ref, событие) вызови
-- Lua-функцию __invoke_conn(id, ...)" — саму функцию она никогда не видит.
-- connect/disconnect/wait — legacy lowercase-алиасы (Roblox 2008-2011
-- годов, до перехода на PascalCase) — без них скрипты того времени падали
-- уже на первом же :connect(), даже когда сам сигнал был честный.
local __conns = {}
-- id подписок должны быть уникальны МЕЖДУ серверной и клиентской Lua-VM: JS хранит их в одной
-- общей таблице luaSignalConns. Раньше обе VM считали с 1, клиентские подписки затирали серверные
-- с теми же номерами, и событие (например, ClickDetector.MouseClick) вызывало чужую функцию
-- в другой VM или не вызывало ничего.
local __nextConnId = (__CONN_BASE or 0) + 1
local __nextAnimTrackId = 0 -- см. Animator:LoadAnimation в InstanceMT.__index ниже
-- InputBegan/InputEnded/InputChanged — единственные события, где JS шлёт
-- НЕ готовые аргументы колбэка, а "сырые" (typeName, x, y) — само
-- превращение в InputObject (с Enum.UserInputType и Position) сделано
-- тут, в момент Connect, а не на JS-стороне: Enum это Lua-таблицы,
-- строить их из JS было бы либо копированием той же кэширующей логики
-- дважды, либо синтетическими объектами, не равными настоящим Enum.*.
local __MOUSE = nil
local __CAS = { actions = {}, hooked = false }
local function __casHook()
    if __CAS.hooked then return end
    __CAS.hooked = true
    local uis = game:GetService("UserInputService")
    local function dispatch(input, state)
        for name, a in pairs(__CAS.actions) do
            for _, key in ipairs(a.keys) do
                if input.KeyCode == key or input.UserInputType == key then
                    a.fn(name, state, input)
                    break
                end
            end
        end
    end
    uis.InputBegan:Connect(function(input) dispatch(input, Enum.UserInputState.Begin) end)
    uis.InputEnded:Connect(function(input) dispatch(input, Enum.UserInputState.End) end)
end
local __CAS_METHODS = {
    BindAction = function(self, name, fn, touch, ...)
        __casHook(); __CAS.actions[name] = { fn = fn, keys = { ... } }
    end,
    BindActionAtPriority = function(self, name, fn, touch, priority, ...)
        __casHook(); __CAS.actions[name] = { fn = fn, keys = { ... } }
    end,
    UnbindAction = function(self, name) __CAS.actions[name] = nil end,
    UnbindAllActions = function(self) __CAS.actions = {} end,
    GetAllBoundActionInfo = function(self) return {} end,
    GetBoundActionInfo = function(self, name) return {} end,
    SetTitle = function() end, SetDescription = function() end, SetImage = function() end,
    SetPosition = function() end, GetButton = function() return nil end,
}
local __TOOL_DEFAULTS = { Enabled = true, TextureId = "", ToolTip = "", CanBeDropped = true, RequiresHandle = true,
    ManualActivationOnly = false }
local function wrapInputEventFn(fn, evName)
    local state = evName == "InputBegan" and "Begin" or (evName == "InputEnded" and "End" or "Change")
    return function(typeName, x, y, keyName)
        local input = setmetatable({
            UserInputType = Enum.UserInputType[typeName],
            UserInputState = Enum.UserInputState[state],
            KeyCode = keyName and Enum.KeyCode[keyName] or Enum.KeyCode.Unknown,
            Position = Vector3.new(x or 0, y or 0, 0),
        }, {})
        return fn(input, false)
    end
end
local function makeEvent(ref, evName)
    local ev = setmetatable({}, { __index = {
        Connect = function(self, fn)
            local id = __nextConnId
            __nextConnId = __nextConnId + 1
            local isInputEvent = evName == "InputBegan" or evName == "InputEnded" or evName == "InputChanged"
            __conns[id] = isInputEvent and wrapInputEventFn(fn, evName) or fn
            __register_conn(id, ref, evName)
            return setmetatable({}, { __index = {
                Disconnect = function() __conns[id] = nil; __unregister_conn(id) end,
                disconnect = function() __conns[id] = nil; __unregister_conn(id) end,
            } })
        end,
        -- Настоящий блокирующий Wait — уступает корутину (__wait_signal
        -- делает lua_yield) и просыпается ровно с теми аргументами, с
        -- которыми в следующий раз выстрелит этот же (ref, evName), см.
        -- luaSignalWaits/fireLuaSignal на JS-стороне. Раньше тут был
        -- "return nil" сразу же, без реального ожидания — старые скрипты
        -- вида "t, s = r.Stepped:wait()" получали t=nil и падали на
        -- следующей же строке арифметикой на nil.
        Wait = function(self) return __wait_signal(ref, evName) end,
        -- Once: сработать один раз и сам отключиться (sound.Ended:Once(fn) и т.п.)
        Once = function(self, fn)
            local conn
            conn = self:Connect(function(...)
                if conn then conn:Disconnect() end
                return fn(...)
            end)
            return conn
        end,
    } })
    local mt = getmetatable(ev).__index
    mt.connect = mt.Connect
    mt.wait = mt.Wait
    mt.once = mt.Once
    return ev
end

-- Вызывается из JS (fireLuaSignal) — по id находит СВОЮ Lua-функцию и
-- зовёт её обычным pcall, вместо того чтобы JS напрямую дёргал
-- lua_rawgeti/lua_pcall по значению, снятому через luaL_ref.
function __invoke_conn(id, ...)
    local fn = __conns[id]
    if fn then
        local ok, err = pcall(fn, ...)
        if not ok then warn("ошибка в обработчике события: " .. tostring(err)) end
    end
end

-- __mode="v" — слабые значения: если Lua-код нигде больше не держит ссылку
-- на обёртку, она может быть собрана сборщиком мусора, а не висеть вечно.
local instances = setmetatable({}, {__mode = "v"})

-- Цепочки наследования классов для IsA (класс -> список ПРЕДКОВ, от
-- ближайшего к дальнему). Не полное дерево Instance API, а только классы,
-- которые реально встречаются в парсере/сцене — этого достаточно, чтобы
-- ":IsA("BasePart")"/":IsA("GuiObject")"/":IsA("PVInstance")" и т.п.
-- работали как в настоящем Roblox, а не только по точному совпадению имени.
INSTANCE_CLASS_ANCESTORS = {
    Part = {"BasePart", "PVInstance", "Instance"},
    MeshPart = {"BasePart", "PVInstance", "Instance"},
    WedgePart = {"BasePart", "PVInstance", "Instance"},
    CornerWedgePart = {"BasePart", "PVInstance", "Instance"},
    TrussPart = {"BasePart", "PVInstance", "Instance"},
    SpherePart = {"BasePart", "PVInstance", "Instance"},
    SpawnLocation = {"BasePart", "PVInstance", "Instance"},
    Seat = {"BasePart", "PVInstance", "Instance"},
    VehicleSeat = {"BasePart", "PVInstance", "Instance"},
    UnionOperation = {"BasePart", "PVInstance", "Instance"},
    NegateOperation = {"BasePart", "PVInstance", "Instance"},
    Model = {"PVInstance", "Instance"},
    Folder = {"Instance"},
    Frame = {"GuiObject", "GuiBase2d", "Instance"},
    ScrollingFrame = {"GuiObject", "GuiBase2d", "Instance"},
    TextLabel = {"GuiObject", "GuiBase2d", "Instance"},
    TextButton = {"GuiObject", "GuiBase2d", "Instance"},
    TextBox = {"GuiObject", "GuiBase2d", "Instance"},
    ImageLabel = {"GuiObject", "GuiBase2d", "Instance"},
    ImageButton = {"GuiObject", "GuiBase2d", "Instance"},
    ViewportFrame = {"GuiObject", "GuiBase2d", "Instance"},
    ScreenGui = {"LayerCollector", "GuiBase2d", "Instance"},
    BillboardGui = {"LayerCollector", "GuiBase2d", "Instance"},
    SurfaceGui = {"LayerCollector", "GuiBase2d", "Instance"},
    Script = {"LuaSourceContainer", "Instance"},
    LocalScript = {"LuaSourceContainer", "Instance"},
    ModuleScript = {"LuaSourceContainer", "Instance"},
    Sound = {"Instance"},
    SoundEffect = {"Instance"},
    PitchShiftSoundEffect = {"SoundEffect", "Instance"},
    RemoteEvent = {"Instance"},
    RemoteFunction = {"Instance"},
    BindableEvent = {"Instance"},
    BindableFunction = {"Instance"},
    Humanoid = {"Instance"},
    Camera = {"Instance"},
}

-- ВАЖНО: -1 (и только -1) — "нет инстанса" (так JS-мост сигналит "родитель
-- не найден"/"ребёнок не найден"). Виртуальные инстансы из Instance.new()
-- используют ДРУГИЕ отрицательные ref'ы (см. __instance_new) — это валидные
-- объекты, их заворачивать НУЖНО, поэтому проверяем именно "== -1", а не
-- "< 0".
local __emuWarned = {}
function __emuWarnOnce(key, text)
    if __emuWarned[key] then return end
    __emuWarned[key] = true
    __emu_warn(key, text)
end
local function wrap(ref)
    if ref == nil or ref == -1 then return nil end
    local existing = instances[ref]
    if existing then return existing end
    local t = setmetatable({}, InstanceMT)
    rawset(t, "__ref", ref)
    instances[ref] = t
    return t
end
__wrap = wrap

InstanceMT.__index = function(t, k)
    local ref = rawget(t, "__ref")
    if k == "Parent" then return wrap(__get_parent(ref)) end
    if k == "Name" then return __get_name(ref) end
    if k == "ClassName" or k == "className" then return __get_class(ref) end
    -- player.Character — модельки настоящего Humanoid-персонажа тут нет,
    -- но в Play есть тот самый ходящий "куб от первого/третьего лица"
    -- (charBody/charMesh) — считаем его персонажем игрока: раньше
    -- player.Character всегда был nil, и "if not player.Character then
    -- player.CharacterAdded:Wait() end" в Main.lua висел бы вечно (ждал
    -- события, которое никто никогда не шлёт) — теперь читаем настоящий
    -- ref через __get_character_ref, so=Wait() до него просто не доходит.
    if k == "Character" and __get_class(ref) == "Player" then
        return wrap(__get_character_ref())
    end
    -- workspace.CurrentCamera — раньше НЕ было особого случая вообще: этот
    -- ключ проваливался в самый нижний fallback __index, который ищет
    -- РЕБЁНКА с именем "CurrentCamera" (а не свойство-ссылку на Camera) —
    -- такого ребёнка не бывает, поэтому workspace.CurrentCamera всегда был
    -- nil. Любой скрипт вида "local camera = workspace.CurrentCamera;
    -- camera.CameraType = ..." падал на первой же строке с камерой
    -- ("attempt to index a nil value") — то есть ВООБЩЕ ничего из логики
    -- сценарной камеры (MenuCamera.lua и подобные) не выполнялось, включая
    -- сам телепорт игрока и переключение CameraType. Находим Camera-ребёнка
    -- Workspace по классу — так же, как реальный Roblox всегда возвращает
    -- единственную настоящую камеру независимо от того, как она названа.
    -- workspace:Raycast(origin, direction, params) -> RaycastResult | nil (раньше метода не было вовсе:
    -- attempt to call a nil value (method 'Raycast') — ломало ИИ врагов и спавнеры).
    if k == "Raycast" and __get_class(ref) == "Workspace" then
        return function(self, origin, direction, params)
            local mode, refs = 0, {}
            if type(params) == "table" then
                local ft = params.FilterType
                local fname = type(ft) == "table" and tostring(ft.Name or ft) or tostring(ft)
                if string.find(fname, "Include", 1, true) then mode = 1 end
                local list = params.FilterDescendantsInstances
                if type(list) == "table" then
                    for _, inst in ipairs(list) do
                        local r = type(inst) == "table" and rawget(inst, "__ref") or nil
                        if r ~= nil then refs[#refs + 1] = r end
                    end
                end
            end
            local hr, px, py, pz, nx, ny, nz, dist = __raycast(mode, origin.X, origin.Y, origin.Z,
                direction.X, direction.Y, direction.Z, table.unpack(refs))
            if hr == nil then return nil end
            local res = { Instance = wrap(hr), Position = Vector3.new(px, py, pz),
                          Normal = Vector3.new(nx, ny, nz), Distance = dist }
            pcall(function() res.Material = Enum.Material.Plastic end)
            return res
        end
    end
    -- workspace:GetPartBoundsInBox(cframe, size, params) / GetPartBoundsInRadius(pos, r, params) / GetPartsInPart(part, params):
    -- пересечение по мировым AABB (повёрнутый бокс заменяется описанным AABB) — для дверей/триггеров/зон этого достаточно.
    if (k == "GetPartBoundsInBox" or k == "GetPartBoundsInRadius" or k == "GetPartsInPart") and __get_class(ref) == "Workspace" then
        return function(self, a, b, c)
            local params, cx, cy, cz, hx, hy, hz, skipRef
            local rx, ry, rz, ux, uy, uz, lx, ly, lz = 1, 0, 0, 0, 1, 0, 0, 0, 1
            local function basis(cf)
                local ok, r, u, l = pcall(function() return cf.RightVector, cf.UpVector, cf.LookVector end)
                if ok and r and u and l then rx, ry, rz, ux, uy, uz, lx, ly, lz = r.X, r.Y, r.Z, u.X, u.Y, u.Z, l.X, l.Y, l.Z end
            end
            if k == "GetPartBoundsInBox" then
                params = c
                cx, cy, cz = a.X, a.Y, a.Z
                hx, hy, hz = b.X / 2, b.Y / 2, b.Z / 2
                basis(a)
            elseif k == "GetPartBoundsInRadius" then
                params = c
                cx, cy, cz = a.X, a.Y, a.Z
                hx, hy, hz = b, b, b
            else
                params = b
                skipRef = type(a) == "table" and rawget(a, "__ref") or nil
                local cf, sz = a.CFrame, a.Size
                cx, cy, cz = cf.X, cf.Y, cf.Z
                hx, hy, hz = sz.X / 2, sz.Y / 2, sz.Z / 2
                basis(cf)
            end
            local mode, maxParts, refs = 0, 0, {}
            if type(params) == "table" then
                local ft = params.FilterType
                local fname = type(ft) == "table" and tostring(ft.Name or ft) or tostring(ft)
                if string.find(fname, "Include", 1, true) then mode = 1 end
                maxParts = tonumber(params.MaxParts) or 0
                local list = params.FilterDescendantsInstances
                if type(list) == "table" then
                    for _, inst in ipairs(list) do
                        local r = type(inst) == "table" and rawget(inst, "__ref") or nil
                        if r ~= nil then refs[#refs + 1] = r end
                    end
                end
            end
            -- весь перебор деталей — на стороне JS (один вызов), иначе по карте в тысячи объектов FPS падает до нуля
            local csv = __overlap(mode, maxParts, skipRef or -1, cx, cy, cz, hx, hy, hz, rx, ry, rz, ux, uy, uz, lx, ly, lz, table.unpack(refs))
            local out = {}
            for id in string.gmatch(csv, "%d+") do out[#out + 1] = wrap(tonumber(id)) end
            return out
        end
    end
    -- Player:GetMouse() — заглушка Mouse (позиция/цель не отслеживаются, сигналы никогда не срабатывают);
    -- без неё скрипты падали на attempt to call a nil value (method 'GetMouse').
    if k == "GetMouse" and __get_class(ref) == "Player" then
        return function(self)
            -- Живая мышь: X/Y (клиентские пиксели — те же, что у AbsolutePosition) и события из UserInputService
            -- (мышь и тач). Раньше события не стреляли, и хотбар (Button1Up/Move/X/Y) не мог принять тап/перетаскивание слота.
            if __MOUSE then return __MOUSE end
            local function sig()
                local s = { fns = {} }
                function s:Connect(fn)
                    table.insert(self.fns, fn)
                    local conn = { Connected = true }
                    function conn:Disconnect()
                        for i, f in ipairs(s.fns) do if f == fn then table.remove(s.fns, i) break end end
                        self.Connected = false
                    end
                    conn.disconnect = conn.Disconnect
                    return conn
                end
                s.connect = s.Connect
                function s:Once(fn)
                    local c
                    c = self:Connect(function(...) c:Disconnect(); fn(...) end)
                    return c
                end
                function s:Wait() return end
                function s:Fire(...) for _, f in ipairs({ table.unpack(self.fns) }) do f(...) end end
                return s
            end
            local m = { Target = nil, X = 0, Y = 0, ViewSizeX = 0, ViewSizeY = 0, Icon = "", TargetFilter = nil }
            pcall(function() m.Hit = CFrame.new(0, 0, 0); m.Origin = CFrame.new(0, 0, 0) end)
            for _, ev in ipairs({ "Button1Down", "Button1Up", "Button2Down", "Button2Up", "Move", "Idle",
                                  "WheelForward", "WheelBackward", "KeyDown", "KeyUp" }) do m[ev] = sig() end
            local uis = game:GetService("UserInputService")
            local UIT = Enum.UserInputType
            local function upd(input) m.X, m.Y = input.Position.X, input.Position.Y end
            uis.InputBegan:Connect(function(input)
                upd(input)
                if input.UserInputType == UIT.MouseButton1 or input.UserInputType == UIT.Touch then m.Button1Down:Fire()
                elseif input.UserInputType == UIT.MouseButton2 then m.Button2Down:Fire() end
            end)
            uis.InputEnded:Connect(function(input)
                upd(input)
                if input.UserInputType == UIT.MouseButton1 or input.UserInputType == UIT.Touch then m.Button1Up:Fire()
                elseif input.UserInputType == UIT.MouseButton2 then m.Button2Up:Fire() end
            end)
            uis.InputChanged:Connect(function(input)
                if input.UserInputType == UIT.MouseMovement or input.UserInputType == UIT.Touch then upd(input); m.Move:Fire() end
            end)
            __MOUSE = m
            return m
        end
    end
    if __get_class(ref) == "Player" then
        if k == "CameraMinZoomDistance" then return 0.5 end
        if k == "CameraMaxZoomDistance" then return 128 end
        if k == "CameraMode" then return "Classic" end
    end
    -- StarterGui:SetCoreGuiEnabled/SetCore/GetCore... — отключать встроенный CoreGui в эмуляторе нечего: no-op
    if __get_class(ref) == "StarterGui" then
        if k == "SetCoreGuiEnabled" then
            return function(self, ty, en) __core_gui(ty and ty.Name or tostring(ty), en and true or false) end
        end
        if k == "SetCore" then return function() end end
        if k == "GetCoreGuiEnabled" then return function() return true end end
        if k == "GetCore" then return function() return nil end end
    end
    if k == "CurrentCamera" and __get_class(ref) == "Workspace" then
        local n = __child_count(ref)
        for i = 1, n do
            local c = __child_at(ref, i - 1)
            if __get_class(c) == "Camera" then return wrap(c) end
        end
        return nil
    end
    -- RunService:BindToRenderStep(name, priority, fn) — вызывать fn(dt) каждый кадр, как RenderStepped (приоритеты
    -- не различаем); UnbindFromRenderStep(name) снимает привязку. Раньше методов не было: attempt to call a nil value.
    if __get_class(ref) == "RunService" then
        if k == "BindToRenderStep" then
            return function(self, name, priority, fn)
                local old = __render_binds[name]
                if old then old:Disconnect() end
                __render_binds[name] = makeEvent(ref, "RenderStepped"):Connect(fn)
            end
        elseif k == "UnbindFromRenderStep" then
            return function(self, name)
                local c = __render_binds[name]
                if c then c:Disconnect(); __render_binds[name] = nil end
            end
        end
    end
    -- Команды: Team.TeamColor/AutoAssignable, Player.Team/Neutral/TeamColor, Teams:GetTeams(). Раньше команд не было
    -- вовсе: RoundGui падал на team.TeamColor, а TDM/Scoring/TeamCollisionFiltering считали игрока нейтральным.
    do
        local cls_ = __get_class(ref)
        if cls_ == "Team" then
            if k == "TeamColor" then
                local n = __team_color(ref)
                if n then return BrickColor.new(n) end
                return nil
            elseif k == "AutoAssignable" then
                return __team_auto(ref)
            end
        elseif cls_ == "Player" then
            if k == "LoadCharacter" then
                return function(self) __load_character() end
            end
            if k == "Team" then
                local t = __player_team(ref)
                if t ~= -1 then return wrap(t) end
                return nil
            elseif k == "Neutral" then
                return __player_team(ref) == -1
            elseif k == "TeamColor" then
                local n = __team_color(ref)
                if n then return BrickColor.new(n) end
                return BrickColor.new(194)
            end
        elseif cls_ == "Teams" and k == "GetTeams" then
            return function(self)
                local out = {}
                for i = 1, __child_count(ref) do
                    local c = __child_at(ref, i - 1)
                    if __get_class(c) == "Team" then out[#out + 1] = wrap(c) end
                end
                return out
            end
        end
    end
    -- PhysicsService: настоящие группы столкновений. Каждая группа — свой бит cannon-тела; part.CollisionGroup = имя
    -- переносит тело в группу (так форсфилд команды пропускает своих и держит чужих).
    if __get_class(ref) == "PhysicsService" then
        if k == "RegisterCollisionGroup" or k == "CreateCollisionGroup" then
            return function(self, name) __phys_register(name) end
        elseif k == "UnregisterCollisionGroup" or k == "RemoveCollisionGroup" then
            return function(self, name) __phys_unregister(name) end
        elseif k == "IsCollisionGroupRegistered" then
            return function(self, name) return __phys_is_registered(name) end
        elseif k == "CollisionGroupSetCollidable" then
            return function(self, a, b, v) __phys_set_collidable(a, b, v and true or false) end
        elseif k == "CollisionGroupsAreCollidable" then
            return function(self, a, b) return __phys_get_collidable(a, b) end
        elseif k == "SetPartCollisionGroup" then
            return function(self, part, name) part.CollisionGroup = name end
        elseif k == "CollisionGroupContainsPart" then
            return function(self, name, part) return part.CollisionGroup == name end
        elseif k == "RenameCollisionGroup" then
            return function(self, from, to) end
        end
    end
    if k == "Position" then
        if __is_gui_ref(ref) then
            local xs, xo, ys, yo = __get_gui_position(ref)
            return UDim2.new(xs, xo, ys, yo)
        end
        local x, y, z = __get_position(ref)
        return Vector3.new(x, y, z)
    end
    if k == "Size" then
        if __is_gui_ref(ref) then
            local xs, xo, ys, yo = __get_gui_size(ref)
            return UDim2.new(xs, xo, ys, yo)
        end
        -- BasePart.Size — раньше не было отдельного случая вообще, и
        -- запрос падал в общий __get_prop-fallback, который для составных
        -- Vector3-свойств не приспособлен (не запись в файле — значение
        -- никогда не оказывалось в мусорном ящике свойств) и всегда отдавал
        -- nil. part.Size.Z на любой нетронутой скриптом детали падало с
        -- "attempt to index a nil value".
        local x, y, z = __get_size(ref)
        return Vector3.new(x, y, z)
    end
    -- Не полноценный CFrame (без умножения/CFrame.Angles) — только чтение
    -- текущей ориентации как Position + три базисных вектора. Этого
    -- достаточно старым скриптам вида "direction = part.CFrame.lookVector",
    -- но НЕ достаточно для составления новых CFrame через "*" — такие
    -- скрипты этот движок пока не поддерживает.
    if k == "CFrame" then
        return CFrame.new(__get_cframe(ref))
    end
    if k == "WorldPivot" then
        return CFrame.new(__get_pivot(ref))
    end
    if k == "FindFirstChild" or k == "findFirstChild" or k == "WaitForChild" or k == "waitForChild" then
        -- Второй аргумент FindFirstChild(name, recursive) раньше игнорировался: ViewModelController искал
        -- MuzzleAttachment глубоко внутри модели и «не находил» его, хотя в файле он есть.
        return function(self, name, recursive)
            local c = __find_first_child(ref, name)
            if c ~= nil and c ~= -1 then return wrap(c) end
            if recursive == true and (k == "FindFirstChild" or k == "findFirstChild") then
                local function search(r)
                    for i = 1, __child_count(r) do
                        local ch = __child_at(r, i - 1)
                        local f = __find_first_child(ch, name)
                        if f ~= nil and f ~= -1 then return f end
                        local deeper = search(ch)
                        if deeper ~= nil then return deeper end
                    end
                    return nil
                end
                local found = search(ref)
                if found ~= nil then return wrap(found) end
            end
            return wrap(c)
        end
    end
    -- AbsolutePosition/AbsoluteSize — реальные пиксельные координаты/размер
    -- GUI-элемента НА ЭКРАНЕ (посчитанные из его Position/Size — UDim2 —
    -- и размеров родителей), раньше вообще не существовали ("attempt to
    -- index a nil value"). Меряем настоящий отрисованный DOM-узел
    -- (getBoundingClientRect через __get_gui_rect), а не пересчитываем
    -- UDim2 вручную — так само собой учитывается вся цепочка родителей.
    -- AbsoluteContentSize — то же самое, но полный (скроллируемый) размер
    -- содержимого: единственный частый практический случай —
    -- UIListLayout/UIGridLayout внутри ScrollingFrame (см. SongMenuScript),
    -- и настоящей раскладки списка (переупорядочивание детей) в этом
    -- движке нет — просто отдаём scrollWidth/scrollHeight родителя.
    if k == "AbsolutePosition" then
        local x, y, w, h = __get_gui_rect(ref)
        return Vector2.new(x, y)
    end
    if k == "AbsoluteSize" then
        local x, y, w, h = __get_gui_rect(ref)
        return Vector2.new(w, h)
    end
    if k == "AbsoluteContentSize" then
        local w, h = __get_gui_content_size(ref)
        return Vector2.new(w, h)
    end
    -- FindFirstChildOfClass/FindFirstChildWhichIsA — раньше отсутствовали
    -- (только в списке ключевых слов подсветки), поэтому такой вызов был
    -- "attempt to call a nil value" — SongMenuScript ищет так свой
    -- UIListLayout. Прямой перебор через __child_count/__child_at, класс
    -- каждого — через уже существующий __get_class.
    if k == "FindFirstChildOfClass" or k == "findFirstChildOfClass" then
        return function(self, cls)
            local n = __child_count(ref)
            for i = 1, n do
                local c = __child_at(ref, i - 1)
                if __get_class(c) == cls then return wrap(c) end
            end
            return nil
        end
    end
    if k == "FindFirstChildWhichIsA" or k == "findFirstChildWhichIsA" then
        -- Через IsA, а не точное совпадение класса: FindFirstChildWhichIsA("BasePart") находит Part/MeshPart
        return function(self, cls, recursive)
            local function search(r)
                for i = 1, __child_count(r) do
                    local c = __child_at(r, i - 1)
                    if __get_class(c) == cls or wrap(c):IsA(cls) then return c end
                end
                if recursive == true then
                    for i = 1, __child_count(r) do
                        local deeper = search(__child_at(r, i - 1))
                        if deeper ~= nil then return deeper end
                    end
                end
                return nil
            end
            local found = search(ref)
            if found ~= nil then return wrap(found) end
            return nil
        end
    end
    -- FindFirstAncestor / FindFirstAncestorOfClass / FindFirstAncestorWhichIsA — вверх по Parent
    if k == "FindFirstAncestor" or k == "FindFirstAncestorOfClass" or k == "FindFirstAncestorWhichIsA" then
        return function(self, arg)
            local cur = __get_parent(ref)
            while cur ~= nil and cur ~= -1 do
                if k == "FindFirstAncestor" then
                    if __get_name(cur) == arg then return wrap(cur) end
                elseif k == "FindFirstAncestorOfClass" then
                    if __get_class(cur) == arg then return wrap(cur) end
                else
                    if __get_class(cur) == arg or wrap(cur):IsA(arg) then return wrap(cur) end
                end
                cur = __get_parent(cur)
            end
            return nil
        end
    end
    if k == "GetChildren" or k == "children" or k == "getChildren" then
        return function(self)
            local n = __child_count(ref)
            local out = {}
            for i = 1, n do out[i] = wrap(__child_at(ref, i - 1)) end
            return out
        end
    end
    -- GetDescendants — раньше вообще не было в мосте (только в списке
    -- ключевых слов подсветки синтаксиса, не в реальной реализации) —
    -- "attempt to call a table value (method 'GetDescendants')" означало,
    -- что __index в принципе не находил такой метод и отдавал пустую
    -- таблицу вместо функции. Рекурсия чисто на Lua поверх тех же
    -- __child_count/__child_at, что и GetChildren.
    if k == "GetDescendants" or k == "getDescendants" then
        return function(self)
            local out = {}
            local function walk(r)
                local n = __child_count(r)
                for i = 1, n do
                    local c = __child_at(r, i - 1)
                    out[#out + 1] = wrap(c)
                    walk(c)
                end
            end
            walk(ref)
            return out
        end
    end
    if k == "IsA" or k == "isA" then
        -- Раньше IsA сравнивала класс только буквально ("Part" ~= "BasePart"),
        -- хотя в реальном Roblox IsA учитывает всю цепочку наследования.
        -- Из-за этого весь код вида "if part:IsA(\"BasePart\") then ..."
        -- (крайне частый паттерн) уходил в false-ветку для любого Part/
        -- MeshPart/WedgePart и т.п. — например, в MenuCamera.lua это
        -- заставляло брать targetSize = Vector3.new(4,4,4) (фиксированную
        -- заглушку) вместо реального Size метки-камеры, и позицию через
        -- GetPivot() у обычного Part вместо .Position — камера каждой
        -- песни считала практически одну и ту же точку.
        return function(self, cls)
            local c = __get_class(ref)
            if c == cls then return true end
            local chain = INSTANCE_CLASS_ANCESTORS[c]
            if chain then
                for i = 1, #chain do
                    if chain[i] == cls then return true end
                end
            end
            return false
        end
    end
    -- GetPropertyChangedSignal(name) — раньше был только заглушкой в списке
    -- подсветки синтаксиса ("attempt to call a nil value"). Отдельный
    -- сигнал на "__prop_<Имя>" (не пересекается с обычными именами событий
    -- вроде Touched) — стреляет из __set_prop на JS-стороне ПОСЛЕ того,
    -- как свойство реально применилось (см. installLuaBridge), так что
    -- scroll.CanvasSize = ... внутри обработчика уже увидит новое значение.
    if k == "GetPropertyChangedSignal" or k == "getPropertyChangedSignal" then
        return function(self, propName) return makeEvent(ref, "__prop_" .. tostring(propName)) end
    end
    -- Animator:LoadAnimation(animation) — настоящего проигрывания анимаций
    -- по AssetId тут быть не может (нет доступа к реальным ассетам с
    -- серверов Roblox — это браузерная песочница), но раньше метод не
    -- существовал ВООБЩЕ ("attempt to call a nil value (method
    -- 'LoadAnimation')"), а вызывается он внутри самих интро-анимаций
    -- (например, Michael_Jackson_-_Billie_Jean.lua) БЕЗ pcall вокруг —
    -- падение обрывало всю функцию, включая task.delay(...) в конце,
    -- который двигает игру дальше после интро. Возвращаем "пустой", но
    -- живой AnimationTrack — .Play()/.Stop() ничего не анимируют, но и не
    -- падают, KeyframeReached/Ended/Stopped существуют и подключаются, но
    -- никогда не выстрелят по-настоящему.
    -- Animator:GetPlayingAnimationTracks() — реально играющих треков нет (см. выше), значит список пуст
    if k == "GetPlayingAnimationTracks" then
        return function(self) return {} end
    end
    if k == "LoadAnimation" or k == "loadAnimation" then
        return function(self, anim)
            __nextAnimTrackId = __nextAnimTrackId + 1
            local base = -600000 - __nextAnimTrackId * 4
            return setmetatable({}, { __index = {
                Play = function() end, Stop = function() end, Pause = function() end,
                AdjustSpeed = function() end, AdjustWeight = function() end,
                GetMarkerReachedSignal = function(self2, name) return makeEvent(base, "Event") end,
                KeyframeReached = makeEvent(base - 1, "Event"),
                Ended = makeEvent(base - 2, "Event"),
                Stopped = makeEvent(base - 3, "Event"),
                Length = 0, TimePosition = 0, Looped = false, Priority = nil, Speed = 1, IsPlaying = false,
            } })
        end
    end
    if k == "Destroy" or k == "remove" or k == "Remove" then
        return function(self) __destroy(ref) end
    end
    if k == "Clone" or k == "clone" then
        -- Настоящая копия — новый виртуальный инстанс (свой ref), с тем же
        -- классом/именем/позицией, не запараентенный никуда (как и в
        -- реальном Roblox — Clone() отвязан от дерева, пока сам скрипт не
        -- выставит .Parent). Для virtual-инстансов (Instance.new()) вместе
        -- с этим копируются и все произвольные свойства из
        -- virtualInstanceProps — см. __clone на стороне JS.
        return function(self)
            local newRef = __clone(ref)
            return wrap(newRef)
        end
    end
    if k == "GetFullName" or k == "getFullName" then
        return function(self) return __get_name(ref) end
    end
    if k == "ClearAllChildren" then
        return function(self)
            local n = __child_count(ref)
            for i = n, 1, -1 do
                local c = __child_at(ref, i - 1)
                if c ~= -1 then __destroy(c) end
            end
        end
    end
    -- Сигналы: RemoteEvent.OnServerEvent/OnClientEvent, TextButton.
    -- MouseButton1Click, и общая физика/иерархия/жизненный цикл — у всех
    -- один и тот же настоящий RBXScriptSignal (:Connect/:Disconnect,
    -- см. makeEvent/__connect/fireLuaSignal), НЕ заглушка: ChildAdded/
    -- ChildRemoved реально стреляют при репарентинге (см. luaSetParent),
    -- Touched — при настоящем контакте в cannon.js (см. beginContact),
    -- Stepped/Heartbeat/RenderStepped — каждый кадр игрового цикла.
    -- Selected/Deselected/PlayerAdded/PlayerRemoving/Chatted/Died —
    -- честные RBXScriptSignal (Connect не падает), но по-настоящему НЕ
    -- срабатывают: нет системы выбора HopperBin/чата/смерти персонажа,
    -- которая могла бы их вызвать. Это реальное ограничение движка, а не
    -- сознательная заглушка "на будущее" — сигнал существует, событие в
    -- игре просто ещё не происходит.
    if k == "OnServerEvent" or k == "OnClientEvent" or k == "MouseClick" or k == "RightMouseClick"
        or k == "MouseHoverEnter" or k == "MouseHoverLeave" or k == "MouseButton1Click"
        or k == "MouseButton1Down" or k == "MouseButton1Up" or k == "MouseEnter" or k == "MouseLeave"
        or k == "InputBegan" or k == "InputEnded" or k == "InputChanged" or k == "LastInputTypeChanged"
        or k == "TouchPan" or k == "TouchPinch" or k == "TouchTap" or k == "TouchTapInWorld" or k == "TouchLongPress"
        or k == "TouchRotate" or k == "TouchSwipe" or k == "TouchStarted" or k == "TouchMoved" or k == "TouchEnded"
        or k == "FocusLost" or k == "Focused"
        or k == "ChildAdded" or k == "ChildRemoved" or k == "DescendantAdded" or k == "DescendantRemoving"
        or k == "Touched" or k == "TouchEnded"
        or k == "Changed" or k == "PropertyChangedSignal"
        or k == "Equipped" or k == "Unequipped" or k == "Selected" or k == "Deselected"
        or k == "Activated" or k == "Deactivated"
        or k == "PlayerAdded" or k == "PlayerRemoving" or k == "Chatted" or k == "Died"
        or k == "CharacterAdded" or k == "CharacterRemoving"
        or k == "FlagCaptured"
        or k == "Ended" or k == "DidLoop" or k == "Loaded"
        or k == "Event" or k == "Stepped" or k == "Heartbeat" or k == "RenderStepped" then
        return makeEvent(ref, k)
    end
    -- Sound:Play()/:play() (и Pause/Resume/Stop, все регистры — старые
    -- скрипты 2008-2011 годов зовут их с маленькой буквы). Раньше это
    -- было no-op ВСЕГДА ("у движка нет реального аудио-плеера") — теперь
    -- для настоящего Sound-инстанса реально играет через __sound_control
    -- (JS поднимает под каждым Sound-рефом настоящий HTMLAudioElement,
    -- см. getOrCreateSoundEl/luaSoundControl). Для прочих классов
    -- (AnimationTrack и т.п., см. LoadAnimation чуть выше) по-прежнему
    -- no-op — там реально нечему играть.
    if k == "Play" or k == "play" or k == "Stop" or k == "stop"
        or k == "Pause" or k == "pause" or k == "Resume" or k == "resume" then
        if __get_class(ref) == "Sound" then
            local action = (k == "Play" or k == "play") and "play"
                or (k == "Stop" or k == "stop") and "stop"
                or (k == "Pause" or k == "pause") and "pause"
                or "resume"
            return function(self, ...) __sound_control(ref, action) end
        end
        return function(self, ...) end
    end
    if k == "Fire" then
        -- BindableEvent:Fire(...) — генерирует .Event тут же, синхронно,
        -- в пределах ОДНОЙ и той же VM (в отличие от FireServer/FireClient,
        -- которые идут через межпроцессную очередь remoteQueue).
        return function(self, ...) __fire_bindable(ref, ...) end
    end
    if k == "FireServer" then
        return function(self, ...) __fire_remote(ref, "server", ...) end
    end
    -- Camera: ViewportSize / FieldOfView (живое значение) / WorldToViewportPoint / ViewportPointToRay
    if k == "ViewportSize" or k == "FieldOfView" or k == "WorldToViewportPoint" or k == "WorldToScreenPoint"
        or k == "ViewportPointToRay" or k == "ScreenPointToRay" then
        if __get_class(ref) == "Camera" then
            if k == "ViewportSize" then
                local w, h = __cam_info()
                return Vector2.new(w, h)
            elseif k == "FieldOfView" then
                local _, _, f = __cam_info()
                return f
            elseif k == "WorldToViewportPoint" or k == "WorldToScreenPoint" then
                return function(self, pos)
                    local x, y, d, on = __cam_project(pos.X, pos.Y, pos.Z)
                    return Vector3.new(x, y, d), on
                end
            else
                return function(self, x, y, depth)
                    local ox, oy, oz, dx, dy, dz = __cam_ray(x, y)
                    local o, dir = Vector3.new(ox, oy, oz), Vector3.new(dx, dy, dz)
                    return { Origin = o, Direction = dir * (depth and depth > 0 and depth or 1) }
                end
            end
        end
    end
    if k == "FireClient" then
        -- первый аргумент — Player, у нас всегда ровно один
        -- (LocalPlayer) — просто отбрасываем его.
        return function(self, player, ...) __fire_remote(ref, "client", ...) end
    end
    local ok, v = pcall(__get_prop, ref, k)
    if not ok then
        __emuWarnOnce("getprop:" .. tostring(__get_class(ref)) .. "." .. tostring(k),
            tostring(__get_class(ref)) .. "." .. tostring(k) .. " — ошибка чтения свойства: " .. tostring(v))
    end
    -- Свойства-перечисления JS хранит строкой ('Scriptable'), а скрипты сравнивают
    -- их с Enum-значениями: camera.CameraType == Enum.CameraType.Scriptable.
    -- Строка никогда не равна таблице-Enum, из-за чего такое условие всегда было
    -- ложным (например, камера после выхода из шкафа навсегда оставалась Scriptable).
    local enumType = __ENUM_PROPS[k]
    if enumType then
        if ok and type(v) == "string" then return Enum[enumType][v] end
        if (not ok or v == nil) and k == "CameraType" and __get_class(ref) == "Camera" then
            return Enum.CameraType.Custom -- значение по умолчанию у камеры в Roblox
        end
    end
    if ok and v ~= nil then return v end
    -- Roblox поддерживает доступ к дочернему объекту прямо через точку —
    -- part.Engine эквивалентно part:FindFirstChild("Engine"), а не только
    -- через явный вызов FindFirstChild. Раньше это падало в __get_prop
    -- (тот про ДАННЫЕ properties, не про детей) и там же тихо давало nil,
    -- хотя ребёнок с таким именем на самом деле есть — отсюда "field
    -- 'Engine'"/"field 'Parts'"/"field 'Weapon'" на объектах, которые
    -- реально существуют в файле карты.
    local child = __find_first_child(ref, k)
    if child ~= nil and child ~= -1 then return wrap(child) end
    -- Ни свойства, ни потомка с таким именем: в Roblox это ошибка "X is not a valid member of Class". Эмулятор
    -- отдавал молча nil — теперь говорим об этом (один раз на Класс.Имя), чтобы было видно, чего не хватает.
    local cls = tostring(__get_class(ref))
    if cls == "Tool" then
        -- значения по умолчанию Tool (Enabled, TextureId, ToolTip, ...): раньше nil + предупреждение, а хотбар читает tool.Enabled
        local d = __TOOL_DEFAULTS[k]
        if d ~= nil then return d end
    end
    __emuWarnOnce("missing:" .. cls .. "." .. tostring(k),
        tostring(k) .. " — не свойство и не потомок " .. tostring(__get_name(ref)) .. " (" .. cls ..
        "); эмулятор вернул nil (в Roblox: 'is not a valid member', либо этого свойства нет в эмуляторе)")
    return nil
end
InstanceMT.__newindex = function(t, k, v)
    local ref = rawget(t, "__ref")
    if k == "Position" then
        if __is_gui_ref(ref) then
            __set_prop(ref, k, v)
        else
            __set_position(ref, v.X, v.Y, v.Z)
        end
        return
    end
    if k == "Parent" then
        __set_parent(ref, v and rawget(v, "__ref") or -1)
        return
    end
    __set_prop(ref, k, v)
end
InstanceMT.__tostring = function(t) return __get_name(rawget(t, "__ref")) end

-- Instance.new(className [, parent]) — создаёт НОВЫЙ виртуальный инстанс
-- (свой отрицательный ref, ниже -1, не пересекается с реальными объектами
-- карты). У него нет меша/физики — это просто узел иерархии с именем,
-- классом и набором произвольных свойств (см. __instance_new/luaGetGenericProp
-- на стороне JS). Для классов без визуального смысла в этом движке (Message,
-- IntValue, Sound и т.п.) этого достаточно, чтобы скрипт не падал.
Instance = {}
function Instance.new(className, parent)
    local ref = __instance_new(className)
    local inst = wrap(ref)
    if parent then inst.Parent = parent end
    return inst
end

workspace = wrap(__workspace_ref())
Workspace = workspace -- в Roblox есть оба глобала

-- game.Players / game.Lighting / game:GetService(...) / game:service(...)
-- (последнее — устаревший, но часто встречающийся в старых скриптах,
-- 2008-2011 годов, вызов) — сначала ищем РЕАЛЬНЫЙ сервис среди корневых
-- объектов карты, и только если такого нет — создаём виртуальный контейнер
-- (пустой, но не роняющий скрипт).
local serviceCache = {}
-- DataStoreService — раньше не была особым случаем: game:GetService(...)
-- создавал ПУСТОЙ виртуальный инстанс без единого метода, отсюда "attempt
-- to call a nil value (method 'GetDataStore')". Настоящего сетевого
-- DataStore тут быть не может (это браузер, а не сервер Roblox) — вместо
-- этого простое ин-memory хранилище: живёт, пока идёт Play, обнуляется по
-- Stop/Play заново (см. luaResetSignals/serviceCache — этот файл вообще не
-- хранит состояние между запусками, так что это ограничение как минимум
-- честное, а не притворяется настоящей персистентностью).
local __dataStores = {}
local DataStoreMT = { __index = {
    GetAsync = function(self, key) return self.__data[key] end,
    SetAsync = function(self, key, value) self.__data[key] = value end,
    UpdateAsync = function(self, key, fn)
        local new = fn(self.__data[key])
        self.__data[key] = new
        return new
    end,
    IncrementAsync = function(self, key, delta)
        delta = delta or 1
        local v = (self.__data[key] or 0) + delta
        self.__data[key] = v
        return v
    end,
    RemoveAsync = function(self, key)
        local v = self.__data[key]
        self.__data[key] = nil
        return v
    end,
    GetSortedAsync = function(self) return { GetCurrentPage = function() return {} end } end,
} }
local function getDataStore(name)
    if not __dataStores[name] then
        __dataStores[name] = setmetatable({ __name = name, __data = {} }, DataStoreMT)
    end
    return __dataStores[name]
end
local DataStoreServiceObj = setmetatable({}, { __index = {
    GetDataStore = function(self, name) return getDataStore(name) end,
    GetOrderedDataStore = function(self, name) return getDataStore(name) end,
} })
-- ContentProvider:PreloadAsync — раньше отсутствовал вообще (виртуальный
-- пустой сервис без единого метода), из-за чего LoadingScreenScript падал
-- бы прямо внутри task.defer(...). Там ошибку ловит сам task.spawn (см.
-- реализацию task выше) и не роняет остальной скрипт — но и не продолжает
-- его: код ПОСЛЕ PreloadAsync (снятие текста "Готово!", fade-out,
-- loadingGui:Destroy()) просто никогда не выполнялся, и экран загрузки
-- оставался висеть навсегда, закрывая собой всё, что должно было
-- появиться под ним. Тут реальных ассетов не грузим (взять их неоткуда
-- в браузере) — сразу отвечаем Success по каждому.
local ContentProviderObj = setmetatable({}, { __index = {
    PreloadAsync = function(self, assets, callback)
        for _, assetId in ipairs(assets or {}) do
            if callback then callback(assetId, Enum.AssetFetchStatus.Success) end
        end
    end,
    GetAssetFetchStatus = function(self, assetId) return Enum.AssetFetchStatus.Success end,
} })
-- HttpService:JSONEncode/JSONDecode — реально используются (SongMenuScript,
-- Main.lua) для разбора чартов песен, оба ЗАВЁРНУТЫ в pcall у авторов
-- скрипта — поэтому раньше, когда HttpService был пустым виртуальным
-- сервисом без единого метода, ошибка "attempt to call a nil value" НЕ
-- падала наружу, а тихо ловилась pcall'ом и просто пропускала песню
-- ("if not ok2 then continue end") — список песен оставался пустым без
-- единой видимой ошибки в Output. GetAsync/PostAsync честно рушатся —
-- настоящих сетевых запросов из браузерной песочницы наружу нет и не
-- будет, тут врать нечем.
local HttpServiceObj = setmetatable({}, { __index = {
    JSONEncode = function(self, v) return __json_encode(v) end,
    JSONDecode = function(self, s) return __json_decode(s) end,
    UrlEncode = function(self, s) return tostring(s) end,
    GetAsync = function(self, url) error("HttpService:GetAsync — реальных сетевых запросов из браузерной песочницы нет", 2) end,
    PostAsync = function(self, url) error("HttpService:PostAsync — реальных сетевых запросов из браузерной песочницы нет", 2) end,
} })
-- TweenService:Create(...):Play() — раньше TweenService был пустым
-- виртуальным сервисом без единого метода: "attempt to call a nil value
-- (method 'Create')" на любом месте, где он используется (а используется
-- он массово — очки в Main.lua, уведомления в SettingsMenuScript, блюр в
-- AgeWarningModule). Само число-в-число покадровое движение — на JS-
-- стороне (см. updateTweens/__tween_register), тут только конструкция
-- объекта Tween с Play/Cancel/Pause и событием Completed.
local __nextTweenId = 1
local function __enumName(e) if type(e) == "table" then return tostring(e.Name or e) end return tostring(e or "") end
local function __ease(a, style, dir)
    style, dir = __enumName(style), __enumName(dir)
    if string.find(style, "Linear", 1, true) then return a end
    if string.find(style, "Sine", 1, true) then
        if string.find(dir, "InOut", 1, true) then return -(math.cos(math.pi * a) - 1) / 2 end
        if string.find(dir, "Out", 1, true) then return math.sin(a * math.pi / 2) end
        return 1 - math.cos(a * math.pi / 2)
    end
    local pw = 2
    if string.find(style, "Cubic", 1, true) then pw = 3 elseif string.find(style, "Quart", 1, true) then pw = 4
    elseif string.find(style, "Quint", 1, true) then pw = 5 end
    if string.find(dir, "InOut", 1, true) then
        if a < 0.5 then return (2 ^ (pw - 1)) * a ^ pw end
        return 1 - ((-2 * a + 2) ^ pw) / 2
    end
    if string.find(dir, "Out", 1, true) then return 1 - (1 - a) ^ pw end
    return a ^ pw
end
local TweenMT = { __index = {
    Play = function(self)
        local cls = __get_class(self.__ref)
        -- CFrameValue/Vector3Value/Color3Value хранят Value в Lua (JS-твин их не двигает): интерполируем тут, шаг за шагом
        -- присваивая Value — так срабатывают GetPropertyChangedSignal("Value")/Changed (DoorOpener: CFrameValue -> PivotTo).
        if (cls == "CFrameValue" or cls == "Vector3Value" or cls == "Color3Value") and self.__props.Value ~= nil then
            local token = {}
            self.__running = token
            task.spawn(function()
                local inst = __wrap(self.__ref)
                local from, target = inst.Value, self.__props.Value
                local dur, t0 = math.max(self.__time or 0, 0), os.clock()
                while self.__running == token do
                    local a = dur > 0 and math.min((os.clock() - t0) / dur, 1) or 1
                    local e = __ease(a, self.__style, self.__dir)
                    local okv, val = pcall(function() return from:Lerp(target, e) end)
                    inst.Value = (okv and val) or (a >= 1 and target) or from
                    if a >= 1 then break end
                    task.wait()
                end
                if self.__running == token then
                    self.__running = nil
                    __fire_signal(self.__completedKey, "Event")
                end
            end)
            return
        end
        for name, target in pairs(self.__props) do
            __tween_register(self.__completedKey, self.__ref, name, target, self.__time)
        end
    end,
    Pause = function(self) end, -- честной паузы нет — покадровый твин на JS-стороне идёт по времени, а не по кадрам
    Cancel = function(self) self.__running = nil end, -- для Value-твинов (Lua) отмена честная; JS-твины остановить пока нельзя
} }
local TweenServiceObj = setmetatable({}, { __index = {
    Create = function(self, instance, tweenInfo, props)
        -- как в Roblox: nil вместо инстанса — ошибка ВЫЗЫВАЮЩЕГО скрипта (уровень 2 показывает его строку, а не прелюдию)
        if type(instance) ~= "table" or rawget(instance, "__ref") == nil then
            error("TweenService:Create: первый аргумент должен быть Instance, получено " .. typeof(instance), 2)
        end
        local id = __nextTweenId
        __nextTweenId = __nextTweenId + 1
        local completedKey = -500000 - id -- отдельный диапазон, не пересекается с обычными ref-ами (см. __tween_register)
        return setmetatable({
            __ref = rawget(instance, "__ref"), __props = props, __time = (tweenInfo and tweenInfo.Time) or 1,
            __completedKey = completedKey, Completed = makeEvent(completedKey, "Event"),
            __style = tweenInfo and tweenInfo.EasingStyle, __dir = tweenInfo and tweenInfo.EasingDirection,
        }, TweenMT)
    end,
} })
TweenInfo = {}
function TweenInfo.new(time, easingStyle, easingDirection, repeatCount, reverses, delayTime)
    return {
        Time = time or 1, EasingStyle = easingStyle, EasingDirection = easingDirection,
        RepeatCount = repeatCount or 0, Reverses = reverses or false, DelayTime = delayTime or 0,
    }
end
-- ============ COMPAT: атрибуты, теги, сигналы, GetPivot и т.п. ============
-- Чисто-Lua простой сигнал (для событий, которых нет на JS-стороне):
-- Connect/Wait/Fire. Wait опрашивает флаг через wait().
local function newSignal()
    local handlers, fired, lastArgs = {}, 0, nil
    local sig = {}
    function sig.Connect(self, fn)
        local h = { fn = fn }
        handlers[#handlers + 1] = h
        return setmetatable({}, { __index = {
            Disconnect = function() h.dead = true end,
            disconnect = function() h.dead = true end,
        } })
    end
    sig.connect = sig.Connect
    function sig.Once(self, fn)
        local conn
        conn = self:Connect(function(...) conn:Disconnect(); fn(...) end)
        return conn
    end
    function sig.Wait(self)
        local start = fired
        while fired == start do wait(0.03) end
        return table.unpack(lastArgs or {})
    end
    sig.wait = sig.Wait
    function sig.__fire(...)
        fired = fired + 1
        lastArgs = { ... }
        for _, h in ipairs(handlers) do
            if not h.dead then
                local ok, err = pcall(h.fn, ...)
                if not ok then warn("ошибка в обработчике: " .. tostring(err)) end
            end
        end
    end
    return sig
end

-- Атрибуты и теги лежат на JS-стороне и ОБЩИЕ для серверной и клиентской
-- Lua-VM (раньше были локальными для каждой VM, и LocalScript не видел
-- SetAttribute из Script).
local __tagAdded, __tagRemoved = {}, {}

local function refOf(inst) return type(inst) == "table" and rawget(inst, "__ref") or nil end

local function attrSignal(ref, name)
    return makeEvent(ref, "__attr_" .. tostring(name))
end

local function addTag(ref, tag)
    if __tag_add(ref, tag) and __tagAdded[tag] then __tagAdded[tag].__fire(wrap(ref)) end
end
local function removeTag(ref, tag)
    if __tag_remove(ref, tag) and __tagRemoved[tag] then __tagRemoved[tag].__fire(wrap(ref)) end
end

local CollectionServiceObj = setmetatable({}, { __index = {
    AddTag = function(self, inst, tag) addTag(refOf(inst), tag) end,
    RemoveTag = function(self, inst, tag) removeTag(refOf(inst), tag) end,
    HasTag = function(self, inst, tag) return __tag_has(refOf(inst), tag) end,
    GetTags = function(self, inst) return __tag_list(refOf(inst)) end,
    GetTagged = function(self, tag)
        local out = {}
        for _, ref in ipairs(__tag_tagged(tag)) do out[#out + 1] = wrap(ref) end
        return out
    end,
    GetInstanceAddedSignal = function(self, tag)
        if not __tagAdded[tag] then __tagAdded[tag] = newSignal() end
        return __tagAdded[tag]
    end,
    GetInstanceRemovedSignal = function(self, tag)
        if not __tagRemoved[tag] then __tagRemoved[tag] = newSignal() end
        return __tagRemoved[tag]
    end,
} })

-- TeleportService: перехода между плейсами в эмуляторе нет (как и в Studio без публикации), поэтому
-- любой запрос на телепорт честно ЗАВЕРШАЕТСЯ ОТКАЗОМ: в Output предупреждение и сигнал
-- TeleportInitFailed(player, Enum.TeleportResult.Failure, сообщение, placeId, options) — скрипты лобби
-- (лифты/матчмейкинг) подписываются на него при старте и раньше падали на "attempt to index a nil value
-- (field 'TeleportInitFailed')", не доходя до остального кода.
local TeleportServiceObj
do
    local initFailed = newSignal()
    local arrived = newSignal()
    local function failure()
        local ok, v = pcall(function() return Enum.TeleportResult.Failure end)
        return ok and v or "Failure"
    end
    local function deny(placeId, players, options)
        local msg = "Teleport недоступен в эмуляторе (placeId " .. tostring(placeId) .. ")"
        warn(msg)
        local list = players
        if type(list) ~= "table" or list.ClassName ~= nil then list = { list } end
        if #list == 0 then list = { game:GetService("Players").LocalPlayer } end
        task.defer(function()
            for _, pl in ipairs(list) do initFailed.__fire(pl, failure(), msg, placeId, options) end
        end)
    end
    TeleportServiceObj = setmetatable({}, { __index = {
        TeleportInitFailed = initFailed,
        LocalPlayerArrivedFromTeleport = arrived,
        Teleport = function(self, placeId, player) deny(placeId, player) end,
        TeleportAsync = function(self, placeId, players, options) deny(placeId, players, options) return nil end,
        TeleportToPlaceInstance = function(self, placeId, instanceId, player) deny(placeId, player) end,
        TeleportToPrivateServer = function(self, placeId, code, players) deny(placeId, players) end,
        TeleportToSpawnByName = function(self, placeId, spawn, player) deny(placeId, player) end,
        TeleportPartyAsync = function(self, placeId, players, teleportData) deny(placeId, players) return "" end,
        ReserveServer = function(self, placeId) return "emu-reserved-" .. tostring(placeId), "emu-private-" .. tostring(placeId) end,
        GetLocalPlayerTeleportData = function(self) return nil end,
        GetArrivingTeleportGui = function(self) return nil end,
        SetTeleportGui = function(self, gui) end,
        GetTeleportSetting = function(self, name) return nil end,
        SetTeleportSetting = function(self, name, value) end,
    } })
end

local function isDescendantOf(ref, ancestor)
    local anc = refOf(ancestor)
    local cur, depth = __get_parent(ref), 0
    while cur ~= nil and cur ~= -1 and depth < 200 do
        if anc ~= nil and cur == anc then return true end
        cur = __get_parent(cur)
        depth = depth + 1
    end
    if ancestor == game then return depth > 0 or __get_parent(ref) ~= -1 end
    return false
end

local COMPAT = {
    -- ParticleEmitter:Emit(n) — выпускает n частиц сразу (см. блок ЧАСТИЦЫ в script.js)
    Emit = function(t, ref) return function(self, count) __particle_emit(ref, tonumber(count) or 1) end end,
    -- Debris:AddItem(item, lifetime) — уничтожить item через lifetime секунд (по умолчанию 10)
    AddItem = function(t, ref) return function(self, item, lifetime)
        if item == nil then return end
        task.delay(tonumber(lifetime) or 10, function()
            if item.Parent ~= nil then item:Destroy() end
        end)
    end end,
    SetAttribute = function(t, ref) return function(self, name, value)
        __attr_set(ref, name, value)
    end end,
    GetAttribute = function(t, ref) return function(self, name)
        return __attr_get(ref, name)
    end end,
    GetAttributes = function(t, ref) return function(self) return __attr_all(ref) end end,
    GetAttributeChangedSignal = function(t, ref) return function(self, name)
        return attrSignal(ref, name)
    end end,
    AddTag = function(t, ref) return function(self, tag) addTag(ref, tag) end end,
    RemoveTag = function(t, ref) return function(self, tag) removeTag(ref, tag) end end,
    HasTag = function(t, ref) return function(self, tag) return __tag_has(ref, tag) end end,
    GetTags = function(t, ref) return function(self) return __tag_list(ref) end end,
    IsDescendantOf = function(t, ref) return function(self, ancestor)
        return isDescendantOf(ref, ancestor)
    end end,
    IsAncestorOf = function(t, ref) return function(self, descendant)
        return isDescendantOf(refOf(descendant), t)
    end end,
    GetPivot = function(t, ref) return function(self)
        return CFrame.new(__get_pivot(ref))
    end end,
    PivotTo = function(t, ref) return function(self, cf)
        cf = __toCFrame(cf)
        -- Если мост (JS) падает — в Output будет настоящая причина, а не голый стек.
        local ok, err = pcall(__set_pivot, ref, cf:GetComponents())
        if not ok then
            error("PivotTo не выполнен: " .. tostring(err) .. " [ref=" .. tostring(ref) .. ", класс=" .. tostring(__get_class(ref)) .. "]", 2)
        end
    end end,
    MoveDirection = function(t, ref) return Vector3.new(__get_move_dir()) end,
    AssemblyLinearVelocity = function(t, ref) return Vector3.new(__get_velocity(ref, 0)) end,
    Velocity = function(t, ref) return Vector3.new(__get_velocity(ref, 0)) end,
    AssemblyAngularVelocity = function(t, ref) return Vector3.new(__get_velocity(ref, 1)) end,
    RotVelocity = function(t, ref) return Vector3.new(__get_velocity(ref, 1)) end,
    GetServerTimeNow = function(t, ref) return function(self) return os.time() end end,
    GetPlayers = function(t, ref) return function(self)
        if __get_class(ref) ~= "Players" then return nil end
        local out = {}
        for _, c in ipairs(t:GetChildren()) do
            if c.ClassName == "Player" then out[#out + 1] = c end
        end
        return out
    end end,
    -- Players:GetPlayerFromCharacter(model) -> Player, чей Character == model (иначе nil)
    GetPlayerFromCharacter = function(t, ref) return function(self, char)
        if char == nil then return nil end
        for _, c in ipairs(t:GetChildren()) do
            if c.ClassName == "Player" and c.Character == char then return c end
        end
        return nil
    end end,
    -- Сигналы Humanoid (Running/Jumping/... стреляют в реальном движке при смене состояния)
    Running = function(t, ref) return makeEvent(ref, "Running") end,
    Jumping = function(t, ref) return makeEvent(ref, "Jumping") end,
    Climbing = function(t, ref) return makeEvent(ref, "Climbing") end,
    GettingUp = function(t, ref) return makeEvent(ref, "GettingUp") end,
    FreeFalling = function(t, ref) return makeEvent(ref, "FreeFalling") end,
    FallingDown = function(t, ref) return makeEvent(ref, "FallingDown") end,
    Seated = function(t, ref) return makeEvent(ref, "Seated") end,
    PlatformStanding = function(t, ref) return makeEvent(ref, "PlatformStanding") end,
    Swimming = function(t, ref) return makeEvent(ref, "Swimming") end,
    StateChanged = function(t, ref) return makeEvent(ref, "StateChanged") end,
    HealthChanged = function(t, ref) return makeEvent(ref, "HealthChanged") end,
    -- Model:GetBoundingBox() -> CFrame центра, Vector3 размер (оси мира, как у модели без PrimaryPart);
    -- для детали — её CFrame и Size.
    GetBoundingBox = function(t, ref) return function(self)
        local cx, cy, cz, sx, sy, sz, r00, r01, r02, r10, r11, r12, r20, r21, r22 = __get_bbox(ref)
        return CFrame.new(cx, cy, cz, r00, r01, r02, r10, r11, r12, r20, r21, r22), Vector3.new(sx, sy, sz)
    end end,
    GetExtentsSize = function(t, ref) return function(self)
        local _, _, _, sx, sy, sz = __get_bbox(ref)
        return Vector3.new(sx, sy, sz)
    end end,
    TakeDamage = function(t, ref) return function(self, amount)
        local ok, hp = pcall(__get_prop, ref, "Health")
        if ok and type(hp) == "number" then __set_prop(ref, "Health", hp - amount) end
    end end,
    -- Сигналы ProximityPrompt и жизненного цикла: Triggered реально
    -- стреляет с JS-стороны (см. updateProximityPrompts), остальные —
    -- честные RBXScriptSignal без срабатывания.
    Triggered = function(t, ref) return makeEvent(ref, "Triggered") end,
    TriggerEnded = function(t, ref) return makeEvent(ref, "TriggerEnded") end,
    PromptTriggered = function(t, ref) return makeEvent(ref, "PromptTriggered") end,
    PromptTriggerEnded = function(t, ref) return makeEvent(ref, "PromptTriggerEnded") end,
    -- prompt:InputHoldBegin()/InputHoldEnd() — программное «нажатие» (кастомный UI зовёт их сам)
    InputHoldBegin = function(t, ref) return function(self) __prompt_input(ref, true) end end,
    InputHoldEnd = function(t, ref) return function(self) __prompt_input(ref, false) end end,
    PromptShown = function(t, ref) return makeEvent(ref, "PromptShown") end,
    PromptHidden = function(t, ref) return makeEvent(ref, "PromptHidden") end,
    PromptButtonHoldBegan = function(t, ref) return makeEvent(ref, "PromptButtonHoldBegan") end,
    PromptButtonHoldEnded = function(t, ref) return makeEvent(ref, "PromptButtonHoldEnded") end,
    AncestryChanged = function(t, ref) return makeEvent(ref, "AncestryChanged") end,
    Destroying = function(t, ref) return makeEvent(ref, "Destroying") end,
}
-- Принимает CFrame-объект ИЛИ «голую» таблицу с X/Y/Z (и R00..R22) —
-- например, Value у CFrameValue из .rbxm может прийти без метатаблицы.
function __toCFrame(v)
    if type(v) ~= "table" then
        error("PivotTo/CFrame ожидает CFrame, получено " .. type(v), 3)
    end
    if v.GetComponents ~= nil then return v end
    local p = rawget(v, "Position") or v
    local x, y, z = rawget(v, "X") or rawget(p, "X") or 0, rawget(v, "Y") or rawget(p, "Y") or 0, rawget(v, "Z") or rawget(p, "Z") or 0
    if rawget(v, "R00") ~= nil then
        return CFrame.new(x, y, z, v.R00, v.R01, v.R02, v.R10, v.R11, v.R12, v.R20, v.R21, v.R22)
    end
    return CFrame.new(x, y, z)
end
local __tblVals = {}   -- Value-свойства, хранящие таблицы (CFrameValue/Vector3Value/ObjectValue)
-- Начальные Value из файла (Vector3Value/CFrameValue/Color3Value/ObjectValue) — вызывается из JS после prelude
function __init_value(ref, kind, a, b, c, ...)
    if kind == "v3" then __tblVals[ref] = Vector3.new(a, b, c)
    elseif kind == "cf" then __tblVals[ref] = CFrame.new(a, b, c, ...)
    elseif kind == "c3" then __tblVals[ref] = Color3.new(a, b, c)
    elseif kind == "ref" then __tblVals[ref] = __wrap(a)
    end
end
local COMPAT_PROPS = {
    AssemblyLinearVelocity = true, Velocity = true, AssemblyAngularVelocity = true, RotVelocity = true,
}
do
local PURE_METHODS = { IsA = true, isA = true, FindFirstChild = true, findFirstChild = true,
    FindFirstChildOfClass = true, FindFirstChildWhichIsA = true, GetChildren = true, getChildren = true,
    GetDescendants = true, getDescendants = true }
    local baseIndex = InstanceMT.__index
    InstanceMT.__index = function(t, k)
        local ref = rawget(t, "__ref")
        -- ContextActionService: BindAction & co. Без него хотбар (SETTINGS:500) падал «attempt to call a nil value (method 'BindAction')».
        -- Действия вызываются по клавишам из UserInputService.InputBegan/InputEnded (Begin/End); touch-кнопки не рисуем.
        if __get_class(ref) == "ContextActionService" then
            local f = __CAS_METHODS[k]
            if f then return f end
        end
        -- PlayerGui:GetGuiObjectsAtPosition(x, y) — GuiObject-ы под точкой (сверху вниз), по реальному DOM
        if k == "GetGuiObjectsAtPosition" and __get_class(ref) == "PlayerGui" then
            return function(self, x, y)
                local t = {}
                for id in string.gmatch(__gui_at_pos(x or 0, y or 0), "[^,]+") do t[#t + 1] = wrap(tonumber(id)) end
                return t
            end
        end
        if k == "EquipTool" and __get_class(ref) == "Humanoid" then
            return function(self, tool)
                local ch = self.Parent
                local pl = game:GetService("Players").LocalPlayer
                if not (ch and tool) then return end
                for _, c in ipairs(ch:GetChildren()) do
                    if c ~= tool and c:IsA("Tool") then c.Parent = pl.Backpack end
                end
                tool.Parent = ch
            end
        end
        if k == "UnequipTools" and __get_class(ref) == "Humanoid" then
            return function(self)
                local ch = self.Parent
                local pl = game:GetService("Players").LocalPlayer
                if not ch then return end
                for _, c in ipairs(ch:GetChildren()) do
                    if c:IsA("Tool") then c.Parent = pl.Backpack end
                end
            end
        end
        if k == "IsKeyDown" and __get_class(ref) == "UserInputService" then
            return function(self, kc) return kc ~= nil and __is_key_down(kc.Name) end
        end
        if k == "GetKeysPressed" and __get_class(ref) == "UserInputService" then
            return function(self)
                local out = {}
                for name in string.gmatch(__keys_down(), "[^,]+") do
                    out[#out + 1] = { KeyCode = Enum.KeyCode[name], UserInputType = Enum.UserInputType.Keyboard,
                                      UserInputState = Enum.UserInputState.Begin }
                end
                return out
            end
        end
        -- UserInputService:GetStringForKeyCode(Enum.KeyCode.E) -> "E" (раскладка клиента не известна — отдаём имя клавиши)
        if k == "GetStringForKeyCode" and __get_class(ref) == "UserInputService" then
            return function(self, kc)
                if kc == nil then return "" end
                local nm = kc.Name
                if #nm == 1 then return nm end
                return ({ Zero="0", One="1", Two="2", Three="3", Four="4", Five="5", Six="6", Seven="7", Eight="8", Nine="9" })[nm] or ""
            end
        end
        -- ProximityPrompt.KeyboardKeyCode / GamepadKeyCode — EnumItem (Enum.KeyCode.E), а не голое число из файла
        if (k == "KeyboardKeyCode" or k == "GamepadKeyCode") and __get_class(ref) == "ProximityPrompt" then
            local ok, n = pcall(__get_prop, ref, k)
            if not ok or n == nil then n = (k == "KeyboardKeyCode") and 101 or 1000 end   -- значения по умолчанию из Roblox: E / ButtonX
            if type(n) == "string" then return Enum.KeyCode[n] end
            if type(n) == "number" then
                local nm
                if n >= 97 and n <= 122 then nm = string.upper(string.char(n))
                elseif n >= 65 and n <= 90 then nm = string.char(n)
                else nm = ({ [32]="Space", [13]="Return", [9]="Tab", [1000]="ButtonX", [1001]="ButtonY", [1002]="ButtonA", [1003]="ButtonB" })[n] or "Unknown" end
                return Enum.KeyCode[nm]
            end
        end
        -- UserInputService:GetLastInputType() — InputCategorizer (Blaster) спрашивает тип последнего ввода при старте
        if k == "GetLastInputType" and __get_class(ref) == "UserInputService" then
            return function(self)
                if __is_touch() then return Enum.UserInputType.Touch end
                return Enum.UserInputType.Keyboard
            end
        end
        if (k == "TouchEnabled" or k == "KeyboardEnabled" or k == "MouseEnabled" or k == "GamepadEnabled")
            and __get_class(ref) == "UserInputService" then
            local touch = __is_touch()
            if k == "TouchEnabled" then return touch end
            if k == "GamepadEnabled" then return false end
            return not touch   -- Keyboard/Mouse: только когда нет сенсорного экрана
        end
        if k == "Value" then
            local v = __tblVals[ref]
            if v ~= nil then return v end
        elseif (k == "Rotation" or k == "Orientation") and not __is_gui_ref(ref) then
            local cf = CFrame.new(__get_cframe(ref))
            local rx, ry, rz = cf:ToOrientation()
            return Vector3.new(math.deg(rx), math.deg(ry), math.deg(rz))
        end
        if k == "Part0" or k == "Part1" or k == "Attachment0" or k == "Attachment1" or k == "PrimaryPart" then
            local rr = __refprop_get(ref, k)
            if rr ~= nil then
                if rr == -1 then return nil end   -- -1 = nil; у клонов ref тоже отрицательные (виртуальные)
                return wrap(rr)
            end
        end
        if (k == "Position" or k == "CFrame" or k == "WorldPosition" or k == "WorldCFrame") and __get_class(ref) == "Attachment" then
            local x, y, z, r00, r01, r02, r10, r11, r12, r20, r21, r22 = __att_get(ref)
            if x then
                if k == "Position" then return Vector3.new(x, y, z) end
                local cf = CFrame.new(x, y, z, r00, r01, r02, r10, r11, r12, r20, r21, r22)
                if k == "CFrame" then return cf end
                local par = t.Parent
                local pcf = par and par.CFrame
                if pcf then
                    local w = pcf * cf
                    if k == "WorldCFrame" then return w end
                    return w.Position
                end
                return nil
            end
        end
        if k == "Color" and not __is_gui_ref(ref) then
            local r, g, b = __get_color(ref)
            if r then return Color3.new(r, g, b) end
        end
        if k == "BrickColor" and not __is_gui_ref(ref) then
            local r, g, b = __get_color(ref)
            if r then return BrickColor.new(Color3.new(r, g, b)) end
        end
        local h = COMPAT[k]
        if h then
            if COMPAT_PROPS[k] then return h(t, ref) end
            return h(t, ref)
        end
        local r = baseIndex(t, k)
        -- Методы, возвращающие замыкание, зависящее ТОЛЬКО от ref, кешируем прямо в обёртке: иначе каждый
        -- d:IsA(...) / part:FindFirstChild(...) заново идёт через сотни сравнений в __index (в циклах по
        -- GetDescendants() это основная причина просадки FPS).
        if PURE_METHODS[k] and type(r) == "function" then rawset(t, k, r) end
        return r
    end
    local baseNew = InstanceMT.__newindex
    InstanceMT.__newindex = function(t, k, v)
        local ref = rawget(t, "__ref")
        if (k == "Part0" or k == "Part1" or k == "Attachment0" or k == "Attachment1") and (v == nil or (type(v) == "table" and rawget(v, "__ref") ~= nil)) then
            local cls0 = __get_class(ref)
            if cls0 == "RigidConstraint" or cls0 == "WeldConstraint" or cls0 == "Weld" or cls0 == "ManualWeld" or cls0 == "Motor6D" or cls0 == "Motor"
               or cls0 == "BallSocketConstraint" or cls0 == "NoCollisionConstraint" or cls0 == "AnimationConstraint" then
                __refprop_set(ref, k, v == nil and -1 or rawget(v, "__ref"))
                return
            end
        end
        if k == "PrimaryPart" and (v == nil or (type(v) == "table" and rawget(v, "__ref") ~= nil)) then
            __refprop_set(ref, k, v == nil and -1 or rawget(v, "__ref"))
            return
        end
        if type(v) == "table" then
            if k == "Position" and rawget(v, "X") ~= nil and __get_class(ref) == "Attachment" then
                __att_set(ref, v.X, v.Y, v.Z)
                return
            elseif k == "CFrame" and rawget(v, "R00") ~= nil and __get_class(ref) == "Attachment" then
                __att_set_cf(ref, v:GetComponents())
                return
            end
            if k == "Size" and type(rawget(v, "X")) == "number" and type(rawget(v, "Z")) == "number" and not __is_gui_ref(ref) then
                __set_size(ref, v.X, v.Y, v.Z)
                return
            elseif k == "BrickColor" and rawget(v, "Number") ~= nil and rawget(v, "Color") ~= nil then
                return baseNew(t, "Color", v.Color)
            elseif k == "Value" then
                __tblVals[ref] = v
                -- GetPropertyChangedSignal("Value") / Changed: без этого CFrameValue+PivotTo (двери, лифты) не двигали модель
                __fire_signal(ref, "__prop_Value")
                __fire_signal(ref, "Changed")
                return
            elseif k == "WorldPivot" and rawget(v, "R00") ~= nil then
                __set_world_pivot(ref, v:GetComponents())
                return
            elseif k == "CFrame" and rawget(v, "R00") ~= nil then
                __set_cframe(ref, v:GetComponents())
                return
            elseif (k == "Rotation" or k == "Orientation") and not __is_gui_ref(ref) and rawget(v, "R00") == nil then
                local x, y, z = __get_position(ref)
                local cf = CFrame.new(x, y, z) * CFrame.fromOrientation(math.rad(v.X), math.rad(v.Y), math.rad(v.Z))
                __set_cframe(ref, cf:GetComponents())
                return
            elseif k == "AssemblyLinearVelocity" or k == "Velocity" then
                __set_velocity(ref, 0, v.X, v.Y, v.Z)
                return
            elseif k == "AssemblyAngularVelocity" or k == "RotVelocity" then
                __set_velocity(ref, 1, v.X, v.Y, v.Z)
                return
            end
        end
        return baseNew(t, k, v)
    end
end

local function getService(name)
    if serviceCache[name] then return serviceCache[name] end
    if name == "DataStoreService" then
        serviceCache[name] = DataStoreServiceObj
        return DataStoreServiceObj
    end
    if name == "ContentProvider" then
        serviceCache[name] = ContentProviderObj
        return ContentProviderObj
    end
    if name == "HttpService" then
        serviceCache[name] = HttpServiceObj
        return HttpServiceObj
    end
    if name == "TweenService" then
        serviceCache[name] = TweenServiceObj
        return TweenServiceObj
    end
    if name == "CollectionService" then
        serviceCache[name] = CollectionServiceObj
        return CollectionServiceObj
    end
    if name == "TeleportService" then
        serviceCache[name] = TeleportServiceObj
        return TeleportServiceObj
    end
    local ref = __find_service(name)
    if ref == -1 then ref = __instance_new(name) end
    local inst = wrap(ref)
    serviceCache[name] = inst
    return inst
end
game = setmetatable({}, {
    __index = function(t, k)
        if k == "GetService" or k == "getService" or k == "service" then
            return function(self, name) return getService(name) end
        end
        if k == "Name" then return "game" end
        if k == "ClassName" or k == "className" then return "DataModel" end
        -- game сам по себе — как обычный Instance с детьми-сервисами
        -- (Workspace/Players/...), только эти дети лежат не в
        -- luaChildrenByRef (у него родитель -1, туда не попадает — см.
        -- __root_count/__root_at), а собираются отдельно. Раньше ничего
        -- этого не было: game:GetDescendants() уходило в общий "else"
        -- (getService("GetDescendants")) и создавало виртуальный инстанс с
        -- таким именем — тот факт, что он ТАБЛИЦА, а не функция, и давал
        -- "attempt to call a table value".
        if k == "GetChildren" or k == "getChildren" then
            return function(self)
                local n = __root_count()
                local out = {}
                for i = 1, n do out[i] = wrap(__root_at(i - 1)) end
                return out
            end
        end
        if k == "GetDescendants" or k == "getDescendants" then
            return function(self)
                local out = {}
                local function walk(r)
                    local n = __child_count(r)
                    for i = 1, n do
                        local c = __child_at(r, i - 1)
                        out[#out + 1] = wrap(c)
                        walk(c)
                    end
                end
                local n = __root_count()
                for i = 1, n do
                    local r = __root_at(i - 1)
                    out[#out + 1] = wrap(r)
                    walk(r)
                end
                return out
            end
        end
        if k == "FindFirstChild" or k == "findFirstChild" or k == "WaitForChild" or k == "waitForChild" then
            return function(self, name) return getService(name) end -- у game "дети" верхнего уровня и есть сервисы
        end
        if k == "IsA" or k == "isA" then
            return function(self, cls) return cls == "DataModel" or cls == "Instance" end
        end
        return getService(k)
    end
})

-- require(moduleScriptInstance) — стандартный require() из библиотек Lua
-- (luaL_openlibs) ждёт СТРОКУ (имя модуля на диске) и падает "bad argument
-- #1 to 'require' (string expected, got table)" на настоящем Roblox-коде
-- вида require(ReplicatedStorage.Modules.Foo). Здесь он полностью
-- переопределён под Roblox-семантику: принимает инстанс ModuleScript,
-- компилирует и выполняет его Source РОВНО ОДИН РАЗ (см. __compile_module
-- на стороне JS), кэширует результат по ref и ловит циклический require —
-- всё как единый Lua-модуль, тем же принципом, что и __conns выше.
local __moduleCache = {}
local __moduleHasRun = {}
local __moduleLoading = {}
function require(mod)
    local ref = (type(mod) == "table") and rawget(mod, "__ref") or mod
    if ref == nil then error("require(): ожидается ModuleScript-инстанс", 2) end
    if __moduleHasRun[ref] then return __moduleCache[ref] end
    if __moduleLoading[ref] then
        error("циклический require() — модуль #" .. tostring(ref) .. " уже выполняется", 2)
    end
    local ok, fnOrErr = __compile_module(ref)
    if not ok then error(fnOrErr, 0) end
    __moduleLoading[ref] = true
    local okRun, result = pcall(fnOrErr, wrap(ref))
    __moduleLoading[ref] = nil
    if not okRun then error(result, 0) end
    __moduleHasRun[ref] = true
    __moduleCache[ref] = result
    return result
end

-- task.* (Luau) — старые скрипты почти все на wait()/spawn(), но часть уже
-- написана под новый task-планировщик. Реализован поверх ТЕХ ЖЕ примитивов
-- (wait() и стандартной coroutine — обе честно работают, см. фикс
-- fireLuaSignal/__wait_signal выше), отдельного JS-шедулера не требуется.
-- wait(t) в Roblox возвращает (сколько реально прошло, время игры с запуска) — Animate: "local _, t = wait(0.1)"
local __gameStart = tick()
do
    local __nativeWait = wait
    function wait(t)
        local t0 = tick()
        __nativeWait(t)
        local now = tick()
        return now - t0, now - __gameStart
    end
end
if time == nil then function time() return tick() - __gameStart end end
task = {}
task.wait = function(t) local e = wait(t) return e end
function task.spawn(fn, ...)
    local co = coroutine.create(fn)
    local ok, err = coroutine.resume(co, ...)
    if not ok then warn("ошибка в task.spawn: " .. tostring(err) .. "\\n" .. (debug and debug.traceback and debug.traceback(co) or "")) end
    return co
end
function task.delay(t, fn, ...)
    local args = { ... }
    return task.spawn(function() wait(t); fn(table.unpack(args)) end)
end
task.defer = task.spawn
function task.cancel(co)
    -- Честной отмены "спящей" в luaWaits корутины отсюда не достать (нет
    -- ссылки на её запись в шедулере) — no-op, чтобы не падать хотя бы.
end
`;


        // co -> имя скрипта, которому принадлежит эта корутина — заполняется
        const luaScriptNameByCo = new WeakMap();
        // co -> 'server'/'client'/'shared', заполняется вместе с
        const luaScriptSideByCo = new WeakMap();

        // Разделение Script (сервер) / LocalScript (клиент) / ModuleScript
        const SCRIPT_BADGES = {
            Script: { icon: '🖥️', label: 'Server', color: '#f87171' },
            LocalScript: { icon: '💻', label: 'Client', color: '#60a5fa' },
            ModuleScript: { icon: '📦', label: 'Module', color: '#a3a3a3' },
        };

        function luaArgToDisplay(L, idx) {
            const { lua, lauxlib } = window.fengari;
            const ty = lua.lua_type(L, idx);
            if (ty === lua.LUA_TSTRING) return lua.lua_tojsstring(L, idx);
            if (ty === lua.LUA_TNUMBER) return String(lua.lua_tonumber(L, idx));
            if (ty === lua.LUA_TBOOLEAN) return lua.lua_toboolean(L, idx) ? 'true' : 'false';
            if (ty === lua.LUA_TNIL) return 'nil';
            try {
                lauxlib.luaL_tolstring(L, idx, null);
                const s = lua.lua_tojsstring(L, -1);
                lua.lua_pop(L, 1);
                return s;
            } catch (e) {
                return '<' + (ty === lua.LUA_TTABLE ? 'table' : ty === lua.LUA_TFUNCTION ? 'function' : 'value') + '>';
            }
        }

        function luaTimestamp() {
            const d = new Date();
            const p2 = n => String(n).padStart(2, '0');
            const p3 = n => String(n).padStart(3, '0');
            return p2(d.getHours()) + ':' + p2(d.getMinutes()) + ':' + p2(d.getSeconds()) + '.' + p3(d.getMilliseconds());
        }

        // source — имя скрипта-источника (для print/warn/error) или null для
        let luaLogSessionId = null;
        let _luaOutputRenderTimer = null;
        // «Проглоченные» ошибки и недостающие возможности эмулятора больше не молчат: любое такое событие один раз
        // (на ключ) попадает в Output с пометкой «⚠ эмулятор». Набор ключей живёт в window, чтобы не зависеть от
        // порядка инициализации (emuWarn вызывается и из кода, который выполняется до объявления Output).
        function emuWarn(key, text) {
            const seen = (window._emuWarned = window._emuWarned || new Set());
            if (seen.has(key)) return;
            seen.add(key);
            try { logLuaOutput('warn', '⚠ эмулятор: ' + text); } catch (e) { console.warn('⚠ эмулятор: ' + text); }
        }
        function _errText(e) { return (e && e.message) ? e.message : String(e); }

        function logLuaOutput(level, text, source, trace, sideCls) {
            // Одинаковая ошибка/предупреждение подряд (обработчик события падает КАЖДЫЙ кадр) — не новая строка, а счётчик
            // «×N»: иначе Output забивается сотнями строк, 200 из них пересобираются через innerHTML на каждый кадр
            // (это съедало FPS), а на сервер уходил POST /api/log на каждое повторение.
            const prevLine = luaOutputLines[luaOutputLines.length - 1];
            if ((level === 'error' || level === 'warn') && prevLine && prevLine.level === level
                && prevLine.text === text && prevLine.source === (source || null)) {
                prevLine.count = (prevLine.count || 1) + 1;
                prevLine.time = luaTimestamp();
                if (!_luaOutputRenderTimer) {
                    _luaOutputRenderTimer = setTimeout(() => { _luaOutputRenderTimer = null; renderLuaOutput(); }, 250);
                }
                return;
            }
            luaOutputLines.push({ level, text, source: source || null, trace: trace || null, sideCls: sideCls || null, time: luaTimestamp() });
            if (luaOutputLines.length > 300) luaOutputLines.shift();
            renderLuaOutput();
            (level === 'error' || level === 'warn' ? console.warn : console.log)(
                '[Lua' + (source ? ':' + source : '') + '] ' + text + (trace ? '\n' + trace : '')
            );
            if (luaLogSessionId) {
                fetch('/api/log', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session: luaLogSessionId, time: luaTimestamp(), level,
                        source: source || sideCls || '', text: trace ? text + '\n' + trace : text,
                    }),
                }).catch(() => { /* нет сети/сервера — молча пропускаем, панель Output и так работает */ });
            }
        }

        function clearLuaOutput() {
            luaOutputLines = [];
            renderLuaOutput();
        }

        function renderLuaOutput() {
            const el = document.getElementById('output-content');
            if (!el) return;
            const filterSel = document.getElementById('output-filter');
            const filter = filterSel ? filterSel.value : 'all';
            // filter — 'all' | 'Script' (Server) | 'LocalScript' (Client).
            const lines = filter === 'all' ? luaOutputLines : luaOutputLines.filter(l => !l.sideCls || l.sideCls === filter);
            if (!lines.length) {
                el.innerHTML = '<span style="color:#6b7280;">' + t('no_output') + '</span>';
                return;
            }
            const colors = { error: '#f87171', warn: '#facc15', print: '#e5e7eb' };
            const icons = { error: '⛔', warn: '⚠️', print: '' };
            el.innerHTML = lines.slice(-200).map(l => {
                const sideBadge = SCRIPT_BADGES[l.sideCls];
                const head = '<span style="color:#6b7280">' + l.time + '</span> ' +
                    (sideBadge ? '<span style="color:' + sideBadge.color + '" title="' + sideBadge.label + '">' + sideBadge.icon + '</span> ' : '') +
                    (l.source ? '<span style="color:#60a5fa">[' + esc(l.source) + ']</span> ' : '') +
                    (icons[l.level] || '');
                const trace = l.trace
                    ? '<div style="color:#9ca3af;padding-left:14px;white-space:pre-wrap;">' + esc(l.trace) + '</div>'
                    : '';
                const rep = l.count > 1 ? ' <span style="color:#9ca3af">×' + l.count + '</span>' : '';
                return '<div style="color:' + (colors[l.level] || '#e5e7eb') + ';margin-bottom:2px;">' +
                    head + esc(l.text) + rep + '</div>' + trace;
            }).join('');
            el.scrollTop = el.scrollHeight;
        }


        // ---- Мост к объектам сцены: только числа/строки/булевы, см. коммент выше ----
        // part.Size = Vector3.new(x,y,z): в Roblox меш/деталь растягивается на Size / (прежний размер).
        // Раньше значение просто копилось в «мусорном ящике» свойств и ничего не менялось визуально, а z терялся.
        function luaSetPartSize(ref, nx, ny, nz) {
            nx = Math.max(0.001, Number(nx) || 0); ny = Math.max(0.001, Number(ny) || 0); nz = Math.max(0.001, Number(nz) || 0);
            const old = luaSizeOfRef(ref);
            const known = old && old.x > 0 && old.y > 0 && old.z > 0;
            const mesh = sceneObjs[ref];
            if (mesh && known) {
                if (mesh.userData.partScale0 === undefined) mesh.userData.partScale0 = mesh.userData.partScale ? mesh.userData.partScale.clone() : null;
                const cur = mesh.userData.partScale || new THREE.Vector3(1, 1, 1);
                mesh.userData.partScale = new THREE.Vector3(cur.x * nx / old.x, cur.y * ny / old.y, cur.z * nz / old.z);
                const p0 = new THREE.Vector3(), q0 = new THREE.Quaternion(), s0 = new THREE.Vector3();
                mesh.matrix.decompose(p0, q0, s0);
                mesh.matrix.compose(p0, q0, mesh.userData.partScale);
                mesh.matrixWorldNeedsUpdate = true;
            }
            loadedObjSize[ref] = { x: nx, y: ny, z: nz };
            const body = physicsBodies[ref];
            if (body && body.shapes.length && body.shapes[0] instanceof CANNON.Box && !body.__unionTrimesh) {
                body.shapes[0].halfExtents.set(nx / 2, ny / 2, nz / 2);
                body.shapes[0].updateConvexPolyhedronRepresentation();
                body.updateBoundingRadius();
                body.aabbNeedsUpdate = true;
            }
            fireLuaSignal(ref, '__prop_Size', []);
        }
        function luaSizeOfRef(ref) {
            const p = loadedObjSize[ref];
            if (p && (p.x || p.y || p.z)) return p;
            // Заглушка не найдена (объект грузился не через
            // addPhysicsBodyForObj/addVisualMeshForObj) — считаем реальный
            // размер геометрии меша как запасной вариант.
            const mesh = sceneObjs[ref];
            if (mesh && mesh.geometry) {
                if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
                const bb = mesh.geometry.boundingBox;
                const sc = new THREE.Vector3();
                mesh.matrix.decompose(new THREE.Vector3(), new THREE.Quaternion(), sc);
                return {
                    x: (bb.max.x - bb.min.x) * sc.x,
                    y: (bb.max.y - bb.min.y) * sc.y,
                    z: (bb.max.z - bb.min.z) * sc.z,
                };
            }
            return { x: 0, y: 0, z: 0 };
        }
        function luaPositionOfRef(ref) {
            const body = physicsBodies[ref];
            if (body) return { x: body.position.x, y: body.position.y, z: body.position.z };
            const p = loadedObjPos[ref];
            if (p) return p;
            const mesh = sceneObjs[ref];
            if (mesh) {
                const pos = new THREE.Vector3(), q = new THREE.Quaternion(), sc = new THREE.Vector3();
                mesh.matrix.decompose(pos, q, sc);
                return { x: pos.x, y: pos.y, z: pos.z };
            }
            const tx = luaPartXform[ref];
            if (tx && luaIsPendingClonePart(ref)) return { x: tx.p[0], y: tx.p[1], z: tx.p[2] };
            const dd = luaDormantData(ref);
            if (dd) return { x: dd.px, y: dd.py, z: dd.pz };
            return { x: 0, y: 0, z: 0 };
        }
        function luaSetPositionOfRef(ref, x, y, z) {
            const body = physicsBodies[ref];
            if (body) body.position.set(x, y, z);
            if (loadedObjPos[ref]) loadedObjPos[ref] = { x, y, z };
            const mesh = sceneObjs[ref];
            if (mesh) {
                const pos = new THREE.Vector3(), q = new THREE.Quaternion(), sc = new THREE.Vector3();
                mesh.matrix.decompose(pos, q, sc);
                mesh.matrix.compose(new THREE.Vector3(x, y, z), q, sc);
            }
        }
        // ============ ПОЛНОЦЕННЫЙ CFrame: поворот, GetPivot/PivotTo ============
        // Мировая матрица детали БЕЗ масштаба (THREE.Matrix4, column-major).
        let luaAttrs = {};  // ref -> {имя: значение}  (SetAttribute/GetAttribute)
        let luaTags = {};   // ref -> Set<tag>        (CollectionService)
        // Данные объектов ИЗ ФАЙЛА (с /api/all_instances): атрибуты, теги, команды. luaAttrs/luaTags пересоздаются при
        // каждом запуске Play (luaResetSignals) и засеваются отсюда — раньше GetAttribute по объектам карты давал nil.
        let luaFileAttrs = {}, luaFileTags = {}, luaTeamInfo = {}, luaPlayerTeam = -1;
        let luaFilePivots = {};   // ref модели -> {p:[x,y,z], r:[9 по строкам]} — WorldPivotData из файла
        // Группы столкновений (PhysicsService): имя -> {bit}; Default = бит 1; бит 2 занят «нет столкновений» (CanCollide=false).
        // В cannon тела сталкиваются, если (A.group & B.mask) && (B.group & A.mask): у каждой группы свой бит, а маска —
        // сумма битов групп, с которыми она сталкивается.
        let luaCollGroups = {}, luaNextGroupBit = 4, luaGroupCollide = {}, luaPartGroup = {};
        function luaGroupBit(name) { if (!name || name === 'Default') return 1; const g = luaCollGroups[name]; return g ? g.bit : 1; }
        function luaGroupsCollide(a, b) {
            a = a || 'Default'; b = b || 'Default';
            return luaGroupCollide[a < b ? a + '\u0000' + b : b + '\u0000' + a] !== false;
        }
        function luaMaskFor(name) {
            let m = luaGroupsCollide(name, 'Default') ? 1 : 0;
            for (const n in luaCollGroups) if (luaGroupsCollide(name, n)) m |= luaCollGroups[n].bit;
            return m;
        }
        function luaApplyGroup(body) {
            if (!body || body.__noCollide) return;
            const name = body.__rbxGroup || 'Default';
            body.collisionFilterGroup = luaGroupBit(name);
            body.collisionFilterMask = luaMaskFor(name);
        }
        function luaRefreshAllGroupMasks() {
            for (const b of Object.values(physicsBodies)) luaApplyGroup(b);
            if (charBody) luaApplyGroup(charBody);
        }
        // Маска лучей персонажа (земля, ступеньки, авто-прыжок, тень): только то, с чем он сталкивается, —
        // сквозь форсфилд своей команды луч «земли» не должен упираться.
        function _charRayMask() { return (charBody && charBody.collisionFilterMask) || 1; }
        const _modelPivots = {}; // ref контейнера (Model/Folder) -> THREE.Matrix4 пивота
        // Деталь стала динамической (скрипт сделал Anchored=false — например, полки
        // холодильника). В Roblox всё, что лежало сверху и само не заякорено в файле
        // (мясо: Anchored=false), начинает падать. Включать динамику для ВСЕХ незаякоренных
        // деталей карты нельзя (в Castle Warfare их 2300+ — это тысячи тел и «рассыпающиеся»
        // стены), поэтому будим только тех, кто касается/стоит на убранной опоре.
        function luaPromoteResting(sbody) {
            if (typeof CANNON === 'undefined') return;
            sbody.computeAABB();
            const lb = sbody.aabb.lowerBound, ub = sbody.aabb.upperBound;
            const M = 0.6;
            let n = 0;
            for (const [k, b] of Object.entries(physicsBodies)) {
                if (n >= 60) break;
                if (b === sbody || b === charBody || b.type !== CANNON.Body.STATIC) continue;
                if (b.collisionFilterMask === 0) continue;                 // CanCollide=false
                const mesh = sceneObjs[k];
                if (!mesh || mesh.userData.anchoredFlag !== false) continue; // заякорена в файле — стоит на месте
                b.computeAABB();
                const bl = b.aabb.lowerBound, bu = b.aabb.upperBound;
                const touches = bl.x <= ub.x + M && bu.x >= lb.x - M &&
                                bl.y <= ub.y + M && bu.y >= lb.y - M &&
                                bl.z <= ub.z + M && bu.z >= lb.z - M;
                if (!touches) continue;
                if (b.position.y < sbody.position.y - 0.3) continue;       // лежит ниже опоры — не падает
                // у падающего тела настоящие габариты (у статики толщина раздута до 1.0)
                const sz = loadedObjSize[k];
                if (sz && mesh.userData.shape !== 'sphere') {
                    const half = new CANNON.Vec3(Math.max(sz.x * 0.5, 0.05), Math.max(sz.y * 0.5, 0.05), Math.max(sz.z * 0.5, 0.05));
                    b.shapes.length = 0; b.shapeOffsets.length = 0; b.shapeOrientations.length = 0;
                    b.addShape(new CANNON.Box(half));
                }
                b.mass = 1;
                b.type = CANNON.Body.DYNAMIC;
                b.updateMassProperties();
                b.allowSleep = true;
                b.wakeUp();
                b.aabbNeedsUpdate = true;
                n++;
            }
        }

        // Габаритный ящик (оси мира): по 8 углам каждой детали внутри Model/Folder.
        // Model:GetBoundingBox(): бокс ориентирован по PIVOT модели (PrimaryPart или WorldPivot), а не по осям мира — как в Roblox.
        // Раньше был мировой AABB: у повёрнутой двери size.X оказывался толщиной вместо ширины, и скрипт, который ставит петлю как
        // bbox * CFrame.new(size.X/2, 0, 0) (DoorOpener), вращал створку вокруг центра, игнорируя pivot. У детали — её собственный CFrame.
        function luaBoundingBox(ref) {
            const leaf = luaIsPartRef(ref) && !(luaChildrenByRef[ref] && luaChildrenByRef[ref].length);
            const refs = leaf ? [ref] : luaCollectParts(ref, []);
            let R = new THREE.Matrix4();   // только вращение ориентации бокса
            if (leaf) R.extractRotation(luaPartMatrix(ref));
            else if (!luaIsCharRef(ref) && !luaIsCameraRef(ref)) { try { R.extractRotation(luaGetPivotMatrix(ref)); } catch (e) { R = new THREE.Matrix4(); } }
            const Rinv = R.clone().invert();
            const mn = new THREE.Vector3(Infinity, Infinity, Infinity), mx = new THREE.Vector3(-Infinity, -Infinity, -Infinity);
            const c = new THREE.Vector3();
            for (const pr of refs) {
                const sz = loadedObjSize[pr];
                if (!sz) continue;
                const M = luaPartMatrix(pr);
                for (let i = 0; i < 8; i++) {
                    c.set((i & 1 ? 0.5 : -0.5) * sz.x, (i & 2 ? 0.5 : -0.5) * sz.y, (i & 4 ? 0.5 : -0.5) * sz.z).applyMatrix4(M).applyMatrix4(Rinv);
                    mn.min(c); mx.max(c);
                }
            }
            const e = R.elements;
            const rot = [e[0], e[4], e[8], e[1], e[5], e[9], e[2], e[6], e[10]];   // R00 R01 R02 / R10 R11 R12 / R20 R21 R22
            if (!isFinite(mn.x)) { const p = luaPositionOfRef(ref) || { x: 0, y: 0, z: 0 }; return { cx: p.x, cy: p.y, cz: p.z, sx: 0, sy: 0, sz: 0, rot }; }
            const lc = new THREE.Vector3((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, (mn.z + mx.z) / 2).applyMatrix4(R);   // центр обратно в мир
            return { cx: lc.x, cy: lc.y, cz: lc.z, sx: mx.x - mn.x, sy: mx.y - mn.y, sz: mx.z - mn.z, rot };
        }

        // ClickDetector: клик/тап по детали (или по детали внутри Model, у которой он есть)
        // в Play -> MouseClick(player) / RightMouseClick(player) на ClickDetector, если игрок
        // в пределах MaxActivationDistance (по умолчанию 32). Сигнал общий для серверной и
        // клиентской Lua-VM (как и у ProximityPrompt).
        let _cdLogT = 0;
        function _cdLog(msg) { /* отладочный лог ClickDetector отключён */ }
        function luaClickDetectorAt(cx, cy, right, fat) {
            if (!isPlaying || (!luaServerL && !luaClientL) || luaControlsDisabled) return false;
            const vp = document.getElementById('viewport');
            const rect = vp.getBoundingClientRect();
            const fire = (det) => {
                const pn = luaByRef[luaParentByRef[det]];
                const evn = right ? 'RightMouseClick' : 'MouseClick';
                const ids = luaSignalsByKey[det + '|' + evn] || [];
                _cdLog(evn + ' → «' + (pn ? pn.name : '?') + '» (ClickDetector ref ' + det + ', подписчиков: ' + ids.length +
                       ', игрок ref ' + luaPlayerRef + ')');
                fireLuaSignal(det, right ? 'RightMouseClick' : 'MouseClick', [{ __instanceRef: luaPlayerRef }]);
                return true;
            };
            const inRange = (det, partRef) => {
                let maxD = luaGetGenericProp(det, 'MaxActivationDistance');
                if (typeof maxD !== 'number' || !(maxD > 0)) maxD = 32;
                const pp = luaPositionOfRef(partRef);
                if (!charBody || !pp) return true;
                return Math.hypot(pp.x - charBody.position.x, pp.y - charBody.position.y, pp.z - charBody.position.z) <= maxD;
            };
            const detectorOf = (partRef) => {
                for (const c of (luaChildrenByRef[partRef] || [])) if (luaByRef[c] && luaByRef[c].cls === 'ClickDetector') return c;
                return null;
            };
            // 1) точное попадание лучом: деталь с ClickDetector (или её родители-Model)
            const m = new THREE.Vector2(((cx - rect.left) / rect.width) * 2 - 1, -((cy - rect.top) / rect.height) * 2 + 1);
            const rc = new THREE.Raycaster();
            rc.setFromCamera(m, camera);
            const hits = rc.intersectObjects(Object.values(sceneObjs), true);
            if (hits.length) {
                let obj = hits[0].object;
                while (obj && !(obj.userData && obj.userData.ref)) obj = obj.parent;
                if (obj) {
                    const hitRef = parseInt(obj.userData.ref);
                    if (!fat) { /* мышь: диагностика ниже */ }
                    let node = hitRef, guard = 0;
                    while (node !== undefined && node !== -1 && guard++ < 200) {
                        for (const c of (luaChildrenByRef[node] || [])) {
                            if (!luaByRef[c] || luaByRef[c].cls !== 'ClickDetector') continue;
                            if (inRange(c, hitRef)) return fire(c);
                        }
                        node = luaParentByRef[node];
                    }
                }
            }
            if (!fat) {
                const h0 = hits.length ? hits[0].object : null;
                let o0 = h0; while (o0 && !(o0.userData && o0.userData.ref)) o0 = o0.parent;
                const r0 = o0 ? parseInt(o0.userData.ref) : null;
                _cdLog('клик попал в ' + (r0 !== null && luaByRef[r0] ? '«' + luaByRef[r0].name + '» (' + luaByRef[r0].cls + ')' : 'пустоту') + ' — ClickDetector нет или он далеко');
                return false; // запас ниже — только для касаний (мышью целимся точно)
            }
            // 2) запас для пальца: кнопки бывают в десятые доли студа (у лифта 0.19), попасть лучом
            // с телефона трудно. Берём ближайший к касанию ClickDetector в радиусе ~30 px
            // (или в проекции размера детали, если она крупнее) — как «щедрый» клик в Roblox на сенсорных.
            let best = null, bestD = Infinity;
            const tanHalf = Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2);
            const v = new THREE.Vector3();
            for (const [cRef, info] of Object.entries(luaByRef)) {
                if (info.cls !== 'ClickDetector') continue;
                const partRef = luaParentByRef[cRef];
                if (!sceneObjs[partRef]) continue;
                const pp = luaPositionOfRef(partRef);
                if (!pp) continue;
                v.set(pp.x, pp.y, pp.z).project(camera);
                if (v.z < -1 || v.z > 1) continue;
                const sx = rect.left + (v.x + 1) / 2 * rect.width, sy = rect.top + (1 - v.y) / 2 * rect.height;
                const dpx = Math.hypot(sx - cx, sy - cy);
                const camD = Math.max(0.1, camera.position.distanceTo(new THREE.Vector3(pp.x, pp.y, pp.z)));
                const pxPerStud = rect.height / (2 * camD * tanHalf);
                const sz = loadedObjSize[partRef] || { x: 1, y: 1, z: 1 };
                const radius = Math.max(30, Math.hypot(sz.x, sz.y, sz.z) / 2 * pxPerStud);
                if (dpx <= radius && dpx < bestD && inRange(Number(cRef), partRef)) { best = Number(cRef); bestD = dpx; }
            }
            if (best !== null) return fire(best);
            {
                const h0 = hits.length ? hits[0].object : null;
                let o0 = h0; while (o0 && !(o0.userData && o0.userData.ref)) o0 = o0.parent;
                const r0 = o0 ? parseInt(o0.userData.ref) : null;
                let n = 0; for (const info of Object.values(luaByRef)) if (info.cls === 'ClickDetector') n++;
                _cdLog('тап попал в ' + (r0 !== null && luaByRef[r0] ? '«' + luaByRef[r0].name + '» (' + luaByRef[r0].cls + ')' : 'пустоту') +
                       '; ClickDetector рядом не найден (всего в карте: ' + n + ')');
            }
            return false;
        }

        function luaIsCharRef(ref) {
            return ref !== -1 && (ref === luaCharacterRef || ref === luaHumanoidRootPartRef || ref === luaHumanoidRef);
        }
        // Клон детали из файла, которому ещё не построили меш (он не в Workspace): для скрипта это всё равно
        // деталь — иначе PivotTo(клона-контейнера) до .Parent = workspace ничего не двигал (см. luaRealizeClonedParts).
        // Данные детали без меша/тела: шаблон из ServerStorage (его не рисуем, см. o.nw) или клон, ещё не попавший в Workspace.
        function luaDormantData(ref) {
            if (sceneObjs[ref] || physicsBodies[ref]) return null;
            const d = playObjData[ref];
            if (d) return d;
            const o = luaCloneOrigin[ref];
            return o !== undefined ? (playObjData[o] || null) : null;
        }
        function luaIsPendingClonePart(ref) { return !!luaDormantData(ref); }
        function luaIsPartRef(ref) { return !!(sceneObjs[ref] || physicsBodies[ref] || luaIsPendingClonePart(ref)); }
        function luaIsCameraRef(ref) {
            return !!(luaByRef[ref] && luaByRef[ref].cls === 'Camera' && typeof camera !== 'undefined');
        }
        // Camera API для Lua: размер вьюпорта, живой FieldOfView, проекция точки и луч из пикселя
        function luaCamInfo() {
            const sz = renderer.getSize(new THREE.Vector2());
            return { w: sz.x, h: sz.y, fov: camera.fov };
        }
        function luaCamProject(x, y, z) {
            camera.updateMatrixWorld();
            const sz = renderer.getSize(new THREE.Vector2());
            const v = new THREE.Vector3(x, y, z);
            const depth = -v.clone().applyMatrix4(camera.matrixWorldInverse).z;
            const n = v.project(camera);
            return {
                x: (n.x * 0.5 + 0.5) * sz.x, y: (1 - (n.y * 0.5 + 0.5)) * sz.y, depth: depth,
                on: depth > 0 && Math.abs(n.x) <= 1 && Math.abs(n.y) <= 1,
            };
        }
        function luaCamRay(px, py) {
            camera.updateMatrixWorld();
            const sz = renderer.getSize(new THREE.Vector2());
            const ndc = new THREE.Vector2((px / sz.x) * 2 - 1, -(py / sz.y) * 2 + 1);
            const rc = new THREE.Raycaster();
            rc.setFromCamera(ndc, camera);
            return { o: rc.ray.origin, d: rc.ray.direction };
        }
        function luaPartMatrix(ref) {
            const p = luaPositionOfRef(ref);
            const q = new THREE.Quaternion();
            const body = physicsBodies[ref];
            const mesh = sceneObjs[ref];
            if (body && ref !== luaHumanoidRootPartRef) {
                q.set(body.quaternion.x, body.quaternion.y, body.quaternion.z, body.quaternion.w);
            } else if (mesh) {
                mesh.matrix.decompose(new THREE.Vector3(), q, new THREE.Vector3());
            } else if (luaPartXform[ref] && luaIsPendingClonePart(ref)) {
                const tq = luaPartXform[ref].q;
                q.set(tq[0], tq[1], tq[2], tq[3]);
            } else {
                const dd = luaDormantData(ref);
                if (dd && dd.rot && dd.rot.length >= 9) {
                    const r9 = dd.rot;
                    q.setFromRotationMatrix(new THREE.Matrix4().set(r9[0], r9[1], r9[2], 0, r9[3], r9[4], r9[5], 0, r9[6], r9[7], r9[8], 0, 0, 0, 0, 1));
                }
            }
            return new THREE.Matrix4().compose(new THREE.Vector3(p.x, p.y, p.z), q, new THREE.Vector3(1, 1, 1));
        }
        function luaPivotOffsetMatrix(ref) {
            const mesh = sceneObjs[ref] || (luaIsPendingClonePart(ref) ? sceneObjs[luaCloneOrigin[ref]] : null);
            const dd = mesh ? null : luaDormantData(ref);
            const po = (mesh && mesh.userData && mesh.userData.pivotOffset) || (dd && dd.pivotOffset);
            const m = new THREE.Matrix4();
            if (!po || po.length < 12) return m;
            m.set(po[3], po[4], po[5], po[0],
                  po[6], po[7], po[8], po[1],
                  po[9], po[10], po[11], po[2],
                  0, 0, 0, 1);
            return m;
        }
        function luaCharMatrix() {
            const m = new THREE.Matrix4().makeRotationY(spherical.theta);
            if (charBody) m.setPosition(charBody.position.x, charBody.position.y, charBody.position.z);
            return m;
        }
        function luaCollectParts(ref, out, depth) {
            if ((depth || 0) > 64) return out;
            if (luaIsPartRef(ref) && !luaIsCharRef(ref)) out.push(ref);
            for (const c of (luaChildrenByRef[ref] || [])) luaCollectParts(c, out, (depth || 0) + 1);
            return out;
        }
        function luaGetPivotMatrix(ref) {
            if (luaIsCharRef(ref)) return luaCharMatrix();
            if (luaIsCameraRef(ref)) {
                return new THREE.Matrix4().compose(camera.position.clone(), camera.quaternion.clone(), new THREE.Vector3(1, 1, 1));
            }
            if (luaIsPartRef(ref)) return luaPartMatrix(ref).multiply(luaPivotOffsetMatrix(ref));
            // Model с PrimaryPart: pivot модели = pivot этой детали (как в Roblox), а не WorldPivot/центр габаритов
            const rpp = luaRefProps[ref];
            if (rpp && rpp.PrimaryPart !== undefined && rpp.PrimaryPart !== -1 && rpp.PrimaryPart !== ref && luaIsPartRef(rpp.PrimaryPart)) {
                return luaPartMatrix(rpp.PrimaryPart).multiply(luaPivotOffsetMatrix(rpp.PrimaryPart));
            }
            if (_modelPivots[ref]) return _modelPivots[ref].clone();
            const fp = luaFilePivots[ref];
            if (fp) {
                const r = fp.r, p = fp.p;
                const fm = new THREE.Matrix4();
                fm.set(r[0], r[1], r[2], p[0], r[3], r[4], r[5], p[1], r[6], r[7], r[8], p[2], 0, 0, 0, 1);
                _modelPivots[ref] = fm.clone();
                return fm;
            }
            const parts = luaCollectParts(ref, []);
            const m = new THREE.Matrix4();
            if (parts.length) {
                const mn = new THREE.Vector3(Infinity, Infinity, Infinity), mx = new THREE.Vector3(-Infinity, -Infinity, -Infinity);
                for (const pr of parts) {
                    const p = luaPositionOfRef(pr);
                    mn.min(new THREE.Vector3(p.x, p.y, p.z)); mx.max(new THREE.Vector3(p.x, p.y, p.z));
                }
                m.setPosition((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, (mn.z + mx.z) / 2);
                _modelPivots[ref] = m.clone();
            }
            return m;
        }
        // ============ СВАРКА (WeldConstraint) ============
        // Раньше Part0/Part1 только запоминались, и приваренная деталь (уран над головой игрока)
        // просто падала. Теперь деталь, приваренная СКРИПТОМ, каждый кадр ставится в
        // CFrame(Part0) * смещение, а смещение запоминается в момент сварки (как в Roblox).
        // Тело Part1 на это время кинематическое (нет гравитации); снята сварка — снова динамическое.
        // Сварки из самого файла не трогаем (они у закреплённых деталей и ничего не двигают).
        function _weldMat(ref, lifted) {
            const M = (luaIsPartRef(ref) && !luaIsCharRef(ref)) ? luaPartMatrix(ref) : luaGetPivotMatrix(ref);
            // HumanoidRootPart в приложении — центр сферы-коллайдера (на CHAR_RADIUS над землёй), а в
            // настоящем R15 он на 2.35 над землёй: приваренное «над головой» должно быть на высоте Roblox.
            if (lifted && ref === luaHumanoidRootPartRef) M.elements[13] += R15_HRP_ABOVE_GROUND - CHAR_RADIUS;
            return M;
        }
        function _releaseWeldBody(w) {
            const b = physicsBodies[w.p1];
            if (!b || !w.prev || typeof CANNON === 'undefined' || b.type !== CANNON.Body.KINEMATIC) return;
            b.type = CANNON.Body.DYNAMIC;
            b.mass = w.prev.mass > 0 ? w.prev.mass : 1;
            b.updateMassProperties();
            b.velocity.set(0, 0, 0);
            b.angularVelocity.set(0, 0, 0);
            b.allowSleep = true;
            b.aabbNeedsUpdate = true;
            b.wakeUp();
            luaPromoteResting(b);
        }
        function luaRegisterWeld(weldRef) {
            const info = luaByRef[weldRef];
            if (!info || info.cls !== 'WeldConstraint') return;
            const rp = luaRefProps[weldRef];
            if (!rp) return;
            const p0 = rp.Part0, p1 = rp.Part1;
            const ok = (r) => r !== undefined && r !== -1 && luaByRef[r];
            if (!ok(p0) || !ok(p1) || p0 === p1 || !luaIsPartRef(p1) || p1 === luaHumanoidRootPartRef) return;
            const off = _weldMat(p0, false).invert().multiply(_weldMat(p1, false));
            const old = luaWelds.findIndex(w => w.ref === weldRef);
            let prev = null;
            if (old >= 0) {
                if (luaWelds[old].p1 === p1) prev = luaWelds[old].prev; // тело уже кинематическое — сохраняем исходное состояние
                else _releaseWeldBody(luaWelds[old]);
            }
            const body = physicsBodies[p1];
            if (!prev && body && typeof CANNON !== 'undefined' && body.type === CANNON.Body.DYNAMIC) {
                prev = { mass: body.mass };
                body.type = CANNON.Body.KINEMATIC;
                body.velocity.set(0, 0, 0);
                body.angularVelocity.set(0, 0, 0);
                body.aabbNeedsUpdate = true;
            }
            const link = { ref: weldRef, p0, p1, off, prev };
            if (old >= 0) luaWelds[old] = link; else luaWelds.push(link);
        }
        function luaStepWelds() {
            if (!luaWelds.length) return;
            for (let i = luaWelds.length - 1; i >= 0; i--) {
                const w = luaWelds[i];
                const par = luaParentByRef[w.ref];
                const rp = luaRefProps[w.ref];
                const alive = par !== undefined && par !== -1 && luaByRef[w.ref] && luaByRef[w.p0] && luaByRef[w.p1]
                    && rp && rp.Part0 === w.p0 && rp.Part1 === w.p1;
                if (!alive) { _releaseWeldBody(w); luaWelds.splice(i, 1); continue; }
                luaApplyPartMatrix(w.p1, _weldMat(w.p0, true).multiply(w.off));
                const b = physicsBodies[w.p1];
                if (b && b.type === CANNON.Body.KINEMATIC) { b.velocity.set(0, 0, 0); b.angularVelocity.set(0, 0, 0); }
            }
        }

        function luaApplyPartMatrix(ref, M) {
            const pos = new THREE.Vector3(), q = new THREE.Quaternion(), sc = new THREE.Vector3();
            M.decompose(pos, q, sc);
            const body = physicsBodies[ref];
            if (ref === luaHumanoidRootPartRef) {
                if (charBody) { charBody.position.set(pos.x, pos.y, pos.z); charBody.wakeUp(); }
                return;
            }
            if (body) {
                body.position.set(pos.x, pos.y, pos.z);
                body.quaternion.set(q.x, q.y, q.z, q.w);
                body.aabbNeedsUpdate = true;
                if (body.wakeUp) body.wakeUp();
            }
            luaPartXform[ref] = { p: [pos.x, pos.y, pos.z], q: [q.x, q.y, q.z, q.w] };
            if (loadedObjPos[ref]) loadedObjPos[ref] = { x: pos.x, y: pos.y, z: pos.z };
            const mesh = sceneObjs[ref];
            if (mesh) {
                const p0 = new THREE.Vector3(), q0 = new THREE.Quaternion(), s0 = new THREE.Vector3();
                mesh.matrix.decompose(p0, q0, s0);
                mesh.matrix.compose(pos, q, s0);
            }
        }
        function luaFirePoseSignals(ref) {
            fireLuaSignal(ref, '__prop_CFrame', []);
            fireLuaSignal(ref, '__prop_Position', []);
        }
        // PivotTo: деталь — с учётом PivotOffset; Model/Folder — жёстким
        // переносом всех деталей внутри; персонаж — телепорт charBody.
        function luaSetPivotMatrix(ref, M) {
            if (luaIsCharRef(ref)) {
                const e = M.elements;
                if (charBody) {
                    charBody.position.set(e[12], e[13], e[14]);
                    charBody.velocity.set(0, 0, 0);
                    charBody.wakeUp();
                }
                charVelX = 0; charVelZ = 0;
                const lx = -e[8], lz = -e[10];
                if (Math.hypot(lx, lz) > 1e-4) spherical.theta = Math.atan2(-lx, -lz);
                return;
            }
            if (luaIsCameraRef(ref)) {
                const e = M.elements;
                applyCFrameValue(ref, e[12], e[13], e[14], -e[8], -e[9], -e[10]);
                return;
            }
            if (luaIsPartRef(ref)) {
                // PVInstance:PivotTo в Roblox переносит деталь ВМЕСТЕ со всеми потомками-деталями
                // (у двери холодильника «стекло» и «ручка» — её дети). Раньше двигалась только сама
                // деталь, и стекло с ручкой оставались на месте, пока дверь распахивалась.
                const oldPart = luaPartMatrix(ref);
                const newPart = M.clone().multiply(luaPivotOffsetMatrix(ref).invert());
                const deltaP = newPart.clone().multiply(oldPart.clone().invert());
                const kids = luaCollectParts(ref, []).filter(pr => pr !== ref);
                const kidMats = kids.map(pr => luaPartMatrix(pr));   // до сдвига
                luaApplyPartMatrix(ref, newPart);
                luaFirePoseSignals(ref);
                kids.forEach((pr, i) => {
                    luaApplyPartMatrix(pr, deltaP.clone().multiply(kidMats[i]));
                    luaFirePoseSignals(pr);
                });
                return;
            }
            const old = luaGetPivotMatrix(ref);
            const delta = M.clone().multiply(old.clone().invert());
            for (const pr of luaCollectParts(ref, [])) {
                luaApplyPartMatrix(pr, delta.clone().multiply(luaPartMatrix(pr)));
                luaFirePoseSignals(pr);
            }
            _modelPivots[ref] = M.clone();
        }
        // part.CFrame = cf — задаёт именно CFrame детали (без PivotOffset)
        function luaSetCFrameMatrix(ref, M) {
            if (luaIsPartRef(ref) && !luaIsCharRef(ref)) {
                luaApplyPartMatrix(ref, M);
                luaFirePoseSignals(ref);
            } else {
                luaSetPivotMatrix(ref, M);
            }
        }
        // Camera — особый случай:
        function applyCFrameValue(ref, x, y, z, lx, ly, lz) {
            if (luaByRef[ref] && luaByRef[ref].cls === 'Camera' && typeof camera !== 'undefined') {
                camera.position.set(x, y, z);
                camera.lookAt(x + lx, y + ly, z + lz);
                _scriptCam = { p: camera.position.clone(), q: camera.quaternion.clone() };
            } else {
                luaSetPositionOfRef(ref, x, y, z);
            }
        }
        // rbxassetid://12345 (или голое число) -> локальный проксирующий
        function rbxAssetIdToProxyUrl(idStr) {
            const m = /\d+/.exec(String(idStr || ''));
            if (!m) return null;
            return '/api/asset-proxy?id=' + m[0];
        }

        let soundElByRef = {};
        // PlaybackSpeed vs PitchShiftSoundEffect.Octave — это НЕ два
        const _soundBaseSpeed = {};   // ref -> PlaybackSpeed (Pitch — алиас того же)
        const _soundPitchOctave = {}; // ref -> Octave активного PitchShiftSoundEffect (реально применяется, см. RobloxSoundElement.pitchOctave/_pitchShiftAsync)
        function _applySoundRate(ref) {
            const speed = _soundBaseSpeed[ref] != null ? _soundBaseSpeed[ref] : 1;
            const octave = _soundPitchOctave[ref] != null ? _soundPitchOctave[ref] : 0;
            const el = getOrCreateSoundEl(ref);
            el.playbackRate = speed;
            el.pitchOctave = octave;
        }

        // ============ WEB AUDIO OLA TIME-STRETCH (сохранение тона) ============
        let _sharedAudioCtx = null;
        function _getAudioCtx() {
            if (!_sharedAudioCtx) {
                const Ctx = window.AudioContext || window.webkitAudioContext;
                _sharedAudioCtx = new Ctx();
            }
            return _sharedAudioCtx;
        }
        // Мобильные браузеры разрешают звуку играть только после реального
        // тача/клика — а AudioContext для звуков с PlaybackSpeed/Octave
        // (фазовый вокодер) раньше создавался и получал .resume() только
        // ГЛУБОКО ВНУТРИ асинхронной цепочки (fetch → decodeAudioData →
        // воркер → ...), когда браузер уже не считает это "прямым откликом"
        // на жест пользователя. .resume() в такой ситуации может остаться
        // подвешенным навсегда — контекст стоит на паузе, и звук просто НЕ
        // ИГРАЕТ (тишина), хотя весь код вокруг отрабатывает без ошибок.
        // Обычные <audio> (без PlaybackSpeed/Octave) эту проблему не
        // получали — у них своя, более мягкая политика автовоспроизведения,
        // отсюда и было "пропадает только у звуков с pitch-эффектами".
        // Лечится стандартно: создать и разблокировать AudioContext сразу
        // на первое же касание/клик по странице, заранее, до того как он
        // реально понадобится какой-либо песне.
        let _audioUnlockDone = false;
        function _unlockAudioContext() {
            if (_audioUnlockDone) return;
            const ctx = _getAudioCtx();
            const finish = () => { if (ctx.state === 'running') _audioUnlockDone = true; };
            if (ctx.state === 'suspended') { ctx.resume().then(finish).catch(() => { }); } else { finish(); }
            // Немой блип нулевой громкости — на iOS одного resume() иногда
            // недостаточно, помогает реальный (пусть и беззвучный) source.start().
            try {
                const buf = ctx.createBuffer(1, 1, ctx.sampleRate);
                const src = ctx.createBufferSource();
                src.buffer = buf; src.connect(ctx.destination); src.start(0);
            } catch (e) { emuWarn('swallow:L7432', 'блок около script.js:7432: ' + _errText(e) + ' (не критично)'); }
        }
        ['touchstart', 'touchend', 'pointerdown', 'mousedown', 'keydown'].forEach((ev) => {
            document.addEventListener(ev, _unlockAudioContext, { passive: true });
        });
        const _stretchedBufferCache = {}; // "src|rate" -> AudioBuffer, чтобы не пересчитывать заново при повторном Play/пересборке сцены

        // Фазовый вокодер — раньше здесь был WSOLA (время-доменный поиск
        const _STRETCH_WORKER_CODE = `
            function _fft(re, im, inverse) {
                const n = re.length;
                for (let i = 1, j = 0; i < n; i++) {
                    let bit = n >> 1;
                    for (; j & bit; bit >>= 1) j ^= bit;
                    j ^= bit;
                    if (i < j) {
                        let t = re[i]; re[i] = re[j]; re[j] = t;
                        t = im[i]; im[i] = im[j]; im[j] = t;
                    }
                }
                for (let len = 2; len <= n; len <<= 1) {
                    const ang = (inverse ? 1 : -1) * 2 * Math.PI / len;
                    const wR = Math.cos(ang), wI = Math.sin(ang);
                    for (let i = 0; i < n; i += len) {
                        let curR = 1, curI = 0;
                        const half = len >> 1;
                        for (let j = 0; j < half; j++) {
                            const uR = re[i + j], uI = im[i + j];
                            const vR = re[i + j + half] * curR - im[i + j + half] * curI;
                            const vI = re[i + j + half] * curI + im[i + j + half] * curR;
                            re[i + j] = uR + vR; im[i + j] = uI + vI;
                            re[i + j + half] = uR - vR; im[i + j + half] = uI - vI;
                            const nextR = curR * wR - curI * wI;
                            const nextI = curR * wI + curI * wR;
                            curR = nextR; curI = nextI;
                        }
                    }
                }
                if (inverse) { for (let i = 0; i < n; i++) { re[i] /= n; im[i] /= n; } }
            }
            function _princarg(x) { return x - 2 * Math.PI * Math.round(x / (2 * Math.PI)); }
            function _stretchChannel(input, speed, frameSize) {
                const synthHop = frameSize / 4;
                const analysisHop = Math.round(synthHop * speed);
                const inLen = input.length;
                const outLen = Math.max(1, Math.floor(inLen / speed));
                const output = new Float32Array(outLen);
                const normArr = new Float32Array(outLen);
                const win = new Float32Array(frameSize);
                for (let i = 0; i < frameSize; i++) win[i] = 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / (frameSize - 1));
                const omega = new Float32Array(frameSize);
                for (let k = 0; k < frameSize; k++) omega[k] = 2 * Math.PI * k * analysisHop / frameSize;
                const re = new Float32Array(frameSize), im = new Float32Array(frameSize);
                const prevPhase = new Float32Array(frameSize), synthPhase = new Float32Array(frameSize);
                let firstFrame = true;
                let inPos = 0, outPos = 0;
                while (outPos < outLen) {
                    const start = Math.round(inPos);
                    for (let k = 0; k < frameSize; k++) {
                        const idx = start + k;
                        re[k] = (idx >= 0 && idx < inLen ? input[idx] : 0) * win[k];
                        im[k] = 0;
                    }
                    _fft(re, im, false);
                    const half = frameSize / 2;
                    for (let k = 0; k <= half; k++) {
                        const mag = Math.sqrt(re[k] * re[k] + im[k] * im[k]);
                        const phase = Math.atan2(im[k], re[k]);
                        let newPhase;
                        if (firstFrame) { newPhase = phase; }
                        else {
                            const delta = phase - prevPhase[k];
                            const deltaUnwrapped = _princarg(delta - omega[k]) + omega[k];
                            const trueFreq = deltaUnwrapped / analysisHop;
                            newPhase = synthPhase[k] + trueFreq * synthHop;
                        }
                        prevPhase[k] = phase;
                        synthPhase[k] = newPhase;
                        re[k] = mag * Math.cos(newPhase);
                        im[k] = mag * Math.sin(newPhase);
                        if (k > 0 && k < half) { re[frameSize - k] = re[k]; im[frameSize - k] = -im[k]; }
                    }
                    firstFrame = false;
                    _fft(re, im, true);
                    for (let k = 0; k < frameSize; k++) {
                        const di = outPos + k;
                        if (di >= outLen) continue;
                        const w = win[k];
                        output[di] += re[k] * w;
                        normArr[di] += w * w;
                    }
                    inPos += analysisHop;
                    outPos += synthHop;
                }
                for (let i = 0; i < outLen; i++) if (normArr[i] > 1e-6) output[i] /= normArr[i];
                return output;
            }
            // Простой линейный ресемплинг — НЕ фазовый вокодер, наоборот:
            function _resampleChannel(input, factor) {
                const outLen = Math.max(1, Math.floor(input.length / factor));
                const output = new Float32Array(outLen);
                for (let i = 0; i < outLen; i++) {
                    const srcPos = i * factor;
                    const i0 = Math.floor(srcPos);
                    const frac = srcPos - i0;
                    const a = input[i0] || 0;
                    const b = input[i0 + 1] !== undefined ? input[i0 + 1] : a;
                    output[i] = a + (b - a) * frac;
                }
                return output;
            }
            self.onmessage = function (e) {
                const { jobId, channels, speed, mode } = e.data;
                const frameSize = 2048; // степень двойки — обязательное требование для _fft; ~46мс при 44.1кГц
                const outChannels = mode === 'resample'
                    ? channels.map((ch) => _resampleChannel(ch, speed))
                    : channels.map((ch) => _stretchChannel(ch, speed, frameSize));
                self.postMessage({ jobId, channels: outChannels }, outChannels.map((c) => c.buffer));
            };
        `;
        let _stretchWorker = null;
        const _stretchPending = {};
        let _stretchJobId = 0;
        function _getStretchWorker() {
            if (!_stretchWorker) {
                const blob = new Blob([_STRETCH_WORKER_CODE], { type: 'application/javascript' });
                _stretchWorker = new Worker(URL.createObjectURL(blob));
                _stretchWorker.onmessage = (e) => {
                    const { jobId, channels } = e.data;
                    const cb = _stretchPending[jobId];
                    if (cb) { delete _stretchPending[jobId]; cb(channels); }
                };
            }
            return _stretchWorker;
        }
        // Возвращает Promise<AudioBuffer> — сам расчёт идёт в воркере
        function _postStretchJob(buffer, speed, mode, audioCtx) {
            return new Promise((resolve) => {
                if (Math.abs(speed - 1) < 0.001) { resolve(buffer); return; }
                const worker = _getStretchWorker();
                const jobId = ++_stretchJobId;
                const channels = [];
                const transferables = [];
                for (let ch = 0; ch < buffer.numberOfChannels; ch++) {
                    const data = buffer.getChannelData(ch).slice(); // копия — оригинал AudioBuffer нельзя "отдать" воркеру (detach испортил бы исходный буфер)
                    channels.push(data);
                    transferables.push(data.buffer);
                }
                _stretchPending[jobId] = (resultChannels) => {
                    const outBuf = audioCtx.createBuffer(resultChannels.length, resultChannels[0].length, buffer.sampleRate);
                    for (let ch = 0; ch < resultChannels.length; ch++) outBuf.copyToChannel(resultChannels[ch], ch);
                    resolve(outBuf);
                };
                worker.postMessage({ jobId, channels, speed, mode }, transferables);
            });
        }
        function _phaseVocoderStretchAsync(buffer, speed, audioCtx) {
            return _postStretchJob(buffer, speed, 'stretch', audioCtx);
        }
        function _resampleAsync(buffer, factor, audioCtx) {
            return _postStretchJob(buffer, factor, 'resample', audioCtx);
        }
        // PitchShiftSoundEffect.Octave — НАСТОЯЩИЙ pitch-only эффект
        async function _pitchShiftAsync(buffer, octave, audioCtx) {
            if (Math.abs(octave) < 0.001) return buffer;
            const p = Math.pow(2, octave);
            const lengthened = await _phaseVocoderStretchAsync(buffer, 1 / p, audioCtx);
            return _resampleAsync(lengthened, p, audioCtx);
        }

        // ============ ПОСТОЯННЫЙ КЭШ РЕЗУЛЬТАТА (IndexedDB) ============
        let _stretchDbPromise = null;
        function _openStretchDb() {
            if (!_stretchDbPromise) {
                _stretchDbPromise = new Promise((resolve, reject) => {
                    const req = indexedDB.open('rsw-sound-cache', 1);
                    req.onupgradeneeded = () => req.result.createObjectStore('stretched');
                    req.onsuccess = () => resolve(req.result);
                    req.onerror = () => reject(req.error);
                });
            }
            return _stretchDbPromise;
        }
        async function _stretchDbGet(key) {
            try {
                const db = await _openStretchDb();
                return await new Promise((resolve) => {
                    const tx = db.transaction('stretched', 'readonly');
                    const req = tx.objectStore('stretched').get(key);
                    req.onsuccess = () => resolve(req.result || null);
                    req.onerror = () => resolve(null);
                });
            } catch (e) { return null; } // кэш — best-effort, не должен ронять воспроизведение
        }
        async function _stretchDbPut(key, value) {
            try {
                const db = await _openStretchDb();
                const tx = db.transaction('stretched', 'readwrite');
                tx.objectStore('stretched').put(value, key);
            } catch (e) { emuWarn('swallow:_stretchDbPut:7631', '_stretchDbPut: ' + _errText(e) + ' (best-effort)'); }
        }

        // Настоящий звуковой движок поверх Sound-инстансов.
        class RobloxSoundElement {
            constructor() {
                this._native = new Audio();
                this._native.preload = 'auto';
                this._mode = 'native';
                this._rate = 1;
                this._pitchOctave = 0; // PitchShiftSoundEffect.Octave — независимый от _rate pitch-only сдвиг, см. _rebuildProcessedBuffer
                this._src = '';
                this._listeners = {};
                this._volume = 0.5;
                this._loop = false;
                // Web Audio часть — создаётся лениво в _upgrade(), чтобы
                this._ctx = null;
                this._gain = null;
                this._rawBuffer = null;
                this._processedBuffer = null;
                this._sourceNode = null;
                this._playing = false;
                this._startCtxTime = 0;
                this._startOffset = 0;
                this._ended = false;
                this._loadToken = 0;
                this._loadedFired = false;

                this._native.addEventListener('ended', () => { if (this._mode === 'native') this._fire('ended'); });
                this._native.addEventListener('canplaythrough', () => { if (this._mode === 'native' && !this._loadedFired) { this._loadedFired = true; this._fire('canplaythrough'); } });
                this._native.addEventListener('error', () => { if (this._mode === 'native') this._fire('error'); });
                let _lastNativeT = 0;
                this._native.addEventListener('timeupdate', () => {
                    if (this._mode !== 'native') return;
                    if (this._native.loop && this._native.currentTime < _lastNativeT - 0.5) this._fire('timeupdate');
                    _lastNativeT = this._native.currentTime;
                });
            }
            addEventListener(type, cb) { (this._listeners[type] = this._listeners[type] || []).push(cb); }
            _fire(type) { (this._listeners[type] || []).forEach((cb) => { try { cb(); } catch (e) { emuWarn('swallow:cb:7670', 'cb: ' + _errText(e) + ''); } }); }

            get src() { return this._src; }
            set src(url) {
                this._src = url;
                this._loadedFired = false;
                if (this._mode === 'native') { this._native.src = url; return; }
                this._loadFromSrcForStretch();
            }
            get volume() { return this._mode === 'native' ? this._native.volume : (this._gain ? this._gain.gain.value : this._volume); }
            set volume(v) {
                this._volume = v;
                this._native.volume = v;
                if (this._gain) this._gain.gain.value = v;
            }
            get loop() { return this._loop; }
            set loop(v) { this._loop = v; this._native.loop = v; }
            get paused() { return this._mode === 'native' ? this._native.paused : !this._playing; }
            get ended() { return this._mode === 'native' ? this._native.ended : this._ended; }
            get duration() {
                if (this._mode === 'native') return this._native.duration;
                return this._processedBuffer ? this._processedBuffer.duration : NaN;
            }
            get currentTime() {
                if (this._mode === 'native') return this._native.currentTime;
                if (!this._playing || !this._processedBuffer) return this._startOffset;
                return Math.min(this._startOffset + (this._ctx.currentTime - this._startCtxTime), this._processedBuffer.duration);
            }
            set currentTime(t) {
                if (this._mode === 'native') { this._native.currentTime = t; return; }
                const wasPlaying = this._playing;
                this._stopSourceNode();
                this._startOffset = Math.max(0, t);
                if (wasPlaying) this._startPlayback(this._startOffset);
            }
            get playbackRate() { return this._rate; }
            set playbackRate(v) {
                v = Number(v) || 1;
                if (Math.abs(v - this._rate) < 0.001) return;
                this._rate = v;
                if (Math.abs(v - 1) < 0.001 && Math.abs(this._pitchOctave) < 0.001) {
                    // Возврат к 1x БЕЗ активного pitch-эффекта — нативного
                    // <audio> достаточно, апгрейд не нужен.
                    return;
                }
                this._upgrade();
            }
            // PitchShiftSoundEffect.Octave — независимый от playbackRate
            // pitch-only эффект (см. _rebuildProcessedBuffer/_pitchShiftAsync).
            get pitchOctave() { return this._pitchOctave; }
            set pitchOctave(v) {
                v = Number(v) || 0;
                if (Math.abs(v - this._pitchOctave) < 0.001) return;
                this._pitchOctave = v;
                if (Math.abs(this._rate - 1) < 0.001 && Math.abs(v) < 0.001) return;
                this._upgrade();
            }
            _upgrade() {
                if (this._mode === 'stretched') { this._rebuildProcessedBuffer(); return; }
                this._mode = 'stretched';
                this._ctx = _getAudioCtx();
                this._gain = this._ctx.createGain();
                this._gain.gain.value = this._volume;
                this._gain.connect(this._ctx.destination);
                const wasPlayingNative = !this._native.paused;
                const nativeTime = this._native.currentTime || 0;
                this._native.pause();
                this._loadFromSrcForStretch(wasPlayingNative, nativeTime);
            }
            _loadFromSrcForStretch(resumePlaying, resumeAt) {
                if (!this._src) return;
                const token = ++this._loadToken;
                fetch(this._src).then((r) => {
                    if (!r.ok) throw new Error('HTTP ' + r.status);
                    return r.arrayBuffer();
                }).then((buf) => this._ctx.decodeAudioData(buf)).then((decoded) => {
                    if (token !== this._loadToken) return; // src/режим сменили, пока грузили — этот результат уже неактуален
                    this._rawBuffer = decoded;
                    // Сам расчёт фазового вокодера (секунды на трек, см.
                    if (!this._loadedFired) { this._loadedFired = true; this._fire('canplaythrough'); }
                    if (resumePlaying) {
                        this._rebuildProcessedBuffer().then(() => {
                            this._startPlayback(Math.min(resumeAt, this._processedBuffer.duration));
                        });
                    }
                }).catch(() => { if (token === this._loadToken) this._fire('error'); });
            }
            async _rebuildProcessedBuffer() {
                if (!this._rawBuffer) return;
                // Версия в ключе кэша (в памяти И в IndexedDB — последний
                // переживает перезагрузку страницы): если когда-либо раньше
                // тут был посчитан и сохранён результат по старой/другой
                // версии алгоритма растяжки, он бы молча продолжал
                // отдаваться из кэша и звучать неправильно (писклявый голос)
                // даже после починки кода — сам код никогда не перезапускался,
                // просто читался готовый файл из IndexedDB. Бампаем версию,
                // чтобы прошлые закэшированные результаты гарантированно не
                // подхватились.
                const key = 'v2|' + this._src + '|' + this._rate.toFixed(3) + '|' + this._pitchOctave.toFixed(3);
                if (_stretchedBufferCache[key]) { this._processedBuffer = _stretchedBufferCache[key]; return; }
                // Дисковый (IndexedDB) кэш — проверяем ДО похода в воркер:
                const cached = await _stretchDbGet(key);
                if (cached) {
                    const outBuf = this._ctx.createBuffer(cached.channels.length, cached.channels[0].length, cached.sampleRate);
                    for (let ch = 0; ch < cached.channels.length; ch++) outBuf.copyToChannel(cached.channels[ch], ch);
                    this._processedBuffer = outBuf;
                    _stretchedBufferCache[key] = outBuf;
                    return;
                }
                // ВАЖНО: в настоящем Roblox Sound.PlaybackSpeed — это НЕ
                // сохраняющая тон растяжка времени, а обычный множитель
                // скорости чтения (как audio.playbackRate у HTML5): меняет
                // И темп, И питч одновременно (это задокументированное и
                // хорошо известное поведение Roblox). Раньше PlaybackSpeed
                // здесь шёл через фазовый вокодер (сохраняя тон) — то есть
                // звучал ИНАЧЕ, чем в настоящем Roblox, а маперы подбирают
                // Octave у PitchShiftSoundEffect ИМЕННО под естественный
                // подъём/понижение тона от PlaybackSpeed (как в примерах
                // этой карты: у превью песен разные PlaybackSpeed и разные
                // компенсирующие Octave). Наша "сохраняющая тон" растяжка
                // ломала этот баланс — отсюда писклявость даже там, где в
                // настоящем Roblox всё звучит нормально.
                // PitchShiftSoundEffect.Octave — НАСТОЯЩИЙ отдельный эффект:
                // он честно меняет питч БЕЗ изменения длительности (в
                // отличие от PlaybackSpeed) — это тоже задокументированное
                // поведение, и его сохраняем как есть.
                const t0 = performance.now();
                logLuaOutput('info', 'Sound: обрабатываю ' + this._src + ' — PlaybackSpeed=' + this._rate.toFixed(3) + ', Octave=' + this._pitchOctave.toFixed(3) + ' (длительность ' + this._rawBuffer.duration.toFixed(2) + 'с, ' + this._rawBuffer.sampleRate + 'Гц)');
                const p = Math.pow(2, this._pitchOctave);
                // PlaybackSpeed — наивный ресемпл (меняет питч, как в Roblox).
                const speedApplied = Math.abs(this._rate - 1) < 0.001
                    ? this._rawBuffer
                    : await _resampleAsync(this._rawBuffer, this._rate, this._ctx);
                // PitchShiftSoundEffect — честный сдвиг тона без изменения темпа.
                this._processedBuffer = Math.abs(p - 1) < 0.001 ? speedApplied : await _pitchShiftAsync(speedApplied, this._pitchOctave, this._ctx);
                _stretchedBufferCache[key] = this._processedBuffer;
                logLuaOutput('info', 'Sound: готово за ' + ((performance.now() - t0) / 1000).toFixed(1) + 'с — новая длительность ' + this._processedBuffer.duration.toFixed(2) + 'с, ' + this._processedBuffer.sampleRate + 'Гц (AudioContext=' + this._ctx.sampleRate + 'Гц)');
                const channels = [];
                for (let ch = 0; ch < this._processedBuffer.numberOfChannels; ch++) {
                    channels.push(this._processedBuffer.getChannelData(ch));
                }
                _stretchDbPut(key, { channels, sampleRate: this._processedBuffer.sampleRate });
            }
            _stopSourceNode() {
                if (this._sourceNode) {
                    try { this._sourceNode.onended = null; this._sourceNode.stop(); } catch (e) { emuWarn('swallow:this._sourceNode.onended:7815', 'this._sourceNode.onended: ' + _errText(e) + ''); }
                    this._sourceNode = null;
                }
                this._playing = false;
            }
            _startPlayback(offset) {
                if (!this._processedBuffer) return;
                if (this._ctx.state === 'suspended') {
                    // На всякий случай (если по какой-то причине разблокировка
                    // при первом тапе не сработала) — пробуем ещё раз при
                    // самом запуске; логируем, чтобы было видно в Output,
                    // если звук всё равно не слышен именно по этой причине.
                    this._ctx.resume().then(() => {
                        if (this._ctx.state !== 'running') {
                            logLuaOutput('warn', 'AudioContext не разблокировался (state=' + this._ctx.state + ') — звук может быть не слышен');
                        }
                    }).catch(() => { });
                }
                const node = this._ctx.createBufferSource();
                node.buffer = this._processedBuffer;
                node.connect(this._gain);
                node.onended = () => {
                    if (this._sourceNode !== node) return; // это был предыдущий source (заменили офсетом/темпом раньше) — игнор
                    this._sourceNode = null;
                    this._playing = false;
                    if (this._loop) {
                        this._startOffset = 0;
                        this._startPlayback(0);
                        this._fire('timeupdate'); // сигнал для DidLoop-детектора (см. регистрацию в getOrCreateSoundEl)
                    } else {
                        this._ended = true;
                        this._fire('ended');
                    }
                };
                node.start(0, offset);
                this._sourceNode = node;
                this._startCtxTime = this._ctx.currentTime;
                this._startOffset = offset;
                this._playing = true;
                this._ended = false;
            }
            play() {
                if (this._mode === 'native') return this._native.play();
                return new Promise((resolve, reject) => {
                    const tryStart = () => {
                        if (this._rawBuffer && !this._processedBuffer && !this._stretchInFlight) {
                            // Первый реальный Play для этого трека — именно
                            this._stretchInFlight = true;
                            this._rebuildProcessedBuffer().finally(() => { this._stretchInFlight = false; });
                        }
                        if (this._processedBuffer) {
                            if (!this._playing) {
                                const restart = this._startOffset >= this._processedBuffer.duration - 0.01;
                                this._startPlayback(restart ? 0 : this._startOffset);
                            }
                            resolve();
                        } else if (this._loadToken > 0) {
                            setTimeout(tryStart, 50); // ещё грузится/декодируется/считается в воркере — подождём
                        } else {
                            reject(new Error('no source'));
                        }
                    };
                    tryStart();
                });
            }
            pause() {
                if (this._mode === 'native') { this._native.pause(); return; }
                if (!this._playing) return;
                this._startOffset = this.currentTime;
                this._stopSourceNode();
            }
        }

        function getOrCreateSoundEl(ref) {
            if (!soundElByRef[ref]) {
                const a = new RobloxSoundElement();
                // Sound.Ended — реальный сигнал Roblox, на который
                a.addEventListener('ended', () => fireLuaSignal(ref, 'Ended', []));
                // Loaded — раньше нечем было понять, что звук вообще готов
                a.addEventListener('canplaythrough', () => fireLuaSignal(ref, 'Loaded', []));
                // DidLoop — родное 'ended' у зацикленного <audio> (loop=true)
                let _lastT = 0;
                a.addEventListener('timeupdate', () => {
                    if (a.loop && a.currentTime < _lastT - 0.5) fireLuaSignal(ref, 'DidLoop', []);
                    _lastT = a.currentTime;
                });
                // Раньше ошибка загрузки звука (плохой/просроченный
                a.addEventListener('error', () => {
                    const nm = (luaByRef[ref] && luaByRef[ref].name) || ref;
                    logLuaOutput('warn', t('warn_sound_failed', { name: nm, src: a.src || '?' }));
                    // Сама ошибка <audio> не говорит, ПОЧЕМУ не загрузилось —
                    // переспрашиваем /api/asset-proxy напрямую и показываем,
                    // что ответил сервер (тот же приём, что и для текстур:
                    // reportAssetFailure). Без этого "Failed to load sound"
                    // ничего не говорит о причине (401 от Roblox, битый файл,
                    // сеть) — и в этой карте таймер "Time: X.XX" в ChartPlayer
                    // считается от sound.TimePosition, так что незагруженный
                    // звук выглядит как "не идёт время в игре", хотя причина
                    // на самом деле в загрузке трека.
                    const m = a.src && a.src.match(/[?&]id=(\d+)/);
                    if (m) reportAssetFailure(m[1]);
                });
                soundElByRef[ref] = a;
            }
            return soundElByRef[ref];
        }
        function luaSoundControl(ref, action) {
            const a = soundElByRef[ref];
            if (!a) return; // SoundId ещё не задан — играть нечего
            if (action === 'play') {
                // currentTime не сбрасываем — Roblox Sound:Play() на уже
                a.play().catch(() => { }); // автоплей иногда блокируется браузером до первого жеста пользователя — не считаем это ошибкой скрипта
            } else if (action === 'stop') {
                a.pause();
                a.currentTime = 0;
            } else if (action === 'pause') {
                a.pause();
            } else if (action === 'resume') {
                a.play().catch(() => { });
            }
        }

        // Разумные Roblox-дефолты для свойств, которых у этого движка нет
        const GENERIC_PROP_DEFAULTS = {
            Volume: 0.5, PlaybackSpeed: 1, Pitch: 1, TimePosition: 0, SoundId: '',
            Looped: false, Playing: false, PlayOnRemove: false,
        };
        let playSpawnPos = null;   // где персонаж появляется при старте Play и после смерти
        let luaCharDead = false;   // Humanoid.Health дошёл до 0, ждём респавн
        let luaCharSavedMove = null;
        let luaRefProps = {};   // ref -> {Part0|Part1|Attachment0|Attachment1: ref (-1 = nil)} у сварок и констрейнтов
        let luaWelds = [];      // активные WeldConstraint, созданные СКРИПТОМ: {ref, p0, p1, off: Matrix4, prev}
        let luaCloneOrigin = {}; // ref клона -> ref оригинала из файла (Clone() аксессуаров и т.п.)
        let luaCloneSource = {}; // ref клона -> ref того, что клонировали (непосредственный источник)
        let luaAttCF = {};   // ref вложения (Attachment) -> [x,y,z,R00..R22]: Position/CFrame, в т.ч. записанные скриптами
        let luaInitValues = []; // [{ref, value:{k,v}}] — табличные Value из файла, заливаются в Lua после prelude
        let luaGenericPropsByRef = {}; // ref -> {propName: value} — общий "мусорный ящик" для свойств без спец-обработки, чтобы хотя бы запись-потом-чтение работала честно

        function luaGetGenericProp(ref, name) {
            if (name === 'Name' && luaByRef[ref]) return luaByRef[ref].name;
            // Sound — живое состояние реального <audio>, а не то, что
            if (luaByRef[ref] && luaByRef[ref].cls === 'Sound' && soundElByRef[ref]) {
                const a = soundElByRef[ref];
                if (name === 'TimePosition') return a.currentTime || 0;
                if (name === 'IsPlaying' || name === 'Playing') return !a.paused && !a.ended;
                if (name === 'TimeLength' || name === 'Length') return a.duration || 0;
                // Pitch — устаревшее (в реальном Roblox давно заменено
                if (name === 'PlaybackSpeed' || name === 'Pitch') return _soundBaseSpeed[ref] != null ? _soundBaseSpeed[ref] : 1;
            }
            // Sound, чей ассет не загрузился (нет сети/куки) — всё равно «не играет», а не nil (скрипты читают IsPlaying/TimeLength)
            if (luaByRef[ref] && luaByRef[ref].cls === 'Sound' && !soundElByRef[ref]) {
                if (name === 'IsPlaying' || name === 'Playing') return false;
                if (name === 'TimePosition' || name === 'TimeLength' || name === 'Length') return 0;
            }
            // GUI-объекты — ПЕРЕД virtualInstanceProps:
            if (guiPropsByRef[ref] && name in guiPropsByRef[ref]) {
                const v = guiPropsByRef[ref][name];
                // Position/Size — составные UDim2-объекты, мост может
                return (v !== null && typeof v === 'object') ? JSON.stringify(v) : v;
            }
            // Instance.new() — нет меша/тела вообще, все свойства просто
            // лежат в обычном JS-объекте, заведённом при создании.
            if (virtualInstanceProps[ref]) {
                const v = virtualInstanceProps[ref][name];
                if (v !== undefined) return v;
                // клон/Instance.new части без записанного свойства — значения по умолчанию Roblox, а не nil
                if (name === 'CanCollide' || name === 'CanTouch' || name === 'CanQuery') return true;
                if (name === 'Anchored' || name === 'Massless') return false;
                if (name === 'Material' && luaByRef[ref] && /Part|UnionOperation/.test(luaByRef[ref].cls)) return 'Plastic';
                const vcls = luaByRef[ref] && luaByRef[ref].cls;
                if (name === 'Transparency' || name === 'Reflectance') {
                    if (vcls && /Part$|^Part$|MeshPart|UnionOperation|WedgePart|TrussPart|SpawnLocation|Decal|Texture/.test(vcls)) return 0;
                }
                if (vcls === 'ProximityPrompt') {
                    const PD = { HoldDuration: 0, MaxActivationDistance: 10, ActionText: '', ObjectText: '', RequiresLineOfSight: true, Enabled: true, ClickablePrompt: true };
                    if (name in PD) return PD[name];
                }
                return null;
            }
            // ProximityPrompt из файла: свойства лежат в реестре подсказок (JS), а не в generic-пропсах
            if (_promptRegistry[ref]) {
                const pr = _promptRegistry[ref];
                if (name in pr && pr[name] !== undefined && name !== 'parentRef') return pr[name];
                const PD = { HoldDuration: 0, MaxActivationDistance: 10, ActionText: '', ObjectText: '', RequiresLineOfSight: true, Enabled: true, ClickablePrompt: true };
                if (name in PD) return PD[name];
            }
            const mesh = sceneObjs[ref];
            if (name === 'Transparency') {
                return mesh && mesh.material ? 1 - (mesh.material.opacity !== undefined ? mesh.material.opacity : 1) : 0;
            }
            if (name === 'CanCollide') {
                const body = physicsBodies[ref];
                return body ? body.collisionFilterMask !== 0 : true;
            }
            if (luaGenericPropsByRef[ref] && name in luaGenericPropsByRef[ref]) return luaGenericPropsByRef[ref][name];
            if (name in GENERIC_PROP_DEFAULTS) return GENERIC_PROP_DEFAULTS[name];
            return null;
        }
        const VALUE_BASE_CLASSES = new Set(['StringValue', 'NumberValue', 'BoolValue',
            'IntValue', 'ObjectValue', 'Vector3Value', 'CFrameValue', 'Color3Value', 'BrickColorValue']);
        // Смерть персонажа: Humanoid.Died, через Players.RespawnTime (5 c) — новый спавн на старом
        // месте со здоровьем MaxHealth; Player.CharacterRemoving / CharacterAdded стреляют как в Roblox.
        function luaKillCharacter() {
            luaCharDead = true;
            luaCharSavedMove = { walk: charWalkSpeed, jump: charJumpPower };
            charWalkSpeed = 0; charJumpPower = 0;
            logLuaOutput('info', 'Humanoid: Health = 0 — персонаж погиб');
            fireLuaSignal(luaHumanoidRef, 'Died', []);
            const hum = luaHumanoidRef;
            setTimeout(() => {
                if (!isPlaying || hum !== luaHumanoidRef || !luaCharDead) return;
                luaRespawnCharacter();
            }, 5000);
        }
        // Респавн: CharacterRemoving -> персонаж на точке появления своей команды со здоровьем и скоростью -> CharacterAdded.
        // Его вызывает и таймер смерти, и Player:LoadCharacter() (раунды Blaster пересоздают персонажей именно так).
        function luaRespawnCharacter() {
            if (!isPlaying || luaHumanoidRef === -1) return;
            const hum = luaHumanoidRef;
            fireLuaSignal(luaPlayerRef, 'CharacterRemoving', [{ __instanceRef: luaCharacterRef }]);
            if (charBody && playSpawnPos) {
                charBody.position.set(playSpawnPos.x, playSpawnPos.y, playSpawnPos.z);
                charBody.velocity.set(0, 0, 0);
                charBody.wakeUp();
            }
            const hp = virtualInstanceProps[hum];
            hp.Health = hp.MaxHealth != null ? hp.MaxHealth : 100;
            if (luaCharSavedMove) { charWalkSpeed = luaCharSavedMove.walk; charJumpPower = luaCharSavedMove.jump; luaCharSavedMove = null; }
            luaCharDead = false;
            fireLuaSignal(hum, 'HealthChanged', [hp.Health]);
            fireLuaSignal(luaPlayerRef, 'CharacterAdded', [{ __instanceRef: luaCharacterRef }]);
        }
        // part.CollisionGroup = "Pink": тело получает бит группы (форсфилды команд: свои проходят, чужие нет).
        // Вызывается ДО ветки virtualInstanceProps — иначе у виртуальных частей персонажа (HumanoidRootPart) значение
        // просто оседало в словаре и тело игрока оставалось в группе Default.
        function luaSetCollisionGroup(ref, value) {
            luaPartGroup[ref] = value;
            if (virtualInstanceProps[ref]) virtualInstanceProps[ref].CollisionGroup = value;
            else (luaGenericPropsByRef[ref] = luaGenericPropsByRef[ref] || {}).CollisionGroup = value;
            const body = physicsBodies[ref];
            if (body) { body.__rbxGroup = value; luaApplyGroup(body); }
            // часть персонажа -> группа тела игрока (в приложении весь персонаж — один charBody)
            if (charBody && luaIsCharRef(ref)) { charBody.__rbxGroup = value; luaApplyGroup(charBody); }
        }
        function luaSetGenericProp(ref, name, value) {
            if (name === 'Name' && luaByRef[ref]) {
                luaByRef[ref].name = String(value);
                if (guiPropsByRef[ref]) {
                    guiPropsByRef[ref].Name = String(value);
                    // SortOrder = Name: смена имени меняет порядок в UIListLayout/UIGridLayout родителя (слоты хотбара: frame.Name = position)
                    const gp = luaParentByRef[ref];
                    if (gp !== undefined && gp !== -1) { try { applyUIListLayout(gp); } catch (e) { /* DOM ещё нет */ } }
                }
                return;
            }
            if (name === 'CollisionGroup') { luaSetCollisionGroup(ref, value); return; }
            // ValueBase.Value — раньше запись просто клалась в общий
            // "мусорный ящик" свойств и на этом всё: сигнал .Changed
            // никогда не стрелял. Это крайне частый паттерн в реальных
            // играх (StringValue как канал связи между скриптами,
            // например CurrentSong в этой карте) — "obj.Changed:Connect(...)"
            // просто никогда не срабатывал, и весь код внутри (в этой карте
            // — включение камеры песни, MenuCamera.lua) не выполнялся ВООБЩЕ,
            // без единой ошибки — выглядело как "телепорт не работает",
            // хотя сам расчёт камеры (уже проверенный) был ни при чём.
            if (name === 'Value' && luaByRef[ref] && VALUE_BASE_CLASSES.has(luaByRef[ref].cls)) {
                (luaGenericPropsByRef[ref] = luaGenericPropsByRef[ref] || {}).Value = value;
                fireLuaSignal(ref, 'Changed', [value]);
                return;
            }
            // Sound — до GUI/virtualInstanceProps веток:
            if (luaByRef[ref] && luaByRef[ref].cls === 'Sound') {
                if (name === 'SoundId') {
                    const url = rbxAssetIdToProxyUrl(value);
                    const a = getOrCreateSoundEl(ref);
                    if (url) a.src = url;
                } else if (name === 'Volume') {
                    getOrCreateSoundEl(ref).volume = Math.max(0, Math.min(1, Number(value) || 0));
                } else if (name === 'Looped') {
                    getOrCreateSoundEl(ref).loop = !!value;
                } else if (name === 'PlaybackSpeed' || name === 'Pitch') {
                    // Оба свойства — один и тот же множитель (см.
                    _soundBaseSpeed[ref] = Number(value) || 1;
                    _applySoundRate(ref);
                } else if (name === 'TimePosition') {
                    getOrCreateSoundEl(ref).currentTime = Number(value) || 0;
                }
                // Падаем ДАЛЬШЕ (не return) — значение всё равно кладём в
            }
            // PitchShiftSoundEffect.Octave/.Enabled — НАСТОЯЩИЙ Roblox-
            if (luaByRef[ref] && luaByRef[ref].cls === 'PitchShiftSoundEffect' && (name === 'Octave' || name === 'Enabled')) {
                const soundRef = luaParentByRef[ref];
                if (soundRef !== undefined && luaByRef[soundRef] && luaByRef[soundRef].cls === 'Sound') {
                    const enabled = name === 'Enabled' ? !!value : (luaGenericPropsByRef[ref] ? luaGenericPropsByRef[ref].Enabled !== false : true);
                    const octave = name === 'Octave' ? Number(value) || 0 : (luaGenericPropsByRef[ref] ? Number(luaGenericPropsByRef[ref].Octave) || 0 : 0);
                    _soundPitchOctave[soundRef] = enabled ? octave : 0;
                    _applySoundRate(soundRef);
                }
            }
            // GUI — ПЕРЕД virtualInstanceProps, той же причине, что и в
            if (guiPropsByRef[ref]) {
                if (guiPatchProp(ref, name, value)) { surfaceGuiMarkDirty(ref); return; }
            }
            if (_promptRegistry[ref] && name in _promptRegistry[ref]) {
                _promptRegistry[ref][name] = value;
            }
            if (name === 'Anchored' && ref !== luaHumanoidRootPartRef) {
                // Anchored=false — деталь становится динамической (падает, летит,
                // получает AssemblyLinearVelocity); true — снова статична.
                const abody = physicsBodies[ref];
                if (abody && typeof CANNON !== 'undefined') {
                    if (!value) {
                        if (!(abody.mass > 0)) abody.mass = 1;
                        abody.type = CANNON.Body.DYNAMIC;
                        abody.updateMassProperties();
                        abody.allowSleep = true;
                        abody.wakeUp();
                        luaPromoteResting(abody);
                    } else {
                        abody.type = CANNON.Body.STATIC;
                        abody.mass = 0;
                        abody.updateMassProperties();
                        abody.velocity.set(0, 0, 0);
                        abody.angularVelocity.set(0, 0, 0);
                    }
                    abody.aabbNeedsUpdate = true;
                }
            }
            if (ref === luaHumanoidRef && name === 'Health') {
                // Health зажат в [0, MaxHealth]; дошёл до 0 — Died, затем респавн (как в Roblox)
                const hp = virtualInstanceProps[ref];
                let nv = Number(value);
                if (!Number.isFinite(nv)) return;
                nv = Math.max(0, Math.min(nv, hp.MaxHealth != null ? hp.MaxHealth : 100));
                const old = hp.Health;
                hp.Health = nv;
                if (nv !== old) fireLuaSignal(ref, 'HealthChanged', [nv]);
                if (nv <= 0 && !luaCharDead) luaKillCharacter();
                return;
            }
            if (ref === luaHumanoidRef && name === 'JumpHeight' && Number(value) <= 0) charJumpPower = 0;
            if (ref === luaHumanoidRef && (name === 'WalkSpeed' || name === 'JumpPower')) {
                // Скрипт поменял скорость/прыжок — пишем в Output, кто и на что
                // (раньше «персонаж не двигается» невозможно было отследить).
                const nv = Number(value);
                if (!Number.isFinite(nv)) {
                    logLuaOutput('warn', 'Humanoid.' + name + ': значение не число (' + String(value) + ') — проигнорировано');
                } else if (name === 'WalkSpeed') charWalkSpeed = nv;
                else charJumpPower = nv;
            }
            if (virtualInstanceProps[ref]) { virtualInstanceProps[ref][name] = value; return; }
            const mesh = sceneObjs[ref];
            if (name === 'Color' && mesh && mesh.material && value && typeof value === 'object' && 'r' in value) {
                // Цвет детали: материалы общие (кеш по цвету), поэтому красим СВОЮ копию; текстурные грани
                // (Decal) не трогаем — цвет детали на них не влияет.
                const col = new THREE.Color(value.r, value.g, value.b);
                const tint = (m) => {
                    if (m.map) return m;
                    if (m.userData && m.userData.ownColor) { m.color.copy(col); return m; }
                    const c = m.clone(); c.userData = Object.assign({}, m.userData, { ownColor: true }); c.color.copy(col); return c;
                };
                mesh.material = Array.isArray(mesh.material) ? mesh.material.map(tint) : tint(mesh.material);
                return;
            }
            if (name === 'Transparency' && mesh && mesh.material) {
                // Материалы деталей ОБЩИЕ (кеш по цвету/прозрачности): раньше opacity менялся прямо у общего
                // материала, и когда скрипт босса делал setVisibility(0), пропадали ВСЕ детали того же цвета
                // (серые стены и т.д.). Теперь у детали своя копия материала (создаётся один раз).
                const tr = Math.max(0, Math.min(1, Number(value) || 0));
                const own = (m) => {
                    if (m.map) return m;                       // грань с текстурой (Decal) — не трогаем
                    if (m.userData && m.userData.ownMat) return m;
                    const c = m.clone(); c.userData = Object.assign({}, m.userData, { ownMat: true }); return c;
                };
                mesh.material = Array.isArray(mesh.material) ? mesh.material.map(own) : own(mesh.material);
                for (const m of (Array.isArray(mesh.material) ? mesh.material : [mesh.material])) {
                    if (m.map) continue;
                    m.transparent = tr > 0;
                    m.opacity = 1 - tr;
                }
                return;
            }
            if (name === 'CanCollide') {
                const body = physicsBodies[ref];
                if (body) {
                    body.__noCollide = !value;
                    if (value) luaApplyGroup(body); else body.collisionFilterMask = 0;
                }
                return;
            }
            (luaGenericPropsByRef[ref] = luaGenericPropsByRef[ref] || {})[name] = value;
        }
        // Отдельный, СЫРОЙ индекс иерархии для Lua-моста — специально НЕ
        let luaByRef = {};          // ref -> {cls, name}
        let luaByRefVer = 0;        // растёт при любом добавлении/удалении записи (кэши списков деталей)
        let luaParentByRef = {};    // ref -> parentRef
        let luaChildrenByRef = {};  // ref -> [childRef, ...]
        // Instance.new() создаёт объекты без меша/физики — их произвольные
        let virtualInstanceProps = {}; // ref -> {propName: value}
        let luaNextVirtualRef = -1000; // счётчик вниз — не пересекается ни с
        // реальными ref'ами карты (положительные), ни с сентинелом "нет
        // инстанса" (-1, см. wrap() в LUA_PRELUDE).

        // ============ Сигналы/RemoteEvent — общее для обеих VM состояние ============
        let luaSignalConns = {};   // id -> {L, fnRef, ref, evName}
        let luaSignalsByKey = {};  // "ref|evName" -> [id, ...]
        let luaNextSignalId = 1;
        let remoteQueue = [];      // [{ref, targetSide, args, dueAt}] — см. __fire_remote

        // Резолвит и дёргает все Connect-колбэки для (ref, evName) — общий
        function pushLuaSignalArgs(L, args) {
            const { lua } = window.fengari;
            let n = 0;
            for (const a of (args || [])) {
                if (a && typeof a === 'object' && '__instanceRef' in a) {
                    lua.lua_getglobal(L, '__wrap');
                    lua.lua_pushnumber(L, a.__instanceRef);
                    lua.lua_call(L, 1, 1);
                } else if (a && typeof a === 'object' && a.__enum) {
                    // Enum.<Type>.<Name> — тот же кэшированный объект, что видит скрипт
                    // (сравнение inputType == Enum.ProximityPromptInputType.Touch — по ссылке)
                    lua.lua_getglobal(L, 'Enum');
                    lua.lua_getfield(L, -1, a.__enum[0]);
                    lua.lua_getfield(L, -1, a.__enum[1]);
                    lua.lua_remove(L, -2);
                    lua.lua_remove(L, -2);
                } else if (typeof a === 'number') lua.lua_pushnumber(L, a);
                else if (typeof a === 'boolean') lua.lua_pushboolean(L, a);
                else if (a === null || a === undefined) lua.lua_pushnil(L);
                else lua.lua_pushstring(L, String(a));
                n++;
            }
            return n;
        }

        function fireLuaSignal(ref, evName, args) {
            const { lua } = window.fengari;
            const ids = (luaSignalsByKey[ref + '|' + evName] || []).slice();
            for (const id of ids) {
                const conn = luaSignalConns[id];
                if (!conn) continue;
                const L = conn.L;
                // Раньше здесь напрямую доставали саму Lua-функцию через
                const co = lua.lua_newthread(L);
                lua.lua_getglobal(co, '__invoke_conn');
                lua.lua_pushnumber(co, id);
                const n = 1 + pushLuaSignalArgs(co, args);
                const status = lua.lua_resume(co, null, n);
                // lua_newthread положил co на стек L (побочный эффект) —
                lua.lua_pop(L, 1);
                if (status !== lua.LUA_OK && status !== lua.LUA_YIELD) {
                    logLuaOutput('error', luaErrToString(co), evName, null, L === luaServerL ? 'Script' : 'LocalScript');
                }
            }
            // Будим тех, кто спал в Event:Wait()/:wait() именно на этот
            if (luaSignalWaits.length) {
                const ready = luaSignalWaits.filter(w => w.ref === ref && w.evName === evName);
                if (ready.length) {
                    luaSignalWaits = luaSignalWaits.filter(w => !(w.ref === ref && w.evName === evName));
                    for (const w of ready) {
                        const n = pushLuaSignalArgs(w.co, args);
                        resumeLuaCoroutine(w.co, evName, n);
                    }
                }
            }
        }

        // Обрабатывает очередь __fire_remote — вызывается из того же тика
        function processRemoteQueue() {
            if (!remoteQueue.length) return;
            const now = performance.now();
            const ready = remoteQueue.filter(x => x.dueAt <= now);
            if (!ready.length) return;
            remoteQueue = remoteQueue.filter(x => x.dueAt > now);
            for (const item of ready) {
                const evName = item.targetSide === 'server' ? 'OnServerEvent' : 'OnClientEvent';
                // RemoteEvent.OnServerEvent(player, ...) — player ПЕРВЫМ
                const args = evName === 'OnServerEvent'
                    ? [{ __instanceRef: luaPlayerRef }, ...item.args]
                    : item.args;
                fireLuaSignal(item.ref, evName, args);
            }
        }

        function luaResetSignals() {
            luaAttrs = {}; luaTags = {};
            for (const r in luaFileAttrs) luaAttrs[r] = Object.assign({}, luaFileAttrs[r]);
            for (const r in luaFileTags) luaTags[r] = new Set(luaFileTags[r]);
            luaSignalConns = {};
            luaSignalsByKey = {};
            luaNextSignalId = 1;
            remoteQueue = [];
            lastRunServiceTick = null; // иначе первый Heartbeat/Stepped после
            // следующего Play дал бы огромную dt — разницу с моментом,
            // когда игра была остановлена в прошлый раз.
        }

        function luaWorkspaceRef() {
            for (const ref in luaByRef) {
                if (luaByRef[ref].cls === 'Workspace') return parseInt(ref);
            }
            return -1;
        }
        function luaFindServiceRef(name) {
            for (const ref in luaByRef) {
                if (luaByRef[ref].cls === name && luaParentByRef[ref] === -1) return parseInt(ref);
            }
            return -1;
        }
        // Корневые сервисы (Workspace/Players/ReplicatedStorage/...) — их
        function luaRootRefs() {
            const out = [];
            for (const ref in luaParentByRef) {
                if (luaParentByRef[ref] === -1) out.push(parseInt(ref));
            }
            return out;
        }
        // Классы, у которых есть визуальное GUI-представление в DOM-оверлее
        const GUI_CLASS_NAMES = new Set([
            'ScreenGui', 'BillboardGui', 'SurfaceGui', 'Frame', 'ScrollingFrame', 'CanvasGroup',
            'TextLabel', 'TextButton', 'TextBox', 'ImageLabel', 'ImageButton',
            'UIListLayout', 'UIGridLayout', 'UIPadding', 'UICorner', 'UIStroke',
            'UIAspectRatioConstraint', 'UIGradient', 'UIScale',
        ]);
        function luaCreateVirtualInstance(className) {
            const ref = luaNextVirtualRef--;
            luaByRef[ref] = { cls: className, name: className }; luaByRefVer++;
            luaParentByRef[ref] = -1;
            virtualInstanceProps[ref] = {};
            // Instance.new("TextButton") и т.п.
            if (GUI_CLASS_NAMES.has(className)) {
                guiPropsByRef[ref] = { ref, cls: className, Name: className, parent: -1 };
            }
            // ProximityPrompt почти всегда создаётся СКРИПТОМ в рантайме
            // (Instance.new("ProximityPrompt")), а не хранится в файле —
            // например, в холодильнике из этого разговора подсказку
            // "Спрятаться"/"Выкинуть полки" создаёт сам Script карты. Раньше
            // список подсказок брался ТОЛЬКО из файла один раз при старте
            // Play — такие подсказки никогда не появлялись вообще. Заводим
            // запись в реестре сразу при создании; .Parent и свойства
            // подтянутся через luaSetParent/luaSetGenericProp ниже.
            if (className === 'ProximityPrompt') {
                _promptRegistry[ref] = _defaultPromptEntry(); // parent проставится через luaSetParent
            }
            return ref;
        }
        // Script, склонированный через :Clone() ВО ВРЕМЯ игры (холодильники/двери/лифты, которые
        // карта размножает из шаблона), раньше не запускался вообще: скрипты стартуют ОДИН раз из
        // файла при нажатии Play, а у виртуального клона нет ни Source, ни запуска — у копии не было
        // ни ProximityPrompt, ни двери. Как в Roblox: когда клон оказывается в Workspace /
        // ServerScriptService — его Script-ы запускаются (script.Parent = склонированный контейнер).
        let luaScriptsByRef = {};            // ref скрипта из файла -> {ref,name,cls,source,...} (из /api/scripts)
        let luaStartedClonedScripts = new Set();
        function luaIsUnderServerContainer(ref) {
            let cur = ref, g = 0, viaBackpack = false;
            while (cur !== undefined && cur !== -1 && g++ < 200) {
                const i = luaByRef[cur];
                if (i && i.cls === 'Backpack') viaBackpack = true;
                if (i && luaParentByRef[cur] === -1) {
                    // Script внутри Tool в Backpack игрока (Players/<Игрок>/Backpack) в Roblox выполняется
                    return i.cls === 'Workspace' || i.cls === 'ServerScriptService' || (i.cls === 'Players' && viaBackpack);
                }
                cur = luaParentByRef[cur];
            }
            return false;
        }
        function luaIsUnderWorkspace(ref) {
            let cur = ref, g = 0;
            while (cur !== undefined && cur !== -1 && g++ < 200) {
                if (luaParentByRef[cur] === -1) return !!(luaByRef[cur] && luaByRef[cur].cls === 'Workspace');
                cur = luaParentByRef[cur];
            }
            return false;
        }
        // Клон детали из файла (UnionOperation/MeshPart/Part холодильника) — пустой виртуальный инстанс: без меша и физики
        // он стоял в (0,0,0) невидимкой. Когда клон попадает в Workspace — строим ему меш и тело по данным оригинала,
        // в позиции, которую клону выставили Clone()/PivotTo (luaPartXform).
        function luaRealizeClonedParts(root) {
            if (!isPlaying || !luaIsUnderWorkspace(root)) return;
            const stack = [root];
            while (stack.length) {
                const r0 = stack.pop();
                for (const c of (luaChildrenByRef[r0] || [])) stack.push(c);
                const origin = luaCloneOrigin[r0];
                if (origin === undefined || sceneObjs[r0]) continue;
                const o = playObjData[origin];
                if (!o) continue;
                try { addPhysicsBodyForObj(Object.assign({}, o, { ref: r0 })); }
                catch (e) { console.warn('Clone: меш/физика клона не построены:', e); }
            }
        }
        function luaStartClonedScripts(root) {
            if (!luaServerL || !luaIsUnderServerContainer(root)) return;
            const stack = [root];
            while (stack.length) {
                const r0 = stack.pop();
                for (const c of (luaChildrenByRef[r0] || [])) stack.push(c);
                const info = luaByRef[r0];
                if (!info || info.cls !== 'Script' || luaStartedClonedScripts.has(r0)) continue;
                const origin = luaCloneOrigin[r0];
                const scr = origin !== undefined ? luaScriptsByRef[origin] : undefined;
                if (!scr || scr.disabled) continue;
                luaStartedClonedScripts.add(r0);
                const runAs = Object.assign({}, scr, { ref: r0, cls: 'Script' });
                // отложенно: как в Roblox, скрипт клона стартует после того, как текущий код доработал до yield
                setTimeout(() => {
                    if (!isPlaying || !luaServerL) return;
                    try { runLuaScript(runAs, luaServerL); }
                    catch (e) { logLuaOutput('error', scr.name + ': ' + e.message, scr.name, null, 'Script'); }
                }, 0);
            }
        }
        function luaCloneRef(ref) {
            // Instance:Clone() — новый виртуальный ref с тем же классом/именем
            const src = luaByRef[ref];
            const cls = src ? src.cls : 'Instance';
            const newRef = luaCreateVirtualInstance(cls);
            luaCloneOrigin[newRef] = luaCloneOrigin[ref] !== undefined ? luaCloneOrigin[ref] : ref;
            luaCloneSource[newRef] = ref;
            if (src) luaByRef[newRef].name = src.name;
            if (virtualInstanceProps[ref]) {
                virtualInstanceProps[newRef] = Object.assign({}, virtualInstanceProps[ref]);
            }
            // Clone() копирует и атрибуты, и теги (раньше у клона холодильника GetAttribute("HideOffset"/"Yaw") был nil)
            if (luaAttrs[ref]) luaAttrs[newRef] = Object.assign({}, luaAttrs[ref]);
            if (luaTags[ref]) luaTags[newRef] = new Set(luaTags[ref]);
            // Sound: у клона раньше не было аудио-элемента (SoundId лежал только у оригинала), поэтому
            // sound:Clone():Play() молчал, а luaSoundControl тихо выходил с «SoundId ещё не задан».
            // свойства «мусорного ящика» (Tool.TextureId/ToolTip из файла и т.п.) копируются у любого класса, не только у Sound
            if (luaGenericPropsByRef[ref]) luaGenericPropsByRef[newRef] = Object.assign({}, luaGenericPropsByRef[ref]);
            if (cls === 'Sound') {
                const sa = soundElByRef[ref];
                if (sa) {
                    const na = getOrCreateSoundEl(newRef);
                    if (sa.src) na.src = sa.src;
                    na.volume = sa.volume;
                    na.loop = sa.loop;
                    if (_soundBaseSpeed[ref] != null) _soundBaseSpeed[newRef] = _soundBaseSpeed[ref];
                    if (_soundPitchOctave[ref] != null) _soundPitchOctave[newRef] = _soundPitchOctave[ref];
                    _applySoundRate(newRef);
                }
            }
            const p = luaPositionOfRef(ref);
            if (p) luaSetPositionOfRef(newRef, p.x, p.y, p.z);
            // Клон детали должен повторять и ПОВОРОТ оригинала (раньше копировалась только позиция —
            // клоны повёрнутых лифтов/дверей вставали «прямо», а PivotTo считался от неверной матрицы).
            if (luaIsPartRef(ref) && !luaIsCharRef(ref)) {
                try { luaApplyPartMatrix(newRef, luaPartMatrix(ref)); } catch (e) { console.warn('Clone: поворот не скопирован:', e); }
            }
            // GUI (Frame/TextButton/...) раньше тут вообще не копировался —
            if (guiPropsByRef[ref]) {
                cloneGuiSubtreeInto(ref, newRef);
            } else {
                // Instance:Clone() копирует и ВСЕХ потомков (Accessory -> Handle -> SpecialMesh/Weld ...):
                // раньше клон приходил пустым, и FindFirstChild("Handle") у склонированного аксессуара был nil.
                for (const childRef of (luaChildrenByRef[ref] || [])) {
                    if (!luaByRef[childRef]) continue;
                    luaSetParent(luaCloneRef(childRef), newRef);
                }
            }
            // PrimaryPart клона Model — КОПИЯ той же детали внутри клона (если PrimaryPart лежал вне модели, у клона nil)
            const rpp0 = luaRefProps[ref];
            if (rpp0 && rpp0.PrimaryPart !== undefined && rpp0.PrimaryPart !== -1) {
                let found = -1;
                const stk = [newRef];
                while (stk.length) {
                    const x = stk.pop();
                    if (x !== newRef && luaCloneSource[x] === rpp0.PrimaryPart) { found = x; break; }
                    for (const c of (luaChildrenByRef[x] || [])) stk.push(c);
                }
                (luaRefProps[newRef] = luaRefProps[newRef] || {}).PrimaryPart = found;
            }
            // Пивот контейнера (Model/Folder): клон наследует пивот оригинала (WorldPivotData), иначе
            // PivotTo(клона) считался бы от центра габаритов и клон вставал бы со смещением.
            if (!luaIsPartRef(ref) && !luaIsCharRef(ref) && !luaIsCameraRef(ref) && (_modelPivots[ref] || luaFilePivots[ref])) {
                _modelPivots[newRef] = luaGetPivotMatrix(ref).clone();
            }
            return newRef;
        }
        // Общая рекурсивная копия GUI-поддерева — используется и Clone()
        function cloneGuiSubtreeInto(origRef, newRef) {
            guiPropsByRef[newRef] = Object.assign({}, guiPropsByRef[origRef], { cls: luaByRef[newRef].cls, ref: newRef, parent: luaParentByRef[newRef] });
            for (const childRef of (luaChildrenByRef[origRef] || [])) {
                const childInfo = luaByRef[childRef];
                if (!childInfo) continue;
                const newChildRef = luaCreateVirtualInstance(childInfo.cls);
                luaByRef[newChildRef].name = childInfo.name;
                if (virtualInstanceProps[childRef]) {
                    virtualInstanceProps[newChildRef] = Object.assign({}, virtualInstanceProps[childRef]);
                }
                if (guiPropsByRef[childRef]) {
                    guiPropsByRef[newChildRef] = Object.assign({}, guiPropsByRef[childRef], { cls: childInfo.cls, ref: newChildRef });
                }
                luaSetParent(newChildRef, newRef);
                if (guiPropsByRef[childRef]) cloneGuiSubtreeInto(childRef, newChildRef);
            }
        }
        function luaSetParent(ref, parentRef) {
            const oldParent = luaParentByRef[ref];
            if (oldParent !== undefined && luaChildrenByRef[oldParent]) {
                luaChildrenByRef[oldParent] = luaChildrenByRef[oldParent].filter(c => c !== ref);
            }
            luaParentByRef[ref] = parentRef;
            if (parentRef !== -1) {
                (luaChildrenByRef[parentRef] = luaChildrenByRef[parentRef] || []).push(ref);
            }
            // ProximityPrompt.Parent = somePart — дистанция меряется от
            // родителя, так что перепривязку нужно отслеживать так же, как
            // и создание (см. luaCreateVirtualInstance).
            if (_promptRegistry[ref]) _promptRegistry[ref].parentRef = parentRef;
            // GUI-репарентинг (например, songCard.Parent = scroll после
            if (guiPropsByRef[ref]) {
                if (oldParent !== undefined && guiChildrenByRef[oldParent]) {
                    guiChildrenByRef[oldParent] = guiChildrenByRef[oldParent].filter(c => c !== ref);
                }
                if (parentRef !== -1) {
                    (guiChildrenByRef[parentRef] = guiChildrenByRef[parentRef] || []).push(ref);
                }
                const selfProps = guiPropsByRef[ref];
                const isDecoration = selfProps.cls === 'UICorner' || selfProps.cls === 'UIStroke';
                const parentEl = guiDomByRef[parentRef];
                if (isDecoration) {
                    // Instance.new("UICorner"); corner.Parent = frame —
                    if (parentEl) applyGuiDecoration(parentEl, selfProps);
                } else {
                    let el = guiDomByRef[ref];
                    if (el && parentEl) {
                        parentEl.appendChild(el); // уже был в DOM (редкий, но валидный повторный репарентинг) — просто переносим узел
                    } else if (!el && parentEl) {
                        guiRenderNode(ref, parentEl); // первое появление в DOM — вместе со всем поддеревом (рекурсивно)
                    } else if (el && !parentEl) {
                        el.remove(); // новый родитель ещё не отрисован (или это Parent=nil) — прячем, пока не понадобится
                        delete guiDomByRef[ref];
                    }
                }
                // Пере-раскладка списка (см.
                if (oldParent !== undefined) applyUIListLayout(oldParent);
                if (parentRef !== -1) applyUIListLayout(parentRef);
            }
            if (parentRef !== -1 && luaByRef[ref] && luaByRef[ref].cls === 'WeldConstraint') luaRegisterWeld(ref);
            if (luaCharacterRef !== -1 && (parentRef === luaCharacterRef || oldParent === luaCharacterRef)) {
                const _oc = luaByRef[ref] && luaByRef[ref].cls;
                if (_oc === 'Accessory' || _oc === 'BodyColors') scheduleCharacterOutfit();
            }
            // Настоящее, а не заглушечное срабатывание — ChildAdded/ChildRemoved
            if (oldParent !== undefined && oldParent !== -1 && oldParent !== parentRef) {
                fireLuaSignal(oldParent, 'ChildRemoved', [{ __instanceRef: ref }]);
            }
            if (parentRef !== -1 && parentRef !== oldParent) {
                fireLuaSignal(parentRef, 'ChildAdded', [{ __instanceRef: ref }]);
            }
            // Tool перешёл в персонажа / вышел из него — Equipped / Unequipped (как в Roblox; на этом строится хотбар)
            if (luaByRef[ref] && luaByRef[ref].cls === 'Tool' && luaCharacterRef !== -1) {
                if (parentRef === luaCharacterRef && oldParent !== luaCharacterRef) fireLuaSignal(ref, 'Equipped', []);
                else if (oldParent === luaCharacterRef && parentRef !== luaCharacterRef) fireLuaSignal(ref, 'Unequipped', []);
            }
            if (parentRef !== -1) { luaRealizeClonedParts(ref); luaStartClonedScripts(ref); }
        }
        function luaDestroyRef(ref) {
            if (playOnlyRefs.has(ref)) {
                removePhysicsBodyForRef(ref);
            } else {
                const mesh = sceneObjs[ref];
                if (mesh) mesh.visible = false;
                const body = physicsBodies[ref];
                if (body && body !== charBody && physicsWorld) { physicsWorld.removeBody(body); delete physicsBodies[ref]; }
            }
            // GUI-узлы (ScreenGui/Frame/TextLabel/...) тут вообще не
            const guiEl = guiDomByRef[ref];
            if (guiEl) {
                if (guiEl.parentNode) guiEl.parentNode.removeChild(guiEl);
                delete guiDomByRef[ref];
                delete guiPropsByRef[ref];
            }
            const guiParentRef = luaParentByRef[ref];
            if (guiParentRef !== undefined && guiChildrenByRef[guiParentRef]) {
                guiChildrenByRef[guiParentRef] = guiChildrenByRef[guiParentRef].filter(c => c !== ref);
                applyUIListLayout(guiParentRef); // осиротевшие места в списке (см. applyUIListLayout)
            }
            delete guiChildrenByRef[ref];
            const parentRef = luaParentByRef[ref];
            if (parentRef !== undefined && luaChildrenByRef[parentRef]) {
                luaChildrenByRef[parentRef] = luaChildrenByRef[parentRef].filter(c => c !== ref);
            }
            delete luaByRef[ref]; luaByRefVer++;
            delete luaParentByRef[ref];
            delete luaChildrenByRef[ref];
            delete virtualInstanceProps[ref];
        }

        function installLuaBridge(L) {
            const { lua } = window.fengari;
            function def(name, fn) {
                lua.lua_pushcfunction(L, fn);
                lua.lua_setglobal(L, name);
            }
            def('print', function (L2) {
                const n = lua.lua_gettop(L2), parts = [];
                for (let i = 1; i <= n; i++) parts.push(luaArgToDisplay(L2, i));
                logLuaOutput('print', parts.join('\t'), luaScriptNameByCo.get(L2), null, luaScriptSideByCo.get(L2));
                return 0;
            });
            def('warn', function (L2) {
                const n = lua.lua_gettop(L2), parts = [];
                for (let i = 1; i <= n; i++) parts.push(luaArgToDisplay(L2, i));
                logLuaOutput('warn', parts.join('\t'), luaScriptNameByCo.get(L2), null, luaScriptSideByCo.get(L2));
                return 0;
            });
            def('tick', function (L2) { lua.lua_pushnumber(L2, performance.now() / 1000); return 1; });
            // __raycast(mode, ox,oy,oz, dx,dy,dz, ...filterRefs) -> ref, px,py,pz, nx,ny,nz, dist | nil
            // mode 0 = Exclude (пропускаем потомков filterRefs), 1 = Include (только потомки filterRefs).
            // Лучом бьём по всем мешам сцены (как Roblox: CanCollide/Transparency не важны), берём ближайшее попадание.
            // __fire_signal(ref, evName): выстрелить событие инстанса из Lua (Tool.Equipped/Unequipped и т.п.)
            // __gui_at_pos(x, y) -> "ref,ref,..." — GUI-узлы под точкой (клиентские координаты), верхний первым
            def('__gui_at_pos', function (L2) {
                const ovr = _guiOverlayRect();
                const x = ovr.left + lua.lua_tonumber(L2, 1) * guiScale, y = ovr.top + lua.lua_tonumber(L2, 2) * guiScale;
                const rev = new Map();
                for (const k in guiDomByRef) rev.set(guiDomByRef[k], Number(k));
                const out = [], seen = new Set();
                for (const el of document.elementsFromPoint(x, y)) {
                    let cur = el;
                    while (cur && cur !== document.body) {
                        const r = rev.get(cur);
                        if (r !== undefined) { if (!seen.has(r)) { seen.add(r); out.push(r); } break; }
                        cur = cur.parentElement;
                    }
                }
                lua.lua_pushstring(L2, out.join(','));
                return 1;
            });
            def('__fire_signal', function (L2) {
                try { fireLuaSignal(lua.lua_tointeger(L2, 1), lua.lua_tojsstring(L2, 2), []); } catch (e) { console.warn('__fire_signal:', e); }
                return 0;
            });
            def('__raycast', function (L2) {
                try {
                    const n = lua.lua_gettop(L2);
                    const mode = lua.lua_tointeger(L2, 1);
                    const num = (i) => lua.lua_tonumber(L2, i);
                    const o = new THREE.Vector3(num(2), num(3), num(4));
                    const d = new THREE.Vector3(num(5), num(6), num(7));
                    const len = d.length();
                    if (!(len > 1e-9)) { lua.lua_pushnil(L2); return 1; }
                    d.divideScalar(len);
                    const roots = new Set();
                    for (let i = 8; i <= n; i++) roots.add(lua.lua_tointeger(L2, i));
                    const inFilter = (ref) => {
                        let cur = ref, g = 0;
                        while (cur !== undefined && cur !== -1 && g++ < 200) {
                            if (roots.has(cur)) return true;
                            cur = luaParentByRef[cur];
                        }
                        return false;
                    };
                    const targets = [];
                    for (const k in sceneObjs) { const m = sceneObjs[k]; if (m) targets.push(m); }
                    const rc = new THREE.Raycaster(o, d, 0, len);
                    const hits = rc.intersectObjects(targets, true);
                    for (const h of hits) {
                        let obj = h.object, ref;
                        while (obj) { if (obj.userData && obj.userData.ref !== undefined) { ref = obj.userData.ref; break; } obj = obj.parent; }
                        if (ref === undefined || !luaIsUnderWorkspace(ref)) continue;
                        if (mode === 1 ? !inFilter(ref) : (roots.size > 0 && inFilter(ref))) continue;
                        const nrm = h.face ? h.face.normal.clone().transformDirection(h.object.matrixWorld).normalize() : d.clone().negate();
                        lua.lua_pushinteger(L2, ref);
                        lua.lua_pushnumber(L2, h.point.x); lua.lua_pushnumber(L2, h.point.y); lua.lua_pushnumber(L2, h.point.z);
                        lua.lua_pushnumber(L2, nrm.x); lua.lua_pushnumber(L2, nrm.y); lua.lua_pushnumber(L2, nrm.z);
                        lua.lua_pushnumber(L2, h.distance);
                        return 8;
                    }
                } catch (e) { console.warn('Raycast:', e); }
                lua.lua_pushnil(L2);
                return 1;
            });
            def('wait', function (L2) {
                const secs = lua.lua_isnumber(L2, 1) ? lua.lua_tonumber(L2, 1) : 0.03;
                luaWaits.push({ co: L2, resumeAt: performance.now() + Math.max(0, secs) * 1000 });
                return lua.lua_yield(L2, 0);
            });
            // JSONEncode/JSONDecode — HttpService:JSONDecode(...) раньше не
            function pushJsAsLua(L2, v) {
                if (v === null || v === undefined) { lua.lua_pushnil(L2); return; }
                if (typeof v === 'number') { lua.lua_pushnumber(L2, v); return; }
                if (typeof v === 'boolean') { lua.lua_pushboolean(L2, v); return; }
                if (typeof v === 'string') { lua.lua_pushstring(L2, v); return; }
                if (Array.isArray(v)) {
                    lua.lua_createtable(L2, v.length, 0);
                    for (let i = 0; i < v.length; i++) {
                        pushJsAsLua(L2, v[i]);
                        lua.lua_rawseti(L2, -2, i + 1);
                    }
                    return;
                }
                if (typeof v === 'object') {
                    lua.lua_createtable(L2, 0, Object.keys(v).length);
                    for (const k in v) {
                        lua.lua_pushstring(L2, k);
                        pushJsAsLua(L2, v[k]);
                        lua.lua_rawset(L2, -3);
                    }
                    return;
                }
                lua.lua_pushnil(L2);
            }
            function luaToJs(L2, idx) {
                const ty = lua.lua_type(L2, idx);
                if (ty === lua.LUA_TNIL) return null;
                if (ty === lua.LUA_TBOOLEAN) return !!lua.lua_toboolean(L2, idx);
                if (ty === lua.LUA_TNUMBER) return lua.lua_tonumber(L2, idx);
                if (ty === lua.LUA_TSTRING) return lua.lua_tojsstring(L2, idx);
                if (ty === lua.LUA_TTABLE) {
                    const n = lua.lua_rawlen(L2, idx);
                    if (n > 0) {
                        const arr = [];
                        for (let i = 1; i <= n; i++) {
                            lua.lua_rawgeti(L2, idx, i);
                            arr.push(luaToJs(L2, -1));
                            lua.lua_pop(L2, 1);
                        }
                        return arr;
                    }
                    const obj = {};
                    lua.lua_pushnil(L2);
                    while (lua.lua_next(L2, idx) !== 0) {
                        const kty = lua.lua_type(L2, -2);
                        let key = null;
                        if (kty === lua.LUA_TSTRING) key = lua.lua_tojsstring(L2, -2);
                        else if (kty === lua.LUA_TNUMBER) key = String(lua.lua_tonumber(L2, -2));
                        if (key !== null) obj[key] = luaToJs(L2, -1);
                        lua.lua_pop(L2, 1);
                    }
                    return obj;
                }
                return null;
            }
            def('__json_encode', function (L2) {
                let out = '{}';
                try { out = JSON.stringify(luaToJs(L2, 1)); } catch (e) { emuWarn('swallow:out:8554', 'out: ' + _errText(e) + ' (циклическая ссылка и т.п. — отдаём безопасный fallback)'); }
                lua.lua_pushstring(L2, out === undefined ? 'null' : out);
                return 1;
            });
            def('__json_decode', function (L2) {
                let val = null;
                try { val = JSON.parse(lua.lua_tojsstring(L2, 1)); } catch (e) { emuWarn('swallow:val:8560', 'val: ' + _errText(e) + ' (невалидный JSON — nil, как и настоящий Roblox упал бы через error(), но тут безопаснее отдать nil)'); }
                pushJsAsLua(L2, val);
                return 1;
            });
            // Signal:Wait()/:wait() — используется тем же принципом, что и
            def('__wait_signal', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                const evName = lua.lua_tojsstring(L2, 2);
                luaSignalWaits.push({ co: L2, ref, evName });
                return lua.lua_yield(L2, 0);
            });
            // require(moduleScriptInstance) — компилирует Source конкретного
            def('__compile_module', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                // ModuleScript, склонированный в рантайме (копия StarterGui в PlayerGui, Clone() шаблона), — виртуальный ref
                // с отрицательным номером: исходник лежит у оригинала из файла. Раньше require(клон) падал «не ModuleScript
                // этой карты» (так ломался InventoryController: require(script.Parent.<Модуль>) в PlayerGui).
                const srcRef = luaModuleSourceByRef[ref] !== undefined ? ref : luaCloneOrigin[ref];
                const src = srcRef !== undefined ? luaModuleSourceByRef[srcRef] : undefined;
                if (src === undefined) {
                    lua.lua_pushboolean(L2, false);
                    lua.lua_pushstring(L2, 'require(): ссылка #' + ref + ' — не ModuleScript этой карты');
                    return 2;
                }
                const chunkname = luaModuleNameByRef[ref] || luaModuleNameByRef[srcRef] || ('Module#' + ref);
                const wrapped = 'return function(script)\n' + src + '\nend';
                let status = loadLuaChunk(L2, wrapped, chunkname);
                if (status !== lua.LUA_OK) {
                    const msg = luaErrToString(L2);
                    lua.lua_pop(L2, 1);
                    lua.lua_pushboolean(L2, false);
                    lua.lua_pushstring(L2, 'ошибка компиляции модуля ' + chunkname + ': ' + msg);
                    return 2;
                }
                status = lua.lua_pcall(L2, 0, 1, 0); // достаём саму function(script)...end как значение
                if (status !== lua.LUA_OK) {
                    const msg = luaErrToString(L2);
                    lua.lua_pop(L2, 1);
                    lua.lua_pushboolean(L2, false);
                    lua.lua_pushstring(L2, msg);
                    return 2;
                }
                lua.lua_pushboolean(L2, true);
                lua.lua_insert(L2, -2); // стек был [function, true] -> [true, function]
                return 2;
            });
            def('__emu_warn', function (L2) {
                emuWarn('lua:' + lua.lua_tojsstring(L2, 1), lua.lua_tojsstring(L2, 2));
                return 0;
            });
            def('__cam_info', function (L2) {
                const i = luaCamInfo();
                lua.lua_pushnumber(L2, i.w / guiScale); lua.lua_pushnumber(L2, i.h / guiScale); lua.lua_pushnumber(L2, i.fov);
                return 3;
            });
            def('__cam_project', function (L2) {
                const r = luaCamProject(lua.lua_tonumber(L2, 1), lua.lua_tonumber(L2, 2), lua.lua_tonumber(L2, 3));
                lua.lua_pushnumber(L2, r.x / guiScale); lua.lua_pushnumber(L2, r.y / guiScale); lua.lua_pushnumber(L2, r.depth);
                lua.lua_pushboolean(L2, r.on ? 1 : 0);
                return 4;
            });
            def('__cam_ray', function (L2) {
                const r = luaCamRay(lua.lua_tonumber(L2, 1) * guiScale, lua.lua_tonumber(L2, 2) * guiScale);
                for (const v of [r.o.x, r.o.y, r.o.z, r.d.x, r.d.y, r.d.z]) lua.lua_pushnumber(L2, v);
                return 6;
            });
            def('__particle_emit', function (L2) {
                try { psEmit(lua.lua_tonumber(L2, 1), Math.max(0, Math.min(500, lua.lua_tonumber(L2, 2) || 1))); } catch (e) { console.error('Emit:', e); }
                return 0;
            });
            def('__get_parent', function (L2) {
                const ref = luaParentByRef[lua.lua_tonumber(L2, 1)];
                lua.lua_pushnumber(L2, ref === undefined ? -1 : ref);
                return 1;
            });
            def('__get_name', function (L2) {
                const nref = lua.lua_tonumber(L2, 1);
                const inst = luaByRef[nref];
                // player.Name / tostring(player) у локального игрока — ник аккаунта Roblox (если вошли), как в настоящем Roblox
                if (inst && nref === luaPlayerRef && playerAccount && playerAccount.name) {
                    lua.lua_pushstring(L2, playerAccount.name);
                    return 1;
                }
                lua.lua_pushstring(L2, inst ? String(inst.name) : ('ref' + nref));
                return 1;
            });
            def('__get_class', function (L2) {
                const inst = luaByRef[lua.lua_tonumber(L2, 1)];
                lua.lua_pushstring(L2, inst ? inst.cls : 'Instance');
                return 1;
            });
            def('__get_position', function (L2) {
                const p = luaPositionOfRef(lua.lua_tonumber(L2, 1));
                lua.lua_pushnumber(L2, p.x); lua.lua_pushnumber(L2, p.y); lua.lua_pushnumber(L2, p.z);
                return 3;
            });
            def('__refprop_get', function (L2) {   // -> ref | -1 (nil) | ничего (свойство не задано)
                const rp = luaRefProps[lua.lua_tonumber(L2, 1)];
                const key = lua.lua_tojsstring(L2, 2);
                if (!rp || !(key in rp)) return 0;
                lua.lua_pushnumber(L2, rp[key]);
                return 1;
            });
            def('__refprop_set', function (L2) {   // ref детали/вложения или -1
                const ref = lua.lua_tonumber(L2, 1);
                (luaRefProps[ref] = luaRefProps[ref] || {})[lua.lua_tojsstring(L2, 2)] = lua.lua_tonumber(L2, 3);
                luaRegisterWeld(ref); // WeldConstraint с обоими Part0/Part1 — деталь начинает следовать за Part0
                return 0;
            });
            def('__att_get', function (L2) {      // Attachment.CFrame -> 12 чисел (или ничего)
                const a = luaAttCF[lua.lua_tonumber(L2, 1)];
                if (!a) return 0;
                for (let i = 0; i < 12; i++) lua.lua_pushnumber(L2, a[i]);
                return 12;
            });
            def('__att_set', function (L2) {      // Attachment.Position = Vector3
                const ref = lua.lua_tonumber(L2, 1);
                const a = luaAttCF[ref] || (luaAttCF[ref] = [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]);
                a[0] = lua.lua_tonumber(L2, 2); a[1] = lua.lua_tonumber(L2, 3); a[2] = lua.lua_tonumber(L2, 4);
                return 0;
            });
            def('__att_set_cf', function (L2) {   // Attachment.CFrame = CFrame (12 компонент)
                const ref = lua.lua_tonumber(L2, 1);
                const a = [];
                for (let i = 0; i < 12; i++) a.push(lua.lua_tonumber(L2, 2 + i));
                luaAttCF[ref] = a;
                return 0;
            });
            def('__set_size', function (L2) {
                luaSetPartSize(lua.lua_tonumber(L2, 1), lua.lua_tonumber(L2, 2), lua.lua_tonumber(L2, 3), lua.lua_tonumber(L2, 4));
                return 0;
            });
            def('__get_size', function (L2) {
                const p = luaSizeOfRef(lua.lua_tonumber(L2, 1));
                lua.lua_pushnumber(L2, p.x); lua.lua_pushnumber(L2, p.y); lua.lua_pushnumber(L2, p.z);
                return 3;
            });
            // GUI-объекты (ScreenGui/Frame/...) хранят Position/Size как
            def('__is_gui_ref', function (L2) {
                lua.lua_pushboolean(L2, !!guiPropsByRef[lua.lua_tonumber(L2, 1)]);
                return 1;
            });
            def('__get_gui_position', function (L2) {
                const p = (guiPropsByRef[lua.lua_tonumber(L2, 1)] || {}).Position || {};
                const x = p.x || {}, y = p.y || {};
                lua.lua_pushnumber(L2, x.scale || 0); lua.lua_pushnumber(L2, x.offset || 0);
                lua.lua_pushnumber(L2, y.scale || 0); lua.lua_pushnumber(L2, y.offset || 0);
                return 4;
            });
            def('__get_gui_size', function (L2) {
                const p = (guiPropsByRef[lua.lua_tonumber(L2, 1)] || {}).Size || {};
                const x = p.x || {}, y = p.y || {};
                lua.lua_pushnumber(L2, x.scale || 0); lua.lua_pushnumber(L2, x.offset || 0);
                lua.lua_pushnumber(L2, y.scale || 0); lua.lua_pushnumber(L2, y.offset || 0);
                return 4;
            });
            // CFrame раньше не читался мостом вообще — .CFrame падал в
            def('__get_cframe_vecs', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                const mesh = sceneObjs[ref];
                let look = { x: 0, y: 0, z: -1 }, right = { x: 1, y: 0, z: 0 }, up = { x: 0, y: 1, z: 0 };
                if (mesh) {
                    const q = new THREE.Quaternion(), pos = new THREE.Vector3(), sc = new THREE.Vector3();
                    mesh.matrix.decompose(pos, q, sc);
                    look = new THREE.Vector3(0, 0, -1).applyQuaternion(q);
                    right = new THREE.Vector3(1, 0, 0).applyQuaternion(q);
                    up = new THREE.Vector3(0, 1, 0).applyQuaternion(q);
                }
                lua.lua_pushnumber(L2, look.x); lua.lua_pushnumber(L2, look.y); lua.lua_pushnumber(L2, look.z);
                lua.lua_pushnumber(L2, right.x); lua.lua_pushnumber(L2, right.y); lua.lua_pushnumber(L2, right.z);
                lua.lua_pushnumber(L2, up.x); lua.lua_pushnumber(L2, up.y); lua.lua_pushnumber(L2, up.z);
                return 9;
            });
            // ---- общие Атрибуты и Теги (для серверной и клиентской VM) ----
            const _pushJsVal = (L2, v) => {
                if (v === null || v === undefined) lua.lua_pushnil(L2);
                else if (typeof v === 'number') lua.lua_pushnumber(L2, v);
                else if (typeof v === 'boolean') lua.lua_pushboolean(L2, v);
                else lua.lua_pushstring(L2, String(v));
            };
            def('__attr_set', function (L2) {
                const ref = lua.lua_tonumber(L2, 1), name = lua.lua_tojsstring(L2, 2);
                const ty = lua.lua_type(L2, 3);
                let v = null;
                if (ty === lua.LUA_TNUMBER) v = lua.lua_tonumber(L2, 3);
                else if (ty === lua.LUA_TBOOLEAN) v = !!lua.lua_toboolean(L2, 3);
                else if (ty === lua.LUA_TSTRING) v = lua.lua_tojsstring(L2, 3);
                const bag = (luaAttrs[ref] = luaAttrs[ref] || {});
                const old = bag[name];
                if (v === null) delete bag[name]; else bag[name] = v;
                if (old !== v && !(old === undefined && v === null)) fireLuaSignal(ref, '__attr_' + name, []);
                return 0;
            });
            // Команды и группы столкновений (Lua-стороны: Team.TeamColor, Player.Team, PhysicsService)
            def('__load_character', function (L2) {
                // Player:LoadCharacter() — асинхронно, как в Roblox (скрипт зовёт его через task.spawn и продолжает работу)
                setTimeout(() => luaRespawnCharacter(), 0);
                return 0;
            });
            def('__team_color', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                let ti = luaTeamInfo[ref];
                if (!ti && ref === luaPlayerRef && luaPlayerTeam !== -1) ti = luaTeamInfo[luaPlayerTeam];
                _pushJsVal(L2, ti && typeof ti.color === 'number' ? ti.color : null);
                return 1;
            });
            def('__team_auto', function (L2) {
                const ti = luaTeamInfo[lua.lua_tonumber(L2, 1)];
                lua.lua_pushboolean(L2, ti ? ti.auto : true);
                return 1;
            });
            def('__player_team', function (L2) {
                lua.lua_pushnumber(L2, lua.lua_tonumber(L2, 1) === luaPlayerRef ? luaPlayerTeam : -1);
                return 1;
            });
            def('__phys_register', function (L2) {
                const name = lua.lua_tojsstring(L2, 1);
                if (name && name !== 'Default' && !luaCollGroups[name] && luaNextGroupBit < 0x40000000) {
                    luaCollGroups[name] = { bit: luaNextGroupBit };
                    luaNextGroupBit *= 2;
                    luaRefreshAllGroupMasks();
                }
                return 0;
            });
            def('__phys_unregister', function (L2) {
                const name = lua.lua_tojsstring(L2, 1);
                if (luaCollGroups[name]) {
                    for (const b of Object.values(physicsBodies)) if (b.__rbxGroup === name) b.__rbxGroup = 'Default';
                    if (charBody && charBody.__rbxGroup === name) charBody.__rbxGroup = 'Default';
                    delete luaCollGroups[name];
                    for (const k of Object.keys(luaGroupCollide)) if (k.split('\u0000').indexOf(name) >= 0) delete luaGroupCollide[k];
                    luaRefreshAllGroupMasks();
                }
                return 0;
            });
            def('__phys_is_registered', function (L2) {
                const name = lua.lua_tojsstring(L2, 1);
                lua.lua_pushboolean(L2, name === 'Default' || !!luaCollGroups[name]);
                return 1;
            });
            def('__phys_set_collidable', function (L2) {
                const a = lua.lua_tojsstring(L2, 1), b = lua.lua_tojsstring(L2, 2), v = !!lua.lua_toboolean(L2, 3);
                luaGroupCollide[a < b ? a + '\u0000' + b : b + '\u0000' + a] = v;
                luaRefreshAllGroupMasks();
                return 0;
            });
            def('__phys_get_collidable', function (L2) {
                lua.lua_pushboolean(L2, luaGroupsCollide(lua.lua_tojsstring(L2, 1), lua.lua_tojsstring(L2, 2)));
                return 1;
            });
            def('__attr_get', function (L2) {
                const bag = luaAttrs[lua.lua_tonumber(L2, 1)];
                _pushJsVal(L2, bag ? bag[lua.lua_tojsstring(L2, 2)] : null);
                return 1;
            });
            def('__attr_all', function (L2) {
                const bag = luaAttrs[lua.lua_tonumber(L2, 1)] || {};
                lua.lua_createtable(L2, 0, 0);
                for (const k of Object.keys(bag)) { _pushJsVal(L2, bag[k]); lua.lua_setfield(L2, -2, k); }
                return 1;
            });
            def('__tag_add', function (L2) {
                const ref = lua.lua_tonumber(L2, 1), tag = lua.lua_tojsstring(L2, 2);
                const set = (luaTags[ref] = luaTags[ref] || new Set());
                const isNew = !set.has(tag);
                set.add(tag);
                lua.lua_pushboolean(L2, isNew);
                return 1;
            });
            def('__tag_remove', function (L2) {
                const ref = lua.lua_tonumber(L2, 1), tag = lua.lua_tojsstring(L2, 2);
                const set = luaTags[ref];
                lua.lua_pushboolean(L2, !!(set && set.delete(tag)));
                return 1;
            });
            def('__tag_has', function (L2) {
                const set = luaTags[lua.lua_tonumber(L2, 1)];
                lua.lua_pushboolean(L2, !!(set && set.has(lua.lua_tojsstring(L2, 2))));
                return 1;
            });
            def('__tag_list', function (L2) {
                const set = luaTags[lua.lua_tonumber(L2, 1)];
                lua.lua_createtable(L2, 0, 0);
                let i = 1;
                if (set) for (const t of set) { lua.lua_pushstring(L2, t); lua.lua_rawseti(L2, -2, i++); }
                return 1;
            });
            def('__tag_tagged', function (L2) {
                const tag = lua.lua_tojsstring(L2, 1);
                lua.lua_createtable(L2, 0, 0);
                let i = 1;
                for (const k of Object.keys(luaTags)) {
                    if (luaTags[k].has(tag)) { lua.lua_pushnumber(L2, Number(k)); lua.lua_rawseti(L2, -2, i++); }
                }
                return 1;
            });
            const _pushMatrix = (L2, M) => {
                const e = M.elements;
                const vals = [e[12], e[13], e[14], e[0], e[4], e[8], e[1], e[5], e[9], e[2], e[6], e[10]];
                for (const v of vals) lua.lua_pushnumber(L2, v);
                return 12;
            };
            const _readMatrix = (L2, first) => {
                const n = (i) => lua.lua_tonumber(L2, first + i);
                return new THREE.Matrix4().set(
                    n(3), n(4), n(5), n(0),
                    n(6), n(7), n(8), n(1),
                    n(9), n(10), n(11), n(2),
                    0, 0, 0, 1);
            };
            def('__get_cframe', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                const M = (luaIsPartRef(ref) && !luaIsCharRef(ref)) ? luaPartMatrix(ref) : luaGetPivotMatrix(ref);
                return _pushMatrix(L2, M);
            });
            def('__get_bbox', function (L2) {
                const b = luaBoundingBox(lua.lua_tonumber(L2, 1));
                for (const v of [b.cx, b.cy, b.cz, b.sx, b.sy, b.sz].concat(b.rot)) lua.lua_pushnumber(L2, v);
                return 15;
            });
            let _overlapPartCls = null, _overlapParts = null;
            def('__overlap', function (L2) {
                // (mode 0=Exclude/1=Include, maxParts, skipRef, cx,cy,cz, hx,hy,hz, фильтр-ref...) -> "ref,ref,..."
                try {
                    const n = lua.lua_gettop(L2), num = (i) => lua.lua_tonumber(L2, i);
                    const mode = lua.lua_tointeger(L2, 1), maxParts = lua.lua_tointeger(L2, 2), skip = lua.lua_tointeger(L2, 3);
                    const cx = num(4), cy = num(5), cz = num(6), hx = num(7), hy = num(8), hz = num(9);
                    const roots = new Set();
                    const rx = num(10), ry = num(11), rz = num(12), ux = num(13), uy = num(14), uz = num(15), lx = num(16), ly = num(17), lz = num(18);
                    // описанный мировой AABB повёрнутого бокса — для быстрого отсева
                    const wx = Math.abs(rx) * hx + Math.abs(ux) * hy + Math.abs(lx) * hz;
                    const wy = Math.abs(ry) * hx + Math.abs(uy) * hy + Math.abs(ly) * hz;
                    const wz = Math.abs(rz) * hx + Math.abs(uz) * hy + Math.abs(lz) * hz;
                    for (let i = 19; i <= n; i++) roots.add(lua.lua_tointeger(L2, i));
                    const inFilter = (ref) => {
                        let cur = ref, g = 0;
                        while (cur !== undefined && cur !== -1 && g++ < 200) { if (roots.has(cur)) return true; cur = luaParentByRef[cur]; }
                        return false;
                    };
                    const out = [], c = new THREE.Vector3();
                    const PARTCLS = _overlapPartCls || (_overlapPartCls = new Set(['Part', 'MeshPart', 'WedgePart', 'CornerWedgePart', 'SpawnLocation',
                        'TrussPart', 'UnionOperation', 'NegateOperation', 'Seat', 'VehicleSeat', 'SpherePart', 'BallPart', 'CylinderPart']));
                    // список ref-ов деталей кэшируем, пока не изменилось число объектов в luaByRef (клоны/удаления его меняют)
                    if (!_overlapParts || _overlapParts.n !== luaByRefVer) {
                        _overlapParts = { n: luaByRefVer, refs: Object.keys(luaByRef).filter(k => luaByRef[k] && PARTCLS.has(luaByRef[k].cls)).map(k => parseInt(k, 10)) };
                    }
                    for (const ref of _overlapParts.refs) {
                        if (ref === skip) continue;
                        const pp = luaPositionOfRef(ref);
                        if (!pp) continue;
                        // размер берём из кэша; тяжёлый luaSizeOfRef (геометрия меша) — только для деталей рядом с запросом
                        let sz = loadedObjSize[ref];
                        if (!sz) {
                            if (Math.abs(pp.x - cx) > wx + 100 || Math.abs(pp.y - cy) > wy + 100 || Math.abs(pp.z - cz) > wz + 100) continue;
                            sz = luaSizeOfRef(ref);
                        }
                        const rad = Math.hypot(sz.x, sz.y, sz.z) / 2;
                        if (Math.abs(pp.x - cx) > wx + rad || Math.abs(pp.y - cy) > wy + rad || Math.abs(pp.z - cz) > wz + rad) continue;
                        if (!luaIsUnderWorkspace(ref)) continue;
                        const M = luaPartMatrix(ref);
                        let mnx = Infinity, mny = Infinity, mnz = Infinity, mxx = -Infinity, mxy = -Infinity, mxz = -Infinity;
                        for (let i = 0; i < 8; i++) {
                            c.set((i & 1 ? 0.5 : -0.5) * sz.x, (i & 2 ? 0.5 : -0.5) * sz.y, (i & 4 ? 0.5 : -0.5) * sz.z).applyMatrix4(M);
                            if (c.x < mnx) mnx = c.x; if (c.x > mxx) mxx = c.x;
                            if (c.y < mny) mny = c.y; if (c.y > mxy) mxy = c.y;
                            if (c.z < mnz) mnz = c.z; if (c.z > mxz) mxz = c.z;
                        }
                        if (mxx < cx - wx || mnx > cx + wx || mxy < cy - wy || mny > cy + wy || mxz < cz - wz || mnz > cz + wz) continue;
                        // ось-за-осью по базису самого бокса: углы детали переводим в его локальные координаты
                        let lmn = [Infinity, Infinity, Infinity], lmx = [-Infinity, -Infinity, -Infinity];
                        for (let i = 0; i < 8; i++) {
                            c.set((i & 1 ? 0.5 : -0.5) * sz.x, (i & 2 ? 0.5 : -0.5) * sz.y, (i & 4 ? 0.5 : -0.5) * sz.z).applyMatrix4(M);
                            const dx = c.x - cx, dy = c.y - cy, dz = c.z - cz;
                            const q0 = dx * rx + dy * ry + dz * rz, q1 = dx * ux + dy * uy + dz * uz, q2 = dx * lx + dy * ly + dz * lz;
                            if (q0 < lmn[0]) lmn[0] = q0; if (q0 > lmx[0]) lmx[0] = q0;
                            if (q1 < lmn[1]) lmn[1] = q1; if (q1 > lmx[1]) lmx[1] = q1;
                            if (q2 < lmn[2]) lmn[2] = q2; if (q2 > lmx[2]) lmx[2] = q2;
                        }
                        if (lmx[0] < -hx || lmn[0] > hx || lmx[1] < -hy || lmn[1] > hy || lmx[2] < -hz || lmn[2] > hz) continue;
                        if (mode === 1 ? !inFilter(ref) : (roots.size > 0 && inFilter(ref))) continue;
                        out.push(ref);
                        if (maxParts > 0 && out.length >= maxParts) break;
                    }
                    lua.lua_pushstring(L2, out.join(','));
                } catch (e) { console.warn('Overlap:', e); lua.lua_pushstring(L2, ''); }
                return 1;
            });
            def('__is_key_down', function (L2) {
                lua.lua_pushboolean(L2, luaKeyIsDown(lua.lua_tojsstring(L2, 1)) ? 1 : 0);
                return 1;
            });
            def('__keys_down', function (L2) {
                const names = Object.keys(luaKeySrc).filter(luaKeyIsDown);
                lua.lua_pushstring(L2, names.join(','));
                return 1;
            });
            def('__get_move_dir', function (L2) {
                lua.lua_pushnumber(L2, luaMoveDir.x);
                lua.lua_pushnumber(L2, 0);
                lua.lua_pushnumber(L2, luaMoveDir.z);
                return 3;
            });
            // UserInputService.TouchEnabled и т.п.: экранный джойстик есть на
            // сенсорных устройствах, WASD — на устройствах с клавиатурой.
            def('__core_gui', function (L2) {
                const nm = lua.lua_tojsstring(L2, 1), en = !!lua.lua_toboolean(L2, 2);
                _coreGuiOff[nm] = !en; if (nm === 'All') _coreGuiOff.Backpack = !en;
                return 0;
            });
            def('__prompt_input', function (L2) {
                window.__promptInput(lua.lua_tonumber(L2, 1), !!lua.lua_toboolean(L2, 2));
                return 0;
            });
            def('__is_touch', function (L2) {
                const touch = (navigator.maxTouchPoints || 0) > 0 || ('ontouchstart' in window);
                lua.lua_pushboolean(L2, touch ? 1 : 0);
                return 1;
            });
            def('__get_pivot', function (L2) {
                return _pushMatrix(L2, luaGetPivotMatrix(lua.lua_tonumber(L2, 1)));
            });
            def('__set_cframe', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                const M = _readMatrix(L2, 2);
                if (luaIsCameraRef(ref)) {
                    const e = M.elements;
                    applyCFrameValue(ref, e[12], e[13], e[14], -e[8], -e[9], -e[10]);
                    fireLuaSignal(ref, '__prop_CFrame', []);
                } else {
                    luaSetCFrameMatrix(ref, M);
                }
                return 0;
            });
            def('__set_world_pivot', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                if (!luaIsPartRef(ref)) _modelPivots[ref] = _readMatrix(L2, 2);   // у Model — только пивот, детали остаются на месте
                return 0;
            });
            def('__set_pivot', function (L2) {
                luaSetPivotMatrix(lua.lua_tonumber(L2, 1), _readMatrix(L2, 2));
                return 0;
            });
            // __set_velocity(ref, kind[0=линейная,1=угловая], x, y, z)
            def('__set_velocity', function (L2) {
                const ref = lua.lua_tonumber(L2, 1), kind = lua.lua_tonumber(L2, 2);
                const x = lua.lua_tonumber(L2, 3), y = lua.lua_tonumber(L2, 4), z = lua.lua_tonumber(L2, 5);
                const body = physicsBodies[ref];
                if (!body) return 0;
                if (ref === luaHumanoidRootPartRef) {
                    if (kind === 0) {
                        body.velocity.y = y;
                        charPushX = x; charPushZ = z; charPushT = 0.4; // горизонтальный толчок затухает
                        body.wakeUp();
                    }
                    return 0;
                }
                if (kind === 0) body.velocity.set(x, y, z); else body.angularVelocity.set(x, y, z);
                if (body.type === CANNON.Body.DYNAMIC && body.wakeUp) body.wakeUp();
                return 0;
            });
            def('__get_velocity', function (L2) {
                const ref = lua.lua_tonumber(L2, 1), kind = lua.lua_tonumber(L2, 2);
                const body = physicsBodies[ref];
                const v = body ? (kind === 0 ? body.velocity : body.angularVelocity) : { x: 0, y: 0, z: 0 };
                lua.lua_pushnumber(L2, v.x); lua.lua_pushnumber(L2, v.y); lua.lua_pushnumber(L2, v.z);
                return 3;
            });
            def('__set_position', function (L2) {
                luaSetPositionOfRef(lua.lua_tonumber(L2, 1), lua.lua_tonumber(L2, 2), lua.lua_tonumber(L2, 3), lua.lua_tonumber(L2, 4));
                return 0;
            });
            // AbsolutePosition/AbsoluteSize — меряем настоящий отрисованный
            def('__get_gui_rect', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                const el = guiDomByRef[ref];
                let x = 0, y = 0, w = 0, h = 0;
                if (el) {
                    const r = el.getBoundingClientRect();
                    [x, y] = _clientToGui(r.left, r.top); w = r.width / guiScale; h = r.height / guiScale;
                }
                lua.lua_pushnumber(L2, x); lua.lua_pushnumber(L2, y);
                lua.lua_pushnumber(L2, w); lua.lua_pushnumber(L2, h);
                return 4;
            });
            // AbsoluteContentSize — свойство UIListLayout/UIGridLayout, а не
            def('__get_gui_content_size', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                const parentRef = luaParentByRef[ref];
                const el = guiDomByRef[parentRef];
                lua.lua_pushnumber(L2, el ? el.scrollWidth : 0);
                lua.lua_pushnumber(L2, el ? el.scrollHeight : 0);
                return 2;
            });
            // PlayerModule:GetControls():Disable()/:Enable() (см.
            def('__set_controls_enabled', function (L2) {
                luaControlsDisabled = !lua.lua_toboolean(L2, 1);
                // Раньше эта блокировка реально отключала ходьбу/поворот
                _updateTouchControlsVisibility();
                return 0;
            });
            def('__get_character_ref', function (L2) {
                lua.lua_pushnumber(L2, luaCharacterRef);
                return 1;
            });
            def('__find_first_child', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                const name = lua.lua_tojsstring(L2, 2);
                let found = -1;
                for (const c of (luaChildrenByRef[ref] || [])) {
                    if (luaByRef[c] && luaByRef[c].name === name) { found = c; break; }
                }
                lua.lua_pushnumber(L2, found);
                return 1;
            });
            def('__child_count', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                lua.lua_pushnumber(L2, (luaChildrenByRef[ref] || []).length);
                return 1;
            });
            def('__child_at', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                const i = lua.lua_tonumber(L2, 2);
                const kids = luaChildrenByRef[ref] || [];
                lua.lua_pushnumber(L2, kids[i] !== undefined ? kids[i] : -1);
                return 1;
            });
            def('__destroy', function (L2) { luaDestroyRef(lua.lua_tonumber(L2, 1)); return 0; });
            def('__sound_control', function (L2) {
                luaSoundControl(lua.lua_tonumber(L2, 1), lua.lua_tojsstring(L2, 2));
                return 0;
            });
            def('__get_color', function (L2) {   // part.Color -> r, g, b (0..1) или ничего
                const m = sceneObjs[lua.lua_tonumber(L2, 1)];
                if (!m || !m.material) return 0;
                const mat = Array.isArray(m.material) ? (m.material.find(x => x && !x.map) || m.material[0]) : m.material;
                if (!mat || !mat.color) return 0;
                lua.lua_pushnumber(L2, mat.color.r); lua.lua_pushnumber(L2, mat.color.g); lua.lua_pushnumber(L2, mat.color.b);
                return 3;
            });
            def('__get_prop', function (L2) {
                const v = luaGetGenericProp(lua.lua_tonumber(L2, 1), lua.lua_tojsstring(L2, 2));
                if (v === null || v === undefined) lua.lua_pushnil(L2);
                else if (typeof v === 'number') lua.lua_pushnumber(L2, v);
                else if (typeof v === 'boolean') lua.lua_pushboolean(L2, v);
                else lua.lua_pushstring(L2, String(v));
                return 1;
            });
            // Составные Roblox-типы (UDim2 у Position/Size, Color3 у
            function luaTableToJsPropValue(L2, idx) {
                const field = (parentKey, childKey) => {
                    lua.lua_getfield(L2, idx, parentKey);
                    lua.lua_getfield(L2, -1, childKey);
                    const v = lua.lua_isnumber(L2, -1) ? lua.lua_tonumber(L2, -1) : 0;
                    lua.lua_pop(L2, 2); // childKey-значение + parentKey-таблица
                    return v;
                };
                lua.lua_getfield(L2, idx, 'X');
                const isUDim2 = lua.lua_type(L2, -1) === lua.LUA_TTABLE;
                lua.lua_pop(L2, 1);
                if (isUDim2) {
                    return {
                        x: { scale: field('X', 'Scale'), offset: field('X', 'Offset') },
                        y: { scale: field('Y', 'Scale'), offset: field('Y', 'Offset') },
                    };
                }
                lua.lua_getfield(L2, idx, 'R');
                const isColor3 = lua.lua_isnumber(L2, -1);
                const r = isColor3 ? lua.lua_tonumber(L2, -1) : 0;
                lua.lua_pop(L2, 1);
                if (isColor3) {
                    lua.lua_getfield(L2, idx, 'G'); const g = lua.lua_isnumber(L2, -1) ? lua.lua_tonumber(L2, -1) : 0; lua.lua_pop(L2, 1);
                    lua.lua_getfield(L2, idx, 'B'); const b = lua.lua_isnumber(L2, -1) ? lua.lua_tonumber(L2, -1) : 0; lua.lua_pop(L2, 1);
                    return { r, g, b };
                }
                // Vector2 (AnchorPoint и т.п.) — плоские числовые X/Y, без
                lua.lua_getfield(L2, idx, 'X');
                const isVector2 = lua.lua_isnumber(L2, -1);
                const vx = isVector2 ? lua.lua_tonumber(L2, -1) : 0;
                lua.lua_pop(L2, 1);
                if (isVector2) {
                    lua.lua_getfield(L2, idx, 'Y'); const vy = lua.lua_isnumber(L2, -1) ? lua.lua_tonumber(L2, -1) : 0; lua.lua_pop(L2, 1);
                    return { x: vx, y: vy };
                }
                // UDim (плоская {Scale, Offset}, без вложенных X/Y) —
                lua.lua_getfield(L2, idx, 'Scale');
                const isUDim = lua.lua_isnumber(L2, -1);
                const uScale = isUDim ? lua.lua_tonumber(L2, -1) : 0;
                lua.lua_pop(L2, 1);
                if (isUDim) {
                    lua.lua_getfield(L2, idx, 'Offset'); const uOffset = lua.lua_isnumber(L2, -1) ? lua.lua_tonumber(L2, -1) : 0; lua.lua_pop(L2, 1);
                    return { scale: uScale, offset: uOffset };
                }
                return null;
            }
            def('__set_prop', function (L2) {
                const ref = lua.lua_tonumber(L2, 1), name = lua.lua_tojsstring(L2, 2);
                // part.CFrame = CFrame.new(...) — раньше вообще ничего не
                if (name === 'CameraType') {
                    let enumName = null;
                    if (lua.lua_type(L2, 3) === lua.LUA_TTABLE) {
                        lua.lua_getfield(L2, 3, 'Name');
                        if (lua.lua_isstring(L2, -1)) enumName = lua.lua_tojsstring(L2, -1);
                        lua.lua_pop(L2, 1);
                    } else if (lua.lua_type(L2, 3) === lua.LUA_TSTRING) {
                        enumName = lua.lua_tojsstring(L2, 3);
                    }
                    if (luaByRef[ref] && luaByRef[ref].cls === 'Camera') {
                        const wasScriptable = cameraIsScriptable;
                        cameraIsScriptable = (enumName === 'Scriptable');
                        logLuaOutput('info', 'Camera: CameraType -> ' + enumName + ' (ref ' + ref + ')');
                        // Scriptable -> Custom (например MenuCamera.lua при
                        // возврате в меню песен): раньше followCharacterCamera
                        // в СЛЕДУЮЩИЙ же кадр мгновенно ставила target на
                        // charBody.position — с точки зрения игрока камера,
                        // всё это время стоявшая где-то у объекта 'camera'
                        // песни, "телепортировалась" обратно к персонажу за
                        // один кадр. Плавно подводим её вместо скачка.
                        if (wasScriptable && !cameraIsScriptable) _camReturnToCharT = 0;
                    }
                    luaSetGenericProp(ref, name, enumName);
                    fireLuaSignal(ref, '__prop_' + name, []);
                    return 0;
                }
                if (name === 'FieldOfView' && lua.lua_type(L2, 3) === lua.LUA_TNUMBER && luaIsCameraRef(ref)) {
                    camera.fov = Math.max(1, Math.min(120, lua.lua_tonumber(L2, 3)));
                    camera.updateProjectionMatrix();
                    fireLuaSignal(ref, '__prop_FieldOfView', []);
                    return 0;
                }
                if (name === 'CFrame' && lua.lua_type(L2, 3) === lua.LUA_TTABLE) {
                    lua.lua_getfield(L2, 3, 'Position');
                    if (lua.lua_type(L2, -1) === lua.LUA_TTABLE) {
                        const gx = (f) => { lua.lua_getfield(L2, -1, f); const v = lua.lua_isnumber(L2, -1) ? lua.lua_tonumber(L2, -1) : 0; lua.lua_pop(L2, 1); return v; };
                        const x = gx('X'), y = gx('Y'), z = gx('Z');
                        lua.lua_pop(L2, 1);
                        // Camera — особый случай:
                        lua.lua_getfield(L2, 3, 'lookVector');
                        let lx = 0, ly = 0, lz = -1;
                        if (lua.lua_type(L2, -1) === lua.LUA_TTABLE) {
                            const gl = (f) => { lua.lua_getfield(L2, -1, f); const v = lua.lua_isnumber(L2, -1) ? lua.lua_tonumber(L2, -1) : 0; lua.lua_pop(L2, 1); return v; };
                            lx = gl('X'); ly = gl('Y'); lz = gl('Z');
                        }
                        lua.lua_pop(L2, 1);
                        applyCFrameValue(ref, x, y, z, lx, ly, lz);
                        fireLuaSignal(ref, '__prop_' + name, []);
                        return 0;
                    }
                    lua.lua_pop(L2, 1);
                }
                const ty = lua.lua_type(L2, 3);
                let value = null;
                if (ty === lua.LUA_TNUMBER) value = lua.lua_tonumber(L2, 3);
                else if (ty === lua.LUA_TBOOLEAN) value = !!lua.lua_toboolean(L2, 3);
                else if (ty === lua.LUA_TSTRING) value = lua.lua_tojsstring(L2, 3);
                else if (ty === lua.LUA_TTABLE) {
                    // EnumItem (prompt.Style = Enum.ProximityPromptStyle.Custom) -> имя; инстанс (gui.Adornee = part) -> ref.
                    // Раньше оба превращались в null: Style игнорировался, Adornee у BillboardGui терялся.
                    // rawget — чтобы не дёргать __index инстанса (он пишет «не свойство» в Output).
                    const raw = (key) => { lua.lua_pushstring(L2, key); lua.lua_rawget(L2, 3); };
                    raw('EnumType');
                    const isEnum = lua.lua_isstring(L2, -1);
                    lua.lua_pop(L2, 1);
                    if (isEnum) {
                        raw('Name');
                        if (lua.lua_isstring(L2, -1)) value = lua.lua_tojsstring(L2, -1);
                        lua.lua_pop(L2, 1);
                    } else {
                        raw('__ref');
                        const isInst = lua.lua_isnumber(L2, -1);
                        const iref = isInst ? lua.lua_tonumber(L2, -1) : null;
                        lua.lua_pop(L2, 1);
                        if (isInst) value = (name === 'Adornee') ? iref : null;
                        else value = luaTableToJsPropValue(L2, 3);
                    }
                }
                luaSetGenericProp(ref, name, value);
                // GetPropertyChangedSignal(name) — стреляем ПОСЛЕ применения
                fireLuaSignal(ref, '__prop_' + name, []);
                // NumberValue/IntValue/... .Changed(newValue)
                if (name === 'Value') fireLuaSignal(ref, 'Changed', [value]);
                return 0;
            });
            def('__workspace_ref', function (L2) { lua.lua_pushnumber(L2, luaWorkspaceRef()); return 1; });
            // __tween_register(completedKey, ref, propName, targetValue, duration)
            def('__tween_register', function (L2) {
                const completedKey = lua.lua_tonumber(L2, 1);
                const ref = lua.lua_tonumber(L2, 2);
                const propName = lua.lua_tojsstring(L2, 3);
                const duration = lua.lua_tonumber(L2, 5) || 0;
                // CFrame — отдельный случай ДО общей ветки composite ниже:
                if (propName === 'CFrame' && lua.lua_type(L2, 4) === lua.LUA_TTABLE) {
                    const gx = (f) => { lua.lua_getfield(L2, 4, f); const v = lua.lua_isnumber(L2, -1) ? lua.lua_tonumber(L2, -1) : 0; lua.lua_pop(L2, 1); return v; };
                    const tx = gx('X'), ty = gx('Y'), tz = gx('Z');
                    lua.lua_getfield(L2, 4, 'lookVector');
                    let tlx = 0, tly = 0, tlz = -1;
                    if (lua.lua_type(L2, -1) === lua.LUA_TTABLE) {
                        const gl = (f) => { lua.lua_getfield(L2, -1, f); const v = lua.lua_isnumber(L2, -1) ? lua.lua_tonumber(L2, -1) : 0; lua.lua_pop(L2, 1); return v; };
                        tlx = gl('X'); tly = gl('Y'); tlz = gl('Z');
                    }
                    lua.lua_pop(L2, 1);
                    let fx = tx, fy = ty, fz = tz, flx = tlx, fly = tly, flz = tlz;
                    if (luaByRef[ref] && luaByRef[ref].cls === 'Camera' && typeof camera !== 'undefined') {
                        fx = camera.position.x; fy = camera.position.y; fz = camera.position.z;
                        const dir = camera.getWorldDirection(new THREE.Vector3());
                        flx = dir.x; fly = dir.y; flz = dir.z;
                    } else if (sceneObjs[ref]) {
                        const p = new THREE.Vector3(), q = new THREE.Quaternion(), sc = new THREE.Vector3();
                        sceneObjs[ref].matrix.decompose(p, q, sc);
                        fx = p.x; fy = p.y; fz = p.z;
                        const dir = new THREE.Vector3(0, 0, -1).applyQuaternion(q);
                        flx = dir.x; fly = dir.y; flz = dir.z;
                    }
                    // Полный поворот цели (R00..R22 у нашего CFrame) — иначе деталь теряла крен/наклон
                    let toQuat = null;
                    if (!(luaByRef[ref] && luaByRef[ref].cls === 'Camera')) {
                        const rr = [];
                        for (const f of ['R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22']) rr.push(gx(f));
                        if (rr.some(v => v !== 0)) {
                            const Rm = new THREE.Matrix4().set(rr[0], rr[1], rr[2], 0, rr[3], rr[4], rr[5], 0, rr[6], rr[7], rr[8], 0, 0, 0, 0, 1);
                            toQuat = new THREE.Quaternion().setFromRotationMatrix(Rm);
                        }
                    }
                    let fromQuat = null;
                    if (toQuat && sceneObjs[ref]) {
                        const p1 = new THREE.Vector3(), s1 = new THREE.Vector3(); fromQuat = new THREE.Quaternion();
                        luaPartMatrix(ref).decompose(p1, fromQuat, s1);
                    }
                    activeTweens.push({
                        ref, propName, cframe: true, fromQuat, toQuat,
                        fromPos: { x: fx, y: fy, z: fz }, toPos: { x: tx, y: ty, z: tz },
                        fromLook: { x: flx, y: fly, z: flz }, toLook: { x: tlx, y: tly, z: tlz },
                        duration, startTime: performance.now(), completedRef: completedKey,
                    });
                    return 0;
                }
                // Position (Vector3) у детали — плавный сдвиг с сохранением поворота, как у твина CFrame
                // (раньше шла общая ветка: без интерполяции и деталь вообще не двигалась).
                if (propName === 'Position' && lua.lua_type(L2, 4) === lua.LUA_TTABLE && luaIsPartRef(ref) && ref !== luaHumanoidRootPartRef) {
                    const gv = (f) => { lua.lua_getfield(L2, 4, f); const v = lua.lua_isnumber(L2, -1) ? lua.lua_tonumber(L2, -1) : 0; lua.lua_pop(L2, 1); return v; };
                    const cur = new THREE.Vector3(), cq = new THREE.Quaternion(), cs = new THREE.Vector3();
                    luaPartMatrix(ref).decompose(cur, cq, cs);
                    activeTweens.push({
                        ref, propName, partPos: true,
                        fromPos: { x: cur.x, y: cur.y, z: cur.z }, toPos: { x: gv('X'), y: gv('Y'), z: gv('Z') },
                        duration, startTime: performance.now(), completedRef: completedKey,
                    });
                    return 0;
                }
                const ty = lua.lua_type(L2, 4);
                let composite = false, toVal;
                if (ty === lua.LUA_TTABLE) { toVal = luaTableToJsPropValue(L2, 4); composite = true; }
                else if (ty === lua.LUA_TNUMBER) { toVal = lua.lua_tonumber(L2, 4); }
                else { toVal = lua.lua_type(L2, 4) === lua.LUA_TBOOLEAN ? !!lua.lua_toboolean(L2, 4) : lua.lua_tojsstring(L2, 4); composite = true; }
                let fromVal = null;
                if (!composite) {
                    const cur = luaGetGenericProp(ref, propName);
                    fromVal = (typeof cur === 'number') ? cur : toVal; // не смогли прочитать текущее число — сразу к цели, без анимации
                }
                activeTweens.push({ ref, propName, from: fromVal, to: toVal, duration, startTime: performance.now(), composite, completedRef: completedKey });
                return 0;
            });
            def('__set_parent', function (L2) {
                luaSetParent(lua.lua_tonumber(L2, 1), lua.lua_tonumber(L2, 2));
                return 0;
            });
            def('__instance_new', function (L2) {
                lua.lua_pushnumber(L2, luaCreateVirtualInstance(lua.lua_tojsstring(L2, 1)));
                return 1;
            });
            def('__clone', function (L2) {
                lua.lua_pushnumber(L2, luaCloneRef(lua.lua_tonumber(L2, 1)));
                return 1;
            });
            def('__find_service', function (L2) {
                lua.lua_pushnumber(L2, luaFindServiceRef(lua.lua_tojsstring(L2, 1)));
                return 1;
            });
            def('__root_count', function (L2) {
                lua.lua_pushnumber(L2, luaRootRefs().length);
                return 1;
            });
            def('__root_at', function (L2) {
                const roots = luaRootRefs();
                const i = lua.lua_tonumber(L2, 1);
                lua.lua_pushnumber(L2, roots[i] !== undefined ? roots[i] : -1);
                return 1;
            });
            // ============ Сигналы (:Connect) и RemoteEvent ============
            def('__register_conn', function (L2) {
                const id = lua.lua_tonumber(L2, 1);
                const ref = lua.lua_tonumber(L2, 2);
                const evName = lua.lua_tojsstring(L2, 3);
                luaSignalConns[id] = { L: L2, ref, evName };
                if (/^(Input(Began|Ended|Changed)|Mouse(Enter|Leave|Moved|Wheel|Button[12](Down|Up|Click)))$/.test(evName) &&
                    (guiPropsByRef[ref] || (luaByRef[ref] && guiClassSet.has(luaByRef[ref].cls)))) {
                    luaGuiInputRefs.add(ref);
                    const node = document.querySelector('#gui-overlay [data-ref="' + ref + '"]');
                    if (node) node.style.pointerEvents = 'auto';
                }
                const key = ref + '|' + evName;
                (luaSignalsByKey[key] = luaSignalsByKey[key] || []).push(id);
                return 0;
            });
            def('__unregister_conn', function (L2) {
                const id = lua.lua_tonumber(L2, 1);
                const conn = luaSignalConns[id];
                if (conn) {
                    const key = conn.ref + '|' + conn.evName;
                    luaSignalsByKey[key] = (luaSignalsByKey[key] || []).filter(x => x !== id);
                    delete luaSignalConns[id];
                }
                return 0;
            });
            // __fire_remote(ref, targetSide, ...) — RemoteEvent:FireServer()/
            def('__fire_remote', function (L2) {
                const ref = lua.lua_tonumber(L2, 1);
                const targetSide = lua.lua_tojsstring(L2, 2);
                const n = lua.lua_gettop(L2);
                const args = [];
                for (let i = 3; i <= n; i++) {
                    const ty = lua.lua_type(L2, i);
                    if (ty === lua.LUA_TNUMBER) args.push(lua.lua_tonumber(L2, i));
                    else if (ty === lua.LUA_TBOOLEAN) args.push(!!lua.lua_toboolean(L2, i));
                    else if (ty === lua.LUA_TSTRING) args.push(lua.lua_tojsstring(L2, i));
                    else args.push(null);
                }
                remoteQueue.push({ ref, targetSide, args, dueAt: performance.now() + 16 });
                return 0;
            });
            def('__fire_bindable', function (L2) {
                // BindableEvent:Fire(...) — синхронно, в отличие от
                const ref = lua.lua_tonumber(L2, 1);
                const n = lua.lua_gettop(L2);
                const args = [];
                for (let i = 2; i <= n; i++) {
                    const ty = lua.lua_type(L2, i);
                    if (ty === lua.LUA_TNUMBER) args.push(lua.lua_tonumber(L2, i));
                    else if (ty === lua.LUA_TBOOLEAN) args.push(!!lua.lua_toboolean(L2, i));
                    else if (ty === lua.LUA_TSTRING) args.push(lua.lua_tojsstring(L2, i));
                    else if (ty === lua.LUA_TTABLE) {
                        lua.lua_getfield(L2, i, '__ref');
                        if (lua.lua_isnumber(L2, -1)) args.push({ __instanceRef: lua.lua_tonumber(L2, -1) });
                        else args.push(null);
                        lua.lua_pop(L2, 1);
                    } else {
                        args.push(null);
                    }
                }
                fireLuaSignal(ref, 'Event', args);
                return 0;
            });
        }

        // ====================== Luau -> Lua препроцессор ======================

        // [{type:'code'|'skip', text}] — 'skip' это строки ('...','"...",
        function splitLuaSegments(src) {
            const segs = [];
            let i = 0, n = src.length, start = 0;
            const flushCode = (end) => { if (end > start) segs.push({ type: 'code', text: src.slice(start, end) }); };
            while (i < n) {
                const c = src[i];
                if (c === '-' && src[i + 1] === '-') {
                    flushCode(i);
                    let j = i + 2;
                    const lb = matchLuaLongBracket(src, j);
                    if (lb) j = lb.end;
                    else { while (j < n && src[j] !== '\n') j++; }
                    segs.push({ type: 'skip', text: src.slice(i, j) });
                    i = j; start = j; continue;
                }
                if (c === '"' || c === "'") {
                    flushCode(i);
                    let j = i + 1;
                    while (j < n && src[j] !== c) { if (src[j] === '\\') j++; j++; }
                    j = Math.min(j + 1, n);
                    segs.push({ type: 'skip', text: src.slice(i, j) });
                    i = j; start = j; continue;
                }
                if (c === '[') {
                    const lb = matchLuaLongBracket(src, i);
                    if (lb) {
                        flushCode(i);
                        segs.push({ type: 'skip', text: src.slice(i, lb.end) });
                        i = lb.end; start = lb.end; continue;
                    }
                }
                i++;
            }
            flushCode(n);
            return segs;
        }
        // [=*[ ... ]=*] — длинная строка/комментарий Lua. null, если в
        // позиции i такой конструкции нет (одиночная '[' — просто скобка).
        function matchLuaLongBracket(src, i) {
            if (src[i] !== '[') return null;
            let j = i + 1, eq = 0;
            while (src[j] === '=') { eq++; j++; }
            if (src[j] !== '[') return null;
            j++;
            const close = ']' + '='.repeat(eq) + ']';
            const idx = src.indexOf(close, j);
            return { end: idx === -1 ? src.length : idx + close.length };
        }

        // "x OP= y" -> "x = x OP (y)" — только внутри code-сегментов.
        function expandCompoundAssign(code) {
            const opRe = /([+\-*/%^]|\.\.|\/\/)=(?!=)/g;
            const lvRe = /([A-Za-z_][A-Za-z0-9_]*(?:\s*\.\s*[A-Za-z_][A-Za-z0-9_]*|\s*\[[^\[\]]*\])*)\s*$/;
            let out = '', last = 0, m;
            while ((m = opRe.exec(code))) {
                const opStart = m.index, opEnd = opStart + m[0].length, op = m[1];
                let ls = opStart;
                while (ls > 0 && /\s/.test(code[ls - 1])) ls--;
                const lvMatch = lvRe.exec(code.slice(0, ls));
                if (!lvMatch) continue; // не похоже на lvalue — не наш случай, оставляем как есть
                const lvalue = lvMatch[1];
                const lvStartIdx = lvMatch.index;
                let re = opEnd, depth = 0;
                while (re < code.length) {
                    const ch = code[re];
                    if (ch === '(' || ch === '[' || ch === '{') depth++;
                    else if (ch === ')' || ch === ']' || ch === '}') { if (depth === 0) break; depth--; }
                    else if (depth === 0 && (ch === ';' || ch === '\n')) break;
                    else if (depth === 0 && /[A-Za-z_]/.test(ch) && !/[A-Za-z0-9_]/.test(code[re - 1] || ' ') &&
                             /^(?:end|else|elseif|until)(?![A-Za-z0-9_])/.test(code.slice(re, re + 7))) break;
                    re++;
                }
                const rhs = code.slice(opEnd, re).trim();
                out += code.slice(last, lvStartIdx) + `${lvalue} = ${lvalue} ${op} (${rhs})`;
                last = re;
                opRe.lastIndex = re;
            }
            out += code.slice(last);
            return out;
        }

        // "for k, v in EXPR do" -> "for k, v in __geniter(EXPR) do"
        // (обобщённый for Luau). Числовой for ("for i = 1, n do") не трогаем.
        function expandGenericFor(segs) {
            const tokRe = /[A-Za-z_][A-Za-z0-9_]*|[()\[\]{}]/g;
            let stage = null, depth = 0;   // stage: null | 'names' | 'expr'
            for (const seg of segs) {
                if (seg.type !== 'code') continue;
                let out = '', last = 0, m;
                tokRe.lastIndex = 0;
                while ((m = tokRe.exec(seg.text))) {
                    const w = m[0], idx = m.index, end = idx + w.length;
                    if (stage === null) {
                        if (w === 'for') stage = 'names';
                    } else if (stage === 'names') {
                        if (w === 'in') {
                            out += seg.text.slice(last, end) + ' __geniter(';
                            last = end; stage = 'expr'; depth = 0;
                        } else if (w === 'do') {
                            stage = null; // числовой for
                        }
                    } else { // expr
                        if (w === '(' || w === '[' || w === '{') depth++;
                        else if (w === ')' || w === ']' || w === '}') depth--;
                        else if (w === 'do' && depth <= 0) {
                            out += seg.text.slice(last, idx) + ') ';
                            last = idx; stage = null;
                        }
                    }
                }
                out += seg.text.slice(last);
                seg.text = out;
            }
        }

        // continue -> goto __continue_N + метка перед закрывающим end/until
        function expandContinue(src) {
            const segs = splitLuaSegments(src);
            let loopId = 0;
            const stack = [];
            let pendingLoopDo = false;
            const wordRe = /[A-Za-z_][A-Za-z0-9_]*/g;
            for (const seg of segs) {
                if (seg.type !== 'code') continue;
                let out = '', last = 0;
                wordRe.lastIndex = 0;
                let m;
                while ((m = wordRe.exec(seg.text))) {
                    const w = m[0], idx = m.index;
                    // `return` обязан быть последним оператором блока, а метка ::__continue_N:: перед `end` цикла
                    // идёт после него -> "'end' expected near '::'". Внутри циклов оборачиваем return в do ... end.
                    if ((w === 'end' || w === 'else' || w === 'elseif' || w === 'until') &&
                        stack.length && stack[stack.length - 1].kind === 'ret') {
                        stack.pop();
                        out += seg.text.slice(last, idx) + ' end ';
                        last = idx;
                    }
                    if (w === 'return') {
                        let inLoop = false;
                        for (let k = stack.length - 1; k >= 0; k--) {
                            if (stack[k].kind === 'function') break;
                            if (stack[k].kind === 'loop' || stack[k].kind === 'repeat') { inLoop = true; break; }
                        }
                        if (inLoop) {
                            out += seg.text.slice(last, idx) + 'do return';
                            stack.push({ kind: 'ret' });
                            last = idx + w.length; continue;
                        }
                    }
                    if (w === 'for' || w === 'while') {
                        stack.push({ kind: 'loop', id: ++loopId, continueUsed: false });
                        pendingLoopDo = true;
                        out += seg.text.slice(last, idx) + w; last = idx + w.length; continue;
                    }
                    if (w === 'repeat') {
                        stack.push({ kind: 'repeat', id: ++loopId, continueUsed: false });
                        out += seg.text.slice(last, idx) + w; last = idx + w.length; continue;
                    }
                    if (w === 'if' || w === 'function') {
                        stack.push({ kind: w === 'if' ? 'if' : 'function' });
                        out += seg.text.slice(last, idx) + w; last = idx + w.length; continue;
                    }
                    if (w === 'do') {
                        if (pendingLoopDo) pendingLoopDo = false;
                        else stack.push({ kind: 'do' });
                        out += seg.text.slice(last, idx) + w; last = idx + w.length; continue;
                    }
                    if (w === 'until') {
                        out += seg.text.slice(last, idx);
                        const frame = stack.pop();
                        if (frame && frame.continueUsed) out += `::__continue_${frame.id}:: `;
                        out += 'until'; last = idx + w.length; continue;
                    }
                    if (w === 'end') {
                        out += seg.text.slice(last, idx);
                        const frame = stack.pop();
                        if (frame && frame.kind === 'loop' && frame.continueUsed) out += `::__continue_${frame.id}:: `;
                        out += 'end'; last = idx + w.length; continue;
                    }
                    if (w === 'continue') {
                        out += seg.text.slice(last, idx);
                        let target = null;
                        for (let k = stack.length - 1; k >= 0; k--) {
                            if (stack[k].kind === 'function') break; // continue не пересекает function
                            if (stack[k].kind === 'loop' || stack[k].kind === 'repeat') { target = stack[k]; break; }
                        }
                        out += target ? (target.continueUsed = true, `goto __continue_${target.id}`) : w;
                        last = idx + w.length; continue;
                    }
                }
                out += seg.text.slice(last);
                seg.text = out;
            }
            return segs.map(s => s.text).join('');
        }

        // ----- Luau: аннотации типов, "::"-касты, type-объявления, if-выражения -----
        // Токенайзер сохраняет пробелы и комментарии, чтобы номера строк в
        // сообщениях об ошибках остались такими же, как в исходнике скрипта.
        function luauTokenize(src) {
            const toks = [], n = src.length;
            const wsRe = /\s+/y, idRe = /[A-Za-z_][A-Za-z0-9_]*/y;
            const numRe = /0[xX][0-9a-fA-F_]+|\d[\d_]*(?:\.[\d_]+)?(?:[eE][+-]?\d+)?/y;
            let i = 0;
            while (i < n) {
                const c = src[i];
                let m;
                wsRe.lastIndex = i;
                if ((m = wsRe.exec(src))) { toks.push({ t: 'ws', s: m[0] }); i += m[0].length; continue; }
                if (c === '-' && src[i + 1] === '-') {
                    let j = i + 2;
                    const lb = matchLuaLongBracket(src, j);
                    if (lb) j = lb.end; else { while (j < n && src[j] !== '\n') j++; }
                    toks.push({ t: 'com', s: src.slice(i, j) }); i = j; continue;
                }
                if (c === '"' || c === "'") {
                    let j = i + 1;
                    while (j < n && src[j] !== c) { if (src[j] === '\\') j++; j++; }
                    j = Math.min(j + 1, n);
                    toks.push({ t: 'str', s: src.slice(i, j) }); i = j; continue;
                }
                if (c === '[') {
                    const lb = matchLuaLongBracket(src, i);
                    if (lb) { toks.push({ t: 'str', s: src.slice(i, lb.end) }); i = lb.end; continue; }
                }
                idRe.lastIndex = i;
                if ((m = idRe.exec(src))) { toks.push({ t: 'id', s: m[0] }); i += m[0].length; continue; }
                numRe.lastIndex = i;
                if (c >= '0' && c <= '9' && (m = numRe.exec(src))) { toks.push({ t: 'num', s: m[0] }); i += m[0].length; continue; }
                if (src.substr(i, 3) === '...') { toks.push({ t: 'p', s: '...' }); i += 3; continue; }
                const two = src.substr(i, 2);
                if (two === '..' || two === '::' || two === '->' || two === '==' || two === '~=' || two === '<=' || two === '>=' || two === '//') {
                    toks.push({ t: 'p', s: two }); i += 2; continue;
                }
                toks.push({ t: 'p', s: c }); i++;
            }
            return toks;
        }

        // local x: T? = v / function f<T>(a: T, ...: U): R / v :: T / type X = {...} / export type ...
        function stripLuauTypes(src) {
            if (!/::|\btype\s+[A-Za-z_]|\blocal\s+[A-Za-z_]\w*\s*[:,]|\)\s*:|function[^()\n]*<|function[^()\n]*\([^()]*[A-Za-z_.]\s*:/.test(src)) return src;
            const toks = luauTokenize(src), N = toks.length, out = [];
            const isTrivia = (k) => toks[k].t === 'ws' || toks[k].t === 'com';
            const sig = (k) => { while (k < N && isTrivia(k)) k++; return k; };
            const isP = (k, s) => k < N && toks[k].t === 'p' && toks[k].s === s;
            const isId = (k, s) => k < N && toks[k].t === 'id' && (s === undefined || toks[k].s === s);
            const copy = (a, b) => { for (let k = a; k < b; k++) out.push(toks[k].s); };
            const dropTo = (a, b) => {   // выбросить [a,b), но сохранить переводы строк
                let nl = 0;
                for (let k = a; k < b; k++) for (const ch of toks[k].s) if (ch === '\n') nl++;
                if (nl) out.push('\n'.repeat(nl));
            };
            const skipBalanced = (p, open, close) => {   // toks[p] — открывающая скобка
                let depth = 0;
                for (; p < N; p++) {
                    if (isP(p, open)) depth++;
                    else if (isP(p, close)) { depth--; if (depth === 0) return p + 1; }
                }
                return N;
            };
            // возвращает индекс сразу после типа, начинающегося с токена p
            const skipType = (p) => {
                for (;;) {
                    p = sig(p);
                    if (isP(p, '...')) p = sig(p + 1);
                    if (p >= N) return N;
                    if (toks[p].t === 'str') p++;
                    else if (isP(p, '(')) {
                        p = skipBalanced(p, '(', ')');
                        const q = sig(p);
                        if (isP(q, '->')) p = skipType(q + 1);
                    } else if (isP(p, '{')) p = skipBalanced(p, '{', '}');
                    else if (isId(p)) {
                        if (toks[p].s === 'typeof' && isP(sig(p + 1), '(')) p = skipBalanced(sig(p + 1), '(', ')');
                        else {
                            p++;
                            while (isP(p, '.') && isId(p + 1)) p += 2;
                            if (isP(p, '<')) p = skipBalanced(p, '<', '>');
                        }
                    } else return p;
                    for (;;) { const q = sig(p); if (isP(q, '?')) p = q + 1; else break; }
                    const q = sig(p);
                    if (isP(q, '|') || isP(q, '&')) { p = q + 1; continue; }
                    return p;
                }
            };
            const prevSigIsDotOrColon = (k) => {
                k--;
                while (k >= 0 && isTrivia(k)) k--;
                return k >= 0 && toks[k].t === 'p' && (toks[k].s === '.' || toks[k].s === ':');
            };
            let i = 0;
            while (i < N) {
                const t = toks[i];
                if (t.t === 'id' && t.s === 'local') {
                    out.push('local'); i++;
                    let j = sig(i);
                    if (isId(j, 'function')) continue;
                    copy(i, j); i = j;
                    while (isId(i)) {
                        out.push(toks[i].s); i++;
                        const k = sig(i);
                        if (isP(k, ':')) { const e = skipType(k + 1); dropTo(i, e); i = e; }
                        const k2 = sig(i);
                        if (isP(k2, ',')) { copy(i, k2 + 1); i = k2 + 1; const k3 = sig(i); copy(i, k3); i = k3; continue; }
                        break;
                    }
                    continue;
                }
                if (t.t === 'id' && t.s === 'function') {
                    out.push('function'); i++;
                    let k = sig(i); copy(i, k); i = k;
                    while (isId(i) || isP(i, '.') || isP(i, ':')) { out.push(toks[i].s); i++; }
                    k = sig(i);
                    if (isP(k, '<')) { const e = skipBalanced(k, '<', '>'); dropTo(i, e); i = e; k = sig(i); }
                    copy(i, k); i = k;
                    if (isP(i, '(')) {
                        out.push('('); i++;
                        while (i < N && !isP(i, ')')) {
                            if (isP(i, ':')) { const e = skipType(i + 1); dropTo(i, e); i = e; continue; }
                            out.push(toks[i].s); i++;
                        }
                        if (i < N) { out.push(')'); i++; }
                        const r = sig(i);
                        if (isP(r, ':')) { const e = skipType(r + 1); dropTo(i, e); i = e; }
                    }
                    continue;
                }
                if (t.t === 'id' && (t.s === 'type' || t.s === 'export') && !prevSigIsDotOrColon(i)) {
                    let k = sig(i + 1);
                    if (t.s === 'export') { if (isId(k, 'type')) k = sig(k + 1); else k = -1; }
                    if (k >= 0 && isId(k)) {
                        let e = sig(k + 1);
                        if (isP(e, '=') || isP(e, '<')) {
                            if (isP(e, '<')) e = sig(skipBalanced(e, '<', '>'));
                            if (isP(e, '=')) { e = skipType(e + 1); dropTo(i, e); i = e; continue; }
                        }
                    }
                }
                if (t.t === 'p' && t.s === '::') { const e = skipType(i + 1); dropTo(i, e); i = e; continue; }
                out.push(t.s); i++;
            }
            return out.join('');
        }

        // Luau: "if c then a elseif c2 then b else d" как ВЫРАЖЕНИЕ
        //   -> (function() if c then return (a) elseif c2 then return (b) else return (d) end end)()
        function expandIfExpressions(src) {
            if (!/(?:[=(,{\[+\-*\/%^#<>]|\.\.|\b(?:return|and|or|not))\s*if\b/.test(src)) return src;
            const toks = luauTokenize(src), N = toks.length;
            const isTrivia = (k) => toks[k].t === 'ws' || toks[k].t === 'com';
            const OPS = new Set(['=', '==', '~=', '<', '>', '<=', '>=', '(', ',', '{', '[', '..', '+', '-', '*', '/', '%', '^', '#', '//']);
            const OPWORDS = new Set(['return', 'and', 'or', 'not']);
            const prevSig = (k, lo) => { k--; while (k >= lo && isTrivia(k)) k--; return k >= lo ? k : -1; };
            // 'if' в позиции k — выражение? lo — начало диапазона-выражения (там 'if' сразу в начале — тоже выражение)
            const isExprIf = (k, lo, rangeIsExpr) => {
                const p = prevSig(k, lo);
                if (p < 0) return !!rangeIsExpr;
                const pt = toks[p];
                return (pt.t === 'p' && OPS.has(pt.s)) || (pt.t === 'id' && OPWORDS.has(pt.s));
            };
            const BLOCK_OPEN = new Set(['function', 'do', 'repeat']);
            // индекс токена-терминатора выражения, начиная с p
            const scanExpr = (p) => {
                let depth = 0, block = 0, nest = 0, prevOperand = false, nl = false;
                for (; p < N; p++) {
                    const t = toks[p];
                    if (t.t === 'ws') { if (t.s.indexOf('\n') >= 0) nl = true; continue; }
                    if (t.t === 'com') continue;
                    if (block > 0) {
                        if (t.t === 'id') {
                            if (BLOCK_OPEN.has(t.s)) block++;
                            else if (t.s === 'if' && !isExprIf(p, 0, false)) block++;
                            else if (t.s === 'end' || t.s === 'until') { block--; if (block === 0) { prevOperand = true; nl = false; } }
                        }
                        continue;
                    }
                    if (t.t === 'p') {
                        const s = t.s;
                        if (s === '(' || s === '[' || s === '{') { depth++; prevOperand = false; }
                        else if (s === ')' || s === ']' || s === '}') { if (depth === 0) return p; depth--; prevOperand = true; }
                        else if ((s === ',' || s === ';') && depth === 0) return p;
                        else prevOperand = (s === '...');
                        nl = false; continue;
                    }
                    if (depth > 0) { if (t.t === 'id' && t.s === 'function') block++; prevOperand = true; continue; }
                    if (t.t === 'num' || t.t === 'str') {
                        if (prevOperand && (nl || t.t === 'num')) return p;
                        prevOperand = true; nl = false; continue;
                    }
                    const w = t.s;
                    if (w === 'and' || w === 'or' || w === 'not') { prevOperand = false; nl = false; continue; }
                    if (w === 'if') {
                        if (prevOperand) return p;          // начало следующего оператора
                        nest++; prevOperand = false; nl = false; continue;
                    }
                    if (w === 'then' || w === 'elseif') { if (nest > 0) { prevOperand = false; nl = false; continue; } return p; }
                    if (w === 'else') { if (nest > 0) { nest--; prevOperand = false; nl = false; continue; } return p; }
                    if (w === 'function') { block++; prevOperand = false; nl = false; continue; }
                    if (w === 'end' || w === 'do' || w === 'until' || w === 'local' || w === 'return' ||
                        w === 'for' || w === 'while' || w === 'repeat' || w === 'break' || w === 'continue') return p;
                    if (w === 'nil' || w === 'true' || w === 'false') { if (prevOperand) return p; prevOperand = true; nl = false; continue; }
                    // обычный идентификатор
                    if (prevOperand) return p;               // два операнда подряд — граница выражения
                    prevOperand = true; nl = false;
                }
                return N;
            };
            const isId = (k, s) => k < N && toks[k].t === 'id' && toks[k].s === s;
            const rewrite = (a, b, rangeIsExpr) => {
                let out = '';
                let k = a;
                while (k < b) {
                    if (isId(k, 'if') && isExprIf(k, a, rangeIsExpr)) {
                        const r = parseIf(k, b);
                        if (r) { out += r.text; k = r.end; continue; }
                    }
                    out += toks[k].s; k++;
                }
                return out;
            };
            const parseIf = (k, limit) => {
                const parts = [];
                let p = k + 1;
                for (;;) {
                    const cEnd = scanExpr(p);
                    if (cEnd >= limit || !isId(cEnd, 'then')) return null;
                    const vStart = cEnd + 1, vEnd = scanExpr(vStart);
                    if (vEnd >= limit) return null;
                    parts.push({ c: [p, cEnd], v: [vStart, vEnd] });
                    if (isId(vEnd, 'elseif')) { p = vEnd + 1; continue; }
                    if (isId(vEnd, 'else')) {
                        const eStart = vEnd + 1, eEnd = Math.min(scanExpr(eStart), limit);
                        let text = '(function() ';
                        parts.forEach((pt, idx) => {
                            text += (idx === 0 ? 'if ' : ' elseif ') + rewrite(pt.c[0], pt.c[1], true) +
                                ' then return (' + rewrite(pt.v[0], pt.v[1], true) + ')';
                        });
                        text += ' else return (' + rewrite(eStart, eEnd, true) + ') end end)()';
                        return { text, end: eEnd };
                    }
                    return null;
                }
            };
            return rewrite(0, N, false);
        }

        // Luau-литералы, которых нет в Lua 5.3: интерполяция `текст {выражение}` -> ("текст" .. tostring(выражение)),
        // числа с подчёркиваниями 1_000_000 и двоичные 0b1010. Строки/комментарии не трогаем; число строк сохраняется
        // (переносы внутри `...` пишутся как \<перевод строки>), поэтому номера строк в ошибках остаются верными.
        function expandLuauLiterals(src) {
            if (src.indexOf('`') < 0 && !/\d_|0[bB][01]/.test(src)) return src;   // быстрый путь
            const n = src.length;
            const numRe = /0[xX][0-9a-fA-F_]+|0[bB][01_]+|\d[\d_]*(?:\.[\d_]*)?(?:[eE][+-]?[\d_]+)?|\.\d[\d_]*(?:[eE][+-]?[\d_]+)?/y;
            const identRe = /[A-Za-z_][A-Za-z0-9_]*/y;
            const longOpen = (k) => {
                if (src[k] !== '[') return 0;
                let j = k + 1;
                while (src[j] === '=') j++;
                return src[j] === '[' ? j - k + 1 : 0;
            };
            const skipLong = (k, openLen) => {
                const close = ']' + '='.repeat(openLen - 2) + ']';
                const e = src.indexOf(close, k + openLen);
                return e < 0 ? n : e + close.length;
            };
            const skipQuoted = (k) => {
                const q = src[k];
                let j = k + 1;
                while (j < n && src[j] !== q && src[j] !== '\n') { if (src[j] === '\\') j++; j++; }
                return Math.min(j + 1, n);
            };
            let skipBraces;
            const skipBacktick = (k) => {            // индекс после закрывающей ` (учитывает вложенные {...})
                let j = k + 1;
                while (j < n) {
                    const c = src[j];
                    if (c === '\\') { j += 2; continue; }
                    if (c === '`') return j + 1;
                    if (c === '{') j = skipBraces(j); else j++;
                }
                return n;
            };
            skipBraces = (k) => {                     // k — на '{'; индекс после парной '}'
                let depth = 0, j = k;
                while (j < n) {
                    const c = src[j];
                    if (c === '"' || c === "'") { j = skipQuoted(j); continue; }
                    if (c === '`') { j = skipBacktick(j); continue; }
                    if (c === '{') depth++;
                    else if (c === '}') { depth--; if (depth === 0) return j + 1; }
                    j++;
                }
                return n;
            };
            const convertInterp = (k) => {
                const end = skipBacktick(k);
                const bodyEnd = (src[end - 1] === '`') ? end - 1 : end;
                const pieces = [];
                let cur = '', j = k + 1;
                const flush = () => { if (cur !== '') { pieces.push('"' + cur + '"'); cur = ''; } };
                while (j < bodyEnd) {
                    const c = src[j];
                    if (c === '\\') {
                        const d = src[j + 1];
                        if (d === '`' || d === '{') cur += d;
                        else if (d === '"') cur += '\\"';
                        else cur += '\\' + (d === undefined ? '' : d);
                        j += 2;
                        continue;
                    }
                    if (c === '{') {
                        const e = skipBraces(j);
                        flush();
                        pieces.push('tostring(' + expandLuauLiterals(src.slice(j + 1, e - 1)) + ')');
                        j = e;
                        continue;
                    }
                    if (c === '"') cur += '\\"';
                    else if (c === '\n') cur += '\\\n';
                    else if (c !== '\r') cur += c;
                    j++;
                }
                flush();
                return { code: '(' + (pieces.length ? pieces.join(' .. ') : '""') + ')', end };
            };
            let out = '', i = 0;
            while (i < n) {
                const c = src[i];
                if (c === '-' && src[i + 1] === '-') {                   // комментарий
                    const lo = (src[i + 2] === '[') ? longOpen(i + 2) : 0;
                    let e;
                    if (lo) e = skipLong(i + 2, lo);
                    else { e = src.indexOf('\n', i); if (e < 0) e = n; }
                    out += src.slice(i, e); i = e; continue;
                }
                if (c === '"' || c === "'") { const e = skipQuoted(i); out += src.slice(i, e); i = e; continue; }
                if (c === '[') {
                    const lo = longOpen(i);
                    if (lo) { const e = skipLong(i, lo); out += src.slice(i, e); i = e; continue; }
                }
                if (c === '`') { const r = convertInterp(i); out += r.code; i = r.end; continue; }
                if (/[A-Za-z_]/.test(c)) {
                    identRe.lastIndex = i;
                    const m = identRe.exec(src);
                    out += m[0]; i += m[0].length; continue;
                }
                if (/\d/.test(c) || (c === '.' && /\d/.test(src[i + 1] || '') && src[i - 1] !== '.')) {
                    numRe.lastIndex = i;
                    const m = numRe.exec(src);
                    if (m) {
                        let tok = m[0];
                        if (tok.indexOf('_') >= 0 || /^0[bB]/.test(tok)) {
                            const t2 = tok.replace(/_/g, '');
                            tok = /^0[bB]/.test(t2) ? String(parseInt(t2.slice(2), 2)) : t2;
                        }
                        out += tok; i += m[0].length; continue;
                    }
                }
                out += c; i++;
            }
            return out;
        }

        function preprocessLuau(src) {
            src = expandIfExpressions(stripLuauTypes(expandLuauLiterals(src)));
            const segs = splitLuaSegments(src);
            for (const seg of segs) if (seg.type === 'code') seg.text = expandCompoundAssign(seg.text);
            expandGenericFor(segs);
            return expandContinue(segs.map(s => s.text).join(''));
        }

        // luaL_loadstring/luaL_loadbuffer работают с байтовыми буферами
        function loadLuaChunk(L, code, chunkname) {
            const { lauxlib, to_luastring } = window.fengari;
            const buf = to_luastring(preprocessLuau(code));
            return lauxlib.luaL_loadbuffer(L, buf, buf.length, to_luastring(chunkname));
        }

        function doLuaString(L, code, chunkname) {
            const { lua } = window.fengari;
            const status = loadLuaChunk(L, code, chunkname || 'chunk');
            if (status !== lua.LUA_OK) return status;
            return lua.lua_pcall(L, 0, 0, 0);
        }

        // Безопасно достаёт текст ошибки с вершины Lua-стека.
        function luaErrToString(L) {
            const { lua, lauxlib } = window.fengari;
            try {
                const s = lua.lua_tojsstring(L, -1);
                if (s !== null && s !== undefined) return s;
            } catch (e) { emuWarn('swallow:luaErrToString:9882', 'luaErrToString: ' + _errText(e) + ' (падаем на luaL_tolstring ниже)'); }
            try {
                lauxlib.luaL_tolstring(L, -1, null);
                const s2 = lua.lua_tojsstring(L, -1);
                lua.lua_pop(L, 1);
                if (s2 !== null && s2 !== undefined) return s2;
            } catch (e) { emuWarn('swallow:luaErrToString:9888', 'luaErrToString: ' + _errText(e) + ' (последний шанс — просто не строка)'); }
            return '(ошибка не строкового типа)';
        }

        // luaL_traceback — тот же стек вызовов, что Roblox Studio показывает
        function luaGetTraceback(co) {
            const { lua, lauxlib } = window.fengari;
            try {
                lauxlib.luaL_traceback(co, co, null, 1);
                const s = lua.lua_tojsstring(co, -1);
                lua.lua_pop(co, 1);
                return s;
            } catch (e) {
                return null;
            }
        }

        function resumeLuaCoroutine(co, name, nargs) {
            const { lua } = window.fengari;
            const status = lua.lua_resume(co, null, nargs);
            if (status === lua.LUA_YIELD) return; // ушёл в wait(), уже в luaWaits
            if (status !== lua.LUA_OK) {
                const msg = luaErrToString(co);
                logLuaOutput('error', msg, name, luaGetTraceback(co), luaScriptSideByCo.get(co));
            }
        }

        // Полный путь до объекта (A.B.C.ScriptName) — на карте полно РАЗНЫХ
        function luaFullPathOf(ref) {
            const parts = [];
            let cur = ref, guard = 0;
            while (cur !== undefined && cur !== -1 && guard++ < 50) {
                const inst = luaByRef[cur];
                if (!inst) break;
                parts.unshift(inst.name);
                cur = luaParentByRef[cur];
            }
            return parts.length ? parts.join('.') : (luaByRef[ref] ? luaByRef[ref].name : ('ref' + ref));
        }

        function runLuaScript(scr, L) {
            const { lua } = window.fengari;
            const path = luaFullPathOf(scr.ref);
            // function(script) ... end — превращает `script` в upvalue КОНКРЕТНОЙ
            const wrapped = 'return function(script)\n' + scr.source + '\nend';
            let status = loadLuaChunk(L, wrapped, path);
            if (status !== lua.LUA_OK) {
                logLuaOutput('error', t('lua_compile_error') + luaErrToString(L), path, null, scr.cls);
                lua.lua_pop(L, 1);
                return;
            }
            status = lua.lua_pcall(L, 0, 1, 0);
            if (status !== lua.LUA_OK) {
                logLuaOutput('error', luaErrToString(L), path, null, scr.cls);
                lua.lua_pop(L, 1);
                return;
            }
            const co = lua.lua_newthread(L);     // пушится на стек L, возвращается co
            lua.lua_pushvalue(L, -2);            // копия функции под свежесозданным потоком
            lua.lua_xmove(L, co, 1);             // переносим функцию на стек co
            lua.lua_getglobal(co, '__wrap');
            lua.lua_pushnumber(co, scr.ref);
            lua.lua_call(co, 1, 1);              // co: [функция, script-инстанс]
            lua.lua_pop(L, 2);                   // со стека L убираем саму функцию и поток
            // (поток жив, пока жива JS-ссылка co — см. luaWaits/резюмирование;
            // сборка Lua-мусора у fengari завязана на JS GC)
            luaScriptNameByCo.set(co, path);
            luaScriptSideByCo.set(co, scr.cls);
            resumeLuaCoroutine(co, path, 1);
        }

        // Клонирует поддерево StarterGui в PlayerGui конкретного клиента —
        function cloneStarterGuiIntoPlayerGui(playerGuiRef) {
            const starterGuiRef = luaFindServiceRef('StarterGui');
            const refMap = {};
            if (starterGuiRef === -1) return refMap;

            function cloneNode(origRef, newParentRef) {
                const origInfo = luaByRef[origRef];
                if (!origInfo) return;
                const newRef = luaCreateVirtualInstance(origInfo.cls);
                luaByRef[newRef].name = origInfo.name;
                luaSetParent(newRef, newParentRef);
                refMap[origRef] = newRef;
                // копия знает оригинал: по нему require(копия-ModuleScript) находит исходник (см. __compile_module)
                luaCloneOrigin[newRef] = luaCloneOrigin[origRef] !== undefined ? luaCloneOrigin[origRef] : origRef;
                luaCloneSource[newRef] = origRef;
                if (guiPropsByRef[origRef]) {
                    guiPropsByRef[newRef] = Object.assign({}, guiPropsByRef[origRef], { cls: origInfo.cls, ref: newRef, parent: newParentRef });
                }
                for (const childRef of (luaChildrenByRef[origRef] || [])) {
                    if (childRef !== newRef) cloneNode(childRef, newRef);
                }
            }
            for (const childRef of (luaChildrenByRef[starterGuiRef] || []).slice()) {
                cloneNode(childRef, playerGuiRef);
            }
            return refMap;
        }

        // Синтетический PlayerModule — в настоящем Roblox это закрытый
        const PLAYER_MODULE_SOURCE = [
            'local PlayerModule = {}',
            'local Controls = {}',
            'Controls.__index = Controls',
            'function Controls:Disable() __set_controls_enabled(false) end',
            'function Controls:Enable() __set_controls_enabled(true) end',
            'function PlayerModule:GetControls() return setmetatable({}, Controls) end',
            'return PlayerModule',
        ].join('\n');

        // Создаёт game.Players.LocalPlayer (виртуальный, как и всё Play-only
        let luaCharacterRef = -1; // ref виртуального "Model", изображающего player.Character (см. __get_character_ref) — тот самый ходящий куб из Play, а не настоящий Humanoid
        let luaPlayerRef = -1;    // ref единственного LocalPlayer (см. bootstrapClientPlayer) — нужен, чтобы подставлять его первым аргументом в OnServerEvent (см. processRemoteQueue)
        let luaHumanoidRootPartRef = -1; // ref виртуального HumanoidRootPart — physicsBodies[этот ref] === charBody (см. bootstrapClientPlayer)
        let luaHumanoidRef = -1;         // ref виртуального Humanoid — WalkSpeed/JumpPower реально применяются (см. luaSetGenericProp)

        function bootstrapClientPlayer() {
            let playersRef = luaFindServiceRef('Players');
            if (playersRef === -1) playersRef = luaCreateVirtualInstance('Players');
            const playerRef = luaCreateVirtualInstance('Player');
            luaByRef[playerRef].name = 'LocalPlayer';
            if (playerAccount) { luaPlayerRef = playerRef; _applyPlayerAccountToLua(); }
            luaSetParent(playerRef, playersRef);
            // Как в Roblox: игрок при входе попадает в AutoAssignable-команду с наименьшим числом игроков (игрок один —
            // первая по порядку файла). Без этого player.Team == nil и скрипты (TDM, Scoring, TeamCollisionFiltering)
            // считают игрока нейтральным.
            const _autoTeams = Object.keys(luaTeamInfo).map(Number).filter(r => luaTeamInfo[r].auto);
            luaPlayerTeam = _autoTeams.length ? _autoTeams[0] : -1;

            luaCharacterRef = luaCreateVirtualInstance('Model');
            luaByRef[luaCharacterRef].name = 'LocalCharacter';
            luaSetParent(luaCharacterRef, luaWorkspaceRef());

            luaHumanoidRootPartRef = luaCreateVirtualInstance('Part');
            luaByRef[luaHumanoidRootPartRef].name = 'HumanoidRootPart';
            luaSetParent(luaHumanoidRootPartRef, luaCharacterRef);
            // Так Position/CFrame-геттеры и сеттеры (luaPositionOfRef/
            // luaSetPositionOfRef/applyCFrameValue) начинают работать сами
            // собой — они уже умеют physicsBodies[ref], отдельный код не
            // нужен: чтение/запись CFrame этого рефа напрямую двигает
            // charBody, то есть по-настоящему телепортирует игрока.
            if (charBody) { physicsBodies[luaHumanoidRootPartRef] = charBody; charBody.__ref = luaHumanoidRootPartRef; }
            touchingTriggers = new Set();

            luaHumanoidRef = luaCreateVirtualInstance('Humanoid');
            luaByRef[luaHumanoidRef].name = 'Humanoid';
            luaSetParent(luaHumanoidRef, luaCharacterRef);
            virtualInstanceProps[luaHumanoidRef].WalkSpeed = charWalkSpeed;
            virtualInstanceProps[luaHumanoidRef].JumpPower = charJumpPower;
            virtualInstanceProps[luaHumanoidRef].Health = 100;
            luaCharDead = false;
            virtualInstanceProps[luaHumanoidRef].MaxHealth = 100;
            virtualInstanceProps[luaHumanoidRef].JumpHeight = 7.2;
            virtualInstanceProps[luaHumanoidRef].HipHeight = 1.35; // R15 (characterR15.rbxm)
            virtualInstanceProps[luaHumanoidRef].AutoJumpEnabled = true;

            const playerGuiRef = luaCreateVirtualInstance('PlayerGui');
            luaSetParent(playerGuiRef, playerRef);
            const backpackRef = luaCreateVirtualInstance('Backpack'); // существует для полноты API; не рендерится
            luaSetParent(backpackRef, playerRef);
            // Как в Roblox: при появлении игрока всё из StarterPack копируется в Backpack. Раньше Backpack оставался пустым, и
            // самописный инвентарь/хотбар (InventoryController: слоты строятся по Backpack) не получал ни одного инструмента.
            const starterPackRef = Object.keys(luaByRef).map(Number).find(r => luaByRef[r] && luaByRef[r].cls === 'StarterPack' && luaParentByRef[r] === -1);
            if (starterPackRef !== undefined) {
                for (const childRef of (luaChildrenByRef[starterPackRef] || []).slice()) {
                    try { luaSetParent(luaCloneRef(childRef), backpackRef); }
                    catch (e) { console.warn('StarterPack -> Backpack:', e); }
                }
            }

            const playerScriptsRef = luaCreateVirtualInstance('PlayerScripts');
            luaSetParent(playerScriptsRef, playerRef);
            const playerModuleRef = luaCreateVirtualInstance('ModuleScript');
            luaByRef[playerModuleRef].name = 'PlayerModule';
            luaSetParent(playerModuleRef, playerScriptsRef);
            luaModuleSourceByRef[playerModuleRef] = PLAYER_MODULE_SOURCE;
            luaModuleNameByRef[playerModuleRef] = 'PlayerModule';

            const refMap = cloneStarterGuiIntoPlayerGui(playerGuiRef);
            return { playerRef, playerGuiRef, refMap };
        }

        async function startLuaScripts() {
            luaOutputLines = [];
            renderLuaOutput();
            try { await startLuaScriptsInner(); }
            catch (e) {
                logLuaOutput('error', t('lua_run_aborted') + (e && e.message ? e.message : String(e)));
                console.error('[Lua] startLuaScripts:', e);
            }
        }

        async function startLuaScriptsInner() {
            luaLogSessionId = 'play_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
            const r = await api('GET', '/api/scripts');
            if (!isPlaying) return;
            if (!r || !r.ok) { logLuaOutput('error', t('lua_scripts_no_reply')); return; }
            if (!r.scripts || !r.scripts.length) { logLuaOutput('warn', t('lua_no_scripts')); return; }

            logLuaOutput('info', 'script.js build: ' + BUILD_LABEL);
            checkBuildConsistency(); // запуск Play чистит Output — проверку версий файлов показываем и здесь
            if (!await ensureFengariLoaded()) {
                logLuaOutput('error', t('lua_fengari_fail'));
                notify(t('lua_vm_fail_notify'), 'err');
                return;
            }
            if (!isPlaying) return; // Play могли остановить, пока грузился fengari

            // Сырой индекс иерархии для script.Parent/GetChildren — из
            // /api/all_instances (весь файл, без фильтров Explorer-дерева).
            const allR = await api('GET', '/api/all_instances');
            luaByRef = {}; luaByRefVer++;
            luaParentByRef = {};
            luaChildrenByRef = {};
            luaInitValues = [];
            luaPartXform = {};
            luaAttCF = {};
            luaRefProps = {};
            luaWelds = [];
            luaCloneOrigin = {};
            luaCloneSource = {};
            luaFileAttrs = {}; luaFileTags = {}; luaTeamInfo = {}; luaPlayerTeam = -1; luaFilePivots = {};
            if (window._emuWarned) window._emuWarned.clear();
            luaCollGroups = {}; luaNextGroupBit = 4; luaGroupCollide = {}; luaPartGroup = {};
            playCamDist = THIRD_PERSON_DIST;
            if (allR && allR.ok && allR.instances) {
                for (const inst of allR.instances) {
                    luaByRef[inst.ref] = { cls: inst.cls, name: inst.name }; luaByRefVer++;
                    luaParentByRef[inst.ref] = inst.parent;
                    if (inst.attrs) luaFileAttrs[inst.ref] = inst.attrs;
                    if (inst.tags) luaFileTags[inst.ref] = inst.tags;
                    if (inst.pivot) luaFilePivots[inst.ref] = inst.pivot;
                    if (inst.gprops) luaGenericPropsByRef[inst.ref] = Object.assign({}, inst.gprops);   // Tool.TextureId/ToolTip/... из файла
                    if (inst.cls === 'Team') luaTeamInfo[inst.ref] = { color: inst.teamColor, auto: inst.autoAssignable !== false };
                    if (inst.att) luaAttCF[inst.ref] = inst.att;
                    if (inst.refs) luaRefProps[inst.ref] = inst.refs;
                    // ValueBase.Value, заданное в самом файле (IntValue = 10, CFrameValue, ...)
                    if (inst.value !== undefined && inst.value !== null) {
                        if (typeof inst.value === 'object') luaInitValues.push({ ref: inst.ref, value: inst.value });
                        else (luaGenericPropsByRef[inst.ref] = luaGenericPropsByRef[inst.ref] || {}).Value = inst.value;
                    }
                    // Sound, уже лежащий В ФАЙЛЕ (не Instance.new(...) из
                    if (inst.cls === 'Sound' && inst.soundId) {
                        const a = getOrCreateSoundEl(inst.ref);
                        const url = rbxAssetIdToProxyUrl(inst.soundId);
                        if (url) a.src = url;
                        (luaGenericPropsByRef[inst.ref] = luaGenericPropsByRef[inst.ref] || {}).SoundId = inst.soundId;
                        if (typeof inst.volume === 'number') a.volume = Math.max(0, Math.min(1, inst.volume));
                        if (inst.looped) a.loop = true;
                        // PlaybackSpeed, заданный ПРЯМО в файле (см.
                        if (typeof inst.playbackSpeed === 'number') _soundBaseSpeed[inst.ref] = inst.playbackSpeed;
                        if (typeof inst.pitchOctave === 'number') _soundPitchOctave[inst.ref] = inst.pitchOctave;
                        _applySoundRate(inst.ref);
                    }
                }
                for (const inst of allR.instances) {
                    if (inst.parent !== undefined && inst.parent !== -1) {
                        (luaChildrenByRef[inst.parent] = luaChildrenByRef[inst.parent] || []).push(inst.ref);
                    }
                }
            } else {
                logLuaOutput('warn', t('lua_instances_no_reply'));
            }
            if (!isPlaying) return; // Play могли остановить, пока шёл запрос

            // GUI-дерево (для клонирования StarterGui->PlayerGui и для
            const guiR = await api('GET', '/api/gui_tree');
            guiPropsByRef = {};
            guiChildrenByRef = {};
            if (guiR && guiR.ok && guiR.elements) {
                for (const item of guiR.elements) guiPropsByRef[item.ref] = item;
            }

            const { lua, lauxlib, lualib } = window.fengari;
            luaServerL = lauxlib.luaL_newstate();
            lualib.luaL_openlibs(luaServerL);
            installLuaBridge(luaServerL);
            luaClientL = lauxlib.luaL_newstate();
            lualib.luaL_openlibs(luaClientL);
            installLuaBridge(luaClientL);

            for (const [L, label] of [[luaServerL, 'сервера'], [luaClientL, 'клиента']]) {
                // база для id подписок: у клиентской VM свой диапазон (см. __nextConnId в prelude)
                lua.lua_pushnumber(L, L === luaClientL ? 1000000 : 0);
                lua.lua_setglobal(L, '__CONN_BASE');
                const preludeStatus = doLuaString(L, LUA_PRELUDE, 'prelude');
                if (preludeStatus !== lua.LUA_OK) {
                    logLuaOutput('error', 'Lua prelude (' + label + '): ' + luaErrToString(L));
                    luaServerL = null; luaClientL = null;
                    return;
                }
                if (luaInitValues.length) {
                    const ivCode = luaInitValues.map(iv =>
                        '__init_value(' + iv.ref + ',"' + iv.value.k + '",' + iv.value.v.join(',') + ')').join('\n');
                    const ivStatus = doLuaString(L, ivCode, 'initvalues');
                    if (ivStatus !== lua.LUA_OK) logLuaOutput('warn', 'initvalues (' + label + '): ' + luaErrToString(L));
                }
            }

            // ModuleScript-исходники по ref — require() ищет тут (см.
            luaScriptsByRef = {};
            luaStartedClonedScripts = new Set();
            for (const scr of r.scripts) luaScriptsByRef[scr.ref] = scr;
            luaModuleSourceByRef = {};
            luaModuleNameByRef = {};
            for (const scr of r.scripts) {
                if (scr.cls !== 'ModuleScript') continue;
                luaModuleSourceByRef[scr.ref] = scr.source;
                luaModuleNameByRef[scr.ref] = scr.name;
            }

            luaWaits = [];
            luaSignalWaits = [];
            luaResetSignals();

            // Script с RunContext=Client (2) — клиентский: идёт вместе с LocalScript-ами (нужен Players.LocalPlayer).
            // Скрипты из StarterCharacterScripts запускаются ПОСЛЕ создания персонажа, как его дети (script.Parent = Character).
            const _isClientScript = (scr) => scr.cls === 'LocalScript' || (scr.cls === 'Script' && scr.runContext === 2);
            const _underCharacterScripts = (ref) => {
                let cur = luaParentByRef[ref], g = 0;
                while (cur !== undefined && cur !== -1 && g++ < 50) {
                    const ii = luaByRef[cur];
                    if (ii && ii.name === 'StarterCharacterScripts') return true;
                    cur = luaParentByRef[cur];
                }
                return false;
            };

            // Server-скрипты (Script) выполняются как есть — по одному
            // разу, "на сервере", видят реальную (нефильтрованную) карту.
            // В Roblox скрипты из ServerStorage не выполняются вообще (это склад шаблонов). Эмулятор запускал и их, из-за чего
            // шаблон врага (EnemyTemplates/ЖИЛЕЦ) жил своей жизнью параллельно настоящему: двойной ИИ, лишние атаки и скримеры.
            // Клоны шаблонов в Workspace по-прежнему запускаются (luaStartClonedScripts), так что спавнеры работают как раньше.
            const _inServerStorage = (ref) => {
                let cur = ref, g = 0;
                while (cur !== undefined && cur !== -1 && g++ < 200) {
                    const ii = luaByRef[cur];
                    if (ii && luaParentByRef[cur] === -1) return ii.cls === 'ServerStorage' || ii.cls === 'StarterPack';
                    cur = luaParentByRef[cur];
                }
                return false;
            };
            for (const scr of r.scripts) {
                if (scr.cls !== 'Script' || _isClientScript(scr) || _underCharacterScripts(scr.ref) || _inServerStorage(scr.ref)) continue;
                try { runLuaScript(scr, luaServerL); }
                catch (e) { logLuaOutput('error', scr.name + ': ' + e.message, scr.name, null, scr.cls); }
            }

            // Client: сначала bootstrapClientPlayer() клонирует StarterGui
            let refMap = {};
            try {
                const bootResult = bootstrapClientPlayer();
                refMap = bootResult.refMap;
                luaPlayerRef = bootResult.playerRef;
            } catch (e) {
                // Раньше исключение тут (не пойманное) обрывало ВСЮ функцию —
                logLuaOutput('error', 'bootstrapClientPlayer упал: ' + e.message + ' — LocalScript-и и GUI не запущены');
            }
            // GUI должен существовать в DOM ДО запуска LocalScript-ов (в Roblox PlayerGui уже собран): иначе AbsoluteSize/
            // AbsolutePosition на старте = 0 и хотбар (hotBar.Grid.CellSize = AbsoluteSize.Y) схлопывал ячейки в ноль.
            // После запуска скриптов overlay перерисовывается начисто (renderGuiOverlayFromClient ниже) уже с их правками.
            try { renderGuiOverlayFromClient(); } catch (e) { console.warn('early GUI render:', e); }
            for (const scr of r.scripts) {
                if (!_isClientScript(scr) || _underCharacterScripts(scr.ref)) continue;
                const clonedRef = refMap[scr.ref];
                const runAs = Object.assign({}, scr, { cls: 'LocalScript' }, clonedRef !== undefined ? { ref: clonedRef } : {});
                try { runLuaScript(runAs, luaClientL); }
                catch (e) { logLuaOutput('error', scr.name + ': ' + e.message, scr.name, null, 'LocalScript'); }
            }

            // Игрок «вошёл»: серверные скрипты уже подписались на Players.PlayerAdded — сообщаем им (раньше событие не
            // приходило вообще, и Gameplay-скрипты Blaster никогда не видели игрока). Затем, если скрипты не выключили
            // Players.CharacterAutoLoads, спавнится первый персонаж (CharacterAdded); иначе его создаст LoadCharacter().
            setTimeout(() => {
                if (!isPlaying || luaPlayerRef === -1) return;
                const playersRef = luaFindServiceRef('Players');
                fireLuaSignal(playersRef, 'PlayerAdded', [{ __instanceRef: luaPlayerRef }]);
                const auto = (luaGenericPropsByRef[playersRef] || {}).CharacterAutoLoads;
                if (auto !== false) setTimeout(() => {
                    if (isPlaying) fireLuaSignal(luaPlayerRef, 'CharacterAdded', [{ __instanceRef: luaCharacterRef }]);
                }, 0);
            }, 0);

            // StarterCharacterScripts: копия скрипта становится ребёнком Character (в Roblox их клонируют в каждого
            // персонажа), поэтому script.Parent.Humanoid и т.п. находятся.
            if (luaCharacterRef !== -1) {
                for (const scr of r.scripts) {
                    if ((scr.cls !== 'Script' && scr.cls !== 'LocalScript') || !_underCharacterScripts(scr.ref)) continue;
                    const client = _isClientScript(scr);
                    const sref = luaCreateVirtualInstance(client ? 'LocalScript' : 'Script');
                    luaByRef[sref].name = scr.name;
                    luaSetParent(sref, luaCharacterRef);
                    const side = client ? 'LocalScript' : 'Script';
                    try { runLuaScript(Object.assign({}, scr, { ref: sref, cls: side }), client ? luaClientL : luaServerL); }
                    catch (e) { logLuaOutput('error', scr.name + ': ' + e.message, scr.name, null, side); }
                }
            }

            renderGuiOverlayFromClient();
            buildSurfaceGuis();
        }

        function stopLuaScripts() {
            luaServerL = null; // JS-ссылки отпущены — обе VM и все их корутины
            luaClientL = null; // станут доступны для сборки мусора JS-движком
            luaWaits = [];
            luaSignalWaits = [];
            // luaOutputLines НЕ чистим: Output остаётся после остановки Play (очищается при следующем запуске или кнопкой 🗑)
            luaByRef = {}; luaByRefVer++;
            luaParentByRef = {};
            luaChildrenByRef = {};
            virtualInstanceProps = {};
            luaGenericPropsByRef = {};
            luaCharacterRef = -1;
            luaPlayerRef = -1;
            luaScriptsByRef = {};
            luaStartedClonedScripts = new Set();
            luaControlsDisabled = false;
            luaReleaseAllKeys();
            luaHollowUnions.clear(); luaGhostedUnions.clear();
            luaNextVirtualRef = -1000;
            luaResetSignals();
            renderLuaOutput();
            clearGuiOverlay();
            // Раньше звук вообще не трогался при Stop — реальный
            for (const a of Object.values(soundElByRef)) {
                a.pause();
                a.currentTime = 0;
            }
            soundElByRef = {};
            // Иначе PlaybackSpeed/Octave, выставленные скриптом ДО Stop, тихо
            for (const k in _soundBaseSpeed) delete _soundBaseSpeed[k];
            for (const k in _soundPitchOctave) delete _soundPitchOctave[k];
        }

        // ============ GUI (ScreenGui/Frame/TextLabel/TextButton/...
        let guiPropsByRef = {};    // ref -> {cls, parent, ...GUI_PROPS}
        let guiChildrenByRef = {}; // ref -> [childRef, ...]
        let guiDomByRef = {};      // ref -> HTMLElement

        function color3ToCss(c, transparency) {
            if (!c || typeof c !== 'object') return '#ffffff';
            const r = Math.round((c.r ?? 1) * 255), g = Math.round((c.g ?? 1) * 255), b = Math.round((c.b ?? 1) * 255);
            const a = 1 - (typeof transparency === 'number' ? transparency : 0);
            return 'rgba(' + r + ',' + g + ',' + b + ',' + a + ')';
        }

        // UDim2 {x:{scale,offset}, y:{scale,offset}} -> CSS calc(), точно как
        function udimToCssLength(u) {
            if (!u || typeof u !== 'object') return '0px';
            return 'calc(' + ((u.scale || 0) * 100) + '% + ' + (u.offset || 0) + 'px)';
        }

        // UICorner: Scale считается от МЕНЬШЕЙ стороны элемента, а радиус не
        // больше половины меньшей стороны (Roblox). CSS-проценты считаются
        // отдельно по ширине и высоте — получался эллипс: ползунок-«линза»,
        // овальные поля и кнопки. Пересчитываем в пиксели по реальному размеру.
        function applyCornerRadius(el, udims) {
            const conv = (u, m) => {
                u = u || {};
                return Math.max(0, Math.min((u.scale || 0) * m + (u.offset || 0), m / 2)) + 'px';
            };
            if (udims.every(u => !u || !u.scale)) {
                el.style.borderRadius = udims.map(u => ((u && u.offset) || 0) + 'px').join(' ');
                return;
            }
            const upd = () => {
                const m = Math.min(el.clientWidth || el.offsetWidth, el.clientHeight || el.offsetHeight);
                if (!m) return;
                el.style.borderRadius = udims.map(u => conv(u, m)).join(' ');
            };
            upd();
            if (typeof ResizeObserver !== 'undefined') {
                if (el._cornerRO) el._cornerRO.disconnect();
                el._cornerRO = new ResizeObserver(upd);
                el._cornerRO.observe(el);
            }
        }

        // Применяет UICorner/UIStroke к DOM-элементу их РОДИТЕЛЯ.
        function applyGuiDecoration(parentEl, decoProps) {
            if (!parentEl || !decoProps) return;
            if (decoProps.cls === 'UICorner') {
                // Часть файлов хранит один общий CornerRadius, часть (в
                if (decoProps.TopLeftRadius || decoProps.TopRightRadius ||
                    decoProps.BottomLeftRadius || decoProps.BottomRightRadius) {
                    applyCornerRadius(parentEl, [decoProps.TopLeftRadius, decoProps.TopRightRadius,
                        decoProps.BottomRightRadius, decoProps.BottomLeftRadius]);
                } else {
                    const cr = decoProps.CornerRadius;
                    applyCornerRadius(parentEl, [cr, cr, cr, cr]);
                }
            } else if (decoProps.cls === 'UIStroke') {
                if (decoProps.Enabled === false) return;
                const thickness = (typeof decoProps.Thickness === 'number' ? decoProps.Thickness : 1);
                // inset box-shadow вместо border — обводка не съедает
                parentEl.style.boxShadow = 'inset 0 0 0 ' + thickness + 'px ' +
                    color3ToCss(decoProps.Color, decoProps.Transparency);
            }
        }

        function udim2ToCssPos(pos) {
            const x = pos && pos.x ? pos.x : { scale: 0, offset: 0 };
            const y = pos && pos.y ? pos.y : { scale: 0, offset: 0 };
            return {
                left: 'calc(' + ((x.scale || 0) * 100) + '% + ' + (x.offset || 0) + 'px)',
                top: 'calc(' + ((y.scale || 0) * 100) + '% + ' + (y.offset || 0) + 'px)',
            };
        }

        function udim2ToCssSize(size) {
            const x = size && size.x ? size.x : { scale: 1, offset: 0 };
            const y = size && size.y ? size.y : { scale: 1, offset: 0 };
            return {
                width: 'calc(' + ((x.scale || 0) * 100) + '% + ' + (x.offset || 0) + 'px)',
                height: 'calc(' + ((y.scale || 0) * 100) + '% + ' + (y.offset || 0) + 'px)',
            };
        }

        // В Roblox Frame/TextLabel/ImageLabel НЕ перехватывают ввод, пока Active=false
        // (и не стоят под курсором с подключённым InputBegan/MouseEnter и т.п.); перехватывают
        // только кнопки, TextBox и ScrollingFrame. Раньше любой Frame получал pointer-events:auto,
        // и полноэкранный прозрачный Frame (затемнение) блокировал вращение камеры и клики по миру.
        const guiClassSet = new Set(['ScreenGui','Frame','TextLabel','TextButton','TextBox','ImageLabel','ImageButton','ScrollingFrame','ViewportFrame','CanvasGroup','BillboardGui','SurfaceGui']);
        const luaGuiInputRefs = new Set(); // ref GUI-объектов, у которых скрипт подписан на мышь/тач
        const _GUI_SINK_CLASSES = new Set(['TextButton', 'ImageButton', 'TextBox', 'ScrollingFrame']);
        function guiApplyPointer(el, props) {
            const ref = Number(el.dataset.ref);
            const interactive = _GUI_SINK_CLASSES.has(props.cls) || props.Active === true || luaGuiInputRefs.has(ref);
            el.style.pointerEvents = interactive ? 'auto' : 'none';
        }
        // UIScale — дочерний модификатор: масштабирует ПАРОДИТЕЛЯ вместе со всем содержимым (в т.ч. пиксельные offset'ы).
        // Раньше не поддерживался вовсе, поэтому скрипт GuiScale (Blaster) менял Scale впустую и интерфейс на маленьком
        // экране оставался в полный размер.
        function guiUIScaleOf(ref) {
            for (const k of (guiChildrenByRef[ref] || [])) {
                const cp = guiPropsByRef[k];
                if (cp && cp.cls === 'UIScale') {
                    const sc = Number(cp.Scale);
                    return (Number.isFinite(sc) && sc > 0) ? sc : 1;
                }
            }
            return 1;
        }
        function applyGuiElementStyle(el, props) {
            const cls = props.cls;
            const pos = udim2ToCssPos(props.Position);
            const size = udim2ToCssSize(props.Size);
            el.style.left = pos.left;
            el.style.top = pos.top;
            el.style.width = size.width;
            el.style.height = size.height;
            // Файл Roblox хранит инстансы, сгруппированные ПО КЛАССАМ
            const isInteractiveCls = props.cls === 'TextButton' || props.cls === 'ImageButton' || props.cls === 'TextBox';
            el.style.zIndex = String((props.ZIndex || 1) * 10 + (isInteractiveCls ? 5 : 0));
            // AnchorPoint — раньше вообще не читался:
            const ap = props.AnchorPoint;
            el.style.transform = ap ? `translate(${-(ap.x || 0) * 100}%, ${-(ap.y || 0) * 100}%)` : '';
            el.style.transformOrigin = '';
            const uiScale = guiUIScaleOf(Number(el.dataset.ref));
            if (uiScale !== 1) {
                if (cls === 'ScreenGui' || cls === 'BillboardGui') {
                    // Виртуальный экран становится в 1/s раз больше и масштабируется обратно: проценты (Scale) всё так же
                    // покрывают весь экран, а пиксели (Offset) и размеры внутри — умножаются на s.
                    el.style.width = 'calc(100% / ' + uiScale + ')';
                    el.style.height = 'calc(100% / ' + uiScale + ')';
                    el.style.transform = 'scale(' + uiScale + ')';
                    el.style.transformOrigin = '0 0';
                } else {
                    // Обычный GuiObject масштабируется вокруг своей точки привязки (AnchorPoint), как в Roblox
                    el.style.transform += ' scale(' + uiScale + ')';
                    el.style.transformOrigin = ((ap && ap.x || 0) * 100) + '% ' + ((ap && ap.y || 0) * 100) + '%';
                }
            }
            // ScreenGui/BillboardGui управляются свойством Enabled (не
            if (cls === 'ScreenGui' || cls === 'BillboardGui') {
                el.style.display = (props.Enabled === false) ? 'none' : 'flex';
            } else {
                el.style.display = (props.Visible === false) ? 'none' : 'flex';
            }

            // ClipsDescendants есть у любого GuiObject (CanvasGroup клипует всегда); по умолчанию потомки НЕ обрезаются.
            // Значение выставляется каждый раз, поэтому выключение флага из Lua тоже снимает обрезку.
            el.style.overflow = (props.ClipsDescendants || cls === 'CanvasGroup') ? 'hidden' : 'visible';
            // CanvasGroup.GroupTransparency — прозрачность ВСЕЙ группы целиком (CSS opacity как раз группирует содержимое)
            el.style.opacity = cls === 'CanvasGroup' ? String(1 - Math.max(0, Math.min(1, Number(props.GroupTransparency) || 0))) : '';
            if (cls === 'Frame' || cls === 'ScrollingFrame' || cls === 'CanvasGroup') {
                el.style.background = color3ToCss(props.BackgroundColor3, props.BackgroundTransparency);
                // BorderSizePixel = 0 (частый случай: затемняющий Frame) раньше превращался
                // в 1 из-за `|| 1` и рисовал рамку вокруг экрана — проверяем на null/undefined.
                const bsp = (props.BorderSizePixel === undefined || props.BorderSizePixel === null) ? 1 : Number(props.BorderSizePixel);
                el.style.border = bsp > 0
                    ? bsp + 'px solid ' + color3ToCss(props.BorderColor3)
                    : 'none';
                if (props.BackgroundTransparency >= 1) el.style.background = 'transparent';
                if (cls === 'ScrollingFrame') {
                    // Раньше ScrollingFrame рендерился 1-в-1 как обычный
                    el.style.overflowY = 'auto';
                    el.style.overflowX = 'hidden';
                    el.style.webkitOverflowScrolling = 'touch';
                }
            } else if (cls === 'TextLabel' || cls === 'TextButton' || cls === 'TextBox') {
                el.style.background = (props.BackgroundTransparency >= 1)
                    ? 'transparent' : color3ToCss(props.BackgroundColor3, props.BackgroundTransparency);
                el.style.color = color3ToCss(props.TextColor3, props.TextTransparency);
                el.style.fontSize = (props.TextSize || 14) + 'px';
                el.style.whiteSpace = props.TextWrapped === false ? 'nowrap' : 'pre-wrap';
                el.style.border = 'none';
                if (cls === 'TextBox') {
                    el.contentEditable = 'true';
                    el.style.cursor = 'text';
                    // ВАЖНО: applyGuiElementStyle вызывается не только при
                    // изменении Text, а на КАЖДЫЙ проход UIListLayout (и на
                    // любой другой patch того же контейнера). Если в этот
                    // момент поле редактируется (сфокусировано), перезапись
                    // el.textContent сбрасывает курсор на начало и стирает
                    // непереданные в Lua символы — с точки зрения игрока
                    // поле просто "не принимает ввод". Пока элемент в
                    // фокусе, доверяем тому, что уже введено в DOM.
                    if (document.activeElement !== el) {
                        _setElText(el, props.Text != null ? String(props.Text) : '');
                    }
                } else {
                    _setElText(el, props.Text != null ? String(props.Text) : '');
                }
                _fitScaledText(el, props);
            } else if (cls === 'ImageLabel' || cls === 'ImageButton') {
                el.style.background = color3ToCss(props.BackgroundColor3, props.BackgroundTransparency);
                _setElText(el, '');
                // Раньше Image просто складывался в title (всплывающая
                // thumb=1: если без входа в Roblox assetdelivery отвечает 401/403 — сервер отдаст публичную миниатюру ассета
                const _pu = rbxAssetIdToProxyUrl(props.Image);
                const proxyUrl = _pu ? _pu + '&thumb=1' : _pu;
                if (proxyUrl) {
                    el.style.backgroundImage = 'url(' + proxyUrl + ')';
                    // Fit — ближе всего к дефолтному ScaleType.Stretch
                    el.style.backgroundSize = (props.ScaleType === 'Fit') ? 'contain' : 'cover';
                    el.style.backgroundPosition = 'center';
                    el.style.backgroundRepeat = 'no-repeat';
                    // background-image сам по себе не даёт события ошибки
                    const probe = new Image();
                    probe.onerror = () => {
                        logLuaOutput('warn', t('warn_image_failed', { name: props.Name || cls, src: proxyUrl }));
                    };
                    probe.src = proxyUrl;
                } else {
                    el.style.backgroundImage = '';
                }
                el.title = props.Image || '';
            }
            guiApplyPointer(el, props);
        }
        // ячейка UIGridLayout переприменяет размер/позицию после любой перекраски элемента (иначе Text/Color затирали раскладку)
        {
            const _ages = applyGuiElementStyle;
            applyGuiElementStyle = function (el, props) { _ages(el, props); if (el && el._gridCell) _applyGridCell(el); };
        }

        // Текст GUI-элемента без затирания вложенных GUI-элементов: el.textContent = ... удаляет ВСЕХ детей, а у ImageLabel/TextLabel
        // в Roblox бывают дочерние элементы (Druns_PP: ButtonText внутри ImageLabel Button — иконка с «E»/«TAP» пропадала после первой перекраски).
        function _setElText(el, text) {
            let first = null;
            for (const n of Array.from(el.childNodes)) {
                if (n.nodeType === 3) { if (first === null) first = n; else el.removeChild(n); }
            }
            if (text === '' || text == null) { if (first) el.removeChild(first); return; }
            if (first) { if (first.nodeValue !== text) first.nodeValue = text; }
            else el.insertBefore(document.createTextNode(text), el.firstChild);
        }
        function domInputTypeName(e, isMove) {
            if (e.touches !== undefined || (e.type && e.type.indexOf('touch') === 0)) return 'Touch';
            if (isMove) return 'MouseMovement';
            if (e.button === 2) return 'MouseButton2';
            if (e.button === 1) return 'MouseButton3';
            return 'MouseButton1';
        }
        // Масштаб игрового GUI (оверлей получает CSS zoom): на телефоне окно Play маленькое, а GUI считается в «пикселях Roblox».
        // Все координаты, которые видит Lua (мышь/тач, AbsolutePosition/AbsoluteSize, ViewportSize), — в единицах GUI,
        // от левого верхнего угла оверлея (как в Roblox), а не в пикселях экрана.
        let guiScale = 1;
        try { const v = parseFloat(localStorage.getItem('rbxstudio-gui-scale')); if (v >= 1 && v <= 3) guiScale = v; } catch (e) { /* нет localStorage */ }
        function _guiOverlayRect() {
            const ov = document.getElementById('gui-overlay');
            return ov ? ov.getBoundingClientRect() : { left: 0, top: 0 };
        }
        function _clientToGui(cx, cy) {
            const r = _guiOverlayRect();
            return [(cx - r.left) / guiScale, (cy - r.top) / guiScale];
        }
        // CSS zoom на оверлее: в Chromium >=128 бокс остаётся равным родителю, а в старых WebView (Android) он становился
        // в guiScale раз больше и нижняя часть GUI (хотбар, anchor снизу) уезжала за экран. Применяем zoom и сверяем
        // реальный размер с родителем: если оверлей вылез — ужимаем его на guiScale.
        function _applyGuiZoom(ov) {
            if (!ov) return;
            ov.style.zoom = String(guiScale);
            ov.style.width = ''; ov.style.height = ''; ov.style.right = ''; ov.style.bottom = '';
            const par = ov.parentElement;
            if (!par || guiScale === 1) return;
            const pr = par.getBoundingClientRect(), orr = ov.getBoundingClientRect();
            if (pr.width > 0 && orr.width > pr.width * 1.02) {
                ov.style.right = 'auto'; ov.style.bottom = 'auto';
                ov.style.width = (pr.width / guiScale) + 'px';
                ov.style.height = (pr.height / guiScale) + 'px';
            }
        }
        window.addEventListener('resize', () => { const ov = document.getElementById('gui-overlay'); if (ov && ov.classList.contains('active')) _applyGuiZoom(ov); });
        function setGuiScale(sc) {
            guiScale = sc;
            try { localStorage.setItem('rbxstudio-gui-scale', String(sc)); } catch (e) { /* ничего */ }
            _markGuiScaleButtons();
            const ov = document.getElementById('gui-overlay');
            _applyGuiZoom(ov);
            if (isPlaying) { try { renderGuiOverlayFromClient(); } catch (e) { console.warn('GUI scale re-render:', e); } }
            _notifyViewportChanged();
        }
        // ViewportSize у камеры (в единицах GUI = экран / guiScale) изменился: скриптам нужно сообщить, иначе, например,
        // хотбар (camera:GetPropertyChangedSignal("ViewportSize") -> Grid.CellSize) остаётся со старым размером ячеек
        // и после смены масштаба UI уезжает за край экрана. Дважды — сразу и после перерисовки DOM (AbsoluteSize берётся из него).
        function _notifyViewportChanged() {
            if (!luaServerL && !luaClientL) return;
            const fire = () => {
                try {
                    for (const ref in luaByRef) {
                        if (luaByRef[ref].cls === 'Camera') fireLuaSignal(parseInt(ref), '__prop_ViewportSize', []);
                    }
                } catch (e) { console.warn('ViewportSize notify:', e); }
            };
            fire(); setTimeout(fire, 120);
        }
        window.addEventListener('resize', () => { if (isPlaying) _notifyViewportChanged(); });
        function _markGuiScaleButtons() {
            document.querySelectorAll('#quality-selector button[id^="g-"]').forEach(b => {
                b.classList.toggle('active', Math.abs(parseFloat(b.dataset.s) - guiScale) < 0.01);
            });
        }
        document.addEventListener('DOMContentLoaded', () => _markGuiScaleButtons());
        // TextScaled у DOM-текста: Roblox подбирает самый крупный шрифт (до 100), при котором текст влезает в элемент по ширине
        // и высоте. Раньше шрифт всегда равнялся TextSize (16px), и подписи слотов хотбара налезали друг на друга.
        let _fitCtx = null;
        function _fitScaledText(el, props) {
            if (!props || !props.TextScaled) {
                if (el._scaledRO) { el._scaledRO.disconnect(); el._scaledRO = null; }
                return;
            }
            const run = () => {
                const w = el.clientWidth, h = el.clientHeight;
                if (!(w > 0 && h > 0)) return;
                const lines = String(el.textContent || '').split('\n');
                if (!_fitCtx) _fitCtx = document.createElement('canvas').getContext('2d');
                let size = Math.max(4, Math.min(100, (h / lines.length) * 0.95));
                _fitCtx.font = size + 'px sans-serif';
                const widest = Math.max(...lines.map(l => _fitCtx.measureText(l).width), 1);
                if (widest > w) size = Math.max(4, size * (w / widest) * 0.98);
                el.style.fontSize = size + 'px';
                el.style.whiteSpace = 'nowrap';
                el.style.lineHeight = 'normal';
                // Канвас меряет другим шрифтом, чем DOM (и по-разному в разных WebView) — добиваем по реальному переполнению
                for (let i = 0; i < 12 && size > 4 && el.scrollWidth > w + 1; i++) {
                    size = Math.max(4, size * 0.9); el.style.fontSize = size + 'px';
                }
            };
            run();
            if (!el._scaledRO && typeof ResizeObserver !== 'undefined') {
                el._scaledRO = new ResizeObserver(run);
                el._scaledRO.observe(el);
            }
        }
        function domInputXY(e) {
            const t = e.touches && e.touches[0] || (e.changedTouches && e.changedTouches[0]);
            return t ? _clientToGui(t.clientX, t.clientY) : _clientToGui(e.clientX, e.clientY);
        }

        function guiCreateDomNode(ref, props) {
            const el = document.createElement(props.cls === 'TextButton' || props.cls === 'ImageButton' ? 'button' : 'div');
            el.className = 'rbx-gui-el';
            el.dataset.ref = ref;
            el.dataset.cls = props.cls;
            applyGuiElementStyle(el, props);
            if (props.cls === 'TextButton' || props.cls === 'ImageButton') {
                el.style.outline = 'none';
                // Клик по кнопке — настоящий Lua-сигнал (fireLuaSignal),
                el.addEventListener('click', () => fireLuaSignal(ref, 'MouseButton1Click', []));
                el.addEventListener('mousedown', () => fireLuaSignal(ref, 'MouseButton1Down', []));
                el.addEventListener('mouseup', () => fireLuaSignal(ref, 'MouseButton1Up', []));
                // touchend НЕ passive и с preventDefault — иначе следом за
                el.addEventListener('touchstart', () => fireLuaSignal(ref, 'MouseButton1Down', []), { passive: true });
                el.addEventListener('touchend', (e) => { e.preventDefault(); fireLuaSignal(ref, 'MouseButton1Up', []); fireLuaSignal(ref, 'MouseButton1Click', []); }, { passive: false });
            }
            // MouseEnter/MouseLeave — у ЛЮБОГО GuiObject в настоящем Roblox,
            // не только у кнопок (Frame/TextLabel тоже их поддерживают).
            el.addEventListener('mouseenter', () => fireLuaSignal(ref, 'MouseEnter', []));
            el.addEventListener('mouseleave', () => fireLuaSignal(ref, 'MouseLeave', []));
            // InputBegan/InputEnded — тоже у ЛЮБОГО GuiObject (в отличие от
            el.addEventListener('mousedown', (e) => fireLuaSignal(ref, 'InputBegan', [domInputTypeName(e, false), ...domInputXY(e)]));
            el.addEventListener('mouseup', (e) => fireLuaSignal(ref, 'InputEnded', [domInputTypeName(e, false), ...domInputXY(e)]));
            // Тач-эквиваленты — см.
            el.addEventListener('touchstart', (e) => fireLuaSignal(ref, 'InputBegan', [domInputTypeName(e, false), ...domInputXY(e)]), { passive: true });
            el.addEventListener('touchend', (e) => fireLuaSignal(ref, 'InputEnded', [domInputTypeName(e, false), ...domInputXY(e)]), { passive: true });
            // FocusLost/Focused — TextBox (contentEditable div, см.
            if (props.cls === 'TextBox') {
                let enterPressed = false;
                // На части мобильных браузеров голый tap по contentEditable
                // div (без tabindex) фокусирует элемент, но НЕ поднимает
                // экранную клавиатуру — нужен явный .focus() внутри самого
                // обработчика тача. Без этого поле выглядит нерабочим: курсор
                // как будто появляется, а печатать нельзя.
                el.tabIndex = 0;
                el.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    el.focus();
                }, { passive: false });
                el.addEventListener('mousedown', () => el.focus());
                // Живая правка contentEditable не попадает в guiPropsByRef
                el.addEventListener('input', () => { if (guiPropsByRef[ref]) guiPropsByRef[ref].Text = el.textContent; });
                el.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') { enterPressed = true; el.blur(); }
                });
                el.addEventListener('focus', () => fireLuaSignal(ref, 'Focused', []));
                el.addEventListener('blur', () => {
                    fireLuaSignal(ref, 'FocusLost', [enterPressed]);
                    enterPressed = false;
                });
            }
            return el;
        }

        // ============ BillboardGui: интерфейс в мире, всегда лицом к камере ============
        // Раньше BillboardGui рисовался как обычный ScreenGui — на весь экран, а не над деталью/Attachment.
        // Якорь: Adornee, иначе родитель (деталь, Attachment, модель). Size: Scale — в студах (px = Scale * px_на_стад
        // на дистанции якоря), Offset — в пикселях. StudsOffsetWorldSpace — в мире, StudsOffset — в системе камеры (x,y).
        // MaxDistance — скрыть дальше. AlwaysOnTop=false — скрываем, если между камерой и якорем есть геометрия
        // (луч, не чаще раза в 5 кадров; части самой модели-владельца не заслоняют).
        const _bbOcc = {};   // ref -> { frame, hidden }
        let _bbFrame = 0;
        function _bbAnchorWorld(ref, out) {
            const info = luaByRef[ref];
            if (!info) return false;
            if (info.cls === 'Attachment') {
                const part = luaParentByRef[ref];
                const a = luaAttCF[ref];
                if (part === undefined || !luaIsPartRef(part)) return false;
                const m = luaPartMatrix(part);
                if (a) {
                    const l = new THREE.Matrix4().set(a[3], a[4], a[5], a[0], a[6], a[7], a[8], a[1], a[9], a[10], a[11], a[2], 0, 0, 0, 1);
                    m.multiply(l);
                }
                out.setFromMatrixPosition(m);
                return true;
            }
            if (luaIsPartRef(ref)) {
                const p = luaPositionOfRef(ref);
                out.set(p.x, p.y, p.z);
                return true;
            }
            // Model/Folder и т.п.: первая деталь среди потомков
            const stack = [ref];
            while (stack.length) {
                const r0 = stack.shift();
                if (luaIsPartRef(r0)) { const p = luaPositionOfRef(r0); out.set(p.x, p.y, p.z); return true; }
                for (const c of (luaChildrenByRef[r0] || [])) stack.push(c);
            }
            return false;
        }
        function _bbOccluded(ref, anchorRef, camPos, target) {
            const st = _bbOcc[ref] || (_bbOcc[ref] = { frame: -99, hidden: false });
            if (_bbFrame - st.frame < 5) return st.hidden;
            st.frame = _bbFrame;
            // части модели-владельца якоря не заслоняют (иначе Attachment внутри торса всегда «закрыт» своим торсом)
            // владелец = САМАЯ ВЕРХНЯЯ Model цепочки (весь враг/персонаж целиком), а не ближайшая вложенная ('head')
            let owner = anchorRef, cur = anchorRef, g = 0;
            while (cur !== undefined && cur !== -1 && g++ < 50) {
                const i = luaByRef[cur];
                if (i && i.cls === 'Model') owner = cur;
                cur = luaParentByRef[cur];
            }
            const dir = target.clone().sub(camPos);
            const dist = dir.length();
            if (dist < 1e-3) { st.hidden = false; return false; }
            dir.divideScalar(dist);
            const inOwner = (r) => {
                let c = r, k = 0;
                while (c !== undefined && c !== -1 && k++ < 200) { if (c === owner) return true; c = luaParentByRef[c]; }
                return false;
            };
            const targets = [];
            for (const k in sceneObjs) { const m = sceneObjs[k]; if (m) targets.push(m); }
            const rc = new THREE.Raycaster(camPos, dir, 0, dist - 0.05);
            let hidden = false;
            try {
                for (const h of rc.intersectObjects(targets, true)) {
                    let o = h.object, r;
                    while (o) { if (o.userData && o.userData.ref !== undefined) { r = o.userData.ref; break; } o = o.parent; }
                    // шаблоны из ServerStorage нарисованы в сцене поверх реальных объектов, но в Roblox их нет в мире
                    if (r === undefined || inOwner(r) || !luaIsUnderWorkspace(r)) continue;
                    hidden = true; break;
                }
            } catch (e) { hidden = false; }
            st.hidden = hidden;
            return hidden;
        }
        function updateBillboardGuis() {
            const overlay = document.getElementById('gui-overlay');
            if (!overlay || !camera) return;
            _bbFrame++;
            const cr = renderer.domElement.getBoundingClientRect(), orc = overlay.getBoundingClientRect();
            const W = cr.width, H = cr.height, offX = cr.left - orc.left, offY = cr.top - orc.top;
            if (!(W > 0 && H > 0)) return;
            camera.updateMatrixWorld();
            const camPos = new THREE.Vector3().setFromMatrixPosition(camera.matrixWorld);
            const tanHalf = Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2);
            const world = new THREE.Vector3(), view = new THREE.Vector3();
            for (const refStr in guiDomByRef) {
                const props = guiPropsByRef[refStr];
                if (!props || props.cls !== 'BillboardGui') continue;
                const ref = Number(refStr), el = guiDomByRef[refStr];
                let anchor = (props.Adornee !== undefined && props.Adornee !== null && props.Adornee !== -1 && luaByRef[props.Adornee])
                    ? props.Adornee : luaParentByRef[ref];
                const hide = () => { el.style.display = 'none'; };
                // шаблоны в ServerStorage/ReplicatedStorage и т.п. в мире не рисуются — только то, что лежит в Workspace
                if (props.Enabled === false || anchor === undefined || anchor === -1 || !luaIsUnderWorkspace(anchor) ||
                    !_bbAnchorWorld(anchor, world)) { hide(); continue; }
                const wo = props.StudsOffsetWorldSpace;
                if (wo) world.add(new THREE.Vector3(wo.x || 0, wo.y || 0, wo.z || 0));
                const dist = world.distanceTo(camPos);
                const maxD = Number(props.MaxDistance);
                if (Number.isFinite(maxD) && maxD > 0 && dist > maxD) { hide(); continue; }
                view.copy(world).applyMatrix4(camera.matrixWorldInverse);
                const so = props.StudsOffset;
                if (so) { view.x += so.x || 0; view.y += so.y || 0; }
                const depth = -view.z;
                if (depth < 0.1) { hide(); continue; }
                if (props.AlwaysOnTop !== true && _bbOccluded(ref, anchor, camPos, world)) { hide(); continue; }
                const pxPerStud = H / (2 * depth * tanHalf);
                const sz = props.Size || { x: { scale: 1, offset: 0 }, y: { scale: 1, offset: 0 } };
                const w = ((sz.x && sz.x.scale) || 0) * pxPerStud + ((sz.x && sz.x.offset) || 0);
                const h = ((sz.y && sz.y.scale) || 0) * pxPerStud + ((sz.y && sz.y.offset) || 0);
                if (!(w > 0.5 && h > 0.5)) { hide(); continue; }
                view.z = -depth;
                const ndc = view.clone().applyMatrix4(camera.projectionMatrix);
                const sx = offX + (ndc.x * 0.5 + 0.5) * W, sy = offY + (-ndc.y * 0.5 + 0.5) * H;
                const so2 = props.SizeOffset;
                const ax = (so2 && so2.x) || 0, ay = (so2 && so2.y) || 0;
                el.style.display = 'flex';
                el.style.position = 'absolute';
                el.style.right = 'auto'; el.style.bottom = 'auto';
                el.style.width = (w / guiScale) + 'px'; el.style.height = (h / guiScale) + 'px';
                el.style.left = (sx / guiScale) + 'px'; el.style.top = (sy / guiScale) + 'px';
                el.style.transform = 'translate(' + (-50 + ax * 100) + '%,' + (-50 - ay * 100) + '%)';
                el.style.transformOrigin = '50% 50%';
                el.style.zIndex = '5';
            }
        }

        function guiRenderNode(ref, parentEl) {
            const props = guiPropsByRef[ref];
            if (!props) return;
            const el = guiCreateDomNode(ref, props);
            guiDomByRef[ref] = el;
            parentEl.appendChild(el);
            for (const childRef of (guiChildrenByRef[ref] || [])) {
                const childProps = guiPropsByRef[childRef];
                if (childProps && childProps.cls === 'UIScale') continue; // применяется в applyGuiElementStyle родителя
                if (childProps && (childProps.cls === 'UIListLayout' || childProps.cls === 'UIGridLayout')) continue; // раскладка: свойства есть, DOM-узла нет
                if (childProps && (childProps.cls === 'UICorner' || childProps.cls === 'UIStroke')) {
                    // Модификатор, не отдельный визуальный узел — красим
                    // el (родителя), а не создаём для него DOM-элемент.
                    applyGuiDecoration(el, childProps);
                    continue;
                }
                guiRenderNode(childRef, el);
            }
            applyUIListLayout(ref);
        }

        // UIGridLayout: ячейки CellSize с зазором CellPadding, строки/столбцы по FillDirection (0 Horizontal), выравнивание
        // Horizontal/VerticalAlignment (HA: 0 Center, 1 Left, 2 Right; VA: 0 Center, 1 Top, 2 Bottom). Раньше раскладки не было:
        // слоты хотбара растягивались во всю ширину строками друг под другом. Размер/позиция ячеек пишутся прямо в style
        // (props не трогаем — Lua читает исходный Size), el._gridCell переприменяется в applyGuiElementStyle.
        // SortOrder раскладки: 0 = Name (по имени), 1 = Custom (порядок потомков), 2 = LayoutOrder (по числу, затем порядок потомков)
        function _sortLayoutKids(kids, lp) {
            const so = lp.SortOrder === undefined ? 2 : lp.SortOrder;
            const idx = new Map(kids.map((k, i) => [k, i]));
            const nm = (k) => String((luaByRef[k] && luaByRef[k].name !== undefined) ? luaByRef[k].name : ((guiPropsByRef[k] || {}).Name || ''));
            if (so === 0 || so === 'Name') return kids.slice().sort((a, b) => (nm(a) < nm(b) ? -1 : nm(a) > nm(b) ? 1 : idx.get(a) - idx.get(b)));
            if (so === 2 || so === 'LayoutOrder') return kids.slice().sort((a, b) => (((guiPropsByRef[a] || {}).LayoutOrder || 0) - ((guiPropsByRef[b] || {}).LayoutOrder || 0)) || (idx.get(a) - idx.get(b)));
            return kids;
        }
        function applyUIGridLayout(containerRef, layoutRef, kids0) {
            const kids = _sortLayoutKids(kids0, guiPropsByRef[layoutRef] || {});
            const cel = guiDomByRef[containerRef];
            const lp = guiPropsByRef[layoutRef] || {};
            if (!cel) return;
            const cw = cel.clientWidth, ch = cel.clientHeight;
            const ud = (u, base) => u ? ((u.x && u.x.scale || 0) * base.x + (u.x && u.x.offset || 0)) : 0;
            const cs = lp.CellSize || { x: { scale: 0, offset: 100 }, y: { scale: 0, offset: 100 } };
            const cp = lp.CellPadding || { x: { scale: 0, offset: 0 }, y: { scale: 0, offset: 0 } };
            const cellW = (cs.x.scale || 0) * cw + (cs.x.offset || 0), cellH = (cs.y.scale || 0) * ch + (cs.y.offset || 0);
            const padX = (cp.x.scale || 0) * cw + (cp.x.offset || 0), padY = (cp.y.scale || 0) * ch + (cp.y.offset || 0);
            const horizontal = !(lp.FillDirection === 1 || lp.FillDirection === 'Vertical');
            const items = [];
            for (const k of kids) {
                const p = guiPropsByRef[k];
                if (!p || k === layoutRef || (p.cls && p.cls.indexOf('UI') === 0) || p.Visible === false) continue;
                if (guiDomByRef[k]) items.push(k);
            }
            const maxCells = lp.FillDirectionMaxCells > 0 ? lp.FillDirectionMaxCells
                : Math.max(1, Math.floor(((horizontal ? cw : ch) + (horizontal ? padX : padY)) / ((horizontal ? cellW + padX : cellH + padY) || 1)));
            const lines = Math.ceil(items.length / maxCells);
            const lineLen = (n) => n * (horizontal ? cellW : cellH) + Math.max(0, n - 1) * (horizontal ? padX : padY);
            const totalCross = lines * (horizontal ? cellH : cellW) + Math.max(0, lines - 1) * (horizontal ? padY : padX);
            const HA = lp.HorizontalAlignment === undefined ? 0 : lp.HorizontalAlignment;   // 0 Center, 1 Left, 2 Right
            const VA = lp.VerticalAlignment === undefined ? 0 : lp.VerticalAlignment;       // 0 Center, 1 Top, 2 Bottom
            items.forEach((k, idx) => {
                const line = Math.floor(idx / maxCells), pos = idx % maxCells;
                const inLine = Math.min(maxCells, items.length - line * maxCells);
                let x, y;
                if (horizontal) {
                    const rowW = lineLen(inLine);
                    const ox = HA === 1 ? 0 : HA === 2 ? cw - rowW : (cw - rowW) / 2;
                    const oy = VA === 1 ? 0 : VA === 2 ? ch - totalCross : (ch - totalCross) / 2;
                    x = ox + pos * (cellW + padX); y = oy + line * (cellH + padY);
                } else {
                    const colH = lineLen(inLine);
                    const oy = VA === 1 ? 0 : VA === 2 ? ch - colH : (ch - colH) / 2;
                    const ox = HA === 1 ? 0 : HA === 2 ? cw - totalCross : (cw - totalCross) / 2;
                    x = ox + line * (cellW + padX); y = oy + pos * (cellH + padY);
                }
                const el = guiDomByRef[k];
                el._gridCell = { x, y, w: cellW, h: cellH };
                _applyGridCell(el);
            });
        }
        function _applyGridCell(el) {
            const g = el._gridCell;
            if (!g) return;
            el.style.position = 'absolute';
            el.style.left = g.x + 'px'; el.style.top = g.y + 'px';
            el.style.width = g.w + 'px'; el.style.height = g.h + 'px';
            el.style.right = 'auto'; el.style.bottom = 'auto'; el.style.transform = 'none';
        }

        // UIListLayout — раньше был только числом-заглушкой в GUI_CLASS_NAMES.
        // Высота/ширина элемента бралась ТОЛЬКО из пиксельной части Size
        // (Size.Y.offset), а в реальных меню размер почти всегда задан в
        // Scale ({0.08, 0} и т.п.) — offset получался 0 у ВСЕХ элементов,
        // список не сдвигался, и все пункты рисовались друг на друге в
        // одной точке (наложенный текст в меню песен). Меряем то, что
        // РЕАЛЬНО отрисовано в DOM (offsetWidth/offsetHeight) — там уже
        // учтены и scale, и offset, как в настоящем AbsoluteSize у Roblox.
        function applyUIListLayout(containerRef) {
            const kids = (guiChildrenByRef[containerRef] || []).slice();
            let layoutRef = null;
            for (const k of kids) {
                if (guiPropsByRef[k] && (guiPropsByRef[k].cls === 'UIListLayout' || guiPropsByRef[k].cls === 'UIGridLayout')) { layoutRef = k; break; }
            }
            if (!layoutRef) return;
            const layoutProps = guiPropsByRef[layoutRef] || {};
            if (layoutProps.cls === 'UIGridLayout') { applyUIGridLayout(containerRef, layoutRef, kids); return; }
            const sortedKids = _sortLayoutKids(kids, layoutProps);
            kids.length = 0; sortedKids.forEach(k => kids.push(k));
            const paddingPx = (layoutProps.Padding && layoutProps.Padding.offset) || 0;
            // FillDirection в файле — число enum (0 = Horizontal, 1 = Vertical), в Lua-присваивании — строка
            const horizontal = layoutProps.FillDirection === 'Horizontal' || layoutProps.FillDirection === 0;
            let offset = 0;
            for (const k of kids) {
                const p = guiPropsByRef[k];
                if (!p || k === layoutRef) continue;
                if (p.cls && p.cls.indexOf('UI') === 0) continue; // UIPadding/UICorner/... — не элементы списка
                // Visible === false — это как раз наш случай "скрытый
                if (p.Visible === false) continue;
                const el = guiDomByRef[k];
                if (!el) continue;
                if (horizontal) {
                    const oldY = (p.Position && p.Position.y) || { scale: 0, offset: 0 };
                    p.Position = { x: { scale: 0, offset }, y: oldY };
                    applyGuiElementStyle(el, p);
                    offset += el.offsetWidth + paddingPx;
                } else {
                    const oldX = (p.Position && p.Position.x) || { scale: 0, offset: 0 };
                    p.Position = { x: oldX, y: { scale: 0, offset } };
                    applyGuiElementStyle(el, p);
                    offset += el.offsetHeight + paddingPx;
                }
            }
        }

        // Рендерит DOM-оверлей из уже готового guiPropsByRef (собранного
        function renderGuiOverlayFromClient() {
            const overlay = document.getElementById('gui-overlay');
            if (!overlay) { logLuaOutput('error', 'renderGuiOverlayFromClient: #gui-overlay не найден в DOM'); return; }
            overlay.innerHTML = '';
            _applyGuiZoom(overlay);
            guiDomByRef = {};
            guiChildrenByRef = {};
            for (const [refStr, props] of Object.entries(guiPropsByRef)) {
                const ref = Number(refStr);
                const parentRef = luaParentByRef[ref];
                if (parentRef !== undefined && parentRef !== -1) {
                    (guiChildrenByRef[parentRef] = guiChildrenByRef[parentRef] || []).push(ref);
                }
            }
            let renderedCount = 0;
            for (const [refStr, props] of Object.entries(guiPropsByRef)) {
                const ref = Number(refStr);
                if (props.cls !== 'ScreenGui' && props.cls !== 'BillboardGui') continue;
                const parentRef = luaParentByRef[ref];
                const parentInfo = parentRef !== undefined ? luaByRef[parentRef] : null;
                const isTemplateUnderStarterGui = parentInfo && parentInfo.cls === 'StarterGui';
                if (isTemplateUnderStarterGui) continue; // шаблон — не рендерим, рендерим клон в PlayerGui
                // ScreenGui рисуется в Roblox ТОЛЬКО внутри PlayerGui. Шаблоны, лежащие в ReplicatedStorage / под скриптом /
                // в ServerStorage (RoundResultsGui и т.п. — скрипт клонирует их сам), раньше рисовались поверх игры сразу.
                if (props.cls === 'ScreenGui') {
                    let cur = parentRef, inPG = false, g = 0;
                    while (cur !== undefined && cur !== -1 && g++ < 60) {
                        const ci = luaByRef[cur];
                        if (ci && ci.cls === 'PlayerGui') { inPG = true; break; }
                        cur = luaParentByRef[cur];
                    }
                    if (!inPG) continue;
                }
                if (props.Enabled === false) continue; // раньше было props.enabled (маленькая e) — никогда не совпадало, ScreenGui.Enabled=false из плейса игнорировался
                guiRenderNode(ref, overlay);
                renderedCount++;
            }
            overlay.classList.add('active');
            // Временный диагностический лог:
            logLuaOutput('info', 'GUI overlay: отрисовано верхних экранов ' + renderedCount
                + ' из ' + Object.keys(guiPropsByRef).length + ' известных GUI-объектов');
        }

        function clearGuiOverlay() {
            clearSurfaceGuis();
            const overlay = document.getElementById('gui-overlay');
            if (overlay) { overlay.innerHTML = ''; overlay.classList.remove('active'); }
            guiPropsByRef = {};
            guiChildrenByRef = {};
            guiDomByRef = {};
        }

        // Патчит уже отрисованный DOM-узел после того, как Lua-скрипт
        // ============ SurfaceGui: интерфейс на грани детали (3D) ============
        // Рисуем потомков SurfaceGui на canvas -> CanvasTexture на плоскости, приклеенной
        // к нужной грани детали. Свойства Lua (TextLabel.Text и т.д.) помечают canvas
        // «грязным», перерисовка — не чаще раза в кадр. Поддержка: Frame/TextLabel/TextButton/
        // TextBox (фон, рамка, текст с TextScaled и выравниванием) и ImageLabel (только фон).
        const surfaceGuis = {}; // ref SurfaceGui -> { partRef, mesh, canvas, ctx, tex, dw, dh, k, local, dirty }
        const _SG_FACES = {
            // NormalId: Right=0 Top=1 Back=2 Left=3 Bottom=4 Front=5 (Front = -Z детали)
            0: { n: [1, 0, 0], ry: Math.PI / 2, rx: 0 },
            // Top/Bottom: холст в Roblox идёт ШИРИНОЙ вдоль Z детали, «верх» — вдоль +X (проверено на A.rbxl: «Рулетка» на
            // грани Bottom детали 4x1x9.5, стоящей торцом, читается горизонтально). basis = [право, верх, нормаль] плоскости.
            1: { n: [0, 1, 0], basis: [[0, 0, 1], [1, 0, 0], [0, 1, 0]] },
            2: { n: [0, 0, 1], ry: 0, rx: 0 },
            3: { n: [-1, 0, 0], ry: -Math.PI / 2, rx: 0 },
            4: { n: [0, -1, 0], basis: [[0, 0, -1], [1, 0, 0], [0, -1, 0]] },
            5: { n: [0, 0, -1], ry: Math.PI, rx: 0 },
        };
        function surfaceGuiRootOf(ref) {
            let cur = ref, guard = 0;
            while (cur !== undefined && cur !== -1 && guard++ < 50) {
                if (surfaceGuis[cur]) return cur;
                cur = luaParentByRef[cur];
            }
            return null;
        }
        function surfaceGuiMarkDirty(ref) {
            const r = surfaceGuiRootOf(ref);
            if (r !== null) surfaceGuis[r].dirty = true;
        }
        function surfaceGuiChildren(ref) {
            return (luaChildrenByRef[ref] || []).filter(c => guiPropsByRef[c]);
        }
        function surfaceGuiDrawNode(ctx, ref, px, py, pw, ph) {
            const p = guiPropsByRef[ref];
            if (!p || p.Visible === false) return;
            if (p.cls === 'UICorner' || p.cls === 'UIStroke') return;
            const sz = p.Size || {}, ps = p.Position || {}, an = p.AnchorPoint || { x: 0, y: 0 };
            const w = ((sz.x && sz.x.scale) || 0) * pw + ((sz.x && sz.x.offset) || 0);
            const h = ((sz.y && sz.y.scale) || 0) * ph + ((sz.y && sz.y.offset) || 0);
            const x = px + ((ps.x && ps.x.scale) || 0) * pw + ((ps.x && ps.x.offset) || 0) - (an.x || 0) * w;
            const y = py + ((ps.y && ps.y.scale) || 0) * ph + ((ps.y && ps.y.offset) || 0) - (an.y || 0) * h;
            if (!(w > 0 && h > 0)) return;
            const bgT = typeof p.BackgroundTransparency === 'number' ? p.BackgroundTransparency : 0;
            if (bgT < 1 && p.cls !== 'ImageLabel' || (p.cls === 'ImageLabel' && bgT < 1)) {
                ctx.fillStyle = color3ToCss(p.BackgroundColor3, bgT);
                ctx.fillRect(x, y, w, h);
            }
            const bsp = (p.BorderSizePixel === undefined || p.BorderSizePixel === null) ? 1 : Number(p.BorderSizePixel);
            if (bsp > 0 && bgT < 1) {
                ctx.strokeStyle = color3ToCss(p.BorderColor3, 0);
                ctx.lineWidth = bsp;
                ctx.strokeRect(x + bsp / 2, y + bsp / 2, w - bsp, h - bsp);
            }
            if (typeof p.Text === 'string' && p.Text !== '' && (p.cls === 'TextLabel' || p.cls === 'TextButton' || p.cls === 'TextBox')) {
                const txtT = typeof p.TextTransparency === 'number' ? p.TextTransparency : 0;
                ctx.fillStyle = color3ToCss(p.TextColor3 || { r: 0, g: 0, b: 0 }, txtT);
                let size = Number(p.TextSize) || 14;
                const family = 'sans-serif';
                const lines = String(p.Text).split('\n');
                if (p.TextScaled) {
                    size = Math.max(4, h / Math.max(1, lines.length) * 0.95);
                    ctx.font = 'bold ' + size + 'px ' + family;
                    const widest = Math.max(...lines.map(l => ctx.measureText(l).width), 1);
                    if (widest > w) size = Math.max(4, size * (w / widest) * 0.98);
                }
                ctx.font = 'bold ' + size + 'px ' + family;
                const xa = p.TextXAlignment === undefined ? 2 : p.TextXAlignment;  // Left=0 Right=1 Center=2
                const ya = p.TextYAlignment === undefined ? 1 : p.TextYAlignment;  // Top=0 Center=1 Bottom=2
                ctx.textAlign = xa === 0 ? 'left' : (xa === 1 ? 'right' : 'center');
                ctx.textBaseline = 'middle';
                const tx = xa === 0 ? x + 2 : (xa === 1 ? x + w - 2 : x + w / 2);
                const lh = size * 1.15, total = lh * lines.length;
                let ty = ya === 0 ? y + total / 2 : (ya === 2 ? y + h - total / 2 : y + h / 2);
                ty -= total / 2 - lh / 2;
                lines.forEach((ln, i) => ctx.fillText(ln, tx, ty + i * lh, w));
            }
            const kids = surfaceGuiChildren(ref);
            if (kids.length) {
                ctx.save();
                if (p.ClipsDescendants) { ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip(); }
                for (const c of kids) surfaceGuiDrawNode(ctx, c, x, y, w, h);
                ctx.restore();
            }
        }
        function surfaceGuiRedraw(sg) {
            const ctx = sg.ctx;
            ctx.setTransform(1, 0, 0, 1, 0, 0);
            ctx.clearRect(0, 0, sg.canvas.width, sg.canvas.height);
            ctx.setTransform(sg.k, 0, 0, sg.k, 0, 0);
            for (const c of surfaceGuiChildren(sg.ref)) surfaceGuiDrawNode(ctx, c, 0, 0, sg.dw, sg.dh);
            sg.tex.needsUpdate = true;
            sg.dirty = false;
        }
        function buildSurfaceGuis() {
            clearSurfaceGuis();
            ensureSurfaceGuis();
        }
        // Достраивает недостающие SurfaceGui. Геометрию карты подгружают порциями (стриминг около
        // игрока), поэтому деталь с табло/кнопкой часто загружается ПОЗЖЕ старта Play — раньше
        // плоскость строилась один раз при старте, пропускала ещё не загруженные детали и больше
        // не создавалась (кнопки лифта оставались без цифр).
        function ensureSurfaceGuis() {
            let made = 0;
            for (const [refStr, p] of Object.entries(guiPropsByRef)) {
                if (p.cls !== 'SurfaceGui' || p.Enabled === false) continue;
                const ref = Number(refStr);
                if (surfaceGuis[ref]) continue;
                const partRef = luaParentByRef[ref];
                const partMesh = sceneObjs[partRef], psz = loadedObjSize[partRef];
                if (!partMesh || !psz) continue;
                const face = _SG_FACES[Number(p.Face === undefined ? 5 : p.Face)] || _SG_FACES[5];
                const fnum = Number(p.Face === undefined ? 5 : p.Face);
                const sideZ = (fnum === 0 || fnum === 3);
                const topBottom = (fnum === 1 || fnum === 4);
                const fw = topBottom ? psz.z : ((fnum === 2 || fnum === 5) ? psz.x : psz.z);
                const fh = topBottom ? psz.x : psz.y;
                let dw, dh;
                if (Number(p.SizingMode) === 0 && p.CanvasSize) {          // FixedSize
                    dw = Number(p.CanvasSize.x) || 800; dh = Number(p.CanvasSize.y) || 600;
                } else {                                                   // PixelsPerStud
                    const pps = Number(p.PixelsPerStud) || 50;
                    dw = Math.max(1, fw * pps); dh = Math.max(1, fh * pps);
                }
                // разрешение текстуры: длинная сторона 128..512 px
                const longest = Math.max(dw, dh);
                const target = Math.min(512, Math.max(128, longest));
                const k = target / longest;
                const canvas = document.createElement('canvas');
                canvas.width = Math.max(2, Math.round(dw * k)); canvas.height = Math.max(2, Math.round(dh * k));
                const tex = new THREE.CanvasTexture(canvas);
                tex.anisotropy = 4;
                const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, side: THREE.FrontSide,
                    depthTest: !p.AlwaysOnTop, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, toneMapped: false });
                const mesh = new THREE.Mesh(new THREE.PlaneGeometry(fw, fh), mat);
                mesh.matrixAutoUpdate = false; mesh.matrixWorldAutoUpdate = false; mesh.frustumCulled = false;
                // локальная матрица плоскости относительно детали: на 0.003 студа от грани наружу
                const half = [psz.x / 2, psz.y / 2, psz.z / 2];
                const off = new THREE.Vector3(face.n[0] * (half[0] + 0.003), face.n[1] * (half[1] + 0.003), face.n[2] * (half[2] + 0.003));
                const q = face.basis
                    ? new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(
                        new THREE.Vector3(...face.basis[0]), new THREE.Vector3(...face.basis[1]), new THREE.Vector3(...face.basis[2])))
                    : new THREE.Quaternion().setFromEuler(new THREE.Euler(face.rx, face.ry, 0, 'YXZ'));
                const local = new THREE.Matrix4().compose(off, q, new THREE.Vector3(1, 1, 1));
                scene.add(mesh);
                const sg = { ref, partRef, mesh, canvas, ctx: canvas.getContext('2d'), tex, dw, dh, k, local, dirty: true };
                surfaceGuis[ref] = sg;
                surfaceGuiRedraw(sg);
                made++;
            }
            return made;
        }
        let _sgEnsureT = 0;
        function clearSurfaceGuis() {
            for (const ref of Object.keys(surfaceGuis)) {
                const sg = surfaceGuis[ref];
                scene.remove(sg.mesh);
                sg.mesh.geometry.dispose(); sg.mesh.material.dispose(); sg.tex.dispose();
                delete surfaceGuis[ref];
            }
        }
        // каждый кадр: приклеить плоскость к детали (она может двигаться) и при необходимости перерисовать
        function updateSurfaceGuis() {
            const nowT = performance.now();
            if (nowT - _sgEnsureT > 500) { _sgEnsureT = nowT; ensureSurfaceGuis(); }
            for (const sg of Object.values(surfaceGuis)) {
                if (sg.dirty) surfaceGuiRedraw(sg);
                if (!sceneObjs[sg.partRef]) { sg.mesh.visible = false; continue; }
                sg.mesh.visible = sceneObjs[sg.partRef].visible !== false;
                // matrix (а не только matrixWorld): в этой версии three.js сцена каждый кадр делает
                // matrixWorld = parent.matrixWorld * matrix, и плоскость с единичной matrix оказывалась в (0,0,0).
                sg.mesh.matrix.copy(luaPartMatrix(sg.partRef)).multiply(sg.local);
                sg.mesh.matrixWorld.copy(sg.mesh.matrix);
                sg.mesh.matrixWorldNeedsUpdate = true;
            }
        }

        function guiPatchProp(ref, name, value) {
            const props = guiPropsByRef[ref];
            if (!props) return false;
            props[name] = value;
            if (props.cls === 'UIListLayout' || props.cls === 'UIGridLayout') {
                // Grid.CellSize = ... / list.Padding = ... — пересчитать раскладку контейнера
                const parentRef = luaParentByRef[ref];
                if (parentRef !== undefined && parentRef !== -1) applyUIListLayout(parentRef);
                return true;
            }
            if (props.cls === 'UIScale') {
                // у UIScale нет своего DOM-узла: пересчитываем стиль родителя (GuiScale меняет Scale на лету)
                const parentRef = luaParentByRef[ref];
                const pel = guiDomByRef[parentRef], pprops = guiPropsByRef[parentRef];
                if (pel && pprops) applyGuiElementStyle(pel, pprops);
                return true;
            }
            let el = guiDomByRef[ref];
            if (!el) {
                // Узла ещё нет — это нормально для ScreenGui/BillboardGui,
                if (name === 'Enabled' && value === true && (props.cls === 'ScreenGui' || props.cls === 'BillboardGui')) {
                    const overlay = document.getElementById('gui-overlay');
                    if (overlay) {
                        guiRenderNode(ref, overlay);
                        overlay.classList.add('active');
                    }
                }
                return true;
            }
            applyGuiElementStyle(el, props);
            return true;
        }

        function updateLuaScheduler() {
            if (!luaServerL && !luaClientL) return;
            processRemoteQueue();
            updateRunServiceSignals();
            updateTweens();
            if (!luaWaits.length) return;
            const now = performance.now();
            const ready = luaWaits.filter(w => w.resumeAt <= now);
            if (!ready.length) return;
            luaWaits = luaWaits.filter(w => w.resumeAt > now);
            for (const w of ready) resumeLuaCoroutine(w.co, 'script', 0);
        }

        // TweenService:Create(...):Play() — раньше TweenService не
        function updateTweens() {
            if (!activeTweens.length) return;
            const now = performance.now();
            const stillActive = [];
            for (const t of activeTweens) {
                const elapsed = (now - t.startTime) / 1000;
                const p = t.duration > 0 ? Math.min(1, elapsed / t.duration) : 1;
                if (t.cframe) {
                    const x = t.fromPos.x + (t.toPos.x - t.fromPos.x) * p;
                    const y = t.fromPos.y + (t.toPos.y - t.fromPos.y) * p;
                    const z = t.fromPos.z + (t.toPos.z - t.fromPos.z) * p;
                    let lx = t.fromLook.x + (t.toLook.x - t.fromLook.x) * p;
                    let ly = t.fromLook.y + (t.toLook.y - t.fromLook.y) * p;
                    let lz = t.fromLook.z + (t.toLook.z - t.fromLook.z) * p;
                    const llen = Math.hypot(lx, ly, lz) || 1;
                    if (t.fromQuat && t.toQuat && luaIsPartRef(t.ref)) {
                        const qq = t.fromQuat.clone().slerp(t.toQuat, p);
                        luaApplyPartMatrix(t.ref, new THREE.Matrix4().compose(new THREE.Vector3(x, y, z), qq, new THREE.Vector3(1, 1, 1)));
                        fireLuaSignal(t.ref, '__prop_CFrame', []); fireLuaSignal(t.ref, '__prop_Position', []);
                    } else {
                        applyCFrameValue(t.ref, x, y, z, lx / llen, ly / llen, lz / llen);
                    }
                    if (p >= 1) fireLuaSignal(t.completedRef, 'Event', []);
                    else stillActive.push(t);
                    continue;
                }
                if (t.partPos) {
                    const x = t.fromPos.x + (t.toPos.x - t.fromPos.x) * p;
                    const y = t.fromPos.y + (t.toPos.y - t.fromPos.y) * p;
                    const z = t.fromPos.z + (t.toPos.z - t.fromPos.z) * p;
                    const cm = luaPartMatrix(t.ref), cp = new THREE.Vector3(), cq = new THREE.Quaternion(), cs = new THREE.Vector3();
                    cm.decompose(cp, cq, cs);
                    luaApplyPartMatrix(t.ref, new THREE.Matrix4().compose(new THREE.Vector3(x, y, z), cq, new THREE.Vector3(1, 1, 1)));
                    fireLuaSignal(t.ref, '__prop_CFrame', []); fireLuaSignal(t.ref, '__prop_Position', []);
                    if (p >= 1) fireLuaSignal(t.completedRef, 'Event', []);
                    else stillActive.push(t);
                    continue;
                }
                if (t.composite) {
                    if (p >= 1) {
                        luaSetGenericProp(t.ref, t.propName, t.to);
                        fireLuaSignal(t.completedRef, 'Event', []);
                    } else {
                        stillActive.push(t);
                    }
                    continue;
                }
                const v = t.from + (t.to - t.from) * p;
                luaSetGenericProp(t.ref, t.propName, v);
                if (t.propName === 'Value') fireLuaSignal(t.ref, 'Changed', [v]);
                fireLuaSignal(t.ref, '__prop_' + t.propName, []);
                if (p >= 1) fireLuaSignal(t.completedRef, 'Event', []);
                else stillActive.push(t);
            }
            activeTweens = stillActive;
        }

        // ============ Виртуальная клавиатура для UserInputService ============
        // Источники нажатия: 'dom' — настоящая клавиатура, 'virt' — экранный
        // джойстик (W/A/S/D) и кнопка прыжка (Space). Клавиша «нажата», если
        // активен любой источник; InputBegan/InputEnded стреляют на переходах,
        // как в Roblox. Так клиентские скрипты на телефоне видят «WASD/пробел».
        const luaKeySrc = {}; // имя KeyCode -> { dom: bool, virt: bool }
        function luaKeyIsDown(name) { const k = luaKeySrc[name]; return !!(k && (k.dom || k.virt)); }
        function luaSetKeySrc(name, src, down) {
            if (!luaServerL && !luaClientL) return;
            const k = luaKeySrc[name] || (luaKeySrc[name] = { dom: false, virt: false });
            const was = k.dom || k.virt;
            k[src] = !!down;
            const now = k.dom || k.virt;
            if (was === now) return;
            const ref = luaFindServiceRef('UserInputService');
            if (ref !== -1) fireLuaSignal(ref, now ? 'InputBegan' : 'InputEnded', ['Keyboard', 0, 0, name]);
        }
        function luaReleaseAllKeys() { for (const k of Object.keys(luaKeySrc)) delete luaKeySrc[k]; }
        const _digitNames = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'];
        const _codeNames = {
            Space: 'Space', ArrowUp: 'Up', ArrowDown: 'Down', ArrowLeft: 'Left', ArrowRight: 'Right',
            ShiftLeft: 'LeftShift', ShiftRight: 'RightShift', ControlLeft: 'LeftControl', ControlRight: 'RightControl',
            AltLeft: 'LeftAlt', AltRight: 'RightAlt', Enter: 'Return', Escape: 'Escape', Tab: 'Tab', Backspace: 'Backspace',
        };
        // e.code — физическая клавиша, поэтому W/A/S/D работают и на русской раскладке
        function luaKeyNameFromDom(e) {
            const c = e.code || '';
            if (/^Key[A-Z]$/.test(c)) return c[3];
            if (/^Digit[0-9]$/.test(c)) return _digitNames[+c[5]];
            return _codeNames[c] || null;
        }
        // Экранный джойстик -> виртуальные W/A/S/D (порог 0.3); вызывается каждый кадр
        function luaUpdateVirtualKeys() {
            if (!luaServerL && !luaClientL) return;
            const T = 0.3;
            luaSetKeySrc('W', 'virt', joyVector.y > T);
            luaSetKeySrc('S', 'virt', joyVector.y < -T);
            luaSetKeySrc('D', 'virt', joyVector.x > T);
            luaSetKeySrc('A', 'virt', joyVector.x < -T);
        }

        // UserInputService.InputBegan/InputChanged/InputEnded — глобальные
        document.addEventListener('mousedown', (e) => {
            if (!luaServerL && !luaClientL) return;
            const ref = luaFindServiceRef('UserInputService');
            if (ref !== -1) fireLuaSignal(ref, 'InputBegan', [domInputTypeName(e, false), ...domInputXY(e)]);
        });
        document.addEventListener('mousemove', (e) => {
            if (!luaServerL && !luaClientL) return;
            const ref = luaFindServiceRef('UserInputService');
            if (ref !== -1) fireLuaSignal(ref, 'InputChanged', [domInputTypeName(e, true), ...domInputXY(e)]);
        });
        document.addEventListener('mouseup', (e) => {
            if (!luaServerL && !luaClientL) return;
            const ref = luaFindServiceRef('UserInputService');
            if (ref !== -1) fireLuaSignal(ref, 'InputEnded', [domInputTypeName(e, false), ...domInputXY(e)]);
        });
        // Тач-эквиваленты — раньше их не было вовсе, только мышиные.
        document.addEventListener('touchstart', () => {
            if (document.body.style.userSelect === 'none' && !currentResizer &&
                !document.querySelector('.resizer-h.active')) {
                document.body.style.userSelect = '';
                document.body.style.webkitUserSelect = '';
            }
        }, { passive: true, capture: true });
        document.addEventListener('touchstart', (e) => {
            if (!luaServerL && !luaClientL) return;
            const ref = luaFindServiceRef('UserInputService');
            if (ref !== -1) fireLuaSignal(ref, 'InputBegan', [domInputTypeName(e, false), ...domInputXY(e)]);
        }, { passive: true });
        document.addEventListener('touchmove', (e) => {
            if (!luaServerL && !luaClientL) return;
            const ref = luaFindServiceRef('UserInputService');
            if (ref !== -1) fireLuaSignal(ref, 'InputChanged', [domInputTypeName(e, true), ...domInputXY(e)]);
        }, { passive: true });
        document.addEventListener('touchend', (e) => {
            if (!luaServerL && !luaClientL) return;
            const ref = luaFindServiceRef('UserInputService');
            if (ref !== -1) fireLuaSignal(ref, 'InputEnded', [domInputTypeName(e, false), ...domInputXY(e)]);
        }, { passive: true });

        // RunService.Stepped/Heartbeat/RenderStepped — настоящий, не
        let lastRunServiceTick = null;
        function updateRunServiceSignals() {
            const ref = luaFindServiceRef('RunService');
            if (ref === -1) return;
            const now = performance.now() / 1000;
            const dt = lastRunServiceTick === null ? 0 : now - lastRunServiceTick;
            lastRunServiceTick = now;
            fireLuaSignal(ref, 'Heartbeat', [dt]);
            fireLuaSignal(ref, 'Stepped', [now, dt]);
            fireLuaSignal(ref, 'RenderStepped', [dt]);
        }

        function buildCannonShape(mesh) {
            const shapeName = mesh.userData.shape;
            const sx = mesh.userData.sx || 1, sy = mesh.userData.sy || 1, sz = mesh.userData.sz || 1;
            // Реальные тонкие плиты пола (трава, базплейты и т.п.) толщиной
            const MIN_COLLIDER_THICKNESS = 1.0;
            switch (shapeName) {
                case 'sphere': {
                    const r = Math.max(sx, sy, sz) * 0.5;
                    return new CANNON.Sphere(r);
                }
                case 'cylinder':
                    return new CANNON.Cylinder(sx * 0.5, sz * 0.5, Math.max(sy, MIN_COLLIDER_THICKNESS), 8);
                // Wedge/Cone у cannon.js нет готовой формы — приближаем боксом
                // по габаритам. Для точных скатов нужен ConvexPolyhedron.
                case 'wedge':
                case 'cone':
                case 'box':
                default:
                    return new CANNON.Box(new CANNON.Vec3(
                        Math.max(sx * 0.5, MIN_COLLIDER_THICKNESS * 0.5),
                        Math.max(sy * 0.5, MIN_COLLIDER_THICKNESS * 0.5),
                        Math.max(sz * 0.5, MIN_COLLIDER_THICKNESS * 0.5)
                    ));
            }
        }

        const luaMoveDir = { x: 0, z: 0 };
        let charVelX = 0, charVelZ = 0; // последняя заданная игроком горизонтальная скорость
        // Устанавливается настоящим PlayerModule:GetControls():Disable()
        let luaControlsDisabled = false;

        function applyCharacterControl() {
            if (!charBody) return;
            charBody.wakeUp();
            luaUpdateVirtualKeys();

            const forward = luaControlsDisabled ? 0 : Math.max(-1, Math.min(1,
                (keysPressed['w'] ? 1 : 0) - (keysPressed['s'] ? 1 : 0) + joyVector.y));
            const strafe = luaControlsDisabled ? 0 : Math.max(-1, Math.min(1,
                (keysPressed['d'] ? 1 : 0) - (keysPressed['a'] ? 1 : 0) + joyVector.x));

            // Движение по горизонтали относительно направления взгляда камеры
            const theta = spherical.theta;
            const fwdX = -Math.sin(theta), fwdZ = -Math.cos(theta);
            const rightX = Math.cos(theta), rightZ = -Math.sin(theta);

            let vx = fwdX * forward + rightX * strafe;
            let vz = fwdZ * forward + rightZ * strafe;
            const len = Math.hypot(vx, vz);
            let dirX = 0, dirZ = 0;
            // Humanoid.MoveDirection: желаемое направление ввода (джойстик/WASD),
            // как в Roblox — не зависит от WalkSpeed (при WalkSpeed=0 оно всё равно
            // ненулевое, по нему клиентские скрипты видят «игрок пытается идти»).
            {
                const mx = len > 0.001 ? vx / len : 0, mz = len > 0.001 ? vz / len : 0;
                if (mx !== luaMoveDir.x || mz !== luaMoveDir.z) {
                    luaMoveDir.x = mx; luaMoveDir.z = mz;
                    if (luaHumanoidRef !== -1) fireLuaSignal(luaHumanoidRef, '__prop_MoveDirection', []);
                }
            }
            if (len > 0.001) {
                dirX = vx / len; dirZ = vz / len;
                vx = dirX * charWalkSpeed;
                vz = dirZ * charWalkSpeed;
            } else {
                vx = 0; vz = 0;
            }

            // Ground-check лучом вниз — определяет, можно ли прыгнуть и
            const from = new CANNON.Vec3(charBody.position.x, charBody.position.y, charBody.position.z);
            const to = new CANNON.Vec3(charBody.position.x, charBody.position.y - CHAR_RADIUS - 0.6, charBody.position.z);
            const result = new CANNON.RaycastResult();
            physicsWorld.raycastClosest(from, to, { collisionFilterMask: _charRayMask(), skipBackfaces: true }, result);
            canJump = result.hasHit;

            // Падаем и уже какое-то время не находим опору — скорее всего
            if (!canJump && charBody.velocity.y < -5) {
                const now = performance.now();
                if (fallingSinceMs === null && !streamInFlight) {
                    fallingSinceMs = now;
                    refreshStreamedGeometry();
                } else if (fallingSinceMs !== null && now - fallingSinceMs > 200 && !streamInFlight) {
                    fallingSinceMs = now;
                    refreshStreamedGeometry();
                }
            } else {
                fallingSinceMs = null;
            }

            if (canJump && (dirX !== 0 || dirZ !== 0)) {
                tryStepUp(dirX, dirZ);
                // Авто-прыжок (Humanoid.AutoJumpEnabled): впереди препятствие выше ступеньки, но ниже прыжка
                if (!jumpQueued && charJumpPower > 0 && _autoJumpEnabled()) {
                    const nowAJ = performance.now();
                    if (nowAJ - _lastAutoJumpMs > 350 && needsAutoJump(dirX, dirZ)) {
                        jumpQueued = true;
                        _lastAutoJumpMs = nowAJ;
                    }
                }
            }

            if (charPushT > 0) { // толчок от HumanoidRootPart.AssemblyLinearVelocity
                const k = Math.min(1, charPushT / 0.4);
                vx += charPushX * k; vz += charPushZ * k;
                charPushT -= 1 / 60;
            }
            charVelX = vx;
            charVelZ = vz;
            charBody.velocity.x = vx;
            charBody.velocity.z = vz;

            if (jumpQueued && canJump && charJumpPower > 0) {
                charBody.velocity.y = charJumpPower * JUMP_POWER_TO_VELOCITY;
                canJump = false;
            }
            jumpQueued = jumpQueued && charJumpPower <= 0 ? false : jumpQueued;
            jumpQueued = false;

            // Страховка: тело игрока обязано быть в физическом мире (раз в секунду).
            const tNow = performance.now();
            if (tNow - _bodyCheckT > 1000) {
                _bodyCheckT = tNow;
                if (physicsWorld.bodies.indexOf(charBody) === -1) physicsWorld.addBody(charBody);
            }
        }
        let _bodyCheckT = 0;

        // Сфера плохо лезет по отдельным боксам-ступеням:
        // Авто-прыжок как у Roblox на телефонах. tryStepUp сам берёт низкие бордюры (до STEP_HEIGHT);
        // сюда доходит то, что выше: прыгаем, если препятствие впереди — СТЕНА (не пологий склон)
        // и его верх ниже высоты прыжка (JumpHeight 7.2, с запасом на сферу — 6.4 от ступней).
        const AUTO_JUMP_MAX_H = 6.4;
        let _lastAutoJumpMs = 0;
        function _autoJumpEnabled() {
            const hp = luaHumanoidRef !== -1 ? virtualInstanceProps[luaHumanoidRef] : null;
            return !hp || hp.AutoJumpEnabled !== false; // по умолчанию включён; скрипт может выключить
        }
        function needsAutoJump(dirX, dirZ) {
            const dist = CHAR_RADIUS + 1.2;
            const feetY = charBody.position.y - CHAR_RADIUS;
            const ray = (h, res) => physicsWorld.raycastClosest(
                new CANNON.Vec3(charBody.position.x, feetY + h, charBody.position.z),
                new CANNON.Vec3(charBody.position.x + dirX * dist, feetY + h, charBody.position.z + dirZ * dist),
                { collisionFilterMask: _charRayMask(), skipBackfaces: true }, res);
            const low = new CANNON.RaycastResult();
            ray(STEP_HEIGHT + 0.3, low);                 // выше того, что берёт tryStepUp
            if (!low.hasHit) return false;               // препятствия выше ступеньки нет
            if (low.hitNormalWorld && low.hitNormalWorld.y > 0.6) return false; // пологий склон — просто идём
            const high = new CANNON.RaycastResult();
            ray(AUTO_JUMP_MAX_H, high);
            return !high.hasHit;                         // сверху свободно — перепрыгнем
        }

        function tryStepUp(dirX, dirZ) {
            const checkDist = CHAR_RADIUS + 1.0;
            const footY = charBody.position.y - CHAR_RADIUS + 0.15;
            const kneeY = charBody.position.y - CHAR_RADIUS + STEP_HEIGHT;

            const footFrom = new CANNON.Vec3(charBody.position.x, footY, charBody.position.z);
            const footTo = new CANNON.Vec3(charBody.position.x + dirX * checkDist, footY, charBody.position.z + dirZ * checkDist);
            const footResult = new CANNON.RaycastResult();
            physicsWorld.raycastClosest(footFrom, footTo, { collisionFilterMask: _charRayMask(), skipBackfaces: true }, footResult);
            if (!footResult.hasHit) return; // впереди на уровне ног пусто — ступенька не нужна

            const kneeFrom = new CANNON.Vec3(charBody.position.x, kneeY, charBody.position.z);
            const kneeTo = new CANNON.Vec3(charBody.position.x + dirX * checkDist, kneeY, charBody.position.z + dirZ * checkDist);
            const kneeResult = new CANNON.RaycastResult();
            physicsWorld.raycastClosest(kneeFrom, kneeTo, { collisionFilterMask: _charRayMask(), skipBackfaces: true }, kneeResult);
            if (kneeResult.hasHit) return; // и выше препятствие — это стена, а не ступенька

            // Низкий порог впереди, сверху свободно — плавно поднимаем,
            // порциями по кадрам (а не телепортом), пока не окажемся над ним.
            charBody.position.y += 0.4;
            if (charBody.velocity.y < 0) charBody.velocity.y = 0;
        }

        // ============ ProximityPrompt — кнопка взаимодействия у детали ============
        // Живой реестр: и подсказки из файла (сервер отдаёт их начальные
        // значения один раз), и созданные скриптом в рантайме через
        // Instance.new (см. luaCreateVirtualInstance/luaSetParent/
        // luaSetGenericProp) — ключи те же, что имена свойств в Roblox.
        let _promptRegistry = {};
        let _activePrompt = null;        // ближайшая подсказка в радиусе прямо сейчас (или null)
        let _promptHoldStart = null;     // performance.now() начала удержания, или null
        const KEYCODE_LABELS = { 69: 'E', 70: 'F', 71: 'G', 32: 'Space' }; // самые частые; иначе просто "E"
        function _defaultPromptEntry(parentRef) {
            return {
                ActionText: 'Interact', ObjectText: '', KeyboardKeyCode: 69,
                HoldDuration: 0, MaxActivationDistance: 10, RequiresLineOfSight: true,
                Enabled: true, parentRef: parentRef !== undefined ? parentRef : -1,
                Style: 0, GamepadKeyCode: 1000,
            };
        }
        async function loadProximityPrompts() {
            try {
                const r = await api('GET', '/api/proximity_prompts');
                if (r && r.ok) {
                    for (const p of r.prompts) {
                        _promptRegistry[p.ref] = {
                            ActionText: p.actionText, ObjectText: p.objectText,
                            KeyboardKeyCode: p.keyCode, HoldDuration: p.holdDuration,
                            MaxActivationDistance: p.maxDistance, RequiresLineOfSight: p.requiresLineOfSight,
                            Enabled: p.enabled, parentRef: p.parentRef,
                            Style: p.style, GamepadKeyCode: p.gamepadKeyCode !== undefined ? p.gamepadKeyCode : 1000,
                        };
                        if (!luaByRef[p.ref]) { luaByRef[p.ref] = { cls: 'ProximityPrompt', name: 'ProximityPrompt' }; luaByRefVer++; }
                    }
                }
            } catch (e) { emuWarn('swallow:for:11240', 'for: ' + _errText(e) + ' (подсказок из файла не будет — рантаймовые всё равно подхватятся через хуки)'); }
        }
        function _promptKeyLabel(p) {
            if (typeof p.KeyboardKeyCode === 'number') return KEYCODE_LABELS[p.KeyboardKeyCode] || 'E';
            if (typeof p.KeyboardKeyCode === 'string' && p.KeyboardKeyCode) return p.KeyboardKeyCode.replace(/^KeyCode\.?/, '').slice(0, 3) || 'E';
            return 'E';
        }
        function _promptWorldPos(p) {
            // Позиция родителя (Part/Model) — та же логика, что и для обычных
            // объектов: физика, если есть, иначе текущая матрица меша.
            const body = physicsBodies[p.parentRef];
            if (body) return body.position;
            const mesh = sceneObjs[p.parentRef];
            if (mesh) { const v = new THREE.Vector3(); mesh.matrix.decompose(v, new THREE.Quaternion(), new THREE.Vector3()); return v; }
            return null;
        }

        // ===== Стандартный хотбар Roblox (CoreGui Backpack) + Tool.Activated =====
        const _coreGuiOff = {};
        let _hotbarEl = null, _hotbarLast = 0, _hotbarSig = '';
        function _toolsOf(parentRef) {
            return (luaChildrenByRef[parentRef] || []).filter(r => luaByRef[r] && luaByRef[r].cls === 'Tool');
        }
        function _backpackRef() {
            for (const k in luaByRef) if (luaByRef[k] && luaByRef[k].cls === 'Backpack') return Number(k);
            return -1;
        }
        function _toggleTool(ref) {
            const bp = _backpackRef();
            if (bp === -1 || luaCharacterRef === -1) return;
            const equipped = luaParentByRef[ref] === luaCharacterRef;
            for (const t of _toolsOf(luaCharacterRef)) luaSetParent(t, bp);   // одновременно — один Tool в руке
            if (!equipped) luaSetParent(ref, luaCharacterRef);
            _hotbarLast = 0;
        }
        function _updateDefaultHotbar() {
            const now = performance.now();
            if (now - _hotbarLast < 250) return;
            _hotbarLast = now;
            const bp = _backpackRef();
            const tools = (isPlaying && bp !== -1 && luaCharacterRef !== -1 && !_coreGuiOff.Backpack)
                ? _toolsOf(bp).concat(_toolsOf(luaCharacterRef)).sort((x, y) => x - y) : [];
            if (!_hotbarEl) {
                _hotbarEl = document.createElement('div');
                _hotbarEl.id = 'default-hotbar';
                _hotbarEl.style.cssText = 'position:absolute;left:50%;bottom:8px;transform:translateX(-50%);display:flex;gap:6px;z-index:60;pointer-events:auto;';
                const vp = document.getElementById('viewport'); if (!vp) return;
                vp.appendChild(_hotbarEl);
            }
            const sig = tools.map(t => t + ':' + (luaParentByRef[t] === luaCharacterRef ? 1 : 0) + ':' + luaByRef[t].name).join('|');
            if (sig === _hotbarSig) return;
            _hotbarSig = sig;
            _hotbarEl.innerHTML = '';
            tools.forEach((t, i) => {
                const b = document.createElement('div');
                const on = luaParentByRef[t] === luaCharacterRef;
                b.style.cssText = 'min-width:56px;height:56px;padding:2px 6px;box-sizing:border-box;display:flex;flex-direction:column;align-items:center;justify-content:center;'
                    + 'background:' + (on ? 'rgba(255,255,255,.35)' : 'rgba(25,27,29,.75)') + ';border:2px solid ' + (on ? '#fff' : 'rgba(255,255,255,.3)') + ';border-radius:6px;color:#fff;font:12px sans-serif;user-select:none;cursor:pointer;text-align:center;';
                b.innerHTML = '<span style="opacity:.7;font-size:10px">' + (i + 1) + '</span><span>' + String(luaByRef[t].name).replace(/</g, '&lt;') + '</span>';
                const act = (e) => { e.preventDefault(); e.stopPropagation(); _toggleTool(t); };
                b.addEventListener('mousedown', act); b.addEventListener('touchstart', act, { passive: false });
                _hotbarEl.appendChild(b);
            });
            _hotbarEl.style.display = tools.length ? 'flex' : 'none';
        }
        window.addEventListener('keydown', (e) => {
            if (!isPlaying || _coreGuiOff.Backpack || e.repeat) return;
            const t = e.target; if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
            const m = /^Digit([1-9])$/.exec(e.code || ''); if (!m) return;
            const bp = _backpackRef(); if (bp === -1 || luaCharacterRef === -1) return;
            const list = _toolsOf(bp).concat(_toolsOf(luaCharacterRef)).sort((x, y) => x - y);
            const tool = list[Number(m[1]) - 1]; if (tool !== undefined) _toggleTool(tool);
        });
        // Tool.Activated / Deactivated: клик или тап по сцене (не по GUI) при экипированном Tool.Enabled ~= false
        let _activatedTool = null;
        function _toolPointerDown(e) {
            if (!isPlaying || luaCharacterRef === -1 || _activatedTool !== null) return;
            const tg = e.target;
            if (!tg || !tg.closest || !tg.closest('#viewport')) return;
            if (tg.closest('#gui-overlay') && tg !== document.getElementById('gui-overlay')) return;
            if (tg.closest('#default-hotbar') || tg.closest('#proximity-prompt') || tg.closest('.mobile-pad, #mobile-pad, #joystick-zone')) return;
            if (e.type === 'mousedown' && e.button !== 0) return;
            const tool = _toolsOf(luaCharacterRef)[0];
            if (tool === undefined) return;
            if (luaGetGenericProp(tool, 'Enabled') === false) return;
            _activatedTool = tool;
            fireLuaSignal(tool, 'Activated', []);
        }
        function _toolPointerUp() {
            if (_activatedTool === null) return;
            const t = _activatedTool; _activatedTool = null;
            fireLuaSignal(t, 'Deactivated', []);
        }
        document.addEventListener('mousedown', _toolPointerDown);
        document.addEventListener('touchstart', _toolPointerDown, { passive: true });
        document.addEventListener('mouseup', _toolPointerUp);
        document.addEventListener('touchend', _toolPointerUp, { passive: true });
        document.addEventListener('touchcancel', _toolPointerUp, { passive: true });

        let _activePromptRef = null;
        let _promptShownRef = null;      // подсказка, для которой уже стрелял PromptShown
        let _promptHeldRef = null;       // подсказка, у которой сейчас «зажата кнопка»
        let _promptTriggered = false;    // Triggered уже выстрелил за текущее удержание
        let _ppsRefCache = null;
        // Style: из файла приходит числом (1 = Custom), из скрипта — именем Enum
        function _promptIsCustom(p) {
            const v = p && p.Style;
            return v === 1 || v === '1' || v === 'Custom' || (v && v.Name === 'Custom') || /Custom$/.test(String(v));
        }
        function _promptInputType() {
            const touch = (navigator.maxTouchPoints || 0) > 0 || ('ontouchstart' in window);
            return { __enum: ['ProximityPromptInputType', touch ? 'Touch' : 'Keyboard'] };
        }
        // Сигналы самого ProximityPromptService (PromptShown/Hidden/Triggered/...): ref сервиса появляется только
        // после game:GetService("ProximityPromptService") — до этого слушать некому.
        function _ppsRef() {
            if (_ppsRefCache !== null && luaByRef[_ppsRefCache] && luaByRef[_ppsRefCache].cls === 'ProximityPromptService') return _ppsRefCache;
            for (const k in luaByRef) { if (luaByRef[k] && luaByRef[k].cls === 'ProximityPromptService') { _ppsRefCache = Number(k); return _ppsRefCache; } }
            return null;
        }
        const _PPS_EV = { Triggered: 'PromptTriggered', TriggerEnded: 'PromptTriggerEnded' };
        function _promptFire(ref, ev, extra) {
            // сигнал на самом prompt + одноимённый на сервисе (там prompt — первый аргумент, Triggered зовётся PromptTriggered)
            fireLuaSignal(Number(ref), ev, extra || []);
            const pps = _ppsRef();
            if (pps !== null) fireLuaSignal(pps, _PPS_EV[ev] || ev, [{ __instanceRef: Number(ref) }].concat(extra || []));
        }
        function _promptHoldBegin(ref) {
            const p = _promptRegistry[ref];
            if (!p || _promptHeldRef === ref) return;
            _promptHeldRef = ref; _promptTriggered = false;
            _promptHoldStart = performance.now();
            _promptFire(ref, 'PromptButtonHoldBegan', [{ __instanceRef: luaPlayerRef }]);
            if (!(p.HoldDuration > 0)) _promptComplete(ref);
        }
        function _promptComplete(ref) {
            if (_promptTriggered) return;
            _promptTriggered = true;
            _promptFire(ref, 'Triggered', [{ __instanceRef: luaPlayerRef }]);
        }
        function _promptHoldEnd(ref) {
            if (_promptHeldRef === null || (ref !== undefined && _promptHeldRef !== ref)) return;
            const r = _promptHeldRef;
            _promptHeldRef = null; _promptHoldStart = null;
            _promptFire(r, 'PromptButtonHoldEnded', [{ __instanceRef: luaPlayerRef }]);
            if (_promptTriggered) _promptFire(r, 'TriggerEnded', [{ __instanceRef: luaPlayerRef }]);
            _promptTriggered = false;
            const ring = document.getElementById('proximity-prompt-ring');
            if (ring) ring.classList.remove('held');
            const fill = document.getElementById('proximity-prompt-fill');
            if (fill) fill.style.height = '0%';
        }
        window.__promptInput = function (ref, down) { if (down) _promptHoldBegin(ref); else _promptHoldEnd(ref); };
        function _promptSetShown(ref) {
            if (_promptShownRef === ref) return;
            const old = _promptShownRef;
            _promptShownRef = ref;
            if (old !== null) {
                if (_promptHeldRef === old) _promptHoldEnd(old);
                if (_promptIsCustom(_promptRegistry[old])) _promptFire(old, 'PromptHidden', []);
            }
            if (ref !== null && _promptIsCustom(_promptRegistry[ref])) _promptFire(ref, 'PromptShown', [_promptInputType()]);
        }
        function updateProximityPrompts() {
            _updateDefaultHotbar();
            const el = document.getElementById('proximity-prompt');
            if (!el) return;
            const refs = Object.keys(_promptRegistry);
            if (!charBody || !refs.length) { el.style.display = 'none'; _activePromptRef = null; _activePrompt = null; _promptSetShown(null); return; }
            let bestRef = null, best = null, bestDist = Infinity;
            for (const refStr of refs) {
                const p = _promptRegistry[refStr];
                if (!p.Enabled || p.parentRef === -1 || p.parentRef === undefined) continue;
                const wp = _promptWorldPos(p);
                if (!wp) continue;
                const d = Math.hypot(wp.x - charBody.position.x, wp.y - charBody.position.y, wp.z - charBody.position.z);
                if (d <= p.MaxActivationDistance && d < bestDist) { best = p; bestRef = refStr; bestDist = d; }
            }
            _activePromptRef = bestRef;
            _activePrompt = best;
            _promptSetShown(bestRef);   // Hidden у старой / Shown у новой (только Custom), сброс удержания
            // Style=Custom: стандартную кнопку Roblox НЕ рисуем — подсказку показывает скрипт карты по PromptShown
            if (!best || _promptIsCustom(best)) { el.style.display = 'none'; }
            else {
                el.style.display = 'flex';
                document.getElementById('proximity-prompt-key').textContent = _promptKeyLabel(best);
                document.getElementById('proximity-prompt-action').textContent = best.ActionText || 'Interact';
                document.getElementById('proximity-prompt-object').textContent = best.ObjectText || '';
            }
            const fill = document.getElementById('proximity-prompt-fill');
            const heldP = _promptHeldRef !== null ? _promptRegistry[_promptHeldRef] : null;
            if (heldP && _promptHoldStart !== null && heldP.HoldDuration > 0) {
                const frac = Math.min(1, (performance.now() - _promptHoldStart) / (heldP.HoldDuration * 1000));
                if (fill) fill.style.height = (frac * 100) + '%';
                if (frac >= 1) _promptComplete(_promptHeldRef);
            } else if (fill) {
                fill.style.height = '0%';
            }
        }
        function _triggerActivePrompt() {
            if (_activePromptRef === null) return;
            _promptHoldBegin(_activePromptRef);
            if (!(_activePrompt && _activePrompt.HoldDuration > 0)) _promptHoldEnd(_activePromptRef);
        }
        function _promptKeyMatches(e, p) {
            let kc = p.KeyboardKeyCode;
            if (typeof kc === 'string') { const n = kc.replace(/^KeyCode\.?/, ''); return n.length === 1 ? e.key.toUpperCase() === n.toUpperCase() : e.code === n || e.key === n; }
            if (kc >= 97 && kc <= 122) kc -= 32;
            return e.keyCode === kc;
        }
        window.addEventListener('keydown', (e) => {
            if (!isPlaying || e.repeat || _activePromptRef === null || !_activePrompt) return;
            const t = e.target;
            if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
            if (_promptKeyMatches(e, _activePrompt)) { _promptHoldBegin(_activePromptRef); }
        });
        window.addEventListener('keyup', (e) => {
            if (_promptHeldRef === null) return;
            const p = _promptRegistry[_promptHeldRef];
            if (p && _promptKeyMatches(e, p)) _promptHoldEnd(_promptHeldRef);
        });
        window.addEventListener('load', () => {
            const ring = document.getElementById('proximity-prompt-ring');
            const onUp = () => _promptHoldEnd();
            if (ring) {
                const onDown = (e) => { e.preventDefault(); if (_activePrompt) _promptHoldBegin(_activePromptRef); };
                ring.addEventListener('touchstart', onDown, { passive: false });
                ring.addEventListener('mousedown', onDown);
            }
            // Custom: тап/клик по BillboardGui подсказки (как ClickablePrompt в Roblox). Элементы Druns_PP имеют Active=false, то есть
            // pointer-events:none — event.target туда не попадает, поэтому проверяем попадание точки в прямоугольник билборда.
            const _inRelated = (a, b) => {   // a — потомок b или b — потомок a (Adornee может быть деталью внутри модели с промптом)
                for (let c = a, g = 0; c !== undefined && c !== -1 && g++ < 80; c = luaParentByRef[c]) if (c === b) return true;
                for (let c = b, g = 0; c !== undefined && c !== -1 && g++ < 80; c = luaParentByRef[c]) if (c === a) return true;
                return false;
            };
            document.addEventListener('pointerdown', (e) => {
                if (!isPlaying || _activePromptRef === null || !_activePrompt || !_promptIsCustom(_activePrompt) || _activePrompt.ClickablePrompt === false) return;
                if (_promptHeldRef !== null) return;
                const tg = e.target;
                if (!tg || !tg.closest || !tg.closest('#viewport')) return;
                if (tg.closest('#mobile-pad, #default-hotbar, #proximity-prompt, button')) return;
                if (tg.closest('#gui-overlay') && tg !== document.getElementById('gui-overlay')) return;   // настоящая GUI-кнопка карты
                for (const ref in guiPropsByRef) {
                    const gp = guiPropsByRef[ref];
                    if (!gp || gp.cls !== 'BillboardGui' || gp.Enabled === false) continue;
                    const bel = guiDomByRef[ref];
                    if (!bel || !bel.isConnected || bel.style.display === 'none') continue;
                    const ad = gp.Adornee;
                    if (ad === undefined || ad === null || ad === -1 || !_inRelated(Number(ad), Number(_activePrompt.parentRef))) continue;
                    const r = bel.getBoundingClientRect();
                    if (e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom) {
                        _promptHoldBegin(_activePromptRef);
                        return;
                    }
                }
            }, true);
            window.addEventListener('pointerup', onUp);
            window.addEventListener('pointercancel', onUp);
            window.addEventListener('touchend', onUp);
            window.addEventListener('mouseup', onUp);
        });

        // Enum.CameraType.Scriptable — настоящий Roblox по нему полностью
        let cameraIsScriptable = false;

        // 0..1 — прогресс плавного возврата камеры к персонажу после
        // CameraType.Scriptable; null, когда обычный (мгновенный) follow.
        let _camReturnToCharT = null;
        const CAM_RETURN_DURATION = 0.35; // секунд
        // Последний CFrame, который скрипт поставил камере. Пока камера Scriptable,
        // переустанавливаем его каждый кадр, чтобы ничто другое не сбивало вид
        // (раньше камера внутри холодильника оставалась под «редакторским» углом).
        let _scriptCam = null;
        function followCharacterCamera() {
            if (charBody && cameraIsScriptable) {
                if (_scriptCam) { camera.position.copy(_scriptCam.p); camera.quaternion.copy(_scriptCam.q); }
                return;
            }
            if (!charBody || cameraIsScriptable) return;
            const desiredX = charBody.position.x;
            const desiredY = charBody.position.y + EYE_HEIGHT;
            const desiredZ = charBody.position.z;
            if (_camReturnToCharT !== null) {
                _camReturnToCharT += (1 / 60) / CAM_RETURN_DURATION;
                if (_camReturnToCharT >= 1) {
                    _camReturnToCharT = null;
                    target.x = desiredX; target.y = desiredY; target.z = desiredZ;
                } else {
                    // ease-out — быстрый старт, плавное сближение к цели
                    const a = 1 - Math.pow(1 - _camReturnToCharT, 3);
                    target.x += (desiredX - target.x) * a * 0.3;
                    target.y += (desiredY - target.y) * a * 0.3;
                    target.z += (desiredZ - target.z) * a * 0.3;
                }
            } else {
                target.x = desiredX;
                target.y = desiredY;
                target.z = desiredZ;
            }
            if (charMesh) {
                charMesh.position.set(charBody.position.x, charBody.position.y, charBody.position.z);
                charMesh.rotation.y = spherical.theta; // куб развёрнут туда же, куда смотрит камера
            }
            updateBlobShadow();
            updateCamera();
        }

        let _physLastT = 0, _physAcc = 0;
        let _syncP = null, _syncQ = null, _syncOne = null;   // создаются лениво: THREE подгружается позже скрипта
        const PHYSICS_MAX_TICKS = 5;   // не больше 5 шагов (1/12 с) за кадр
        const PHYSICS_SUBSTEPS = 4; // дробим шаг — у cannon.js 0.6.2 нет CCD,
        // быстро падающая сфера может за один большой шаг проскочить сквозь
        // тонкий пол ("проваливаюсь"). Мельче шаг — меньше смещение за шаг.
        const MAX_FALL_SPEED = 300; // студов/сек — подстраховка на случай
        // разгона до нереальной скорости (например, пока не подгрузился пол).

        // Touched/TouchEnded для частей с CanCollide=false (триггеры): у них collisionFilterMask=0, поэтому
        // cannon контактов не создаёт, а в Roblox такие части Touched всё равно получают (если CanTouch).
        let touchingTriggers = new Set();
        // Touched/TouchEnded от обычных контактов тел. cannon.js 0.6 не шлёт beginContact, поэтому
        // после шага смотрим physicsWorld.contacts: новая пара -> Touched, пара пропала -> TouchEnded.
        let touchContacts = new Map();   // "a|b" -> {a, b, frame}
        let touchFrame = 0;
        function updateContactTouches() {
            if (!physicsWorld) return;
            touchFrame++;
            const listened = (ref) => {
                const l1 = luaSignalsByKey[ref + '|Touched'], l2 = luaSignalsByKey[ref + '|TouchEnded'];
                return (l1 && l1.length) || (l2 && l2.length);
            };
            for (const c of physicsWorld.contacts) {
                const a = c.bi.__ref, b = c.bj.__ref;
                if (a === undefined || b === undefined || a === b) continue;
                const key = a < b ? a + '|' + b : b + '|' + a;
                const rec = touchContacts.get(key);
                if (rec) { rec.frame = touchFrame; continue; }
                if (!listened(a) && !listened(b)) continue;
                touchContacts.set(key, { a, b, frame: touchFrame });
                fireLuaSignal(a, 'Touched', [{ __instanceRef: b }]);
                fireLuaSignal(b, 'Touched', [{ __instanceRef: a }]);
            }
            for (const [key, rec] of touchContacts) {
                if (touchFrame - rec.frame > 3) {   // небольшой гистерезис, чтобы не мигало на дребезге контакта
                    touchContacts.delete(key);
                    fireLuaSignal(rec.a, 'TouchEnded', [{ __instanceRef: rec.b }]);
                    fireLuaSignal(rec.b, 'TouchEnded', [{ __instanceRef: rec.a }]);
                }
            }
        }
        function updateTouchTriggers() {
            if (!charBody || luaHumanoidRootPartRef === -1) return;
            const refs = new Set();
            for (const key of Object.keys(luaSignalsByKey)) {
                const bar = key.indexOf('|');
                const ev = key.slice(bar + 1);
                if ((ev === 'Touched' || ev === 'TouchEnded') && luaSignalsByKey[key] && luaSignalsByKey[key].length) refs.add(key.slice(0, bar));
            }
            const c = charBody.position, r = CHAR_RADIUS;
            for (const refStr of refs) {
                const body = physicsBodies[refStr];
                if (!body || body === charBody || body.collisionFilterMask !== 0 || !body.shapes.length) continue;
                const sh = body.shapes[0];
                let inside = false;
                if (sh instanceof CANNON.Box) {
                    const local = body.quaternion.inverse().vmult(new CANNON.Vec3(c.x - body.position.x, c.y - body.position.y, c.z - body.position.z));
                    const h = sh.halfExtents;
                    const dx = Math.max(Math.abs(local.x) - h.x, 0), dy = Math.max(Math.abs(local.y) - h.y, 0), dz = Math.max(Math.abs(local.z) - h.z, 0);
                    inside = dx * dx + dy * dy + dz * dz <= r * r;
                } else if (sh instanceof CANNON.Sphere) {
                    inside = Math.hypot(c.x - body.position.x, c.y - body.position.y, c.z - body.position.z) <= sh.radius + r;
                } else {
                    body.computeAABB();
                    const a = body.aabb;
                    inside = c.x >= a.lowerBound.x - r && c.x <= a.upperBound.x + r && c.y >= a.lowerBound.y - r && c.y <= a.upperBound.y + r && c.z >= a.lowerBound.z - r && c.z <= a.upperBound.z + r;
                }
                const was = touchingTriggers.has(refStr);
                if (inside && !was) {
                    touchingTriggers.add(refStr);
                    fireLuaSignal(Number(refStr), 'Touched', [{ __instanceRef: luaHumanoidRootPartRef }]);
                    fireLuaSignal(luaHumanoidRootPartRef, 'Touched', [{ __instanceRef: Number(refStr) }]);
                } else if (!inside && was) {
                    touchingTriggers.delete(refStr);
                    fireLuaSignal(Number(refStr), 'TouchEnded', [{ __instanceRef: luaHumanoidRootPartRef }]);
                    fireLuaSignal(luaHumanoidRootPartRef, 'TouchEnded', [{ __instanceRef: Number(refStr) }]);
                }
            }
        }

        function stepPhysics() {
            if (!isPlaying || !physicsWorld) return;
            // Физика идёт по РЕАЛЬНОМУ времени, как в Roblox (WalkSpeed 16 студов/с — именно в секунду, а не
            // «за кадр»): накопитель + фиксированный шаг 1/60. Раньше на каждый кадр делался ровно один шаг,
            // и при 7 FPS мир шёл в ~8 раз медленнее. За кадр не больше PHYSICS_MAX_TICKS шагов, иначе на
            // слабом телефоне каждый тяжёлый кадр порождал бы ещё более тяжёлый (спираль).
            const nowT = performance.now();
            const dtReal = _physLastT ? (nowT - _physLastT) / 1000 : 1 / 60;
            _physLastT = nowT;
            _physAcc = Math.min(_physAcc + dtReal, PHYSICS_MAX_TICKS / 60);
            let ticks = 0;
            while (_physAcc >= 1 / 60 - 1e-6 && ticks < PHYSICS_MAX_TICKS) {
                _physAcc -= 1 / 60; ticks++;
                applyCharacterControl();
                if (charBody && charBody.velocity.y < -MAX_FALL_SPEED) {
                    charBody.velocity.y = -MAX_FALL_SPEED;
                }
                const subDt = (1 / 60) / PHYSICS_SUBSTEPS;
                for (let i = 0; i < PHYSICS_SUBSTEPS; i++) {
                    physicsWorld.step(subDt);
                    // Ступеньки лестницы — это отдельные боксы с вертикальными
                    if (charBody) {
                        charBody.velocity.x = charVelX;
                        charBody.velocity.z = charVelZ;
                    }
                }
            }
            updateHollowUnionGhosts();
            updateSurfaceGuis();
            if (ticks === 0) return;   // экран быстрее 60 Гц: новых шагов нет, картинка не изменилась
            luaStepWelds();

            if (!_syncP) { _syncP = new THREE.Vector3(); _syncQ = new THREE.Quaternion(); _syncOne = new THREE.Vector3(1, 1, 1); }
            for (const [refStr, body] of Object.entries(physicsBodies)) {
                const mesh = sceneObjs[refStr];
                if (!mesh) continue;
                mesh.matrix.compose(
                    _syncP.set(body.position.x, body.position.y, body.position.z),
                    _syncQ.set(body.quaternion.x, body.quaternion.y, body.quaternion.z, body.quaternion.w),
                    mesh.userData.partScale || _syncOne
                );
            }
            updateTouchTriggers();
            updateContactTouches();
            followCharacterCamera();
            updateProximityPrompts();
            maybeStreamGeometry();
            updateLuaScheduler();
        }

        // ============ ДЕРЕВО ============
        async function loadTree() {
            const r = await api('GET', '/api/tree');
            if (!r.ok) return;
            treeData = r.tree;
            for (const n of treeData) {
                expanded.add(n.ref);
            }
            rebuildTreeIndex();
            renderTree();
            reloadScene();
            refreshMapLighting();
        }

        // ref -> node и ref -> parentRef — плоские индексы поверх вложенного
        let treeByRef = {};
        let parentByRef = {};
        function rebuildTreeIndex() {
            treeByRef = {};
            parentByRef = {};
            function walk(nodes, parentRef) {
                for (const n of nodes) {
                    treeByRef[n.ref] = n;
                    parentByRef[n.ref] = parentRef;
                    if (n.children && n.children.length) walk(n.children, n.ref);
                }
            }
            walk(treeData, -1);
        }

        function updateInventoryCount() {
            // Раньше это писало текст в #inv-selected-info — элемент из
        }

        function findNodeByRef(nodes, ref) {
            for (const n of nodes) {
                if (n.ref === ref) return n;
                if (n.children) {
                    const found = findNodeByRef(n.children, ref);
                    if (found) return found;
                }
            }
            return null;
        }

        function onSearch(v) {
            searchText = v.trim().toLowerCase();
            if (searchText) {
                for (const n of treeData) {
                    expandAll(n);
                }
            }
            renderTree();
        }

        function expandAll(n) {
            expanded.add(n.ref);
            for (const c of n.children) {
                expandAll(c);
            }
        }

        function collapseAll() {
            expanded.clear();
            renderTree();
        }

        function expandAllVisible() {
            for (const n of treeData) {
                expandAll(n);
            }
            renderTree();
        }

        function renderTree() {
            const et = document.getElementById('explorer-title');
            if (et) et.textContent = 'Explorer' + (selectedRefs.size > 1 ? ' (' + selectedRefs.size + ')' : '');
            const c = document.getElementById('tree');
            c.innerHTML = '';
            for (const n of treeData) {
                renderNode(c, n, 0);
            }
        }

        function renderNode(parentEl, node, depth) {
            const matchesSearch = !searchText ||
                node.name.toLowerCase().includes(searchText) ||
                node.cls.toLowerCase().includes(searchText);
            const hasMatchingChildren = searchText ? node.children.some(child => anyMatch(child)) : false;
            const isVisible = matchesSearch || hasMatchingChildren;

            if (!isVisible) return;

            const row = document.createElement('div');
            row.className = 'tree-node' + (selectedRefs.has(node.ref) ? ' selected' : '');
            row.style.paddingLeft = (depth * 14 + 2) + 'px';
            row.dataset.ref = node.ref;
            row.style.webkitTouchCallout = 'none';

            const arrow = document.createElement('span');
            arrow.className = 'tree-arrow';
            if (node.children.length) {
                arrow.textContent = expanded.has(node.ref) ? '▼' : '▶';
                arrow.onclick = (e) => {
                    e.stopPropagation();
                    toggleExpand(node.ref);
                };
            }
            row.appendChild(arrow);

            if (node.icon) {
                const img = document.createElement('img');
                img.className = 'tree-icon';
                img.src = node.icon;
                img.onerror = () => { img.style.display = 'none'; };
                row.appendChild(img);
            }

            const label = document.createElement('span');
            label.className = 'tree-label';
            if (searchText && node.name.toLowerCase().includes(searchText)) {
                const idx = node.name.toLowerCase().indexOf(searchText);
                label.innerHTML = esc(node.name.slice(0, idx)) +
                    '<mark>' + esc(node.name.slice(idx, idx + searchText.length)) + '</mark>' +
                    esc(node.name.slice(idx + searchText.length));
            } else {
                label.textContent = node.name;
            }
            label.title = node.cls;

            row.onclick = (e) => {
                if (performance.now() < _treeSuppressClickUntil) return; // клик после отпускания при перетаскивании
                selectRef(node.ref, {
                    additive: e.ctrlKey || e.metaKey || multiSelectMode,
                    range: e.shiftKey
                });
            };
            row.appendChild(label);

            parentEl.appendChild(row);

            if (expanded.has(node.ref)) {
                for (const child of node.children) {
                    renderNode(parentEl, child, depth + 1);
                }
            }
        }

        // ============ EXPLORER: перетаскивание объектов (смена Parent) ============
        // Мышь: потянуть строку. Телефон: удерживать строку ~0.35 с, затем вести
        // палец (пока держишь — прокрутка списка не срабатывает). Если навести на
        // строку с потомками и подержать ~0.6 с, ветка раскрывается. Отпустить на
        // строке = сделать её родителем (на сервере /api/reparent).
        const TREE_LONGPRESS_MS = 350;
        const TREE_HOVER_EXPAND_MS = 600;
        const TREE_MOVE_CANCEL_PX = 8;      // сдвиг до долгого нажатия = это прокрутка, не перетаскивание
        const TREE_MOUSE_START_PX = 6;
        let _tdrag = null;
        let _treeSuppressClickUntil = 0;

        function treeCanDrag(ref) {
            if (isPlaying) return false;
            const n = treeByRef[ref];
            if (!n) return false;
            const par = parentByRef[ref];
            if (par === undefined || par === -1) return false;       // сервисы/корни
            if (n.cls === 'Terrain' || n.cls === 'Camera') return false;
            return true;
        }
        function treeInside(ref, ancestorRef) { // ref лежит внутри ancestorRef (или это он сам)
            let cur = ref, guard = 0;
            while (cur !== undefined && cur !== null && cur !== -1 && guard++ < 500) {
                if (cur === ancestorRef) return true;
                cur = parentByRef[cur];
            }
            return false;
        }
        function treeDropValid(targetRef) {
            if (targetRef === null || !_tdrag) return false;
            if (!treeByRef[targetRef]) return false;
            for (const r of _tdrag.refs) {
                if (treeInside(targetRef, r)) return false;           // в себя или в своего потомка
            }
            return _tdrag.refs.some(r => parentByRef[r] !== targetRef); // всё уже там — нечего делать
        }
        function treeRowAt(x, y) {
            const el = document.elementFromPoint(x, y);
            return el && el.closest ? el.closest('#tree .tree-node') : null;
        }
        function treeDragMarkRows() {
            if (!_tdrag || !_tdrag.active) return;
            const treeEl = document.getElementById('tree');
            for (const row of treeEl.querySelectorAll('.tree-node')) {
                const ref = Number(row.dataset.ref);
                row.classList.toggle('dragging-src', _tdrag.refs.indexOf(ref) !== -1);
                const isHover = _tdrag.hoverRef === ref;
                row.classList.toggle('drop-target', isHover && treeDropValid(ref));
                row.classList.toggle('drop-invalid', isHover && !treeDropValid(ref));
            }
        }
        function treeScrollParent(el) {
            let cur = el;
            while (cur && cur !== document.body) {
                const oy = getComputedStyle(cur).overflowY;
                if ((oy === 'auto' || oy === 'scroll') && cur.scrollHeight > cur.clientHeight + 1) return cur;
                cur = cur.parentElement;
            }
            return null;
        }
        function treeDragStart() {
            const d = _tdrag;
            if (!d || d.active) return;
            // что тащим: все выделенные (если тянем выделенный), иначе одну строку
            let refs = (selectedRefs.has(d.srcRef) && selectedRefs.size > 1) ? [...selectedRefs] : [d.srcRef];
            refs = refs.filter(treeCanDrag);
            refs = refs.filter(r => !refs.some(o => o !== r && treeInside(r, o)));  // вложенные не нужны — поедут с родителем
            if (!refs.length) { treeDragEnd(false); return; }
            d.refs = refs;
            d.active = true;
            document.body.classList.add('tree-dragging');
            const treeEl = document.getElementById('tree');
            try { treeEl.setPointerCapture(d.pointerId); } catch (e) { emuWarn('swallow:treeEl.setPointerCapture:11730', 'treeEl.setPointerCapture: ' + _errText(e) + ''); }
            const ghost = document.createElement('div');
            ghost.id = 'tree-drag-ghost';
            const first = treeByRef[refs[0]];
            ghost.textContent = (refs.length > 1 ? t('mv_ghost_n', { n: refs.length }) : '↕ ' + (first ? first.name : ''));
            document.body.appendChild(ghost);
            d.ghost = ghost;
            d.scrollEl = treeScrollParent(treeEl);
            if (navigator.vibrate) { try { navigator.vibrate(15); } catch (e) { emuWarn('swallow:navigator.vibrate:11738', 'navigator.vibrate: ' + _errText(e) + ''); } }
            treeDragUpdate(d.lastX, d.lastY);
            const tick = () => {
                if (!_tdrag || !_tdrag.active) return;
                const sc = _tdrag.scrollEl;
                if (sc) {
                    const r = sc.getBoundingClientRect();
                    const EDGE = 44;
                    if (_tdrag.lastY < r.top + EDGE) sc.scrollTop -= Math.ceil((r.top + EDGE - _tdrag.lastY) / 4);
                    else if (_tdrag.lastY > r.bottom - EDGE) sc.scrollTop += Math.ceil((_tdrag.lastY - (r.bottom - EDGE)) / 4);
                }
                _tdrag.raf = requestAnimationFrame(tick);
            };
            d.raf = requestAnimationFrame(tick);
        }
        function treeDragUpdate(x, y) {
            const d = _tdrag;
            if (!d || !d.active) return;
            d.lastX = x; d.lastY = y;
            if (d.ghost) { d.ghost.style.left = (x + 14) + 'px'; d.ghost.style.top = (y - 14) + 'px'; }
            const row = treeRowAt(x, y);
            const ref = row ? Number(row.dataset.ref) : null;
            if (ref !== d.hoverRef) {
                d.hoverRef = ref;
                clearTimeout(d.hoverTimer);
                d.hoverTimer = null;
                const n = ref !== null ? treeByRef[ref] : null;
                // наведение на строку с потомками: через паузу раскрыть ветку
                if (n && n.children && n.children.length && !expanded.has(ref)) {
                    d.hoverTimer = setTimeout(() => {
                        if (!_tdrag || !_tdrag.active || _tdrag.hoverRef !== ref) return;
                        expanded.add(ref);
                        renderTree();
                        treeDragMarkRows();
                    }, TREE_HOVER_EXPAND_MS);
                }
            }
            treeDragMarkRows();
        }
        function treeDragEnd(commit) {
            const d = _tdrag;
            if (!d) return;
            clearTimeout(d.timer);
            clearTimeout(d.hoverTimer);
            if (d.raf) cancelAnimationFrame(d.raf);
            if (d.ghost) d.ghost.remove();
            document.body.classList.remove('tree-dragging');
            const treeEl = document.getElementById('tree');
            try { treeEl.releasePointerCapture(d.pointerId); } catch (e) { emuWarn('swallow:treeEl.releasePointerCapture:11786', 'treeEl.releasePointerCapture: ' + _errText(e) + ''); }
            for (const row of treeEl.querySelectorAll('.drop-target,.drop-invalid,.dragging-src')) {
                row.classList.remove('drop-target', 'drop-invalid', 'dragging-src');
            }
            const wasActive = d.active;
            const target = d.hoverRef;
            const refs = d.refs;
            _tdrag = null;
            if (wasActive) _treeSuppressClickUntil = performance.now() + 500;
            if (wasActive && commit && target !== null && target !== undefined) {
                // проверяем с теми же правилами (d уже обнулён — временно восстановим)
                _tdrag = { refs };
                const ok = treeDropValid(target);
                _tdrag = null;
                if (ok) treeReparent(refs, target);
            }
        }
        async function treeReparent(refs, targetRef) {
            const r = await api('POST', '/api/reparent', { refs, parent: targetRef });
            if (!r || !r.ok) { notify((r && r.error) || t('mv_failed'), 'err'); return; }
            if (r.moved.length) {
                expanded.add(targetRef);
                const tr = await api('GET', '/api/tree');
                if (tr && tr.ok) {
                    treeData = tr.tree;
                    rebuildTreeIndex();
                    renderTree();
                }
                notify(t('mv_done', { n: r.moved.length }) + (r.skipped.length ? t('mv_skipped', { n: r.skipped.length }) : ''));
            } else {
                notify(t('mv_none'), 'err');
            }
        }
        function initTreeDragDrop() {
            const treeEl = document.getElementById('tree');
            if (!treeEl || treeEl._dndInit) return;
            treeEl._dndInit = true;
            treeEl.addEventListener('pointerdown', (e) => {
                if (e.pointerType === 'mouse' && e.button !== 0) return;
                if (e.target.closest && e.target.closest('.tree-arrow')) return;
                const row = e.target.closest ? e.target.closest('.tree-node') : null;
                if (!row) return;
                const ref = Number(row.dataset.ref);
                if (!treeCanDrag(ref)) return;
                if (_tdrag) treeDragEnd(false);
                _tdrag = { pointerId: e.pointerId, pointerType: e.pointerType, startX: e.clientX, startY: e.clientY,
                           lastX: e.clientX, lastY: e.clientY, srcRef: ref, active: false, refs: [], hoverRef: null };
                if (e.pointerType !== 'mouse') {
                    _tdrag.timer = setTimeout(() => { if (_tdrag && !_tdrag.active) treeDragStart(); }, TREE_LONGPRESS_MS);
                }
            });
            treeEl.addEventListener('pointermove', (e) => {
                const d = _tdrag;
                if (!d || e.pointerId !== d.pointerId) return;
                d.lastX = e.clientX; d.lastY = e.clientY;
                if (!d.active) {
                    const dist = Math.hypot(e.clientX - d.startX, e.clientY - d.startY);
                    if (d.pointerType === 'mouse') {
                        if (dist > TREE_MOUSE_START_PX) treeDragStart();
                    } else if (dist > TREE_MOVE_CANCEL_PX) {
                        treeDragEnd(false);            // палец поехал раньше долгого нажатия — это прокрутка
                    }
                    return;
                }
                e.preventDefault();
                treeDragUpdate(e.clientX, e.clientY);
            });
            const finish = (commit) => (e) => {
                const d = _tdrag;
                if (!d || e.pointerId !== d.pointerId) return;
                if (d.active && commit) { d.lastX = e.clientX; d.lastY = e.clientY; treeDragUpdate(e.clientX, e.clientY); }
                treeDragEnd(commit);
            };
            treeEl.addEventListener('pointerup', finish(true));
            treeEl.addEventListener('pointercancel', finish(false));
            // Пока тащим — не даём браузеру прокручивать список/вызывать меню
            treeEl.addEventListener('touchmove', (e) => { if (_tdrag && _tdrag.active && e.cancelable) e.preventDefault(); }, { passive: false });
            treeEl.addEventListener('contextmenu', (e) => { if (_tdrag) e.preventDefault(); });
            window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && _tdrag) treeDragEnd(false); });
        }
        if (document.getElementById('tree')) initTreeDragDrop();
        else document.addEventListener('DOMContentLoaded', initTreeDragDrop);

        function anyMatch(n) {
            if (!searchText) return true;
            if (n.name.toLowerCase().includes(searchText)) return true;
            return n.children.some(child => anyMatch(child));
        }

        function toggleExpand(ref) {
            if (expanded.has(ref)) {
                expanded.delete(ref);
            } else {
                expanded.add(ref);
            }
            renderTree();
        }

        function esc(s) {
            // Раньше падал на null/undefined — TypeError здесь обрывает
            if (s === null || s === undefined) return '';
            return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        }

        // ============ ВЫБОР ОБЪЕКТА ============
        // Строки Explorer в порядке отображения (для диапазона по Shift+клик).
        function visibleRefs() {
            const out = [];
            const walk = (n) => {
                const matches = !searchText || n.name.toLowerCase().includes(searchText) ||
                    n.cls.toLowerCase().includes(searchText);
                if (!(matches || (searchText && n.children.some(anyMatch)))) return;
                out.push(n.ref);
                if (expanded.has(n.ref)) n.children.forEach(walk);
            };
            treeData.forEach(walk);
            return out;
        }

        // opts.additive (Ctrl/⌘/режим мультивыбора) — добавить или убрать объект из выделения,
        // opts.range (Shift) — выделить всё от якоря до объекта в порядке Explorer.
        async function selectRef(ref, opts) {
            opts = opts || {};
            await saveCurrentScriptIfDirty(); // иначе несохранённые правки терялись при переключении объекта
            if (opts.range && selAnchorRef !== null && selAnchorRef !== ref) {
                const order = visibleRefs();
                const a = order.indexOf(selAnchorRef), b = order.indexOf(ref);
                if (a >= 0 && b >= 0) {
                    selectedRefs = new Set(order.slice(Math.min(a, b), Math.max(a, b) + 1));
                    selectedRef = ref;
                } else {
                    selectedRefs = new Set([ref]); selectedRef = ref; selAnchorRef = ref;
                }
            } else if (opts.additive) {
                if (selectedRefs.has(ref)) {
                    selectedRefs.delete(ref);
                    if (selectedRef === ref) selectedRef = selectedRefs.size ? [...selectedRefs].pop() : null;
                } else {
                    selectedRefs.add(ref);
                    selectedRef = ref;
                }
                selAnchorRef = ref;
                if (selectedRef === null) { deselect(); return; }
            } else {
                selectedRefs = new Set([ref]);
                selectedRef = ref;
                selAnchorRef = ref;
            }
            highlightSelected(selectedRef);
            renderTree();
            updateInventoryCount();
            const r = await api('GET', '/api/instance/' + selectedRef);
            if (!r.ok) return;
            renderProps(r);
        }

        // Раскрыть предков и прокрутить Explorer к объекту: новые объекты (ассистент, Add) добавляются в КОНЕЦ списка
        // родителя, а дочерние скрипты лежат в свёрнутом родителе — без этого их не видно.
        function revealRefs(refs, scrollTo) {
            for (const ref of refs) {
                let p = parentByRef[ref], guard = 0;
                while (p !== undefined && p !== null && p !== -1 && guard++ < 100) { expanded.add(p); p = parentByRef[p]; }
            }
            renderTree();
            const tgt = scrollTo !== undefined ? scrollTo : refs[0];
            const row = document.querySelector('#tree .tree-node[data-ref="' + tgt + '"]');
            if (row && row.scrollIntoView) row.scrollIntoView({ block: 'nearest' });
        }

        function deselect() {
            saveCurrentScriptIfDirty(); // fire-and-forget — иначе клик мимо объекта тоже терял правки
            selectedRef = null;
            selectedRefs = new Set();
            selAnchorRef = null;
            currentScriptRef = null;
            currentScriptOrigSource = null;
            highlightSelected(null);
            renderTree();
            updateInventoryCount();
            document.getElementById('tab-props').innerHTML = '<p style="color:#6b7280;font-size:12px;padding:8px">' + t('props_placeholder') + '</p>';
        }

        function toggleMultiSelect() {
            multiSelectMode = !multiSelectMode;
            const b = document.getElementById('multisel-btn');
            if (b) b.classList.toggle('active', multiSelectMode);
        }

        // ============ ПРОСЛУШАТЬ ЗВУК ИЗ EXPLORER (вне Play) ============
        let _editorPreviewAudio = null;
        let _editorPreviewBtn = null;
        let _editorPreviewSoundId = null;
        function _stopEditorPreview() {
            if (_editorPreviewAudio) { _editorPreviewAudio.pause(); _editorPreviewAudio.currentTime = 0; }
            if (_editorPreviewBtn) _editorPreviewBtn.textContent = '🔊 ' + t('preview_listen');
            _editorPreviewBtn = null;
            _editorPreviewSoundId = null;
        }
        function buildSoundPreviewRow(soundId, playbackSpeed, pitchOctave) {
            playbackSpeed = playbackSpeed || 1;
            pitchOctave = pitchOctave || 0;
            const row = document.createElement('div');
            row.style.cssText = 'margin-bottom:4px;padding:4px;background:#111827;border-radius:4px';
            const btn = document.createElement('button');
            btn.textContent = '🔊 ' + t('preview_listen');
            btn.style.cssText = 'width:100%;padding:6px;font-size:12px;background:#2563eb;color:#fff;border:none;border-radius:4px';
            const url = rbxAssetIdToProxyUrl(soundId);
            btn.onclick = () => {
                if (!url) { notify(t('notify_error'), 'err'); return; }
                // Повторное нажатие на ТОТ ЖЕ звук, пока он играет — это
                // "Стоп", а не перезапуск с начала.
                if (_editorPreviewSoundId === soundId && _editorPreviewAudio && !_editorPreviewAudio.paused) {
                    _stopEditorPreview();
                    return;
                }
                _stopEditorPreview();
                // Раньше тут был голый <audio> без PlaybackSpeed/Octave —
                // прослушивание из Explorer звучало не так, как в самой
                // игре (например, ускоренные/питчнутые треки играли
                // обычным голосом). RobloxSoundElement — тот же движок,
                // что и в Play, с тем же объединённым стретч+ресемпл.
                if (!_editorPreviewAudio) _editorPreviewAudio = new RobloxSoundElement();
                _editorPreviewAudio.src = url;
                _editorPreviewAudio.playbackRate = playbackSpeed;
                _editorPreviewAudio.pitchOctave = pitchOctave;
                // RobloxSoundElement — не настоящий <audio>, у него нет
                // IDL-свойства onended, только addEventListener (как и у
                // остальных Sound-обёрток в этом файле) — прямое
                // "audio.onended = fn" тут молча ничего не делает.
                _editorPreviewAudio.addEventListener('ended', () => _stopEditorPreview());
                _editorPreviewAudio.play().catch((e) => { notify(String(e.message || e), 'err'); _stopEditorPreview(); });
                _editorPreviewBtn = btn;
                _editorPreviewSoundId = soundId;
                btn.textContent = '⏸ ' + t('preview_stop');
            };
            row.appendChild(btn);
            return row;
        }

        // ============ СВОЙСТВА ============
        function renderProps(r) {
            const SCLS = ['Script', 'LocalScript', 'ModuleScript'];
            const panel = document.getElementById('tab-props');
            panel.innerHTML = '';

            const hdr = document.createElement('div');
            hdr.className = 'prop-header';
            if (r.icon) {
                const img = document.createElement('img');
                img.style.cssText = 'width:32px;height:32px;object-fit:contain;background:#374151;border-radius:4px;margin-bottom:4px;display:block';
                img.src = r.icon;
                hdr.appendChild(img);
            }
            const cls = document.createElement('div');
            cls.className = 'prop-cls';
            cls.textContent = r.cls;
            // Имя инстанса — раньше шапка Properties показывала ТОЛЬКО класс
            if (r.props && r.props.Name && r.props.Name !== r.cls) {
                const nameEl = document.createElement('div');
                nameEl.className = 'prop-name-title';
                nameEl.style.cssText = 'font-weight:bold;font-size:13px;color:#e5e7eb;word-break:break-word';
                nameEl.textContent = r.props.Name;
                hdr.appendChild(nameEl);
                cls.style.cssText = 'font-size:11px;color:#9ca3af';
            }
            const ref = document.createElement('div');
            ref.className = 'prop-ref';
            ref.textContent = 'ref ' + r.ref;
            hdr.appendChild(cls);
            hdr.appendChild(ref);
            panel.appendChild(hdr);

            // Прослушать звук прямо из Explorer, вне Play — раньше это
            if (r.cls === 'Sound' && r.props.SoundId) {
                const rawSpeed = r.props.PlaybackSpeed != null ? r.props.PlaybackSpeed
                    : (r.props.Pitch != null ? r.props.Pitch : 1);
                panel.appendChild(buildSoundPreviewRow(r.props.SoundId, rawSpeed, r.pitchOctave || 0));
            }

            // Position, Rotation, Size
            const specialProps = ['Position', 'Rotation', 'Size'];
            for (const propName of specialProps) {
                if (r.props[propName]) {
                    addVector3Prop(panel, r.ref, propName, r.props[propName]);
                }
            }

            // Остальные свойства
            for (const [k, v] of Object.entries(r.props).sort()) {
                if (k === 'Source' || k === 'CFrame' || specialProps.includes(k) || k === '_assets') {
                    continue;
                }
                addPropRow(panel, r.ref, k, v);
            }

            if (SCLS.includes(r.cls)) {
                // Script выполняется на сервере, LocalScript — на клиенте,
                const badge = SCRIPT_BADGES[r.cls] || SCRIPT_BADGES.Script;
                document.getElementById('script-name').innerHTML =
                    '<span style="color:' + badge.color + '">' + badge.icon + ' ' + badge.label + '</span>'
                    + ' — ' + esc(r.cls) + ': ' + esc(r.props.Name || '?');
                if (cmEditor) cmEditor.setValue(r.props.Source || '');
                currentScriptRef = r.ref;
                currentScriptOrigSource = r.props.Source || '';
                switchTab('script');
                refreshCM();
            } else {
                currentScriptRef = null;
                currentScriptOrigSource = null;
                switchTab('props');
            }
        }

        function addVector3Prop(panel, ref, propName, value) {
            const container = document.createElement('div');
            container.style.cssText = 'margin-bottom:4px;padding:4px;background:#111827;border-radius:4px';

            const label = document.createElement('div');
            label.style.cssText = 'font-size:calc(11px*var(--fs));color:#9ca3af;margin-bottom:4px;font-weight:bold';
            label.textContent = propName;
            container.appendChild(label);

            const coords = ['x', 'y', 'z'];
            const colors = ['#ef4444', '#22c55e', '#3b82f6'];

            const row = document.createElement('div');
            row.style.cssText = 'display:grid;grid-template-columns:repeat(auto-fit,minmax(calc(96px*var(--fs)),1fr));gap:4px';

            coords.forEach((coord, i) => {
                const inputGroup = document.createElement('div');
                inputGroup.style.cssText = 'flex:1;display:flex;align-items:center;gap:2px';

                const coordLabel = document.createElement('span');
                coordLabel.style.cssText = 'font-size:calc(11px*var(--fs));color:' + colors[i] + ';font-weight:bold;min-width:12px';
                coordLabel.textContent = coord.toUpperCase();

                const input = document.createElement('input');
                input.className = 'prop-val';
                input.type = 'number';
                input.step = propName === 'Rotation' ? '1' : '0.1';
                input.value = typeof value === 'object' ? (Math.round((value[coord] || 0) * 10000) / 10000) : 0; // без хвоста float — влезает в поле
                input.inputMode = 'decimal';
                input.style.cssText = 'min-width:0';

                input.onchange = async () => {
                    const newValue = { ...value };
                    newValue[coord] = parseFloat(input.value) || 0;
                    // ВАЖНО: value — общий объект для всех трёх инпутов
                    value[coord] = newValue[coord];
                    await api('POST', '/api/instance/' + ref, {
                        prop: propName,
                        value: newValue
                    });
                    reloadScene();
                };

                inputGroup.appendChild(coordLabel);
                inputGroup.appendChild(input);
                row.appendChild(inputGroup);
            });

            container.appendChild(row);
            panel.appendChild(container);
        }

        // Экспорт ассета (меш/текстура/звук) по долгому нажатию на строку свойства: берём тот же файл, что и
        // игра (/api/asset-proxy, он кешируется на диск), и отдаём через «Поделиться» или обычным скачиванием.
        const ASSET_PROP_RE = /(mesh\s*id|texture\s*id|sound\s*id|animation\s*id|image|colormap|normalmap|texture)$/i;
        async function exportAssetById(id, label) {
            try {
                notify(t('exp_asset_start', { label: label, id: id }));
                // Приложение Android: системный диалог «Сохранить как» (сам выбираешь папку) через мост —
                // та же схема, что у экспорта .rbxl. WebView сам файл скачать/поделиться не умеет.
                if (window.AndroidBridge && typeof window.AndroidBridge.getDataDir === 'function' &&
                    typeof window.AndroidBridge.exportRbxlFile === 'function') {
                    const er = await api('POST', '/api/asset-export', { id });
                    if (!er || !er.ok) { notify(t('exp_asset_fail', { id: id, err: (er && er.error) || t('exp_generic_err') }), 'warn'); return; }
                    window.AndroidBridge.exportRbxlFile(er.path, er.name);
                    return;
                }
                const r = await fetch('/api/asset-proxy?id=' + id);
                if (!r.ok) { notify(t('exp_asset_fail_http', { id: id, status: r.status }), 'warn'); return; }
                const blob = await r.blob();
                const head = new Uint8Array(await blob.slice(0, 16).arrayBuffer());
                const txt = String.fromCharCode.apply(null, head);
                let ext = '.bin';
                if (txt.startsWith('version ')) ext = '.mesh';
                else if (head[0] === 0x89 && txt.slice(1, 4) === 'PNG') ext = '.png';
                else if (txt.startsWith('OggS')) ext = '.ogg';
                else if (head[0] === 0xFF && head[1] === 0xD8) ext = '.jpg';
                const name = 'asset_' + id + ext;
                const file = new File([blob], name, { type: blob.type || 'application/octet-stream' });
                if (navigator.canShare && navigator.canShare({ files: [file] })) {
                    try { await navigator.share({ files: [file], title: name }); notify(t('exp_shared', { name: name, kb: Math.round(blob.size / 1024) })); return; }
                    catch (e) { if (e && e.name === 'AbortError') return; /* иначе — обычное скачивание */ }
                }
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob); a.download = name;
                document.body.appendChild(a); a.click(); a.remove();
                setTimeout(() => URL.revokeObjectURL(a.href), 10000);
                notify(t('exp_saved', { name: name, kb: Math.round(blob.size / 1024) }));
            } catch (e) {
                notify(t('exp_error', { msg: (e && e.message ? e.message : e) }), 'warn');
            }
        }
        function attachAssetExport(row, k, v) {
            if (typeof v !== 'string' || !ASSET_PROP_RE.test(k)) return;
            const m = /(\d{5,})/.exec(v);
            if (!m) return;
            let timer = null, sx = 0, sy = 0;
            const cancel = () => { if (timer) { clearTimeout(timer); timer = null; } };
            const start = (e) => {
                const p = e.touches ? e.touches[0] : e;
                sx = p.clientX; sy = p.clientY; cancel();
                timer = setTimeout(() => { timer = null; exportAssetById(m[1], k); }, 700);
            };
            const move = (e) => {
                const p = e.touches ? e.touches[0] : e;
                if (Math.abs(p.clientX - sx) > 10 || Math.abs(p.clientY - sy) > 10) cancel();
            };
            row.addEventListener('touchstart', start, { passive: true });
            row.addEventListener('touchmove', move, { passive: true });
            row.addEventListener('touchend', cancel); row.addEventListener('touchcancel', cancel);
            row.addEventListener('mousedown', start); row.addEventListener('mousemove', move);
            row.addEventListener('mouseup', cancel); row.addEventListener('mouseleave', cancel);
            row.title = (row.title ? row.title + ' — ' : '') + t('exp_longpress', { id: m[1] });
        }

        function addPropRow(panel, ref, k, v) {
            const row = document.createElement('div');
            row.className = 'prop-row';
            attachAssetExport(row, k, v);

            const nm = document.createElement('span');
            nm.className = 'prop-name';
            nm.textContent = k;
            nm.title = k;
            row.appendChild(nm);

            if (typeof v === 'boolean') {
                const cb = document.createElement('input');
                cb.type = 'checkbox';
                cb.className = 'prop-bool';
                cb.checked = v;
                cb.onchange = () => setProp(ref, k, cb.checked);
                row.appendChild(cb);
            } else if (v && typeof v === 'object' && 'r' in v && 'g' in v && 'b' in v) {
                const pr = document.createElement('div');
                pr.className = 'prop-color-preview';
                const hex = '#' + [v.r, v.g, v.b].map(x =>
                    Math.min(255, Math.max(0, Math.round(x * 255))).toString(16).padStart(2, '0')
                ).join('');
                pr.style.background = hex;
                pr.onclick = () => {
                    const inp = document.createElement('input');
                    inp.type = 'color';
                    inp.value = hex;
                    inp.onchange = () => {
                        const color = {
                            r: parseInt(inp.value.slice(1, 3), 16) / 255,
                            g: parseInt(inp.value.slice(3, 5), 16) / 255,
                            b: parseInt(inp.value.slice(5, 7), 16) / 255
                        };
                        setProp(ref, k, color);
                        pr.style.background = inp.value;
                        reloadScene();
                    };
                    inp.click();
                };
                row.appendChild(pr);
            } else if (typeof v === 'number' && ['Transparency', 'Reflectance', 'BackgroundTransparency', 'TextTransparency', 'ImageTransparency'].includes(k)) {
                // Ползунок 0..1 + числовое поле
                const rng = document.createElement('input');
                rng.type = 'range'; rng.min = 0; rng.max = 1; rng.step = 0.01;
                rng.value = v; rng.className = 'prop-range';
                const num = document.createElement('input');
                num.className = 'prop-val prop-num';
                num.type = 'number'; num.step = '0.01'; num.inputMode = 'decimal';
                num.value = Math.round(v * 1000) / 1000;
                const commit = () => {
                    let x = parseFloat(num.value);
                    if (isNaN(x)) return;
                    x = Math.max(0, Math.min(1, x));
                    rng.value = x; num.value = x;
                    setProp(ref, k, x).then(() => { if (k === 'Transparency' || k === 'Reflectance') reloadScene(); });
                };
                rng.oninput = () => { num.value = rng.value; };
                rng.onchange = () => { num.value = rng.value; commit(); };
                num.onchange = commit;
                row.appendChild(rng);
                row.appendChild(num);
            } else {
                const inp = document.createElement('input');
                inp.className = 'prop-val';
                inp.value = typeof v === 'object' ? JSON.stringify(v).slice(0, 80) : String(v ?? '');
                inp.onchange = () => {
                    let val = inp.value;
                    try { val = JSON.parse(val); } catch (e) { emuWarn('swallow:val:12270', 'val: ' + _errText(e) + ''); }
                    setProp(ref, k, val);
                };
                row.appendChild(inp);
            }
            panel.appendChild(row);
        }

        async function setProp(ref, prop, val) {
            await api('POST', '/api/instance/' + ref, {
                prop: prop,
                value: val
            });
            if (prop !== 'Source') _psSchedule();
        }

        async function saveScript() {
            if (selectedRef === null) {
                notify(t('notify_script_none'), 'warn');
                return;
            }
            if (!cmEditor) {
                notify(t('notify_editor_unavailable'), 'err');
                return;
            }
            const src = cmEditor.getValue();
            await api('POST', '/api/instance/' + selectedRef, {
                prop: 'Source',
                value: src
            });
            currentScriptOrigSource = src; // синхронизируем трекер "грязности" — см. saveCurrentScriptIfDirty
            notify(t('notify_script_saved'));
        }

        function switchTab(t) {
            document.querySelectorAll('.tab').forEach((el, i) => {
                const tabNames = ['props', 'script'];
                el.classList.toggle('active', tabNames[i] === t);
            });
            document.getElementById('tab-props').style.display = t === 'props' ? '' : 'none';
            document.getElementById('tab-script').style.display = t === 'script' ? 'flex' : 'none';
            if (t === 'script') refreshCM();
        }

        // ============ БЫСТРОЕ ДОБАВЛЕНИЕ ============
        async function quickAdd(cls) {
            const name = 'New' + cls;
            let parent = selectedRef;
            if (parent === null) {
                const findWs = ns => {
                    for (const n of ns) {
                        if (n.cls === 'Workspace') return n.ref;
                        const c = findWs(n.children);
                        if (c !== null) return c;
                    }
                    return null;
                };
                parent = findWs(treeData) ?? -1;
            }
            const r = await api('PUT', '/api/instance', {
                class: cls,
                name: name,
                parent: parent
            });
            if (r.ok) {
                notify(t('notify_quickadd', { cls: cls }));
                loadTree();
                _psSchedule();
            } else {
                notify(r.error || t('notify_error'), 'err');
            }
        }

        // ============ ФАЙЛОВЫЙ БРАУЗЕР ============
        let _fbMode = 'open';
        let _fbPath = '';

        // ============ СОХРАНЕНИЕ "КАК" ============
        async function openFileBrowser(mode) {
            _fbMode = mode;

            // ОТКРЫТИЕ — см. pickRbxlFileForOpen().
            if (mode === 'open') {
                pickRbxlFileForOpen();
                return;
            }

            showModal(saveAsModal());
        }

        function saveAsModal() {
            return '<h3>' + t('fb_saveas_title') + '</h3>' +
                '<input id="fb-name" placeholder="' + t('fb_name_ph') + '" value="place.rbxl">' +
                '<div class="modal-row">' +
                '<button onclick="confirmSaveAs()" style="background:#065f46">' + t('btn_save') + '</button>' +
                '<button onclick="closeModal()">' + t('btn_cancel') + '</button>' +
                '</div>';
        }

        async function confirmSaveAs() {
            const nm = document.getElementById('fb-name');
            const name = (nm && nm.value.trim()) || 'place.rbxl';
            closeModal();

            if (window.AndroidBridge && typeof window.AndroidBridge.getDataDir === 'function' &&
                typeof window.AndroidBridge.exportRbxlFile === 'function') {
                // Android: сервер сначала пишет .rbxl во временный файл в
                const dataDir = window.AndroidBridge.getDataDir();
                const tempPath = dataDir + '/export_' + name.replace(/[^A-Za-z0-9._-]/g, '_');
                const r = await api('POST', '/api/save', { path: tempPath });
                if (!r.ok) {
                    notify(r.error || t('notify_error'), 'err');
                    return;
                }
                window.AndroidBridge.exportRbxlFile(tempPath, name);
                return;
            }

            // Браузер: обычная нативная загрузка файла — вызывается сразу
            const a = document.createElement('a');
            a.href = '/api/save/download?name=' + encodeURIComponent(name);
            a.download = name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            notify('💾 ' + name);
        }

        // Вызывается из Kotlin после того как пользователь выбрал место
        // через SAF и файл скопирован (или отменил диалог / произошла ошибка).
        window.onAndroidFileExported = function (ok) {
            notify(ok ? t('notify_saved_simple') : t('notify_save_cancelled'), ok ? undefined : 'err');
        };

        // ============ RBXM: ЭКСПОРТ ВЫБРАННЫХ ОБЪЕКТОВ / ИМПОРТ МОДЕЛИ ============
        // Выбранные объекты в порядке Explorer (сервер сам отбрасывает вложенные дубли).
        function selectedRefsInTreeOrder() {
            const order = new Map();
            (function walk(nodes) { nodes.forEach(n => { order.set(n.ref, order.size); walk(n.children || []); }); })(treeData);
            return [...selectedRefs].sort((a, b) => (order.get(a) ?? 0) - (order.get(b) ?? 0));
        }

        function exportSelectedRbxm() {
            if (!selectedRefs.size) { notify(t('notify_not_selected'), 'warn'); return; }
            let base = 'model';
            if (selectedRefs.size === 1 && treeByRef[selectedRef]) base = treeByRef[selectedRef].name || base;
            base = base.replace(/[\\/:*?"<>|]+/g, '_').trim() || 'model';
            showModal('<h3>' + t('rbxm_export_title', { n: selectedRefs.size }) + '</h3>' +
                '<input id="rbxm-name" placeholder="' + t('fb_name_ph') + '" value="' + esc(base) + '.rbxm">' +
                '<div class="modal-row">' +
                '<button onclick="confirmExportRbxm()" style="background:#065f46">' + t('btn_save') + '</button>' +
                '<button onclick="closeModal()">' + t('btn_cancel') + '</button>' +
                '</div>');
        }

        async function confirmExportRbxm() {
            const nm = document.getElementById('rbxm-name');
            let name = (nm && nm.value.trim()) || 'model.rbxm';
            if (!/\.rbxm$/i.test(name)) name += '.rbxm';
            closeModal();
            const refs = selectedRefsInTreeOrder();

            if (window.AndroidBridge && typeof window.AndroidBridge.getDataDir === 'function' &&
                typeof window.AndroidBridge.exportRbxlFile === 'function') {
                // Android: как в confirmSaveAs — файл во временную папку приложения, дальше SAF.
                const tempPath = window.AndroidBridge.getDataDir() + '/export_' + name.replace(/[^A-Za-z0-9._-]/g, '_');
                const r = await api('POST', '/api/export/rbxm', { refs: refs, path: tempPath });
                if (!r.ok) { notify(r.error || t('notify_error'), 'err'); return; }
                if (r.warnings && r.warnings.length) notify(t('notify_rbxm_warn', { msg: r.warnings[0] }), 'warn');
                window.AndroidBridge.exportRbxlFile(tempPath, name);
                return;
            }

            // Браузер: сначала fetch (чтобы показать ошибку, а не скачать JSON под видом .rbxm), затем загрузка.
            try {
                const resp = await fetch('/api/export/rbxm?refs=' + refs.join(',') + '&name=' + encodeURIComponent(name));
                if (!resp.ok) {
                    let msg = t('notify_error');
                    try { msg = (await resp.json()).error || msg; } catch (e) { emuWarn('swallow:msg:12448', 'msg: ' + _errText(e) + ''); }
                    notify(msg, 'err');
                    return;
                }
                const blob = await resp.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = name;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                setTimeout(() => URL.revokeObjectURL(url), 10000);
                notify(t('notify_rbxm_exported', { n: resp.headers.get('X-Rbxm-Count') || refs.length }));
                let warns = [];
                try { warns = JSON.parse(decodeURIComponent(resp.headers.get('X-Rbxm-Warnings') || '[]')); } catch (e) { emuWarn('swallow:warns:12463', 'warns: ' + _errText(e) + ''); }
                if (warns.length) notify(t('notify_rbxm_warn', { msg: warns[0] }), 'warn');
            } catch (err) {
                console.error('Экспорт rbxm:', err);
                notify(t('notify_error'), 'err');
            }
        }

        // Куда вставлять: в выбранный контейнер (Model/Folder/объект с детьми), иначе сервер берёт Workspace.
        function rbxmImportParent() {
            const n = selectedRef !== null ? treeByRef[selectedRef] : null;
            if (n && ((n.children && n.children.length) || ['Model', 'Folder', 'Workspace'].includes(n.cls))) return n.ref;
            return null;
        }

        async function afterRbxmImport(r) {
            if (!r.ok) { notify(r.error || t('notify_error'), 'err'); return; }
            await loadTree();
            const roots = r.roots || [];
            if (roots.length) {
                // раскрыть путь до новых объектов и выделить их все
                let par = parentByRef[roots[0]];
                while (par !== undefined && par !== null && par !== -1) { expanded.add(par); par = parentByRef[par]; }
                selectedRefs = new Set(roots);
                selectedRef = roots[roots.length - 1];
                selAnchorRef = selectedRef;
                highlightSelected(selectedRef);
                renderTree();
                updateInventoryCount();
                const pr = await api('GET', '/api/instance/' + selectedRef);
                if (pr.ok) renderProps(pr);
            }
            notify(t('notify_rbxm_imported', { n: r.count }));
            if (r.warnings && r.warnings.length) notify(t('notify_rbxm_warn', { msg: r.warnings[0] }), 'warn');
        }

        function importRbxm() {
            if (window.AndroidBridge && typeof window.AndroidBridge.pickRbxlFile === 'function') {
                // Тот же SAF-пикер (type */*), но результат уходит в /api/import/rbxm — см. onAndroidFileImported.
                window._rbxmImportPending = true;
                window.AndroidBridge.pickRbxlFile();
                return;
            }
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = '.rbxm';
            fileInput.style.display = 'none';
            document.body.appendChild(fileInput);
            fileInput.addEventListener('change', async function (event) {
                const file = event.target.files[0];
                document.body.removeChild(fileInput);
                if (!file) return;
                const formData = new FormData();
                formData.append('file', file);
                const parent = rbxmImportParent();
                if (parent !== null) formData.append('parent', String(parent));
                try {
                    const resp = await fetch('/api/import/rbxm/upload', { method: 'POST', body: formData });
                    await afterRbxmImport(await resp.json());
                } catch (err) {
                    console.error('Импорт rbxm:', err);
                    notify(t('notify_error'), 'err');
                }
            });
            fileInput.click();   // синхронно, в рамках клика — иначе браузер откажет
        }

        // Открытие .rbxl/.rbxlx нативным способом ОС вместо /api/browse.
        function pickRbxlFileForOpen() {
            // ВАЖНО: здесь раньше стояли блокирующие alert() между кликом
            console.log('pickRbxlFileForOpen вызвана. AndroidBridge=' +
                (typeof window.AndroidBridge) +
                ', pickRbxlFile=' +
                (window.AndroidBridge ? typeof window.AndroidBridge.pickRbxlFile : 'n/a'));

            if (window.AndroidBridge && typeof window.AndroidBridge.pickRbxlFile === 'function') {
                window.AndroidBridge.pickRbxlFile();
                return;
            }

            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = '.rbxl,.rbxlx';
            fileInput.style.display = 'none';
            document.body.appendChild(fileInput);

            fileInput.addEventListener('change', function (event) {
                const file = event.target.files[0];
                if (!file) {
                    document.body.removeChild(fileInput);
                    return;
                }

                console.log('выбран файл ' + file.name + ', размер ' + file.size + ' байт. Отправляю на /api/open/upload...');

                const formData = new FormData();
                formData.append('file', file);

                fetch('/api/open/upload', { method: 'POST', body: formData })
                    .then(response => response.json())
                    .then(data => {
                        document.body.removeChild(fileInput);
                        if (data.ok) {
                            window._rbxOrigin = null;
                            window._startMode = false;
                            hideStartScreen();
                            notify(t('notify_loaded_count', { n: data.count }));
                            loadTree();
                        } else {
                            notify(data.error || t('notify_error'), 'err');
                        }
                    })
                    .catch(err => {
                        document.body.removeChild(fileInput);
                        console.error('Ошибка загрузки файла:', err);
                        notify(t('notify_error'), 'err');
                    });
            });

            // Вызывается сразу, синхронно, в рамках того же клика — без
            // alert()/await между ними, иначе браузер молча откажет.
            fileInput.click();
        }

        // Вызывается из Kotlin (MainActivity.AndroidBridge) после того как
        window.onAndroidFileImported = async function (path, errMsg, shownName) {
            const wasRbxmImport = !!window._rbxmImportPending;
            window._rbxmImportPending = false;
            if (!path) {
                notify(errMsg || t('notify_error'), 'err');
                return;
            }
            if (wasRbxmImport) {
                const parent = rbxmImportParent();
                await afterRbxmImport(await api('POST', '/api/import/rbxm', { path: path, parent: parent }));
                return;
            }
            const r = await api('POST', '/api/open', { path: path, name: shownName || '' });
            if (r.ok) {
                window._rbxOrigin = null;
                window._startMode = false;
                hideStartScreen();
                notify(t('notify_loaded_count', { n: r.count }));
                loadTree();
            } else {
                notify(r.error || t('notify_error'), 'err');
            }
        };

        async function doSave(path) {
            const r = await api('POST', '/api/save', { path: path });
            if (!r.ok) { notify(r.error || t('notify_error'), 'err'); return; }
            // Android: открытый файл — это внутренняя копия (imported_*.rbxl). Переписываем ещё и оригинал, выбранный в пикере.
            try {
                if (window.AndroidBridge && typeof window.AndroidBridge.writeBackToSource === 'function') {
                    const wb = String(window.AndroidBridge.writeBackToSource(r.path || path));
                    if (wb === 'ok') { notify(t('notify_saved_original')); return; }
                    if (wb.indexOf('err:') === 0) {
                        notify(t('notify_save_original_failed', { err: wb.slice(4) }), 'err');
                        openFileBrowser('save');   // оригинал не перезаписать (нет права записи) — предлагаем «Сохранить как»
                        return;
                    }
                }
            } catch (e) { console.error('writeBackToSource:', e); }
            notify('💾 ' + r.path);
        }

        async function newProject(template, fromStart) {
            // Создаёт пустую сцену на сервере (набор стандартных сервисов
            if (!fromStart && !window._startMode && !confirm(t('confirm_discard_unsaved'))) return;
            const r = await api('POST', '/api/new', { template: (template === 'empty' ? 'empty' : 'baseplate') });
            if (!r.ok) {
                notify(r.error || t('notify_error'), 'err');
                return;
            }
            window._startMode = false;
            hideStartScreen();
            window._rbxOrigin = null;
            selectedRef = null;
            selectedRefs = new Set();
            expanded.clear();
            window._avatarMeshCache = {};
            await loadTree();
            notify(t('notify_new_scene'));
        }

        async function saveFile() {
            const r = await api('GET', '/api/status');
            if (!r.file) {
                openFileBrowser('save');
                return;
            }
            doSave(r.file);
        }

        // ============ ДИАЛОГИ ============

        // === Меню «Файл» (как в строке меню macOS): действия с файлами и плейсами одним выпадающим списком.
        // Рисуется position:fixed поверх страницы — панель инструментов прокручивается по горизонтали
        // (overflow), внутри неё выпадающее меню обрезалось бы.
        function closeFileMenu() {
            const m = document.getElementById('file-menu');
            if (m) m.remove();
            const b = document.getElementById('file-menu-btn');
            if (b) b.classList.remove('open');
            document.removeEventListener('pointerdown', _fileMenuOutside, true);
        }

        function _fileMenuOutside(e) {
            const m = document.getElementById('file-menu');
            const b = document.getElementById('file-menu-btn');
            if (m && !m.contains(e.target) && !(b && b.contains(e.target))) closeFileMenu();
        }

        function toggleFileMenu(ev) {
            if (ev) ev.stopPropagation();
            if (document.getElementById('file-menu')) { closeFileMenu(); return; }
            if (!document.getElementById('file-menu-css')) {
                const st = document.createElement('style');
                st.id = 'file-menu-css';
                st.textContent =
                    '#file-menu{position:fixed;z-index:150;min-width:260px;max-width:92vw;padding:6px;border-radius:12px;' +
                    'background:rgba(40,44,56,.92);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);' +
                    'border:1px solid rgba(255,255,255,.12);box-shadow:0 14px 40px rgba(0,0,0,.5);color:#e8ebf3;' +
                    'font:14px/1.2 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;animation:fmpop .12s ease-out}' +
                    '@keyframes fmpop{from{opacity:0;transform:translateY(-4px) scale(.98)}to{opacity:1;transform:none}}' +
                    '#file-menu .fm-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:7px;cursor:pointer;white-space:nowrap}' +
                    '#file-menu .fm-item:hover,#file-menu .fm-item:active{background:#2f6bff;color:#fff}' +
                    '#file-menu .fm-item.dis{opacity:.4;cursor:default}' +
                    '#file-menu .fm-item.dis:hover{background:transparent;color:inherit}' +
                    '#file-menu .fm-ico{width:20px;text-align:center}' +
                    '#file-menu .fm-lbl{flex:1}' +
                    '#file-menu .fm-hint{opacity:.55;font-size:12px;margin-left:18px}' +
                    '#file-menu .fm-sep{height:1px;margin:5px 8px;background:rgba(255,255,255,.14)}' +
                    '#file-menu-btn.open{background:#2f6bff !important}';
                document.head.appendChild(st);
            }
            const fromRoblox = !!window._rbxOrigin;   // Save — только для файлов: плейс из Roblox сохраняем через «Сохранить как»
            const items = [
                { ico: '🆕', k: 'menu_new', act: () => newProject() },
                'sep',
                { ico: '📂', k: 'menu_open_file', hint: 'Ctrl+O', act: () => openFileBrowser('open') },
                { ico: '⬇', k: 'menu_open_roblox', act: () => showStartScreen(false) },
                'sep',
                { ico: '💾', k: 'menu_save', hint: fromRoblox ? t('menu_save_note') : 'Ctrl+S', dis: fromRoblox, act: () => saveFile() },
                { ico: '💾', k: 'menu_save_as', hint: '⇧Ctrl+S', act: () => openFileBrowser('save') },
                'sep',
                { ico: '📥', k: 'menu_import', act: () => importRbxm() },
                { ico: '📤', k: 'menu_export', act: () => exportSelectedRbxm() },
            ];
            const menu = document.createElement('div');
            menu.id = 'file-menu';
            menu.setAttribute('role', 'menu');
            for (const it of items) {
                if (it === 'sep') {
                    const s = document.createElement('div'); s.className = 'fm-sep'; menu.appendChild(s); continue;
                }
                const row = document.createElement('div');
                row.className = 'fm-item' + (it.dis ? ' dis' : '');
                row.setAttribute('role', 'menuitem');
                row.innerHTML = '<span class="fm-ico">' + it.ico + '</span><span class="fm-lbl">' + esc(t(it.k)) +
                    '</span>' + (it.hint ? '<span class="fm-hint">' + esc(it.hint) + '</span>' : '');
                if (!it.dis) row.addEventListener('click', () => { closeFileMenu(); it.act(); });
                menu.appendChild(row);
            }
            document.body.appendChild(menu);
            const btn = document.getElementById('file-menu-btn');
            if (btn) {
                btn.classList.add('open');
                const r = btn.getBoundingClientRect();
                const w = menu.offsetWidth;
                menu.style.top = (r.bottom + 6) + 'px';
                menu.style.left = Math.max(6, Math.min(r.left, window.innerWidth - w - 6)) + 'px';
            }
            document.addEventListener('pointerdown', _fileMenuOutside, true);
        }

        function showAddDialog() {
            const ALL_CLS = [
                'Part', 'WedgePart', 'SpherePart', 'MeshPart', 'Model', 'Folder',
                'Script', 'LocalScript', 'ModuleScript', 'RemoteEvent', 'RemoteFunction',
                'BindableEvent', 'BindableFunction', 'ScreenGui', 'Frame', 'TextLabel',
                'TextButton', 'TextBox', 'ImageLabel', 'ImageButton', 'Sound',
                'ParticleEmitter', 'Attachment', 'Fire', 'Smoke', 'PointLight', 'SpotLight',
                'SurfaceLight', 'NumberValue', 'StringValue', 'BoolValue', 'IntValue',
                'Animation', 'Tool', 'Camera'
            ].sort();
            if (!document.getElementById('add-grid-css')) {
                const st = document.createElement('style');
                st.id = 'add-grid-css';
                st.textContent =
                    '#add-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:6px;max-height:44vh;overflow-y:auto;padding:2px}' +
                    '#add-grid .add-tile{display:flex;flex-direction:column;align-items:center;gap:4px;padding:8px 4px;border-radius:8px;' +
                    'background:#374151;border:2px solid transparent;cursor:pointer;text-align:center;font-size:11px;line-height:1.15;word-break:break-word}' +
                    '#add-grid .add-tile:hover{background:#4b5563}' +
                    '#add-grid .add-tile.sel{border-color:#3b82f6;background:#1e3a8a}' +
                    '#add-grid .add-tile img{width:28px;height:28px;image-rendering:auto}' +
                    '#add-grid .add-tile .ph{width:28px;height:28px}';
                document.head.appendChild(st);
            }
            showModal(
                '<h3>' + t('tb_add') + '</h3>' +
                '<input id="add-search" placeholder="' + _escAttr(t('add_search_ph')) + '" oninput="addFilterClasses()">' +
                '<div id="add-grid">' + ALL_CLS.map(c =>
                    '<div class="add-tile' + (c === 'Part' ? ' sel' : '') + '" data-cls="' + c + '" onclick="addPickClass(\'' + c + '\')">' +
                    '<div class="ph"></div><span>' + c + '</span></div>').join('') + '</div>' +
                '<input id="add-cls" type="hidden" value="Part">' +
                '<input id="add-name" placeholder="' + t('add_name_ph') + '" value="NewPart" oninput="this.dataset.edited=1">' +
                '<p style="font-size:11px;color:#9ca3af;margin-top:4px">' + t('add_parent_label') + ' ' +
                (selectedRef !== null ? 'ref ' + selectedRef : 'Workspace') + '</p>' +
                '<div class="modal-row">' +
                '<button onclick="doAdd()" style="background:#065f46">' + t('btn_add') + '</button>' +
                '<button onclick="closeModal()">' + t('btn_cancel') + '</button>' +
                '</div>'
            );
            // иконки подгружаем после показа окна (один запрос; кэшируем на время сессии)
            const fill = (icons) => {
                document.querySelectorAll('#add-grid .add-tile').forEach(el => {
                    const src = icons[el.dataset.cls];
                    const ph = el.querySelector('.ph');
                    if (src && ph) {
                        const img = document.createElement('img');
                        img.src = src;
                        img.onerror = () => { img.style.visibility = 'hidden'; };
                        ph.replaceWith(img);
                    }
                });
            };
            if (window._addIcons) fill(window._addIcons);
            else api('GET', '/api/class_icons?classes=' + ALL_CLS.join(',')).then(r => {
                if (r && r.ok) { window._addIcons = r.icons; fill(r.icons); }
            }).catch(e => console.warn('class_icons:', e));
        }

        function addPickClass(cls) {
            document.getElementById('add-cls').value = cls;
            document.querySelectorAll('#add-grid .add-tile').forEach(el => el.classList.toggle('sel', el.dataset.cls === cls));
            const nm = document.getElementById('add-name');
            if (nm && !nm.dataset.edited) nm.value = 'New' + cls;
        }

        function addFilterClasses() {
            const q = (document.getElementById('add-search').value || '').trim().toLowerCase();
            document.querySelectorAll('#add-grid .add-tile').forEach(el => {
                el.style.display = (!q || el.dataset.cls.toLowerCase().includes(q)) ? '' : 'none';
            });
        }

        async function doAdd() {
            const cls = document.getElementById('add-cls').value;
            const name = document.getElementById('add-name').value || 'New' + cls;
            closeModal();
            let parent = selectedRef;
            if (parent === null) {
                const findWs = ns => {
                    for (const n of ns) {
                        if (n.cls === 'Workspace') return n.ref;
                        const c = findWs(n.children);
                        if (c !== null) return c;
                    }
                    return null;
                };
                parent = findWs(treeData) ?? -1;
            }
            const r = await api('PUT', '/api/instance', {
                class: cls,
                name: name,
                parent: parent
            });
            if (r.ok) {
                notify('✅ ' + cls);
                loadTree();
                _psSchedule();
            } else {
                notify(r.error || t('notify_error'), 'err');
            }
        }

        async function deleteSelected() {
            if (selectedRef === null) {
                notify(t('notify_not_selected'), 'warn');
                return;
            }
            const r = await api('DELETE', '/api/instance/' + selectedRef);
            _psSchedule();
            if (r.ok) {
                notify(t('notify_deleted'));
                selectedRef = null;
                selectedRefs = new Set();
                loadTree();
            }
        }

        // ===== Скачивание мест с Roblox — как стартовый экран Studio =====
        // Список Experiences аккаунта (карточки), клик → место скачивается и
        // открывается в редакторе. Нужен вход в аккаунт (Account). Запасной
        // путь — по Place ID. После правок — ☁ Публикация: Universe/Place ID
        // подставляются из того, что было открыто.
        let _experiences = [];
        window._rbxOrigin = null;
        window._rbxPendingName = '';

        function _escAttr(s) { return esc(s).replace(/"/g, '&quot;'); }

        let _recents = [];
        window._startMode = false;   // true — стартовый экран при запуске: вопросов «потерять сцену?» нет

        function _confirmDiscardForOpen() {
            return window._startMode || confirm(t('dl_discard'));
        }

        function _fmtDate(iso) {
            if (!iso) return '';
            const d = new Date(iso);
            return isNaN(d) ? '' : d.toLocaleString(undefined, { year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
        }

        // ---- Стартовый экран (как у Studio): слева разделы, справа карточки ----
        let _stView = 'home', _stQuery = '';
        let _stExp = { ok: false };          // ответ /api/roblox/experiences
        let _stArch = null;                  // ответ ...?archived=1 (грузится при первом заходе в Archive)
        let _stWho = '';
        let _stStudio = { ok: false, games: [] };   // ответ /api/studio/games

        function _startVisible() {
            const el = document.getElementById('start-screen');
            return !!(el && el.classList.contains('show'));
        }

        function hideStartScreen() {
            const el = document.getElementById('start-screen');
            if (el) el.classList.remove('show');
        }

        function _stTileFail(img) {
            if (!window._stThumbDiag) {   // причина — один раз, не на каждую карточку
                window._stThumbDiag = true;
                fetch(img.src).then(r => r.text().then(tx =>
                    console.error('thumb HTTP ' + r.status + ': ' + tx.slice(0, 300))))
                    .catch(e => console.error('thumb fetch: ' + e));
            }
            const d = document.createElement('div');
            d.className = 'st-tile';
            d.textContent = img.getAttribute('data-glyph') || '🌐';
            img.replaceWith(d);
        }

        function _stTile(icon, glyph, extra) {
            return icon
                ? '<img class="st-tile" src="/api/roblox/thumb?u=' + encodeURIComponent(icon) + '" data-src="' + _escAttr(icon) +
                  '" data-glyph="' + _escAttr(glyph) + '" onerror="_stTileFail(this)" referrerpolicy="no-referrer">'
                : '<div class="st-tile' + (extra ? ' ' + extra : '') + '">' + glyph + '</div>';
        }

        function _stCard(onclick, tile, pill, name, sub1, sub2, dotsIdx) {
            return '<div class="st-card" onclick="' + onclick + '">' + tile +
                '<div class="st-meta"><span class="st-pill">' + pill + '</span>' +
                (dotsIdx !== undefined ? '<button class="st-dots" title="' + _escAttr(t('st_menu')) + '" onclick="event.stopPropagation(); removeRecent(' + dotsIdx + ')">⋮</button>' : '') +
                '</div>' +
                '<div class="st-name">' + esc(name) + '</div>' +
                (sub1 ? '<div class="st-sub">' + esc(sub1) + '</div>' : '') +
                (sub2 ? '<div class="st-sub">' + esc(sub2) + '</div>' : '') + '</div>';
        }

        function _stMatch(name) {
            return !_stQuery || String(name).toLowerCase().indexOf(_stQuery) >= 0;
        }

        function _stExpList() { return (_stExp && _stExp.ok && _stExp.experiences) || []; }

        function _stRecentCards(limit) {
            let html = '', n = 0;
            _recents.forEach((x, i) => {
                if (!_stMatch(x.name) || (limit && n >= limit)) return;
                n++;
                const sub1 = x.opened ? t('st_opened', { d: _fmtDate(x.opened) }) : '';
                if (x.kind === 'roblox') {
                    const e = _stExpList().find(y => String(y.placeId) === String(x.placeId));
                    const pill = e ? (e.private ? '🔒 ' + t('exp_private') : '🌐 ' + t('exp_public')) : '🌐 ' + t('start_roblox');
                    html += _stCard('openRecent(' + i + ')', _stTile(e && e.icon, '🌐'), pill, x.name, sub1, e ? e.owner : '', i);
                } else {
                    html += _stCard('openRecent(' + i + ')', _stTile(null, '📄'), '💾 ' + t('st_local'), x.name, sub1, '', i);
                }
            });
            return html;
        }

        function _stExpCards(list) {
            let html = '';
            list.forEach((x, i) => {
                if (!_stMatch(x.name)) return;
                html += _stCard('openExperience(' + i + ')', _stTile(x.icon, '🌐'), x.private ? '🔒 ' + t('exp_private') : '🌐 ' + t('exp_public'),
                    x.name, x.updated ? t('st_modified', { d: _fmtDate(x.updated) }) : '', x.owner);
            });
            return html;
        }

        function _stStudioCards() {
            let html = '';
            ((_stStudio && _stStudio.games) || []).forEach((x, i) => {
                if (!_stMatch(x.name)) return;
                html += _stCard('openStudioGame(' + i + ')', _stTile(x.icon, '🎮'), '🎮 ' + t('st_studio_pill'),
                    x.name, x.updated ? t('st_modified', { d: _fmtDate(x.updated) }) : '', x.owner);
            });
            return html;
        }

        function _stStudioBlock() {
            const cards = _stStudioCards();
            let h = cards ? '<div class="st-grid">' + cards + '</div>'
                : '<p class="st-msg">' + t('st_studio_empty') + '</p>';
            if (_stStudio && _stStudio.groupError) h += '<p class="st-msg">' + t('st_studio_group_err', { err: esc(_stStudio.groupError) }) + '</p>';
            return h;
        }

        function openStudioGame(i) {
            const x = _stStudio && _stStudio.games && _stStudio.games[i];
            if (!x || !_confirmDiscardForOpen()) return;
            window._rbxPendingName = x.name;
            loadPlaceFromRoblox(x.placeId, x.universeId || '');
        }

        function _stTemplateCards() {
            return _stCard("startNew('baseplate')", _stTile(null, '🏠', 'tpl'), '🧩 ' + t('st_tpl_sub'), t('st_tpl_base'), '', '') +
                _stCard("startNew('empty')", _stTile(null, '⬜'), '🧩 ' + t('st_tpl_sub'), t('st_tpl_empty'), '', '');
        }

        function _stExpBlock(resp, isArchive) {
            if (resp && resp.ok) {
                const list = resp.experiences || [];
                const cards = isArchive ? _stArchCards() : _stExpCards(list);
                return cards ? '<div class="st-grid">' + cards + '</div>' : '<p class="st-msg">' + t('exp_empty') + '</p>';
            }
            if (resp && resp.needLogin) {
                return '<p class="st-msg">' + t('exp_login_needed') + '</p>' +
                    '<button class="st-btn" onclick="showAccountDialog()">' + t('tb_account') + '</button>';
            }
            return '<p class="st-msg">' + t('start_err', { err: esc((resp && resp.error) || '—') }) + '</p>';
        }

        function _stArchCards() {
            let html = '';
            ((_stArch && _stArch.experiences) || []).forEach((x, i) => {
                if (!_stMatch(x.name)) return;
                html += _stCard('openArchived(' + i + ')', _stTile(x.icon, '🗄'), x.private ? '🔒 ' + t('exp_private') : '🌐 ' + t('exp_public'),
                    x.name, x.updated ? t('st_modified', { d: _fmtDate(x.updated) }) : '', x.owner);
            });
            return html;
        }

        function _stRenderSide() {
            const nav = (v, ico, label) => '<button class="st-nav' + (_stView === v ? ' active' : '') + '" onclick="setStartView(\'' + v + '\')">' +
                '<span class="st-ico">' + ico + '</span><span class="st-lbl">' + label + '</span></button>';
            document.getElementById('st-side').innerHTML =
                '<div class="st-logo">Roblox Studio Web</div>' +
                '<button class="st-nav" onclick="startNew(\'baseplate\')"><span class="st-plus">+</span><span class="st-lbl">' + t('st_new') + '</span></button>' +
                nav('studio', '🎮', (_stStudio && _stStudio.title) || t('st_studio')) +
                nav('recents', '🕘', t('st_recents')) + nav('home', '🏠', t('st_home')) +
                nav('experiences', '📁', t('st_experiences')) + nav('templates', '🗂', t('st_templates')) +
                nav('archive', '🗄', t('st_archive'));
        }

        function _stRenderContent() {
            const c = document.getElementById('st-content');
            if (!c) return;
            let h = '';
            if (_stView === 'home') {
                h += '<div class="st-h1">' + (_stWho ? t('start_welcome', { name: esc(_stWho) }) : t('start_title')) + '</div>' +
                    '<div class="st-banner"><h3>' + t('st_banner_t') + '</h3><p>' + t('st_banner_p') + '</p><div class="st-row">' +
                    '<button class="st-btn" onclick="startOpenFile()">' + t('start_open') + '</button>' +
                    '<button class="st-btn sec" onclick="showDownloadPlaceDialog()">' + t('exp_by_id') + '</button></div></div>';
                if (_stStudio && _stStudio.configured) h += '<div class="st-h2">🎮 ' + esc(_stStudio.title || t('st_studio')) + '</div>' + _stStudioBlock();
                const rc = _stRecentCards(8);
                h += '<div class="st-h2">' + t('st_recent_h') + '</div>' + (rc ? '<div class="st-grid">' + rc + '</div>' : '<p class="st-msg">' + t('exp_empty') + '</p>');
                h += '<div class="st-h2">' + t('st_tpl_h') + '</div><div class="st-grid">' + _stTemplateCards() + '</div>';
            } else if (_stView === 'studio') {
                h += '<div class="st-h1">🎮 ' + esc((_stStudio && _stStudio.title) || t('st_studio')) + '</div>' + _stStudioBlock();
            } else if (_stView === 'recents') {
                const rc = _stRecentCards(0);
                h += '<div class="st-h1">' + t('st_recents') + '</div>' + (rc ? '<div class="st-grid">' + rc + '</div>' : '<p class="st-msg">' + t('exp_empty') + '</p>');
            } else if (_stView === 'experiences') {
                h += '<div class="st-h1">' + t('st_experiences') + '</div>' + _stExpBlock(_stExp, false);
            } else if (_stView === 'templates') {
                h += '<div class="st-h1">' + t('st_templates') + '</div><div class="st-grid">' + _stTemplateCards() + '</div>';
            } else if (_stView === 'archive') {
                h += '<div class="st-h1">' + t('st_archive') + '</div>' +
                    (_stArch ? _stExpBlock(_stArch, true) : '<p class="st-msg">' + t('exp_loading') + '</p>');
            }
            c.innerHTML = h;
        }

        function _stEnsureDom() {
            let el = document.getElementById('start-screen');
            if (el) return el;
            el = document.createElement('div');
            el.id = 'start-screen';
            el.innerHTML = '<div class="st-side" id="st-side"></div>' +
                '<div class="st-main"><div class="st-top">' +
                '<input class="st-search" id="st-search" placeholder="' + _escAttr(t('exp_search')) + '" oninput="_stQuery = this.value.trim().toLowerCase(); _stRenderContent()">' +
                '<button class="st-btn sec" title="' + _escAttr(t('st_refresh')) + '" onclick="_stLoad()">↻</button>' +
                '<button class="st-btn sec" onclick="startOpenFile()">' + t('start_open') + '</button>' +
                '<button class="st-btn sec" onclick="showDownloadPlaceDialog()">' + t('exp_by_id') + '</button>' +
                '<button class="st-btn sec" onclick="hideStartScreen()">✕ ' + t('st_close') + '</button>' +
                '</div><div id="st-content"></div></div>';
            document.body.appendChild(el);
            return el;
        }

        async function _stLoad() {
            const safe = (p, fallback) => p.catch(() => fallback);
            const c = document.getElementById('st-content');
            if (c) c.innerHTML = '<p class="st-msg">' + t('exp_loading') + '</p>';
            const [rec, exp, me, studio] = await Promise.all([
                safe(api('GET', '/api/recents'), {}),
                safe(api('GET', '/api/roblox/experiences'), { ok: false, error: '—' }),
                safe(api('GET', '/api/roblox/me'), {}),
                safe(api('GET', '/api/studio/games'), { ok: false, games: [] })
            ]);
            _stStudio = studio || { ok: false, games: [] };
            _recents = (rec && rec.ok && rec.recents) || [];
            _stExp = exp || { ok: false };
            _stWho = (me && me.ok && me.loggedIn) ? (me.displayName || me.name || '') : '';
            _stArch = null;
            _stRenderSide();
            _stRenderContent();
            if (_stView === 'archive') _stLoadArchive();
        }

        async function _stLoadArchive() {
            _stArch = await api('GET', '/api/roblox/experiences?archived=1').catch(() => ({ ok: false, error: '—' }));
            if (_stView === 'archive') _stRenderContent();
        }

        function setStartView(v) {
            _stView = v;
            _stRenderSide();
            _stRenderContent();
            if (v === 'archive' && !_stArch) _stLoadArchive();
            const m = document.querySelector('#start-screen .st-main');
            if (m) m.scrollTop = 0;
        }

        // isStartup=true — показ при запуске (см. DOMContentLoaded внизу).
        function showStartScreen(isStartup) {
            window._startMode = !!isStartup;
            const el = _stEnsureDom();
            closeModal();
            _stView = 'home';          // как в Studio: экран всегда открывается на Home
            _stQuery = '';
            const si = document.getElementById('st-search');
            if (si) si.value = '';
            el.classList.add('show');
            _stRenderSide();
            return _stLoad();
        }

        function startNew(tpl) {
            if (!_confirmDiscardForOpen()) return;
            newProject(tpl, true);
        }

        function startOpenFile() {
            // выбор файла должен вызываться синхронно из клика; экран скрывается после успешного открытия
            openFileBrowser('open');
        }

        async function removeRecent(i) {
            const x = _recents[i];
            if (!x || !confirm(t('st_remove'))) return;
            const r = await api('POST', '/api/recents/remove', x.kind === 'roblox'
                ? { kind: 'roblox', placeId: x.placeId } : { kind: 'file', path: x.path });
            if (r.ok) {
                _recents.splice(i, 1);
                _stRenderContent();
            } else {
                notify(r.error || t('notify_error'), 'err');
            }
        }

        function openArchived(i) {
            const x = _stArch && _stArch.experiences && _stArch.experiences[i];
            if (!x || !_confirmDiscardForOpen()) return;
            window._rbxPendingName = x.name;
            loadPlaceFromRoblox(x.placeId, x.universeId);
        }

        async function openRecent(i) {
            const x = _recents[i];
            if (!x) return;
            if (!_confirmDiscardForOpen()) return;
            if (x.kind === 'roblox') {
                window._rbxPendingName = x.name;
                loadPlaceFromRoblox(x.placeId, x.universeId || '');   // всегда свежая версия
                return;
            }
            const r = await api('POST', '/api/open', { path: x.path });
            if (r.ok) {
                hideStartScreen();
                window._rbxOrigin = null;
                window._startMode = false;
                selectedRef = null;
                selectedRefs = new Set();
                expanded.clear();
                window._avatarMeshCache = {};
                await loadTree();
                notify(t('notify_loaded_count', { n: r.count }));
            } else {
                notify(r.error || t('notify_error'), 'err');
            }
        }

        async function openExperience(i) {
            const x = _stExpList()[i];
            if (!x) { console.error('openExperience: нет элемента #' + i); return; }
            if (!_confirmDiscardForOpen()) return;
            window._rbxPendingName = x.name;
            console.log('openExperience:', x.name, x.placeId, x.universeId);
            const pr = await api('GET', '/api/roblox/experience/places?universeId=' + x.universeId + '&rootPlaceId=' + x.placeId);
            if (pr.ok && pr.places && pr.places.length > 1) {
                let h = '<h3>' + esc(x.name) + '</h3><p style="opacity:.8">' + t('exp_pick_place') + '</p>' +
                    '<div style="display:flex;flex-direction:column;gap:6px;max-height:50vh;overflow-y:auto">';
                pr.places.forEach((p) => {
                    h += '<button onclick="loadPlaceFromRoblox(' + Number(p.id) + ',' + Number(x.universeId) + ')" style="text-align:left">' +
                        (p.root ? '⭐ ' : '') + esc(p.name) + ' <span style="opacity:.6">(' + Number(p.id) + ')</span></button>';
                });
                h += '</div><div class="modal-row"><button onclick="closeModal()">←</button>' +
                    '<button onclick="closeModal()">' + t('btn_cancel') + '</button></div>';
                showModal(h);
                return;
            }
            loadPlaceFromRoblox(x.placeId, x.universeId);
        }

        // === Крутилка на время загрузки плейса/файла
        function showLoading(text) {
            if (!document.getElementById('rsw-loading-css')) {
                const st = document.createElement('style');
                st.id = 'rsw-loading-css';
                st.textContent =
                    '#rsw-loading{position:fixed;inset:0;z-index:5000;display:none;flex-direction:column;align-items:center;justify-content:center;gap:16px;background:rgba(10,14,26,.72);color:#fff;font:600 15px/1.3 sans-serif;text-align:center;padding:20px;touch-action:none}' +
                    '#rsw-loading.show{display:flex}#rsw-loading .rsw-load-text{white-space:pre-line}' +
                    '#rsw-loading .rsw-spin{width:54px;height:54px;border-radius:50%;border:5px solid rgba(255,255,255,.25);border-top-color:#fff;animation:rswspin .8s linear infinite}' +
                    '@keyframes rswspin{to{transform:rotate(360deg)}}';
                document.head.appendChild(st);
            }
            let el = document.getElementById('rsw-loading');
            if (!el) {
                el = document.createElement('div');
                el.id = 'rsw-loading';
                el.innerHTML = '<div class="rsw-spin"></div><div class="rsw-load-text"></div>';
                document.body.appendChild(el);
            }
            el.querySelector('.rsw-load-text').textContent = text || '';
            el.classList.add('show');
        }

        function hideLoading() {
            const el = document.getElementById('rsw-loading');
            if (el) el.classList.remove('show');
        }

        async function loadPlaceFromRoblox(placeId, universeId, version) {
            closeModal();
            const _nm = window._rbxPendingName || '';
            showLoading(t('dl_loading') + (_nm ? '\n' + _nm : ''));
            try {
                const r = await api('POST', '/api/open/place', {
                    place_id: placeId, universe_id: universeId || '', version: version || '',
                    name: _nm
                });
                if (r.ok) {
                    hideStartScreen();
                    window._startMode = false;
                    window._rbxOrigin = {
                        placeId: r.place_id,
                        universeId: r.universe_id || universeId || '',
                        name: window._rbxPendingName || ''
                    };
                    window._rbxPendingName = '';
                    selectedRef = null;
                    selectedRefs = new Set();
                    expanded.clear();
                    window._avatarMeshCache = {};
                    await loadTree();
                    notify(t('dl_ok', { n: r.count }));
                } else {
                    notify(r.error || t('notify_error'), 'err');
                }
            } catch (e) {
                console.error('loadPlaceFromRoblox:', e);
                notify(String(e), 'err');
            } finally {
                hideLoading();
            }
        }


        // === Панель «Войти в Roblox» при запуске, если аккаунт не подключён
        function _loginPromptVisible() {
            const el = document.getElementById('login-prompt');
            return !!(el && el.classList.contains('show'));
        }

        function hideLoginPrompt(never) {
            const el = document.getElementById('login-prompt');
            if (el) el.classList.remove('show');
            const cb = document.getElementById('lp-never');
            if (never || (cb && cb.checked)) {
                try { localStorage.setItem('rsw-login-never', '1'); } catch (e) { emuWarn('swallow:localStorage.setItem:13227', 'localStorage.setItem: ' + _errText(e) + ''); }
            }
            if (_pendingUpdateRelease) showUpdatePrompt();
        }

        function lpLoginAndroid() {
            try { window.AndroidBridge.loginToRoblox(); } catch (e) { console.error('loginToRoblox:', e); }
        }

        async function lpSaveCookie() {
            const el = document.getElementById('lp-cookie');
            const val = el ? el.value.trim() : '';
            if (!val) { notify(t('cookie_bad'), 'err'); return; }
            const r = await api('POST', '/api/roblox/cookie', { cookie: val });
            if (el) el.value = '';
            if (r.ok) {
                hideLoginPrompt();
                notify(t('cookie_ok', { name: r.name || '' }));
                if (_startVisible()) _stLoad();
            } else {
                notify(r.error || t('cookie_bad'), 'err');
            }
        }

        function showLoginPrompt() {
            if (!document.getElementById('login-prompt-css')) {
                const st = document.createElement('style');
                st.id = 'login-prompt-css';
                st.textContent =
                    '#login-prompt{position:fixed;inset:0;z-index:200;display:none;align-items:center;justify-content:center;padding:16px;background:rgba(8,12,24,.62);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}' +
                    '#login-prompt.show{display:flex;animation:lpfade .25s ease}' +
                    '@keyframes lpfade{from{opacity:0}to{opacity:1}}' +
                    '@keyframes lppop{from{transform:translateY(14px) scale(.97);opacity:0}to{transform:none;opacity:1}}' +
                    '#login-prompt .lp-card{width:100%;max-width:400px;max-height:94vh;overflow-y:auto;border-radius:12px;background:#1f2937;color:#f3f4f6;border:1px solid #374151;box-shadow:0 24px 70px rgba(0,0,0,.55);animation:lppop .3s ease}' +
                    '#login-prompt .lp-hero{padding:26px 22px 20px;text-align:center;color:#fff;background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);border-radius:12px 12px 0 0}' +
                    '#login-prompt .lp-logo{width:64px;height:64px;margin:0 auto 12px;border-radius:18px;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;font-size:34px}' +
                    '#login-prompt .lp-title{font:800 21px/1.2 sans-serif;margin:0}' +
                    '#login-prompt .lp-body{padding:18px 22px 20px}' +
                    '#login-prompt .lp-text{margin:0 0 14px;font:14px/1.45 sans-serif;color:#d1d5db}' +
                    '#login-prompt .lp-feat{display:flex;flex-direction:column;gap:8px;margin:0 0 16px;font:600 14px/1.3 sans-serif}' +
                    '#login-prompt .lp-feat div{background:#111827;border-radius:8px;padding:9px 12px}' +
                    '#login-prompt .lp-input{width:100%;box-sizing:border-box;padding:11px 12px;margin-bottom:10px;border:1px solid #4b5563;border-radius:6px;font:14px sans-serif;background:#374151;color:#f3f4f6}' +
                    '#login-prompt .lp-btn{display:block;width:100%;padding:13px;border:none;border-radius:6px;font:700 15px sans-serif;cursor:pointer;background:#2563eb;color:#fff}' +
                    '#login-prompt .lp-btn.sec{margin-top:8px;background:transparent;color:#9ca3af;font-weight:600}' +
                    '#login-prompt .lp-never{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:10px;font:13px sans-serif;color:#9ca3af}' +
                    '#login-prompt .lp-note{margin-top:12px;text-align:center;font:12px sans-serif;color:#9ca3af}' +
                    '#login-prompt .lp-help{margin:0 0 10px;font:12px/1.4 sans-serif;color:#9ca3af}';
                document.head.appendChild(st);
            }
            let el = document.getElementById('login-prompt');
            if (!el) {
                el = document.createElement('div');
                el.id = 'login-prompt';
                el.addEventListener('click', (e) => { if (e.target === el) hideLoginPrompt(); });
                document.body.appendChild(el);
            }
            el.innerHTML =
                '<div class="lp-card">' +
                '<div class="lp-hero"><div class="lp-logo">🎮</div><h2 class="lp-title">' + esc(t('lp_title')) + '</h2></div>' +
                '<div class="lp-body">' +
                '<p class="lp-text">' + esc(t('lp_text')) + '</p>' +
                '<div class="lp-feat"><div>' + esc(t('lp_f1')) + '</div><div>' + esc(t('lp_f2')) + '</div><div>' + esc(t('lp_f3')) + '</div></div>' +
                (IS_ANDROID
                    ? '<button class="lp-btn" onclick="lpLoginAndroid()">' + esc(t('lp_btn')) + '</button>'
                    : '<p class="lp-help">' + esc(t('cookie_help')) + '</p>' +
                      '<input id="lp-cookie" class="lp-input" type="password" autocomplete="off" placeholder="' + _escAttr(t('cookie_ph')) + '" ' +
                      'onkeydown="if(event.key===\'Enter\')lpSaveCookie()">' +
                      '<button class="lp-btn" onclick="lpSaveCookie()">' + esc(t('cookie_btn')) + '</button>') +
                '<button class="lp-btn sec" onclick="hideLoginPrompt()">' + esc(t('lp_later')) + '</button>' +
                '<label class="lp-never"><input type="checkbox" id="lp-never"> ' + esc(t('lp_never')) + '</label>' +
                '<div class="lp-note">🔒 ' + esc(t('lp_note')) + '</div>' +
                '</div></div>';
            el.classList.add('show');
        }

        async function _maybeShowLoginPrompt() {
            try { if (localStorage.getItem('rsw-login-never') === '1') return; } catch (e) { emuWarn('swallow:L13302', 'блок около script.js:13302: ' + _errText(e) + ''); }
            let ok = false;
            try {
                if (IS_ANDROID) ok = !!window.AndroidBridge.isRobloxLoggedIn();
                else { const st = await api('GET', '/api/roblox/auth-status'); ok = !!(st && st.ok && st.loggedIn); }
            } catch (e) { return; }
            if (!ok) showLoginPrompt();
        }

        // === Меню «Вышла новая версия» (только Android-приложение, только stable-релизы v1.N)
        // Hot-update релизы (hot-N) помечены prerelease и сюда не попадают — они ставятся сами.
        let _pendingUpdateRelease = null;

        function showUpdatePrompt() {
            const rel = _pendingUpdateRelease;
            if (!rel) return;
            _pendingUpdateRelease = null;
            showModal(
                '<h3>' + esc(t('upd_title')) + '</h3>' +
                '<p style="font-size:14px; line-height:1.45;">' + esc(t('upd_text', { ver: rel.tag })) + '</p>' +
                '<div class="modal-row">' +
                '<button onclick="goToUpdate(' + _escAttr(JSON.stringify(rel.url)) + ')" style="background:#2563eb">' + esc(t('upd_go')) + '</button>' +
                '<button onclick="closeModal()">' + esc(t('upd_later')) + '</button>' +
                '</div>'
            );
        }

        function goToUpdate(url) {
            closeModal();
            try {
                if (window.AndroidBridge && typeof window.AndroidBridge.openUrl === 'function') {
                    window.AndroidBridge.openUrl(url);
                    return;
                }
            } catch (e) { console.error('openUrl:', e); }
            window.open(url, '_blank');
        }

        async function _maybeShowUpdatePrompt() {
            try {
                if (!IS_ANDROID || typeof window.AndroidBridge.getAppVersionCode !== 'function') return;
                const cur = Number(window.AndroidBridge.getAppVersionCode());
                if (!cur) return;
                const ctl = new AbortController();
                const timer = setTimeout(() => ctl.abort(), 7000);
                let list;
                try {
                    const r = await fetch('https://api.github.com/repos/suscersal/roblox-studio-web/releases?per_page=30',
                        { signal: ctl.signal, headers: { 'Accept': 'application/vnd.github+json' } });
                    if (!r.ok) return;
                    list = await r.json();
                } finally { clearTimeout(timer); }
                let best = null;
                for (const rel of (Array.isArray(list) ? list : [])) {
                    if (rel.prerelease || rel.draft) continue;
                    const m = /^v1\.(\d+)$/.exec(rel.tag_name || '');
                    if (!m) continue;
                    const n = Number(m[1]);
                    if (!best || n > best.n) best = { n: n, tag: rel.tag_name, url: rel.html_url };
                }
                if (!best || best.n <= cur) return;
                _pendingUpdateRelease = best;
                if (!_loginPromptVisible()) showUpdatePrompt();
            } catch (e) { /* нет сети — молча пропускаем, обновление не критично */ }
        }

        function showDownloadPlaceDialog() {
            showModal(
                '<h3>' + t('dl_title') + '</h3>' +
                '<p style="opacity:.8; font-size:13px;">' + t('dl_hint') + '</p>' +
                '<input id="dlp" placeholder="' + t('dl_place') + '" inputmode="numeric">' +
                '<input id="dlv" placeholder="' + t('dl_version') + '" inputmode="numeric">' +
                '<div class="modal-row">' +
                '<button onclick="doDownloadPlace()" style="background:#2563eb">' + t('dl_btn') + '</button>' +
                '<button onclick="closeModal()">' + t('btn_cancel') + '</button>' +
                '</div>'
            );
        }

        function doDownloadPlace() {
            const placeId = document.getElementById('dlp').value.trim();
            const version = document.getElementById('dlv').value.trim();
            if (!/^\d+$/.test(placeId)) { notify(t('notify_error'), 'err'); return; }
            if (version && !/^\d+$/.test(version)) { notify(t('notify_error'), 'err'); return; }
            if (!_confirmDiscardForOpen()) return;
            window._rbxPendingName = '';
            loadPlaceFromRoblox(placeId, '', version);
        }

        function showPublishDialog() {
            showModal(
                '<h3>☁ Open Cloud</h3>' +
                (window._rbxOrigin ? '<p style="opacity:.8; font-size:13px;">' + t('pub_origin', { name: esc(window._rbxOrigin.name || '—'), id: esc(window._rbxOrigin.placeId) }) + '</p>' : '') +
                '<input id="pu" placeholder="Universe ID" value="' + (window._rbxOrigin ? _escAttr(window._rbxOrigin.universeId) : '') + '">' +
                '<input id="pp" placeholder="Place ID" value="' + (window._rbxOrigin ? _escAttr(window._rbxOrigin.placeId) : '') + '">' +
                '<input id="pk" placeholder="API Key" type="password">' +
                '<select id="pv">' +
                '<option value="Published">' + t('pub_ver_published') + '</option>' +
                '<option value="Saved">' + t('pub_ver_saved') + '</option>' +
                '</select>' +
                '<div class="modal-row">' +
                '<button onclick="doPub()" style="background:#2563eb">' + t('btn_publish') + '</button>' +
                '<button onclick="closeModal()">' + t('btn_cancel') + '</button>' +
                '</div>'
            );
        }

        // === Open Cloud API-ключ + вход в Roblox — теперь одно меню
        async function _apiKeySectionHtml() {
            const st = await api('GET', '/api/roblox/api-key');
            const has = st.ok && st.hasKey;
            const fromEnv = has && st.source === 'env';
            const statusLine = has
                ? (t('apikey_status_set', { last4: st.last4 }) + (fromEnv ? t('apikey_status_set_env') : ''))
                : t('apikey_status_unset');
            return '<h4 style="margin:14px 0 4px">' + t('account_section_apikey') + '</h4>' +
                '<p style="opacity:.8; font-size:13px;">' + t('apikey_desc') + '</p>' +
                '<p style="margin:6px 0;">' + statusLine + '</p>' +
                (fromEnv
                    ? ('<div class="modal-row" style="margin-top:6px;"><button onclick="validateRobloxApiKey()" style="background:#3b82f6">' + t('apikey_validate') + '</button></div>' +
                        '<p id="rbx-apikey-validate-result" style="margin:6px 0 0; font-size:13px;"></p>')
                    :
                    '<input id="rbx-apikey-input" type="password" placeholder="' + t('apikey_placeholder') + '" style="width:100%; padding:6px; box-sizing:border-box;">' +
                    '<div class="modal-row" style="margin-top:6px;">' +
                    '<button onclick="saveRobloxApiKey()" style="background:#2563eb">' + t('apikey_save') + '</button>' +
                    (has ? '<button onclick="clearRobloxApiKey()" style="background:#b91c1c">' + t('apikey_delete') + '</button>' : '') +
                    (has ? '<button onclick="validateRobloxApiKey()" style="background:#3b82f6">' + t('apikey_validate') + '</button>' : '') +
                    '</div>' +
                    (has ? '<p id="rbx-apikey-validate-result" style="margin:6px 0 0; font-size:13px;"></p>' : ''));
        }

        async function saveRobloxApiKey() {
            const el = document.getElementById('rbx-apikey-input');
            const key = el ? el.value.trim() : '';
            if (!key) { notify(t('apikey_empty'), 'err'); return; }
            const r = await api('POST', '/api/roblox/api-key', { api_key: key });
            if (r.ok) {
                notify(t('apikey_saved_notify', { last4: r.last4 }));
                showAccountDialog();
            } else {
                notify(t('apikey_error', { msg: r.error || r.text }), 'err');
            }
        }

        async function clearRobloxApiKey() {
            const r = await api('DELETE', '/api/roblox/api-key');
            if (r.ok) {
                notify(t('apikey_deleted_notify'));
                showAccountDialog();
            } else {
                notify(t('apikey_error', { msg: r.error || r.text }), 'err');
            }
        }

        async function validateRobloxApiKey() {
            const resEl = document.getElementById('rbx-apikey-validate-result');
            if (resEl) resEl.textContent = t('apikey_validating');
            // Пробуем реальным ассетом со сцены, если он уже загружен
            let testAssetId = null;
            for (const ref in (typeof soundElByRef !== 'undefined' ? soundElByRef : {})) {
                const src = soundElByRef[ref].src || '';
                const m = /[?&]id=(\d+)/.exec(src);
                if (m) { testAssetId = m[1]; break; }
            }
            const r = await api('POST', '/api/roblox/api-key/validate', testAssetId ? { assetId: testAssetId } : {});
            if (!r.ok) {
                if (resEl) resEl.textContent = '❌ ' + t('apikey_error', { msg: r.error || r.text });
                return;
            }
            if (r.valid) {
                if (resEl) resEl.textContent = t('apikey_valid');
            } else {
                if (resEl) resEl.textContent = t('apikey_invalid');
            }
        }

        async function doPub() {
            const b = {
                universe_id: document.getElementById('pu').value,
                place_id: document.getElementById('pp').value,
                api_key: document.getElementById('pk').value,
                version_type: document.getElementById('pv').value
            };
            closeModal();
            const r = await api('POST', '/api/publish', b);
            if (r.ok) notify(t('notify_published'));
            else notify('HTTP ' + r.status + ': ' + (r.text || r.error), 'err');
        }

        async function fetchUserIdByUsername() {
            const username = document.getElementById('av-username').value.trim();
            if (!username) {
                notify(t('acc_enter_username'), 'warn');
                return;
            }
            try {
                const resp = await fetch(`/api/roblox/userid?username=${encodeURIComponent(username)}`);
                const json = await resp.json();
                if (json.ok) {
                    document.getElementById('av-uid').value = json.id;
                    const preview = document.getElementById('avatar-preview');
                    if (preview) {
                        preview.src = `https://www.roblox.com/headshot-thumbnail/image?userId=${json.id}&width=100&height=100&format=png`;
                        preview.style.display = 'block';
                    }
                    notify(t('acc_id_found', { id: json.id, name: json.displayName || json.name || '' }));
                } else {
                    notify(json.error || t('acc_user_not_found'), 'err');
                }
            } catch (e) {
                notify(t('acc_request_error', { msg: e.message }), 'err');
            }
        }

        // === Скачивание 3D-аватара пользователя по Roblox User ID ===
        window.onRobloxAuthUpdated = function (loggedIn) {
            const fromPrompt = _loginPromptVisible();
            hideLoginPrompt();
            closeModal();
            if (loggedIn) {
                notify(t('acc_login_done'));
                if (_startVisible()) _stLoad();
                if (!fromPrompt) showAccountDialog();
            } else {
                notify(t('acc_login_failed'), 'err');
            }
        };

        // showAvatar3dDialog — старое имя, оставлено как алиас (на него
        function showAvatar3dDialog() { return showAccountDialog(); }

        // Раньше кнопка выхода звала ТОЛЬКО window.AndroidBridge.logoutRoblox()
        async function logoutRoblox() {
            if (IS_ANDROID && window.AndroidBridge && window.AndroidBridge.logoutRoblox) {
                window.AndroidBridge.logoutRoblox();
            } else {
                await api('POST', '/api/roblox/logout');
            }
            closeModal();
            showAccountDialog();
        }

        // Скачать ассет по ID из диалога Account: меш / текстура / звук. Дальше — тот же путь, что у долгого
        // нажатия на MeshId: в приложении системное окно «Сохранить как», в браузере «Поделиться»/скачивание.
        function downloadAssetFromAccount() {
            const inp = document.getElementById('acc-asset-id');
            const ids = Array.from(new Set(((inp ? inp.value : '').match(/\d{4,}/g)) || []));
            if (!ids.length) { notify(t('acc_asset_bad'), 'warn'); return; }
            if (ids.length === 1) { exportAssetById(ids[0], 'Asset'); return; }
            exportAssetsZip(ids);
        }
        function fillFailedMeshIds() {
            const inp = document.getElementById('acc-asset-id');
            if (!inp) return;
            inp.value = Array.from(failedMeshIds).join(' ');
            notify(failedMeshIds.size ? t('mesh_failed_n', { n: failedMeshIds.size }) : t('mesh_failed_none'));
        }
        // Несколько ассетов одним ZIP: в приложении — окно «Сохранить как», в браузере — «Поделиться»/скачивание.
        async function exportAssetsZip(ids) {
            try {
                notify(t('exp_assets_start', { n: ids.length }));
                const bridge = window.AndroidBridge && typeof window.AndroidBridge.exportRbxlFile === 'function' &&
                    typeof window.AndroidBridge.getDataDir === 'function';
                const er = await api('POST', '/api/asset-export', { ids, inline: !bridge });
                if (!er || !er.ok) { notify(t('exp_assets_fail', { err: (er && er.error) || t('exp_generic_err') }), 'warn'); return; }
                if (er.missing && er.missing.length) notify(t('exp_assets_missing', { list: er.missing.join(', ') }), 'warn');
                if (bridge) { window.AndroidBridge.exportRbxlFile(er.path, er.name); return; }
                const blob = _b64ToBlob(er.b64, 'application/zip');
                const file = new File([blob], er.name, { type: 'application/zip' });
                if (navigator.canShare && navigator.canShare({ files: [file] })) {
                    try { await navigator.share({ files: [file], title: er.name }); return; }
                    catch (e) { if (e && e.name === 'AbortError') return; }
                }
                _downloadBlob(blob, er.name);
                notify(t('exp_assets_saved', { name: er.name, kb: Math.round(er.size / 1024), n: er.got.length }));
            } catch (e) {
                notify(t('exp_error', { msg: (e && e.message ? e.message : e) }), 'warn');
            }
        }
        async function saveRobloxCookie() {
            const el = document.getElementById('rbx-cookie-input');
            const val = el ? el.value.trim() : '';
            if (!val) { notify(t('cookie_bad'), 'err'); return; }
            const r = await api('POST', '/api/roblox/cookie', { cookie: val });
            if (el) el.value = '';
            if (r.ok) {
                notify(t('cookie_ok', { name: r.name || '' }));
                if (_startVisible()) _stLoad();
                showAccountDialog();
            } else {
                notify(r.error || t('cookie_bad'), 'err');
            }
        }

        async function showAccountDialog() {
            let loggedIn = false;
            if (IS_ANDROID) {
                loggedIn = window.AndroidBridge.isRobloxLoggedIn();
            } else {
                const st = await api('GET', '/api/roblox/auth-status');
                loggedIn = !!(st.ok && st.loggedIn);
            }

            // Кнопка импорта ZIP теперь доступна всегда, без проверки IS_ANDROID
            const localImportRow = '<div class="modal-row"><button onclick="pickAvatarFileForImport()">' + t('avatar_import_file') + '</button></div>';
            const apiKeyHtml = await _apiKeySectionHtml();
            const hr = '<hr style="border-color:#374151;border-style:solid;margin:12px 0 4px">';
            const assetHtml =
                '<h4 style="margin:4px 0">' + t('acc_asset_title') + '</h4>' +
                '<div style="display:flex; gap:6px; margin-bottom:8px;">' +
                '<input id="acc-asset-id" inputmode="numeric" placeholder="' + t('acc_asset_ph') + '" style="flex:1; padding:6px;" ' +
                'onkeydown="if(event.key===\'Enter\')downloadAssetFromAccount()">' +
                '<button onclick="downloadAssetFromAccount()" style="background:#3b82f6; padding:4px 12px;">' + t('acc_asset_btn') + '</button>' +
                '</div>' +
                '<div class="modal-row" style="margin-bottom:6px"><button onclick="fillFailedMeshIds()" style="padding:4px 10px;">' + t('acc_asset_failed') + '</button></div>';

            if (!loggedIn) {
                showModal(
                    '<h3>' + t('account_title') + '</h3>' +
                    '<h4 style="margin:4px 0">' + t('account_section_login') + '</h4>' +
                    localImportRow +
                    '<p style="margin-top:10px">' + t('avatar_login_needed') + '</p>' +
                    '<div class="modal-row">' +
                    (IS_ANDROID
                        ? '<button onclick="window.AndroidBridge.loginToRoblox()" style="background:#2563eb">' + t('avatar_login_btn') + '</button>'
                        : '<p style="opacity:.7; font-size:13px;">' + t('cookie_help') + '</p>' +
                          '<input id="rbx-cookie-input" type="password" autocomplete="off" placeholder="' + t('cookie_ph') + '" style="width:100%; padding:6px; box-sizing:border-box;">' +
                          '<div class="modal-row" style="margin-top:6px;"><button onclick="saveRobloxCookie()" style="background:#2563eb">' + t('cookie_btn') + '</button></div>') +
                    '</div>' +
                    hr + assetHtml + hr + apiKeyHtml +
                    '<div class="modal-row" style="margin-top:10px">' +
                    '<button onclick="closeModal()">' + t('btn_cancel') + '</button>' +
                    '</div>'
                );
                return;
            }

            showModal(`
        <h3>${t('account_title')}</h3>
        <h4 style="margin:4px 0">${t('account_section_login')}</h4>
        <div style="display:flex; gap:6px; margin-bottom:8px;">
            <input id="av-username" placeholder="${t('acc_username_ph')}" style="flex:1; padding:6px;">
            <button onclick="fetchUserIdByUsername()" style="background:#3b82f6; padding:4px 12px;">${t('acc_get_id_btn')}</button>
        </div>
        <input id="av-uid" placeholder="${t('acc_uid_ph')}">
        <img id="avatar-preview" style="width:80px; height:80px; border-radius:50%; display:none; margin:6px auto; background:#1f2937;">
        <div class="modal-row">
            <button onclick="doDownloadAvatar3d('import')" style="background:#2563eb">${t('avatar_import_scene')}</button>
            <button onclick="doDownloadAvatar3d('save')">${t('avatar_download_zip')}</button>
        </div>
        ${localImportRow}
        <div class="modal-row">
            <button onclick="logoutRoblox()">${t('avatar_logout')}</button>
        </div>
        ${hr}${assetHtml}${hr}${apiKeyHtml}
        <div class="modal-row" style="margin-top:10px">
            <button onclick="closeModal()">${t('btn_cancel')}</button>
        </div>
    `);
        }

        function _b64ToBlob(b64, mime) {
            const bytes = atob(b64);
            const arr = new Uint8Array(bytes.length);
            for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
            return new Blob([arr], { type: mime });
        }

        function _downloadBlob(blob, name) {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = name;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        }

        function _avatarProgressHtml(steps, activeIndex, errorText) {
            const rows = steps.map((label, i) => {
                let icon = '⚪';
                let style = 'opacity:.5';
                if (i < activeIndex) { icon = '✅'; style = ''; }
                else if (i === activeIndex && !errorText) { icon = '⏳'; style = 'font-weight:600'; }
                else if (i === activeIndex && errorText) { icon = '❌'; style = 'font-weight:600;color:#f87171'; }
                return '<div style="display:flex;gap:8px;align-items:center;padding:4px 0;' + style + '">' +
                    '<span>' + icon + '</span><span>' + label + '</span></div>';
            }).join('');
            const errBlock = errorText
                ? '<div style="margin-top:10px;padding:8px;background:#3f1d1d;border-radius:6px;color:#fca5a5;font-size:13px;white-space:pre-wrap;word-break:break-word">' + errorText + '</div>'
                : '';
            return '<h3>' + t('avatar_progress_title') + '</h3>' + rows + errBlock +
                '<div class="modal-row" style="margin-top:12px">' +
                (errorText
                    ? '<button onclick="showAccountDialog()">' + t('avatar_progress_back') + '</button>'
                    : '<button onclick="cancelAvatar3dDownload()">' + t('avatar_progress_cancel') + '</button>') +
                '</div>';
        }

        // AbortController текущей загрузки — доступен снаружи doDownloadAvatar3d,
        let _avatar3dAbort = null;
        let _avatar3dCancelled = false;

        function cancelAvatar3dDownload() {
            _avatar3dCancelled = true;
            if (_avatar3dAbort) _avatar3dAbort.abort();
            closeModal();
            notify(t('notify_download_cancelled'));
        }

        async function _apiAbortable(url, signal) {
            const r = await fetch(url, { headers: { 'Content-Type': 'application/json' }, signal });
            return r.json();
        }

        function pickAvatarFileForImport() {
            // Если есть Android-мост — используем нативный выбор файла
            if (window.AndroidBridge && typeof window.AndroidBridge.pickAvatarZipFile === 'function') {
                window.AndroidBridge.pickAvatarZipFile();
                return;
            }

            // Веб-версия: создаём скрытый input для выбора ZIP
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = '.zip,application/zip';
            fileInput.style.display = 'none';
            document.body.appendChild(fileInput);

            fileInput.addEventListener('change', function (event) {
                const file = event.target.files[0];
                if (!file) {
                    document.body.removeChild(fileInput);
                    return;
                }

                // Отправляем файл на сервер (multipart/form-data)
                const formData = new FormData();
                formData.append('file', file);

                fetch('/api/roblox/avatar3d/import-local-upload', {
                    method: 'POST',
                    body: formData
                })
                    .then(response => response.json())
                    .then(data => {
                        document.body.removeChild(fileInput);
                        if (data.ok) {
                            // Вызываем реальную функцию импорта в сцену
                            importAvatarIntoScene(data.obj_text, data.mtl_text, data.textures, 'local')
                                .then(() => notify(t('avatar_added_to_scene')))
                                .catch(e => notify(t('notify_import_failed') + e.message, 'err'));
                        } else {
                            notify(data.error || t('notify_import_error'), 'err');
                        }
                    })
                    .catch(err => {
                        document.body.removeChild(fileInput);
                        console.error('Ошибка загрузки файла:', err);
                        notify(t('notify_import_net'), 'err');
                    });
            });

            fileInput.click();
        }


        window.onAvatarFilePicked = async function (path) {
            if (!path) return; // пользователь отменил выбор
            closeModal();
            notify(t('notify_reading_file'));
            let r;
            try {
                r = await api('GET', '/api/roblox/avatar3d/import-local?path=' + encodeURIComponent(path));
            } catch (e) {
                notify(t('notify_read_error') + (e && e.message || e), 'err');
                return;
            }
            if (!r.ok) {
                notify(r.error || t('notify_archive_failed'), 'err');
                return;
            }
            try {
                await importAvatarIntoScene(r.obj_text, r.mtl_text, r.textures, 'local');
                notify(t('avatar_added_to_scene'));
            } catch (e) {
                notify(t('notify_import_failed') + (e && e.message || e), 'err');
            }
        };


        async function doDownloadAvatar3d(mode) {
            const userId = (document.getElementById('av-uid').value || '').trim();
            if (!/^[0-9]+$/.test(userId)) {
                notify(t('avatar_enter_uid'), 'err');
                return;
            }

            _avatar3dCancelled = false;
            _avatar3dAbort = new AbortController();
            const signal = _avatar3dAbort.signal;

            const steps = [t('av_step_status'), t('av_step_wait'), t('av_step_download'),
                mode === 'import' ? t('av_step_add') : t('av_step_save')];
            let step = 0;
            showModal(_avatarProgressHtml(steps, step));

            const maxWaitMs = 120000;
            const pollEveryMs = 1500;
            const startedAt = Date.now();
            let bundleUrl = null;
            let sawGenerating = false;

            while (Date.now() - startedAt < maxWaitMs) {
                if (_avatar3dCancelled) return;
                let st;
                try {
                    st = await _apiAbortable('/api/roblox/avatar3d/status?userId=' + encodeURIComponent(userId), signal);
                } catch (e) {
                    if (_avatar3dCancelled || e.name === 'AbortError') return;
                    showModal(_avatarProgressHtml(steps, step, t('av_net_error') + (e && e.message || e)));
                    return;
                }
                if (!st.ok) {
                    showModal(_avatarProgressHtml(steps, step, st.message || st.error || t('av_status_failed')));
                    return;
                }
                if (st.ready) {
                    bundleUrl = st.bundleUrl;
                    break;
                }
                if (st.state === 'Error') {
                    showModal(_avatarProgressHtml(steps, step, t('av_roblox_failed')));
                    return;
                }
                if (!sawGenerating) {
                    sawGenerating = true;
                    step = 1;
                    showModal(_avatarProgressHtml(steps, step));
                }
                await new Promise(res => setTimeout(res, pollEveryMs));
            }

            if (_avatar3dCancelled) return;

            if (!bundleUrl) {
                showModal(_avatarProgressHtml(steps, step, t('av_timeout')));
                return;
            }

            step = 2;
            showModal(_avatarProgressHtml(steps, step));

            // savePath: на Android — приватная папка приложения (для SAF-
            const dataDir = (typeof IS_ANDROID !== 'undefined' && IS_ANDROID)
                ? window.AndroidBridge.getDataDir() : '.';

            let fetchUrl = '/api/roblox/avatar3d/fetch?bundleUrl=' + encodeURIComponent(bundleUrl) +
                '&userId=' + encodeURIComponent(userId) +
                '&savePath=' + encodeURIComponent(dataDir);
            if (mode === 'import') fetchUrl += '&includeAssets=1';

            let r;
            try {
                r = await _apiAbortable(fetchUrl, signal);
            } catch (e) {
                if (_avatar3dCancelled || e.name === 'AbortError') return;
                showModal(_avatarProgressHtml(steps, step, t('av_download_error') + (e && e.message || e)));
                return;
            }
            if (_avatar3dCancelled) return;
            if (!r.ok) {
                showModal(_avatarProgressHtml(steps, step, r.message || r.error || t('av_download_failed')));
                return;
            }

            step = 3;
            showModal(_avatarProgressHtml(steps, step));

            if (mode === 'import') {
                try {
                    await importAvatarIntoScene(r.obj_text, r.mtl_text, r.textures, userId);
                } catch (e) {
                    showModal(_avatarProgressHtml(steps, step, t('av_import_failed') + (e && e.message || e)));
                    return;
                }
                closeModal();
                notify(t('avatar_added_to_scene'));
                return;
            }

            if (!IS_ANDROID) {
                showModal(_avatarProgressHtml(steps, step, t('av_zip_android', { path: r.zipPath })));
                return;
            }
            // Тот же поток, что уже работает для сохранения .rbxl:
            window.AndroidBridge.exportRbxlFile(r.zipPath, r.zipName);
        }

        // Загружает OBJ+MTL+текстуры (уже скачанные с сервера как текст/
        async function importAvatarIntoScene(objText, mtlText, textures, userId) {
            await ensureObjMtlLoaders();

            // КРИТИЧНЫЙ ФИКС: Roblox отдаёт НЕстандартный .obj — строки вершин
            const fixedObjText = objText.replace(
                /^v(\s+-?[\d.eE+-]+\s+-?[\d.eE+-]+\s+-?[\d.eE+-]+)(?:\s+-?[\d.eE+-]+)*\s*$/gm,
                'v$1'
            );

            const texByName = {};
            (textures || []).forEach(t => { texByName[t.name] = t.data_url; });

            const manager = new THREE.LoadingManager();
            manager.setURLModifier((url) => {
                const clean = url.split('/').pop();
                return texByName[clean] || url;
            });

            // ФИКС ПРОЗРАЧНОСТИ: THREE.MTLLoader (r128) трактует тег "Tr"
            const mtlLoader = new THREE.MTLLoader(manager);
            mtlLoader.setMaterialOptions({ invertTrProperty: true });
            const materials = mtlLoader.parse(mtlText, '');
            materials.preload();
            // ФИКС КАЧЕСТВА 1/2: MTLLoader по умолчанию делает материалы
            for (const key in materials.materials) {
                const m = materials.materials[key];
                m.side = THREE.DoubleSide;
                // Принудительно делаем непрозрачным: ошибочно распарсенный
                // d/Tr — самая частая причина "полупрозрачного" аватара.
                m.transparent = false;
                m.opacity = 1;
                m.alphaTest = 0;
                m.needsUpdate = true;
            }

            const objLoader = new THREE.OBJLoader(manager);
            objLoader.setMaterials(materials);
            const object = objLoader.parse(fixedObjText);

            // ФИКС КАЧЕСТВА 2/2: текстуры из data:
            object.traverse(n => {
                if (n.isMesh) {
                    n.castShadow = true;
                    n.receiveShadow = true;
                    // ФИКС "ГРАНЁНОГО" ВИДА:
                    if (n.geometry) n.geometry.computeVertexNormals();
                    const mats = Array.isArray(n.material) ? n.material : [n.material];
                    mats.forEach(m => {
                        if (m && m.map) {
                            m.map.encoding = THREE.sRGBEncoding;
                            // ФИКС ЗЕРНИСТОСТИ ТЕКСТУР НА ТЕЛЕФОНЕ:
                            m.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
                            m.map.needsUpdate = true;
                        }
                    });
                }
            });

            let vertCount = 0;
            object.traverse(n => { if (n.isMesh && n.geometry && n.geometry.attributes.position) vertCount += n.geometry.attributes.position.count; });
            if (vertCount === 0) {
                throw new Error(t('av_err_empty_geom'));
            }

            object.name = 'RobloxAvatar_' + userId;

            if (!(typeof scene !== 'undefined' && scene)) {
                throw new Error(t('av_err_scene_not_ready'));
            }
            scene.add(object);

            // ВАЖНО: координаты вершин в OBJ от Roblox абсолютные — они
            const box = new THREE.Box3().setFromObject(object);
            const center = box.getCenter(new THREE.Vector3());

            let targetPos = new THREE.Vector3(0, 0, 0);
            if (typeof camera !== 'undefined' && camera) {
                const dir = new THREE.Vector3();
                camera.getWorldDirection(dir);
                targetPos.copy(camera.position).add(dir.multiplyScalar(15));
            }
            object.position.copy(targetPos).sub(center);

            // Сохраняем смещение центра, чтобы использовать при reloadScene
            const centerOffset = center.clone();

            // Чтобы аватар появился в Explorer, был выбираемым/удаляемым
            let ref = null;
            if (typeof api === 'function') {
                const findWs = ns => {
                    for (const n of ns) {
                        if (n.cls === 'Workspace') return n.ref;
                        const c = findWs(n.children);
                        if (c !== null) return c;
                    }
                    return null;
                };
                const parent = findWs(treeData) ?? -1;
                const r = await api('PUT', '/api/instance', {
                    class: 'Part',
                    name: object.name,
                    parent: parent,
                });
                if (r.ok) {
                    ref = r.ref;
                } else {
                    // ВАЖНО: PUT /api/instance молча возвращает {ok:false},
                    throw new Error(t('av_err_not_saved'));
                }
                if (ref !== null) {
                    // КРИТИЧНЫЙ ФИКС #2: /api/scene на сервере (make_scene_objects)
                    const p = object.position;
                    const size = box.getSize(new THREE.Vector3());
                    // Формат CFrame, который реально понимает сервер (см.
                    await api('POST', '/api/instance/' + ref, {
                        prop: 'CFrame',
                        value: {
                            position: { x: p.x, y: p.y, z: p.z },
                            matrix: [1, 0, 0, 0, 1, 0, 0, 0, 1],
                        },
                    });
                    await api('POST', '/api/instance/' + ref, {
                        prop: 'Position',
                        value: { x: p.x, y: p.y, z: p.z },
                    });
                    await api('POST', '/api/instance/' + ref, {
                        prop: 'Size',
                        value: { x: size.x || 1, y: size.y || 1, z: size.z || 1 },
                    });
                    await api('POST', '/api/instance/' + ref, { prop: 'Anchored', value: true });
                }
            }
            if (ref !== null) {
                // Без userData.ref луч в pick() не может определить, какому
                object.userData.ref = ref;
                window._avatarMeshCache = window._avatarMeshCache || {};
                window._avatarMeshCache[ref] = { object, centerOffset: centerOffset };
                sceneObjs[ref] = object;
                await loadTree();
            }

            // Рендер-цикл приложения не всегда рисует каждый кадр по
            if (typeof renderer !== 'undefined' && renderer && typeof camera !== 'undefined') {
                try { renderer.render(scene, camera); } catch (e) { emuWarn('swallow:renderer.render:13989', 'renderer.render: ' + _errText(e) + ''); }
            }

            return { vertCount, ref };
        }

        // Тот же колбэк уже используется для сохранения .rbxl — здесь
        // просто закрываем прогресс-модалку аватара, если она открыта.
        const _prevOnAndroidFileExported = window.onAndroidFileExported;
        window.onAndroidFileExported = function (ok) {
            if (_prevOnAndroidFileExported) _prevOnAndroidFileExported(ok);
            const overlay = document.getElementById('modal-overlay');
            if (overlay && overlay.classList.contains('show')) {
                closeModal();
            }
            notify(ok ? t('avatar_saved') : t('avatar_save_cancelled'), ok ? undefined : 'err');
        };

        function showModal(html) {
            document.getElementById('modal-content').innerHTML = html;
            document.getElementById('modal-overlay').classList.add('show');
        }

        function closeModal() {
            document.getElementById('modal-overlay').classList.remove('show');
        }

        // ============ КЛАВИШИ ============
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' ||
                e.target.classList.contains('CodeMirror') || e.target.closest('.CodeMirror')) {
                return;
            }

            keysPressed[e.key.toLowerCase()] = true;
            if (!e.repeat) { const kn = luaKeyNameFromDom(e); if (kn) luaSetKeySrc(kn, 'dom', true); }

            if (isPlaying && !luaControlsDisabled && (e.key === ' ' || e.key.toLowerCase() === 'e')) {
                e.preventDefault();
                jumpQueued = true;
            }

            if (e.ctrlKey && e.key === 'o') {
                e.preventDefault();
                openFileBrowser('open');
            } else if (e.ctrlKey && e.shiftKey && e.key === 'S') {
                e.preventDefault();
                openFileBrowser('save');
            } else if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                saveFile();
            } else if (e.key === 'Delete') {
                deleteSelected();
            } else if (e.key === 'Escape') {
                closeFileMenu();
                closeModal();
                deselect();
            } else if (e.key === 'F5') {
                e.preventDefault();
                reloadScene();
            } else if (e.key === 'f' && !e.ctrlKey) {
                if (selectedRef && sceneObjs[selectedRef]) {
                    const p = sceneObjs[selectedRef].position;
                    target = { x: p.x, y: p.y, z: p.z };
                    updateCamera();
                    notify(t('notify_focus'));
                }
            }
        });

        document.addEventListener('keyup', (e) => {
            keysPressed[e.key.toLowerCase()] = false;
            const kn = luaKeyNameFromDom(e); if (kn) luaSetKeySrc(kn, 'dom', false);
        });
        window.addEventListener('blur', () => { for (const n of Object.keys(luaKeySrc)) luaSetKeySrc(n, 'dom', false); });

        document.getElementById('modal-overlay').onclick = e => {
            if (e.target.id === 'modal-overlay') closeModal();
        };

        // ============ ИНИЦИАЛИЗАЦИЯ ============
        // script.js, app.py и style.css — три файла одной сборки. Если обновили только часть, баги «не исправлены»
        // (например, прозрачные текстуры на High чинятся парой script.js + app.py) — говорим об этом прямо в Output.
        async function checkBuildConsistency() {
            try {
                const st = await api('GET', '/api/status');
                const cssBuild = (getComputedStyle(document.documentElement).getPropertyValue('--css-build') || '').trim().replace(/^["']|["']$/g, '');
                const problems = [];
                if (!st || st.build === undefined) problems.push('app.py устарел (нет метки сборки)');
                else if (st.build !== BUILD_LABEL) problems.push('app.py: ' + st.build);
                if (cssBuild !== BUILD_LABEL) problems.push('style.css: ' + (cssBuild || 'нет метки'));
                if (problems.length) {
                    logLuaOutput('warn', 'Файлы разных сборок! script.js: ' + BUILD_LABEL + ' | ' + problems.join(' | ')
                        + ' — замените ВСЕ три файла (script.js, app.py, style.css) и перезапустите приложение.');
                } else {
                    logLuaOutput('info', 'script.js, app.py и style.css одной сборки ✓');
                }
            } catch (e) { emuWarn('swallow:L14086', 'блок около script.js:14086: ' + _errText(e) + ' (без сервера нечего сравнивать)'); }
        }

        window.addEventListener('DOMContentLoaded', () => {
            loadLayout();
            initResizers();

            refreshCM();
            console.log('Build: ' + BUILD_LABEL);
            try { logLuaOutput('info', 'Build: ' + BUILD_LABEL); } catch (e) { /* Output ещё не готов */ }
            checkBuildConsistency();
            // Стартовый экран при запуске — только если на сервере ещё нет открытой сцены
            // (обновление страницы посреди работы его не вызывает).
            api('GET', '/api/status').then(st => {
                if (st && st.ok && !st.loaded) showStartScreen(true);
            }).catch(() => { /* сервер недоступен — нечего показывать */ })
                .then(() => _maybeShowLoginPrompt())
                .then(() => _maybeShowUpdatePrompt());
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && _loginPromptVisible()) { hideLoginPrompt(); return; }
            if (e.key === 'Escape' && _startVisible() &&
                !document.getElementById('modal-overlay').classList.contains('show')) hideStartScreen();
        });

        window.addEventListener('resize', refreshCM);
        // Обычный window 'resize' на многих мобильных браузерах/WebView НЕ
        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', () => {
                refreshCM();
                if (cmEditor && cmEditor.state && cmEditor.state.completionActive) {
                    cmEditor.closeCompletion(); // старая позиция всё равно неверна — не показывать её "зависшей"
                }
            });
        }
