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
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.io.File
import java.net.InetSocketAddress
import java.net.Socket
import org.json.JSONObject
import android.util.Log
import android.app.AlertDialog
import android.webkit.JsResult
import android.webkit.WebChromeClient

class MainActivity : AppCompatActivity() {

    companion object {
        // Process state, not Activity state — the server must start
        // only once per process lifetime (see the comment in maxclient:
        // a repeated app.run() call on an already busy port will fail).
        private var serverStarted = false
        private const val PORT = 47182 // keep in sync with PORT in app.py; 8080 is often taken by other apps/ADB
    }

    private lateinit var webView: WebView
    private var lastBackPressAt = 0L   // for «press Back again to exit»

    // Importing an .rbxl file through the system picker (SAF) — the only
    // reliable way to get a file chosen by the user under scoped
    // storage on Android 10+. We copy it into the app's private folder and
    // tell the page through a JS callback.
    //
    // A FIXED name "imported.rbxl" used to be used — if
    // the previous copy of that file for some reason stayed with
    // broken permissions (for example, MIUI/HyperOS "Memory cleanup"/
    // "Security manager" sometimes touches app files as part of
    // its storage optimization, or the file came from a data
    // restore on reinstall — neither can be reproduced live from a
    // sandbox, but both honestly explain Permission denied ON
    // READING a file that the very same process had just calmly
    // overwritten), EVERY following import ran into the same
    // broken file. Now — a new name for every import (a
    // timestamp), and if an old file with the fixed name is still lying around
    // from earlier app versions — we try to delete it too (not
    // critical if it fails). Plus: a copy error no longer
    // silently fails with an unhandled exception — we tell the page explicitly.
    // The real name of the chosen file (SAF gives a Uri like content://…/msf:1234 —
    // the name can't be derived from it, a DISPLAY_NAME query is needed). Without this «Recent»
    // showed the file under the name of our internal copy: imported_<digits>.rbxl.
    private fun displayNameOf(uri: Uri): String? = try {
        contentResolver.query(uri, arrayOf(android.provider.OpenableColumns.DISPLAY_NAME), null, null, null)
            ?.use { c -> if (c.moveToFirst()) c.getString(0) else null }
    } catch (e: Exception) {
        null
    }

    // The app works with a COPY of the chosen file (imported_<time>.rbxl in the private folder), so «Save»
    // used to change only the copy, while the original stayed untouched. We remember the original's Uri (SharedPreferences —
    // survives a restart, copyPath -> uri) and after writing the copy we rewrite the original with it.
    private val srcPrefs by lazy { getSharedPreferences("rsw_source_uris", MODE_PRIVATE) }

    private fun rememberSourceUri(copyPath: String, uri: Uri) {
        try {
            contentResolver.takePersistableUriPermission(
                uri, Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
        } catch (e: Exception) {
            try { contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION) } catch (_: Exception) {}
        }
        srcPrefs.edit().putString(copyPath, uri.toString()).apply()
    }

