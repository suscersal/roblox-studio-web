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
 * Обновление "горячих" файлов (app.py, rbxl_parser.py, index.html) без
 * пересборки и переустановки APK. Иконки (icons.txt, icons/) сюда
 * намеренно не входят — любое их изменение теперь всегда идёт через
 * полную сборку APK (см. build-and-release.yml), поэтому OtaUpdater про
 * них ничего не знает.
 *
 * Логика:
 *  0. Если versionCode установленного APK вырос с прошлого запуска (значит,
 *     только что поставили новый полный релиз) — стираем старый hotpatch,
 *     чтобы он не перекрывал свежий baked-in код (см.
 *     invalidateHotpatchIfAppWasUpdated). Это нужно, потому что полные
 *     релизы больше не публикуют version.json — см. пункт про эндпоинт ниже.
 *  1. Скачиваем ota/version.json из САМОГО СВЕЖЕГО GitHub Release репозитория
 *     (его туда кладёт CI — см. .github/workflows/build-and-release.yml и
 *     scripts/generate-ota-manifest.sh).
 *  2. Сравниваем версию с сохранённой локально (SharedPreferences).
 *  3. Если версия новее — качаем изменившиеся файлы (по sha256) в
 *     filesDir/hotpatch и сохраняем новую версию.
 *
 * ВАЖНО про выбор эндпоинта: используем /releases (список), а НЕ
 * /releases/latest. Причина — hot-update релизы (см. workflow,
 * publish-hot-update) специально помечены prerelease: true, чтобы не быть
 * "latest release" для releases/latest/download/app-debug.apk (та ссылка
 * обязана указывать на релиз, где есть APK). Но раз они prerelease —
 * GitHub-эндпоинт /releases/latest их не отдаст, и это приложение
 * перестало бы видеть hot-обновления.
 *
 * ВАЖНО про сортировку: порядок элементов в /releases НИГДЕ не
 * гарантирован GitHub'ом (в отличие от /releases/latest, где явно
 * задокументировано "сортировка по created_at"). На практике он иногда
 * не совпадает с датой публикации. Поэтому просто брать releases[0] как
 * "самый новый" — ошибка: он может внезапно оказаться НЕ последним, и
 * тогда приложение перестаёт видеть новые hot-update'ы (символ этого бага
 * — "первое обновление подтянулось, следующие — нет"). Вместо этого
 * забираем небольшое окно последних релизов и сами выбираем среди них
 * самый новый по полю created_at.
 */
object OtaUpdater {

    private const val OWNER = "suscersal"
    private const val REPO = "roblox-studio-web"
    private const val PREFS = "ota_prefs"
    private const val KEY_VERSION = "hot_version"
    private const val KEY_APP_VERSION_CODE = "app_version_code"

    // Окно последних релизов, среди которых сами ищем самый новый по
    // created_at — см. пояснение про ненадёжный порядок /releases выше.
    private val RELEASES_LIST_URL =
        "https://api.github.com/repos/$OWNER/$REPO/releases?per_page=10"

    interface ProgressListener {
        /** percent от 0 до 100, statusText — что показать пользователю */
        fun onProgress(percent: Int, statusText: String)
        /** updated — true, если только что реально скачали новые/изменённые файлы */
        fun onFinished(hotpatchDir: File?, updated: Boolean)
    }

    fun hotpatchDir(ctx: Context): File = File(ctx.filesDir, "hotpatch")

