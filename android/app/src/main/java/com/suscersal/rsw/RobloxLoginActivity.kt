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
 * Shows the ordinary roblox.com login page in a WebView (the same
 * system WebView as the main screen — but separate from it, so as not to
 * mix Roblox cookies into the local server's 127.0.0.1 cookies).
 *
 * As soon as a valid .ROBLOSECURITY appears in the CookieManager for the .roblox.com domain
 * (it is set only after a successful sign-in), we take
 * it and close the screen with RESULT_OK, returning the cookie via an extra.
 *
 * The Kotlin side uses this cookie nowhere else — it just saves it
 * into a private app file, from which Python (app.py) reads it for
 * authorized requests to the Roblox API.
 */
class RobloxLoginActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_COOKIE = "roblox_cookie"
        private const val LOGIN_URL = "https://www.roblox.com/login"
        private const val COOKIE_DOMAIN = "https://www.roblox.com"
        // We check cookies not after every single micro-navigation inside the
        // login SPA, but on a timer — this catches more reliably the moment when the
        // Roblox server really set .ROBLOSECURITY after login.
        private const val POLL_INTERVAL_MS = 700L
    }

    private lateinit var webView: WebView
    private val handler = Handler(Looper.getMainLooper())
    private var finished = false
    // true as soon as the WebView has shown /login at least once — needed
    // to tell "we haven't left the sign-in page yet" (the cookie may already
    // exist, but it's a guest/technical one) from "the user really logged in and
    // Roblox moved them to another page".
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

    /** true if the WebView's current URL is no longer the login page —
     * meaning the form was submitted and Roblox took us further (home/to
     * confirmation, etc.). Exactly THIS moment, not the mere presence of
     * .ROBLOSECURITY, reliably indicates a real sign-in: the guest version of the
     * cookie is present already on the /login page itself, before the password is entered. */
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

        // A separate WebView for login mustn't share cookies with the user's ordinary
        // browsing outside the app — but must
        // share them between its own requests (a JS fetch on the
        // login page itself uses the same CookieManager). This is the default behavior
        // for android.webkit.CookieManager — there is one per
        // process, so no explicit action is needed.
        val cookieManager = CookieManager.getInstance()
        cookieManager.setAcceptCookie(true)

        webView = findViewById(R.id.loginWebView)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        // Without these two flags the WebView renders the page in a fixed
        // "desktop" viewport (~980px) and then shrinks it to the screen —
        // hence the effect "everything is small/scaled not for the real
        // resolution". useWideViewPort makes it honor <meta
        // viewport>, loadWithOverviewMode fits the initial scale to
        // the screen width.
        webView.settings.useWideViewPort = true
        webView.settings.loadWithOverviewMode = true
        webView.settings.builtInZoomControls = true
        webView.settings.displayZoomControls = false
        // Roblox serves a trimmed/differently laid out page for a desktop
        // User-Agent — we swap in a mobile Chrome one to get
        // a normal mobile login layout.
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
        // A cookie is valid only if the value is non-empty and it isn't the technical
        // "guest" version — just in case we check a minimum length.
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
