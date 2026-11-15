package com.suscersal.rsw

import android.content.Context
import android.util.Log
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/**
 * Updating the "hot" files (app.py, rbxl_parser.py, index.html,
 * style.css, script.js — the exact list is set in
 * scripts/generate-ota-manifest.sh, this Kotlin side doesn't hardcode it,
 * but honestly takes it from version.json) without rebuilding or reinstalling the APK.
 * Icons (icons.txt, icons/) are
 * deliberately not included — any change to them now always goes through a
 * full APK build (see build-and-release.yml), so OtaUpdater knows
 * nothing about them.
 *
 * Logic:
 *  0. If the installed APK's versionCode has grown since the last launch (meaning
 *     a new full release was just installed) — we erase the old hotpatch
 *     so that it doesn't override the fresh baked-in code (see
 *     invalidateHotpatchIfAppWasUpdated). This is needed because full
 *     releases no longer publish version.json — see the endpoint note below.
 *  1. We download ota/version.json from the NEWEST GitHub Release of the repository
 *     (CI puts it there — see .github/workflows/build-and-release.yml and
 *     scripts/generate-ota-manifest.sh).
 *  2. We compare the version with the locally saved one (SharedPreferences).
 *  3. If the version is newer — we download the changed files (by sha256) into
 *     filesDir/hotpatch and save the new version.
 *
 * IMPORTANT about the endpoint choice: we use /releases (the list), NOT
 * /releases/latest. The reason: hot-update releases (see the workflow,
 * publish-hot-update) are deliberately marked prerelease: true so as not to become
 * the "latest release" for releases/latest/download/app-debug.apk (that link
 * must point to a release that has an APK). But since they are prereleases —
 * GitHub's /releases/latest endpoint won't return them, and this app
 * would stop seeing hot updates.
 *
 * IMPORTANT about sorting: the order of items in /releases is NOWHERE
 * guaranteed by GitHub (unlike /releases/latest, where "sorted by created_at"
 * is explicitly documented). In practice it sometimes
 * doesn't match the publication date. So simply taking releases[0] as
 * "the newest" is a mistake: it may suddenly turn out NOT to be the latest, and
 * then the app stops seeing new hot updates (the symptom of this bug
 * is "the first update came through, the following ones didn't"). Instead we
 * fetch a small window of the latest releases and pick the newest among them ourselves
 * by the created_at field.
 */
object OtaUpdater {

    private const val OWNER = "suscersal"
    private const val REPO = "roblox-studio-web"
    private const val PREFS = "ota_prefs"
    private const val KEY_VERSION = "hot_version"
    private const val KEY_APP_VERSION_CODE = "app_version_code"

    // The window of the latest releases, among which we ourselves look for the newest by
    // created_at — see the note about the unreliable /releases order above.
    private val RELEASES_LIST_URL =
        "https://api.github.com/repos/$OWNER/$REPO/releases?per_page=10"

    interface ProgressListener {
        /** percent from 0 to 100, statusText — what to show the user */
        fun onProgress(percent: Int, statusText: String)
        /** updated — true only if new/changed files were really just downloaded */
        fun onFinished(hotpatchDir: File?, updated: Boolean)
    }

    fun hotpatchDir(ctx: Context): File = File(ctx.filesDir, "hotpatch")