    /**
     * Вызывать из фонового потока (не UI thread) — делает сетевые запросы.
     * Колбэки listener'а вызывающая сторона сама переводит на UI-поток при
     * необходимости (см. MainActivity).
     */
    fun checkAndUpdate(ctx: Context, listener: ProgressListener) {
        try {
            listener.onProgress(0, "Проверка обновлений…")

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

            // Ищем среди ассетов релиза version.json
            var versionAssetUrl: String? = null
            val fileAssetUrls = HashMap<String, String>() // имя файла -> browser_download_url
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
                // В этом релизе нет OTA-пакета — это нормально для обычных
                // "полных" релизов (там всё уже запечено в APK, см.
                // build-and-release.yml). Он есть только у hot-update
                // релизов. Просто продолжаем со старой версией, если она
                // уже скачана раньше.
                listener.onFinished(existingHotpatchOrNull(ctx), false)
                return
            }

            val remoteManifest = httpGetJson(versionAssetUrl)
            val remoteVersion = remoteManifest.getString("version")
            val remoteFiles = remoteManifest.getJSONObject("files")

            val prefs = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            val localVersion = prefs.getString(KEY_VERSION, null)

            val dir = hotpatchDir(ctx)

            // Даже если версия совпадает, но папки ещё нет (первый запуск
            // после установки) — качаем всё равно.
            if (localVersion == remoteVersion && dir.exists()) {
                listener.onFinished(dir, false)
                return
            }

            dir.mkdirs()

            val names = remoteFiles.keys().asSequence().toList()
            var done = 0
            var downloaded = 0
            for (name in names) {
                val expectedHash = remoteFiles.getString(name)
                val destFile = File(dir, name)
                val actualHash = if (destFile.exists()) sha256(destFile) else null
                Log.d(
                    "OtaUpdater",
                    "check $name: expected=$expectedHash actual=$actualHash exists=${destFile.exists()} size=${destFile.length()}"
                )

                // Пропускаем файл, если он уже скачан и хэш совпадает —
                // это ускоряет докачку, когда изменилась только часть файлов.
                if (actualHash == expectedHash) {
                    done++
                    listener.onProgress(
                        (done * 100 / names.size),
                        "Проверено $done/${names.size} (без изменений)"
                    )
                    continue
                }

                val downloadUrl = fileAssetUrls[name] ?: fileAssetUrls[name.substringAfterLast('/')]
                if (downloadUrl != null) {
                    destFile.parentFile?.mkdirs()
                    downloadToFile(downloadUrl, destFile)
                    downloaded++
                }

                done++
                listener.onProgress(
                    (done * 100 / names.size),
                    "Скачано $downloaded, проверено $done/${names.size}"
                )
            }

            prefs.edit().putString(KEY_VERSION, remoteVersion).apply()
            listener.onFinished(dir, true)
        } catch (e: Exception) {
            // Нет сети / GitHub недоступен / репозиторий приватный и т.п. —
            // не блокируем запуск приложения, просто работаем на том, что
            // уже было скачано раньше (или на версии из APK, если ничего
            // ещё не скачивалось).
            listener.onFinished(existingHotpatchOrNull(ctx), false)
        }
    }

    /**
     * Полные релизы (v1.N) больше не публикуют version.json (см.
     * build-and-release.yml — там теперь только APK), поэтому
     * checkAndUpdate() не может узнать "вышел новый полный релиз" по сети.
     * Вместо этого узнаём это локально: versionCode установленного APK
     * (см. android/app/build.gradle, ANDROID_VERSION_CODE) растёт только
     * при полной пересборке и всегда >= версии любого hot-update,
     * опубликованного до неё. Если он вырос с прошлого запуска — значит,
     * только что установили новый полный APK, и код внутри него уже как
     * минимум не старее любого ранее скачанного hot-patch. Стираем
     * устаревший hotpatch, чтобы он не перекрывал свежий baked-in код
     * из нового APK (bridge_launcher.py подставляет hotpatch в начало
     * sys.path, если папка существует).
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
     * created_at — формат ISO-8601 UTC ("2026-07-26T12:00:00Z"), поэтому
     * обычное лексикографическое сравнение строк корректно даёт
     * хронологический порядок — полноценный парсинг даты не нужен.
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
        // HttpURLConnection иногда сам добавляет "Accept-Encoding: gzip" и
        // прозрачно разжимает ответ — отключаем это явно, чтобы не гадать,
        // не отсюда ли берётся расхождение в байтах/хэше.
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
