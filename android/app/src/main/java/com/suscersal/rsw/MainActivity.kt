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

class MainActivity : AppCompatActivity() {

    companion object {
        // Состояние процесса, а не Activity — сервер должен стартовать
        // только один раз за жизнь процесса (см. комментарий в maxclient:
        // повторный вызов app.run() на уже занятом порту упадёт).
        private var serverStarted = false
        private const val PORT = 8080
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

        startPythonServerOnce()
        waitForServerThenLoad()
    }

    private fun startPythonServerOnce() {
        if (serverStarted) {
            // Сервер в этом процессе уже поднят — просто грузим страницу.
            webView.post { webView.loadUrl("http://127.0.0.1:$PORT/") }
            return
        }
        serverStarted = true

        Thread {
            val py = Python.getInstance()
            val launcher = py.getModule("bridge_launcher")
            launcher.callAttr("start_server", PORT, filesDir.absolutePath)
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

    /** Доступно из JS страницы как window.AndroidBridge.pickRbxlFile(). */
    inner class AndroidBridge {
        @JavascriptInterface
        fun pickRbxlFile() {
            val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                addCategory(Intent.CATEGORY_OPENABLE)
                type = "*/*"
            }
            filePickerLauncher.launch(intent)
        }
    }
}