    /**
     * Call from a background thread (not the UI thread) — it makes network requests.
     * The caller itself moves the listener's callbacks to the UI thread when
     * needed (see MainActivity).
     */
    fun checkAndUpdate(ctx: Context, listener: ProgressListener) {
        try {
            listener.onProgress(0, ctx.getString(R.string.ota_checking))

            invalidateHotpatchIfAppWasUpdated(ctx)

            val releasesArray = httpGetJsonArray(RELEASES_LIST_URL)
            if (releasesArray.length() == 0) {
                listener.onFinished(existingHotpatchOrNull(ctx), false)
                return
            }
            val releaseJson = pickNewestByCreatedAt(releasesArray)
            val assets = releaseJson.optJSONArray("assets")
            if (assets == null || assets.length() == 0) {
                listener.onFinished(existingHotpatchOrNull(ctx), false)
                return
            }

            // We look for version.json among the release's assets
            var versionAssetUrl: String? = null
            val fileAssetUrls = HashMap<String, String>() // file name -> browser_download_url
            for (i in 0 until assets.length()) {
                val a = assets.getJSONObject(i)
                val name = a.getString("name")
                val url = a.getString("browser_download_url")
                if (name == "version.json") {
                    versionAssetUrl = url
                } else {
                    fileAssetUrls[name] = url
                }
            }

            if (versionAssetUrl == null) {
                // This release has no OTA package — that's normal for ordinary
                // "full" releases (everything is already baked into the APK there, see
                // build-and-release.yml). It exists only for hot-update
                // releases. We simply continue with the old version, if it
                // was already downloaded earlier.
                listener.onFinished(existingHotpatchOrNull(ctx), false)
                return
            }

            val remoteManifest = httpGetJson(versionAssetUrl)
            val remoteVersion = remoteManifest.getString("version")
            val remoteFiles = remoteManifest.getJSONObject("files")

            val prefs = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            val localVersion = prefs.getString(KEY_VERSION, null)

            val dir = hotpatchDir(ctx)

            // Even if the version matches but the folder doesn't exist yet (the first launch
            // after installation) — we download anyway.
            if (localVersion == remoteVersion && dir.exists()) {
                listener.onFinished(dir, false)
                return
            }

            dir.mkdirs()

            // We download into a TEMPORARY folder, not straight into hotpatch/, which
            // bridge_launcher.py immediately puts into sys.path and imports.
            // Previously, when the network dropped IN THE MIDDLE of the download (for example, app.py
            // was already overwritten with the new version while index.html was still old),
            // hotpatch/ was left with a mixed, inconsistent version of the code,
            // and the app either crashed or behaved unpredictably
            // depending on what exactly had managed to download before the drop.
            // Now we swap the files with a single atomic rename() only after
            // ALL files have been successfully downloaded and validated by hash.
            val stagingDir = File(ctx.filesDir, "hotpatch_staging")
            stagingDir.deleteRecursively()
            stagingDir.mkdirs()
            // We start with a copy of the current up-to-date files already present — we will
            // re-download only what has really changed.
            if (dir.exists()) {
                dir.copyRecursively(stagingDir, overwrite = true)
            }

            val names = remoteFiles.keys().asSequence().toList()
            var done = 0
            var downloaded = 0
            for (name in names) {
                val expectedHash = remoteFiles.getString(name)
                val destFile = File(stagingDir, name)
                val actualHash = if (destFile.exists()) sha256(destFile) else null
                Log.d(
                    "OtaUpdater",
                    "check $name: expected=$expectedHash actual=$actualHash exists=${destFile.exists()} size=${destFile.length()}"
                )

                // We skip a file if it is already downloaded and the hash matches —
                // this speeds up downloading when only some of the files changed.
                if (actualHash == expectedHash) {
                    done++
                    listener.onProgress(
                        (done * 100 / names.size),
                        ctx.getString(R.string.ota_checked, done, names.size)
                    )
                    continue
                }

                val downloadUrl = fileAssetUrls[name] ?: fileAssetUrls[name.substringAfterLast('/')]
                if (downloadUrl != null) {
                    destFile.parentFile?.mkdirs()
                    downloadToFile(downloadUrl, destFile)
                    // We check the hash right after downloading — a connection drop
                    // in the middle of a file must not silently pass as a "success".
                    val gotHash = sha256(destFile)
                    if (gotHash != expectedHash) {
                        throw java.io.IOException("Hash mismatch for $name after download")
                    }
                    downloaded++
                }

                done++
                listener.onProgress(
                    (done * 100 / names.size),
                    ctx.getString(R.string.ota_downloaded, downloaded, done, names.size)
                )
            }

            // All files are in place and verified — now in one atomic step
            // we swap the working hotpatch/ for the staging version. If the process
            // is killed right on this line, the disk still holds
            // EITHER a fully old OR a fully new folder — never
            // a mix.
            dir.deleteRecursively()
            stagingDir.renameTo(dir)

            prefs.edit().putString(KEY_VERSION, remoteVersion).apply()
            listener.onFinished(dir, true)
        } catch (e: Exception) {
            // No network / GitHub unavailable / the repository is private, etc. —
            // we don't block the app launch, we just work with what was
            // already downloaded earlier (or the version from the APK, if nothing
            // has been downloaded yet).
            listener.onFinished(existingHotpatchOrNull(ctx), false)
        }
    }

