package com.suscersal.rsw

import android.annotation.SuppressLint
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.webkit.CookieManager
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

/**
 * Показывает обычную страницу логина roblox.com в WebView (тот же
 * системный WebView, что и основной экран — отдельный от него, чтобы не
 * подмешивать куки Roblox в куки локального сервера 127.0.0.1).
 *
 * Как только в CookieManager для домена .roblox.com появляется валидный
 * .ROBLOSECURITY (он выставляется только после успешного входа), забираем
 * его и закрываем экран с RESULT_OK, вернув куку через extra.
 *
 * Kotlin-сторона больше нигде эту куку не использует — просто сохраняет
 * в приватный файл приложения, откуда её читает Python (app.py) для
 * авторизованных запросов к Roblox API.
 */
class RobloxLoginActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_COOKIE = "roblox_cookie"
        private const val LOGIN_URL = "https://www.roblox.com/login"
        private const val COOKIE_DOMAIN = "https://www.roblox.com"
        // Проверяем куки не после каждой отдельной micro-навигации внутри
        // SPA-логина, а по таймеру — так надёжнее ловим момент, когда
        // сервер Roblox реально проставил .ROBLOSECURITY после логина.
        private const val POLL_INTERVAL_MS = 700L
    }

    private lateinit var webView: WebView
    private val handler = Handler(Looper.getMainLooper())
    private var finished = false

    private val pollCookies = object : Runnable {
        override fun run() {
            if (finished) return
            val cookie = extractRoblosecurity()
            if (cookie != null) {
                finishWithCookie(cookie)
            } else {
                handler.postDelayed(this, POLL_INTERVAL_MS)
            }
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_roblox_login)

        // Отдельная WebView для логина не должна делить куки с обычным
        // просмотром сайтов пользователя вне приложения — но обязана
        // делить их между собственными запросами (JS fetch на самой
        // странице логина использует тот же CookieManager). Это поведение
        // по умолчанию для android.webkit.CookieManager — он один на
        // процесс, поэтому явных действий не требуется.
        val cookieManager = CookieManager.getInstance()
        cookieManager.setAcceptCookie(true)
        cookieManager.setAcceptThirdPartyCookies(webViewOrNull(), true)

        webView = findViewById(R.id.loginWebView)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true)
        webView.webViewClient = WebViewClient()
        webView.loadUrl(LOGIN_URL)

        findViewById<android.widget.Button>(R.id.closeLoginBtn).setOnClickListener {
            finished = true
            setResult(RESULT_CANCELED)
            finish()
        }

        handler.postDelayed(pollCookies, POLL_INTERVAL_MS)
    }

    private fun webViewOrNull(): WebView? = if (::webView.isInitialized) webView else null

    /** Ищет .ROBLOSECURITY в куках домена roblox.com. Возвращает полную
     * строку "ИМЯ=значение" — именно её ждёт заголовок Cookie в HTTP. */
    private fun extractRoblosecurity(): String? {
        val raw = CookieManager.getInstance().getCookie(COOKIE_DOMAIN) ?: return null
        val pair = raw.split(";")
            .map { it.trim() }
            .firstOrNull { it.startsWith(".ROBLOSECURITY=") }
            ?: return null
        // Кука валидна только если значение непустое и это не техническая
        // "гостевая" версия — на всякий случай проверяем минимальную длину.
        val value = pair.substringAfter("=")
        return if (value.length > 20) pair else null
    }

    private fun finishWithCookie(cookie: String) {
        finished = true
        handler.removeCallbacks(pollCookies)
        val intent = intent
        intent.putExtra(EXTRA_COOKIE, cookie)
        setResult(RESULT_OK, intent)
        finish()
    }

    override fun onDestroy() {
        handler.removeCallbacks(pollCookies)
        super.onDestroy()
    }
}
