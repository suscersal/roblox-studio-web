package com.suscersal.rsw

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.webkit.JavascriptInterface
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.io.File
import java.net.InetSocketAddress
import java.net.Socket
import org.json.JSONObject

class MainActivity : AppCompatActivity() {

    companion object {
        // Состояние процесса, а не Activity — сервер должен стартовать
        // только один раз за жизнь процесса (см. комментарий в maxclient:
        // повторный вызов app.run() на уже занятом порту упадёт).
        private var serverStarted = false
        private const val PORT = 47182 // держим синхронно с PORT в app.py; 8080 часто занят другими приложениями/ADB
    }

    private lateinit var webView: WebView

    // Импорт .rbxl-файла через системный пикер (SAF) — единственный
    // надёжный способ достать файл, выбранный пользователем, при scoped
    // storage на Android 10+. Копируем в приватную папку приложения и
    // сообщаем странице через JS-колбэк.
    private val filePickerLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val uri: Uri? = if (result.resultCode == RESULT_OK) result.data?.data else null
        if (uri == null) return@registerForActivityResult
        val dest = File(filesDir, "imported.rbxl")
        contentResolver.openInputStream(uri)?.use { input ->
            dest.outputStream().use { output -> input.copyTo(output) }
        }
        webView.evaluateJavascript(
            "window.onAndroidFileImported && window.onAndroidFileImported(${
                org.json.JSONObject.quote(dest.absolutePath)
            });",
            null
        )
    }

    // Путь временного файла (в приватном хранилище приложения), который
    // Flask-сервер только что записал через /api/save — сохраняем его здесь
    // между запуском SAF-диалога "Сохранить как" (exportRbxlFile) и
    // получением выбранного пользователем Uri в saveFileLauncher.
    private var pendingExportSourcePath: String? = null

    // Файл, где хранится .ROBLOSECURITY между запусками приложения — тот же
    // filesDir, что уже прокидывается в Python как RSW_DATA_DIR (см.
    // bridge_launcher.start_server), так что app.py читает куку напрямую
    // оттуда, без дополнительного канала передачи.
    private val robloxAuthFile: File
        get() = File(filesDir, "roblox_auth.json")

    private val robloxLoginLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val cookie = if (result.resultCode == RESULT_OK)
            result.data?.getStringExtra(RobloxLoginActivity.EXTRA_COOKIE) else null

        val loggedIn = cookie != null
        if (cookie != null) {
            val payload = JSONObject().apply {
                put("cookie", cookie)
                put("savedAt", System.currentTimeMillis())
            }
            robloxAuthFile.writeText(payload.toString())
        }
        webView.evaluateJavascript(
            "window.onRobloxAuthUpdated && window.onRobloxAuthUpdated($loggedIn);",
            null
        )
    }

    // Экспорт через системный пикер (SAF, ACTION_CREATE_DOCUMENT) —
    // единственный способ дать пользователю сохранить файл в выбранное им
    // место (Загрузки, другое приложение и т.п.) при scoped storage.
    // Сервер сам писать туда не может — не имеет доступа к SAF-Uri.
    private val saveFileLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val sourcePath = pendingExportSourcePath
        pendingExportSourcePath = null
        val uri: Uri? = if (result.resultCode == RESULT_OK) result.data?.data else null

        val ok = if (sourcePath != null && uri != null) {
            try {
                File(sourcePath).inputStream().use { input ->
                    contentResolver.openOutputStream(uri)?.use { output ->
                        input.copyTo(output)
                    }
                }
                true
            } catch (e: Exception) {
                false
            }
        } else {
            false
        }

        webView.evaluateJavascript(
            "window.onAndroidFileExported && window.onAndroidFileExported($ok);",
            null
        )
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }

        webView = findViewById(R.id.webView)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        // WebGL для 3D-вьюпорта — включено по умолчанию в современном
        // системном WebView, явных флагов не требуется.
        webView.webViewClient = WebViewClient()
        webView.addJavascriptInterface(AndroidBridge(), "AndroidBridge")

        val loadingStatus = findViewById<TextView>(R.id.loadingStatus)
        loadingStatus.visibility = View.VISIBLE

        // OtaUpdater.checkAndUpdate сама ловит сетевые ошибки и не должна
        // зависать дольше своих HTTP-таймаутов (~8-16 сек), но если сети нет
        // вообще (DNS-резолвинг иногда виснет дольше connectTimeout) —
        // подстраховываемся отдельным таймером, чтобы приложение в любом
        // случае стартовало на уже скачанном ранее hotpatch'е (или на коде
        // из APK, если ничего ещё не скачивалось), а не стояло на заставке
        // бесконечно.
        val proceededOnce = java.util.concurrent.atomic.AtomicBoolean(false)

        fun proceedWithHotpatch(hotpatchDir: File?) {
            if (!proceededOnce.compareAndSet(false, true)) return
            loadingStatus.text = "Запуск…"
            startPythonServerOnce(hotpatchDir)
            waitForServerThenLoad()
        }

        android.os.Handler(mainLooper).postDelayed({
            if (!proceededOnce.get()) {
                val existing = OtaUpdater.hotpatchDir(this).let {
                    if (it.exists() && it.listFiles()?.isNotEmpty() == true) it else null
                }
                loadingStatus.text = "Нет соединения, запуск без обновлений…"
                proceedWithHotpatch(existing)
            }
        }, 5000)

        Thread {
            OtaUpdater.checkAndUpdate(this, object : OtaUpdater.ProgressListener {
                override fun onProgress(percent: Int, statusText: String) {
                    runOnUiThread { loadingStatus.text = statusText }
                }

                override fun onFinished(hotpatchDir: File?, updated: Boolean) {
                    runOnUiThread {
                        if (updated && serverStarted) {
                            // Сервер в этом процессе уже когда-то запускался
                            // со старым кодом — "на лету" его не подменить
                            // (модуль app уже импортирован и закэширован
                            // Python'ом, порт уже занят). Единственный
                            // надёжный способ подхватить свежескачанный
                            // app.py — перезапустить процесс целиком.
                            loadingStatus.text = "Обновление готово, перезапуск…"
                            restartProcessToApplyUpdate()
                            return@runOnUiThread
                        }
                        proceedWithHotpatch(hotpatchDir)
                    }
                }
            })
        }.start()
    }

    /** Полный перезапуск приложения — единственный надёжный способ подхватить
     * hot-patch, скачанный поверх уже работающего в этом процессе сервера. */
    private fun restartProcessToApplyUpdate() {
        val intent = packageManager.getLaunchIntentForPackage(packageName)
        intent?.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivity(intent)
        Runtime.getRuntime().exit(0)
    }

    private fun startPythonServerOnce(hotpatchDir: File?) {
        if (serverStarted) {
            // Сервер в этом процессе уже поднят — просто грузим страницу.
            webView.post { webView.loadUrl("http://127.0.0.1:$PORT/") }
            return
        }
        serverStarted = true

        val hotpatchPath = hotpatchDir?.absolutePath ?: ""

        Thread {
            val py = Python.getInstance()
            val launcher = py.getModule("bridge_launcher")
            launcher.callAttr("start_server", PORT, filesDir.absolutePath, hotpatchPath)
        }.start()
    }

    private fun waitForServerThenLoad() {
        Thread {
            var up = false
            var attempts = 0
            while (!up && attempts < 200) {
                attempts++
                try {
                    Socket().use { s ->
                        s.connect(InetSocketAddress("127.0.0.1", PORT), 300)
                        up = true
                    }
                } catch (e: Exception) {
                    Thread.sleep(200)
                }
            }
            runOnUiThread {
                val status = findViewById<TextView>(R.id.loadingStatus)
                if (up) {
                    status.visibility = View.GONE
                    webView.loadUrl("http://127.0.0.1:$PORT/")
                } else {
                    status.text = "Не удалось запустить локальный сервер.\nПерезапустите приложение."
                }
            }
        }.start()
    }

    /** Доступно из JS страницы как window.AndroidBridge.<метод>(). */
    inner class AndroidBridge {
        @JavascriptInterface
        fun pickRbxlFile() {
            val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                addCategory(Intent.CATEGORY_OPENABLE)
                type = "*/*"
            }
            filePickerLauncher.launch(intent)
        }

        /** Приватная папка приложения — сюда сервер пишет временные файлы
         * перед экспортом через SAF (сам сервер SAF-Uri не видит). */
        @JavascriptInterface
        fun getDataDir(): String = filesDir.absolutePath

        /** sourcePath — файл, который сервер уже записал в приватное
         * хранилище (см. getDataDir). suggestedName — имя по умолчанию
         * в диалоге "Сохранить как". */
        @JavascriptInterface
        fun exportRbxlFile(sourcePath: String, suggestedName: String) {
            pendingExportSourcePath = sourcePath
            val intent = Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
                addCategory(Intent.CATEGORY_OPENABLE)
                type = "application/octet-stream"
                putExtra(Intent.EXTRA_TITLE, suggestedName)
            }
            saveFileLauncher.launch(intent)
        }

        /** Открывает экран логина roblox.com. Результат (успех/неудача)
         * приходит на страницу через window.onRobloxAuthUpdated(bool). */
        @JavascriptInterface
        fun loginToRoblox() {
            robloxLoginLauncher.launch(Intent(this@MainActivity, RobloxLoginActivity::class.java))
        }

        /** true, если ранее уже успешно логинились и кука ещё сохранена
         * локально (её актуальность на сервере Roblox не проверяется —
         * это делает сам Python при первом запросе). */
        @JavascriptInterface
        fun isRobloxLoggedIn(): Boolean = robloxAuthFile.exists()

        @JavascriptInterface
        fun logoutRoblox() {
            robloxAuthFile.delete()
        }
    }
}