    private val filePickerLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val uri: Uri? = if (result.resultCode == RESULT_OK) result.data?.data else null
        if (uri == null) return@registerForActivityResult
        File(filesDir, "imported.rbxl").delete() // the old fixed name — best-effort cleanup
        val shownName: String? = displayNameOf(uri)
        val dest = File(filesDir, "imported_${System.currentTimeMillis()}.rbxl")
        try {
            contentResolver.openInputStream(uri)?.use { input ->
                dest.outputStream().use { output -> input.copyTo(output) }
            } ?: throw java.io.IOException("contentResolver returned an empty stream for $uri")
            rememberSourceUri(dest.absolutePath, uri)
            webView.evaluateJavascript(
                "window.onAndroidFileImported && window.onAndroidFileImported(${
                    org.json.JSONObject.quote(dest.absolutePath)
                }, null, ${shownName?.let { org.json.JSONObject.quote(it) } ?: "null"});",
                null
            )
        } catch (e: Exception) {
            dest.delete()
            webView.evaluateJavascript(
                "window.onAndroidFileImported && window.onAndroidFileImported(null, ${
                    org.json.JSONObject.quote(e.message ?: e.toString())
                });",
                null
            )
        }
    }

    // Importing an arbitrary local file (a zip with an avatar model
    // chosen/downloaded by the user beforehand) — the same SAF pattern
    // as filePickerLauncher for .rbxl, but it writes to a separate file and
    // calls its own JS callback so as not to be confused with opening a scene.
    private val avatarFilePickerLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val uri: Uri? = if (result.resultCode == RESULT_OK) result.data?.data else null
        if (uri == null) {
            webView.evaluateJavascript("window.onAvatarFilePicked && window.onAvatarFilePicked(null);", null)
            return@registerForActivityResult
        }
        val dest = File(filesDir, "avatar_import_tmp.zip")
        contentResolver.openInputStream(uri)?.use { input ->
            dest.outputStream().use { output -> input.copyTo(output) }
        }
        webView.evaluateJavascript(
            "window.onAvatarFilePicked && window.onAvatarFilePicked(${
                org.json.JSONObject.quote(dest.absolutePath)
            });",
            null
        )
    }

    // The path of the temporary file (in the app's private storage) that the
    // Flask server has just written via /api/save — we keep it here
    // between launching the SAF "Save as" dialog (exportRbxlFile) and
    // receiving the Uri chosen by the user in saveFileLauncher.
    private var pendingExportSourcePath: String? = null

    // The file where .ROBLOSECURITY is kept between app launches — the same
    // filesDir that is already passed into Python as RSW_DATA_DIR (see
    // bridge_launcher.start_server), so app.py reads the cookie directly
    // from there, without an additional transfer channel.
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

    // Export through the system picker (SAF, ACTION_CREATE_DOCUMENT) —
    // the only way to let the user save a file to a place of their choice
    // (Downloads, another app, etc.) under scoped storage.
    // The server can't write there itself — it has no access to the SAF Uri.
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

    // «Open with» from a file manager (ACTION_VIEW on an .rbxl): we copy the file the same way as after the picker,
    // and pass it to the page via window.onAndroidFileImported. If the page hasn't loaded yet (a cold start) —
    // the result waits in pendingIncomingJs until onPageFinished.
    @Volatile private var pendingIncomingJs: String? = null

    private fun handleIncomingIntent(intent: Intent?) {
        if (intent == null || intent.action != Intent.ACTION_VIEW) return
        val uri = intent.data ?: return
        intent.data = null   // don't process again when recreated
        Thread {
            val dest = File(filesDir, "imported_${System.currentTimeMillis()}.rbxl")
            val js: String = try {
                val shownName = displayNameOf(uri) ?: uri.lastPathSegment
                contentResolver.openInputStream(uri)?.use { input ->
                    dest.outputStream().use { output -> input.copyTo(output) }
                } ?: throw java.io.IOException("contentResolver returned an empty stream for $uri")
                rememberSourceUri(dest.absolutePath, uri)
                "window.onAndroidFileImported(${org.json.JSONObject.quote(dest.absolutePath)}, null, " +
                    "${shownName?.let { org.json.JSONObject.quote(it) } ?: "null"});"
            } catch (e: Exception) {
                dest.delete()
                "window.onAndroidFileImported(null, ${org.json.JSONObject.quote(e.message ?: e.toString())});"
            }
            // the function appears once script.js loads — we wait for it up to ~15 s
            pendingIncomingJs = "(function t(n){ if (window.onAndroidFileImported) { $js } else if (n < 50) setTimeout(function(){ t(n + 1); }, 300); })(0);"
            runOnUiThread { flushIncoming() }
        }.start()
    }

    private fun flushIncoming() {
        val js = pendingIncomingJs ?: return
        val url = webView.url ?: return
        if (!url.startsWith("http://127.0.0.1")) return   // the app is still loading — we'll call it from onPageFinished
        pendingIncomingJs = null
        webView.evaluateJavascript(js, null)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleIncomingIntent(intent)
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
        // Without a WebChromeClient the WebView silently returns false from window.confirm() and ignores alert(): because of this
        // «Open from Roblox» with a world already open was cancelled without a single dialog («Unsaved changes will be lost…»).
        webView.webChromeClient = object : WebChromeClient() {
            override fun onJsConfirm(view: WebView?, url: String?, message: String?, result: JsResult): Boolean {
                if (isFinishing) { result.cancel(); return true }
                AlertDialog.Builder(this@MainActivity)
                    .setMessage(message)
                    .setPositiveButton(android.R.string.ok) { _, _ -> result.confirm() }
                    .setNegativeButton(android.R.string.cancel) { _, _ -> result.cancel() }
                    .setOnCancelListener { result.cancel() }
                    .show()
                return true
            }

            override fun onJsAlert(view: WebView?, url: String?, message: String?, result: JsResult): Boolean {
                if (isFinishing) { result.confirm(); return true }
                AlertDialog.Builder(this@MainActivity)
                    .setMessage(message)
                    .setPositiveButton(android.R.string.ok) { _, _ -> result.confirm() }
                    .setOnCancelListener { result.confirm() }
                    .show()
                return true
            }
        }
        // WebGL for the 3D viewport — enabled by default in the modern
        // system WebView, no explicit flags are needed.
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                // the app page has loaded — we hand it the .rbxl we were opened with from the file manager
                if (url != null && url.startsWith("http://127.0.0.1")) flushIncoming()
            }
        }
        webView.addJavascriptInterface(AndroidBridge(), "AndroidBridge")
        handleIncomingIntent(intent)

        // «Back»: first we let the page close the topmost layer (a dialog, a menu, Play, «Panels» → «Scene»…) —
        // window.__handleBack() returns true if it closed something. Otherwise — WebView history, and exiting the app
        // only on a second press within 2 seconds.
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                webView.evaluateJavascript(
                    "(function(){try{return !!(window.__handleBack && window.__handleBack());}catch(e){return false;}})()"
                ) { handled ->
                    if (handled == "true") return@evaluateJavascript
                    if (webView.canGoBack()) {
                        webView.goBack()
                        return@evaluateJavascript
                    }
                    val now = System.currentTimeMillis()
                    if (now - lastBackPressAt < 2000) {
                        finish()
                    } else {
                        lastBackPressAt = now
                        Toast.makeText(this@MainActivity, getString(R.string.back_press_exit), Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })

        val loadingStatus = findViewById<TextView>(R.id.loadingStatus)
        loadingStatus.visibility = View.VISIBLE

        // OtaUpdater.checkAndUpdate catches network errors itself and shouldn't
        // hang longer than its HTTP timeouts (~8-16 s), but if there is no network
        // at all (DNS resolution sometimes hangs longer than connectTimeout) —
        // we hedge with a separate timer so that the app starts in any
        // case on the previously downloaded hotpatch (or on the code
        // from the APK, if nothing has been downloaded yet), rather than sitting on the splash
        // forever.
        val proceededOnce = java.util.concurrent.atomic.AtomicBoolean(false)

        fun proceedWithHotpatch(hotpatchDir: File?) {
            if (!proceededOnce.compareAndSet(false, true)) return
            loadingStatus.text = getString(R.string.loading_start)
            startPythonServerOnce(hotpatchDir)
            waitForServerThenLoad()
        }

        // Whether we have already started via the 5-second fallback (meaning the server
        // runs on OLD code while the OTA was still dragging on over a slow network).
        // If so and updated=true arrives later — we do NOT kill the process: the player
        // may already be actively working in the editor, and Runtime.exit(0) in the middle of a
        // session looks like "the app restarts/crashes by itself".
        // The new hotpatch is already fully on disk and its version is already saved
        // in SharedPreferences (see OtaUpdater.checkAndUpdate) — it simply
        // gets picked up on the next ordinary launch.
        val startedViaTimeoutFallback = java.util.concurrent.atomic.AtomicBoolean(false)

        android.os.Handler(mainLooper).postDelayed({
            if (!proceededOnce.get()) {
                val existing = OtaUpdater.hotpatchDir(this).let {
                    if (it.exists() && it.listFiles()?.isNotEmpty() == true) it else null
                }
                startedViaTimeoutFallback.set(true)
                loadingStatus.text = getString(R.string.loading_no_connection)
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
                        if (updated && serverStarted && !startedViaTimeoutFallback.get()) {
                            // The server in this process was already started at some point
                            // with the old code — it can't be swapped "on the fly"
                            // (the app module is already imported and cached by
                            // Python, the port is already taken). The only
                            // reliable way to pick up the freshly downloaded
                            // app.py is to restart the whole process.
                            //
                            // This path is possible only if the server started
                            // NOT via the 5-second fallback (that case is
                            // handled separately above) — for example, on
                            // re-entering an already created Activity.
                            loadingStatus.text = getString(R.string.loading_update_ready)
                            restartProcessToApplyUpdate()
                            return@runOnUiThread
                        }
                        proceedWithHotpatch(hotpatchDir)
                    }
                }
            })
        }.start()
    }

    /** A full app restart — the only reliable way to pick up a
     * hot patch downloaded on top of a server already running in this process. */
    private fun restartProcessToApplyUpdate() {
        val intent = packageManager.getLaunchIntentForPackage(packageName)
        intent?.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivity(intent)
        Runtime.getRuntime().exit(0)
    }

    private fun startPythonServerOnce(hotpatchDir: File?) {
        if (serverStarted) {
            // The server in this process is already up — we just load the page.
            // The port may differ from PORT (see waitForServerThenLoad), we take
            // it from the same file rather than from the constant.
            val portFile = File(filesDir, "server_port.txt")
            val resolvedPort = portFile.takeIf { it.exists() }
                ?.readText()?.trim()?.toIntOrNull() ?: PORT
            webView.post { webView.loadUrl("http://127.0.0.1:$resolvedPort/") }
            return
        }
        serverStarted = true

        // We clean up the file from the previous (possibly already dead) launch
        // so that waitForServerThenLoad doesn't connect by mistake to a port
        // on which nobody has been listening for a long time.
        File(filesDir, "server_port.txt").delete()

        val hotpatchPath = hotpatchDir?.absolutePath ?: ""

        Thread {
            try {
                val py = Python.getInstance()
                val launcher = py.getModule("bridge_launcher")
                launcher.callAttr("start_server", PORT, filesDir.absolutePath, hotpatchPath)
            } catch (e: Exception) {
                Log.e("MainActivity", "Server start failed", e)
                runOnUiThread {
                    findViewById<TextView>(R.id.loadingStatus).text = getString(R.string.loading_error, e.message)
                }
            }
    }.start()
    }

    private fun waitForServerThenLoad() {
        Thread {
            // bridge_launcher.py may move to PORT+1..+20 if the original
            // port hasn't been released since the process's previous launch (see the
            // comment in bridge_launcher.start_server). Previously the code here
            // always knocked on the fixed PORT and didn't notice that the
            // server had really come up on another port — the server worked,
            // but the webView never connected. The server_port.txt file
            // is written by the Python side right after a successful bind().
            val portFile = File(filesDir, "server_port.txt")
            var resolvedPort = PORT
            var up = false
            var attempts = 0
            while (!up && attempts < 100) {
                attempts++
                if (portFile.exists()) {
                    portFile.readText().trim().toIntOrNull()?.let { resolvedPort = it }
                }
                try {
                    Socket().use { s ->
                        s.connect(InetSocketAddress("127.0.0.1", resolvedPort), 700)
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
                    webView.loadUrl("http://127.0.0.1:$resolvedPort/")
                } else {
                    status.text = getString(R.string.server_start_failed)
                }
            }
        }.start()
    }

    /** Available from the page's JS as window.AndroidBridge.<method>(). */
    inner class AndroidBridge {
        @JavascriptInterface
        fun pickRbxlFile() {
            val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                addCategory(Intent.CATEGORY_OPENABLE)
                type = "*/*"
                // write permission + «remember» — so that «Save» can overwrite the chosen file, not only the copy
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION or
                        Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)
            }
            filePickerLauncher.launch(intent)
        }

        /** The app's private folder — the server writes temporary files here
         * before exporting via SAF (the server itself doesn't see the SAF Uri). */
        @JavascriptInterface
        fun getDataDir(): String = filesDir.absolutePath

        /** The versionCode of the installed APK (= the CI run number, tag v1.N). */
        @JavascriptInterface
        fun getAppVersionCode(): Int = try {
            packageManager.getPackageInfo(packageName, 0).versionCode
        } catch (e: Exception) { 0 }

        /** Writes the saved copy (copyPath = imported_*.rbxl) back into the ORIGINAL file chosen in the picker.
         * Returns "ok", "nosource" (this file has no source Uri — it wasn't opened via the picker) or "err:<reason>". */
        @JavascriptInterface
        fun writeBackToSource(copyPath: String): String {
            val uriStr = srcPrefs.getString(copyPath, null) ?: return "nosource"
            return try {
                val uri = Uri.parse(uriStr)
                val out = contentResolver.openOutputStream(uri, "wt") ?: return "err:no output stream"
                File(copyPath).inputStream().use { input -> out.use { input.copyTo(it) } }
                "ok"
            } catch (e: Exception) {
                "err:" + (e.message ?: e.toString())
            }
        }

        /** Opens a link (the release page) in an external browser. */
        @JavascriptInterface
        fun openUrl(url: String) {
            if (!url.startsWith("https://github.com/")) return
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        }

        /** sourcePath — a file that the server has already written into private
         * storage (see getDataDir). suggestedName — the default name
         * in the "Save as" dialog. */
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

        /** Opens the roblox.com login screen. The result (success/failure)
         * arrives at the page via window.onRobloxAuthUpdated(bool). */
        /** Opens the system picker to choose a .zip with an avatar (the one
         * downloaded earlier via "Download .zip", or any other with the same
         * set of files inside: avatar.obj, avatar.mtl, textures).
         * The result arrives in window.onAvatarFilePicked(path|null). */
        @JavascriptInterface
        fun pickAvatarZipFile() {
            val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                addCategory(Intent.CATEGORY_OPENABLE)
                type = "application/zip"
                putExtra(Intent.EXTRA_MIME_TYPES, arrayOf("application/zip", "application/octet-stream"))
            }
            avatarFilePickerLauncher.launch(intent)
        }

        @JavascriptInterface
        fun loginToRoblox() {
            robloxLoginLauncher.launch(Intent(this@MainActivity, RobloxLoginActivity::class.java))
        }

        /** true if we have already logged in successfully before and the cookie is still stored
         * locally (its validity on the Roblox server isn't checked —
         * the Python side does that itself on the first request). */
        @JavascriptInterface
        fun isRobloxLoggedIn(): Boolean = robloxAuthFile.exists()

        @JavascriptInterface
        fun logoutRoblox() {
            robloxAuthFile.delete()
        }
    }
}