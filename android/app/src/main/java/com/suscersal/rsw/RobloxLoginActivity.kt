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
    // true, как только WebView хоть раз показал именно /login — нужно,
    // чтобы отличать "мы ещё не покидали страницу входа" (кука может уже
    // быть, но это гостевая/техническая) от "юзер реально залогинился и
    // Roblox увёл его на другую страницу".
    private var sawLoginPage = false

    private val pollCookies = object : Runnable {
        override fun run() {
            if (finished) return
            if (sawLoginPage && loggedInByUrl()) {
                val cookie = extractRoblosecurity()
                if (cookie != null) {
                    finishWithCookie(cookie)
                    return
                }
            }
            handler.postDelayed(this, POLL_INTERVAL_MS)
        }
    }

    /** true, если текущий URL WebView больше не страница логина —
     * значит форма отправлена и Roblox увёл нас дальше (домой/на
     * подтверждение и т.п.). Именно ЭТОТ момент, а не факт наличия
     * .ROBLOSECURITY, надёжно говорит о реальном входе: гостевая версия
     * куки присутствует уже на самой странице /login, до ввода пароля. */
    private fun loggedInByUrl(): Boolean {
        val url = webView.url ?: return false
        return !url.contains("/login", ignoreCase = true) &&
            !url.contains("/signup", ignoreCase = true) &&
            (url.contains("roblox.com", ignoreCase = true))
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

        webView = findViewById(R.id.loginWebView)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        // Без этих двух флагов WebView рендерит страницу в фиксированном
        // "desktop" viewport (~980px) и потом сжимает её под экран —
        // отсюда эффект "всё мелкое/масштабировано не под реальное
        // разрешение". useWideViewPort включает уважение к <meta
        // viewport>, loadWithOverviewMode подгоняет начальный масштаб под
        // ширину экрана.
        webView.settings.useWideViewPort = true
        webView.settings.loadWithOverviewMode = true
        webView.settings.builtInZoomControls = true
        webView.settings.displayZoomControls = false
        // Roblox отдаёt урезанную/иначе свёрстанную страницу под desktop
        // User-Agent — подменяем на мобильный Chrome, чтобы получить
        // нормальную мобильную вёрстку логина.
        webView.settings.userAgentString =
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 " +
            "(KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
        cookieManager.setAcceptThirdPartyCookies(webView, true)
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView, url: String) {
                super.onPageFinished(view, url)
                if (url.contains("/login", ignoreCase = true)) {
                    sawLoginPage = true
                }
            }
        }
        webView.loadUrl(LOGIN_URL)

        findViewById<android.widget.Button>(R.id.closeLoginBtn).setOnClickListener {
            finished = true
            setResult(RESULT_CANCELED)
            finish()
        }

        handler.postDelayed(pollCookies, POLL_INTERVAL_MS)
    }

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