    /**
     * Full releases (v1.N) no longer publish version.json (see
     * build-and-release.yml — only the APK is there now), so
     * checkAndUpdate() can't learn "a new full release came out" over the network.
     * Instead we learn it locally: the installed APK's versionCode
     * (see android/app/build.gradle, ANDROID_VERSION_CODE) grows only
     * on a full rebuild and is always >= the version of any hot-update
     * published before it. If it has grown since the last launch — it means
     * a new full APK was just installed, and the code inside it is already at
     * least as new as any previously downloaded hot patch. We erase the
     * outdated hotpatch so that it doesn't override the fresh baked-in code
     * from the new APK (bridge_launcher.py puts hotpatch at the start of
     * sys.path if the folder exists).
     */
    private fun invalidateHotpatchIfAppWasUpdated(ctx: Context) {
        val currentVersionCode = try {
            @Suppress("DEPRECATION")
            ctx.packageManager.getPackageInfo(ctx.packageName, 0).versionCode
        } catch (e: Exception) {
            return
        }

        val prefs = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val seenVersionCode = prefs.getInt(KEY_APP_VERSION_CODE, -1)

        if (seenVersionCode != -1 && currentVersionCode > seenVersionCode) {
            hotpatchDir(ctx).deleteRecursively()
            prefs.edit()
                .remove(KEY_VERSION)
                .putInt(KEY_APP_VERSION_CODE, currentVersionCode)
                .apply()
        } else if (seenVersionCode == -1) {
            prefs.edit().putInt(KEY_APP_VERSION_CODE, currentVersionCode).apply()
        }
    }

    /**
     * created_at is the ISO-8601 UTC format ("2026-07-26T12:00:00Z"), so
     * an ordinary lexicographic string comparison correctly gives
     * chronological order — full date parsing isn't needed.
     */
    private fun pickNewestByCreatedAt(releases: JSONArray): JSONObject {
        var newest = releases.getJSONObject(0)
        var newestCreatedAt = newest.optString("created_at", "")
        for (i in 1 until releases.length()) {
            val candidate = releases.getJSONObject(i)
            val createdAt = candidate.optString("created_at", "")
            if (createdAt > newestCreatedAt) {
                newest = candidate
                newestCreatedAt = createdAt
            }
        }
        return newest
    }

    private fun existingHotpatchOrNull(ctx: Context): File? {
        val dir = hotpatchDir(ctx)
        return if (dir.exists() && dir.listFiles()?.isNotEmpty() == true) dir else null
    }

    private fun httpGetJson(urlStr: String): JSONObject {
        val conn = URL(urlStr).openConnection() as HttpURLConnection
        conn.setRequestProperty("Accept", "application/vnd.github+json")
        conn.connectTimeout = 8000
        conn.readTimeout = 8000
        conn.inputStream.use { input ->
            val text = input.bufferedReader().readText()
            return JSONObject(text)
        }
    }

    private fun httpGetJsonArray(urlStr: String): JSONArray {
        val conn = URL(urlStr).openConnection() as HttpURLConnection
        conn.setRequestProperty("Accept", "application/vnd.github+json")
        conn.connectTimeout = 8000
        conn.readTimeout = 8000
        conn.inputStream.use { input ->
            val text = input.bufferedReader().readText()
            return JSONArray(text)
        }
    }

    private fun downloadToFile(urlStr: String, dest: File) {
        val conn = URL(urlStr).openConnection() as HttpURLConnection
        conn.connectTimeout = 8000
        conn.readTimeout = 15000
        conn.instanceFollowRedirects = true
        // HttpURLConnection sometimes adds "Accept-Encoding: gzip" by itself and
        // transparently decompresses the response — we disable this explicitly so as not to guess
        // whether the byte/hash mismatch comes from there.
        conn.setRequestProperty("Accept-Encoding", "identity")
        conn.inputStream.use { input ->
            dest.outputStream().use { output ->
                input.copyTo(output)
            }
        }
    }

    private fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buf = ByteArray(8192)
            var n: Int
            while (input.read(buf).also { n = it } >= 0) {
                digest.update(buf, 0, n)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }
}