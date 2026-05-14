import java.io.*
import java.net.*
import java.security.MessageDigest
import org.json.JSONObject
import org.json.JSONArray

const val TOKEN = System.getenv("BOT_TOKEN") ?: error("BOT_TOKEN not set")
const val SITE_URL = "https://komorok.ru"
const val UPDATE_FILE = "last_update_id.txt"
const val FEEDBACK_FILE = "feedbacks.txt"

fun main() {
    val lastUpdateId = readLastUpdateId()
    val updates = getUpdates(lastUpdateId)
    
    for (update in updates) {
        val updateObj = update as JSONObject
        val updateId = updateObj.getInt("update_id")
        
        if (updateObj.has("message")) {
            val message = updateObj.getJSONObject("message")
            val chatId = message.getJSONObject("chat").getLong("id")
            val text = message.optString("text", "")
            
            when {
                text == "/start" -> handleStart(chatId)
                text.startsWith("/admin") -> handleAdmin(chatId, text.removePrefix("/admin").trim())
                text.startsWith("/") -> sendMessage(chatId, "Неизвестная команда. Используйте /start")
            }
        }
        
        if (updateObj.has("callback_query")) {
            val query = updateObj.getJSONObject("callback_query")
            val chatId = query.getJSONObject("message").getJSONObject("chat").getLong("id")
            val data = query.getString("data")
            
            when (data) {
                "check" -> handleCheck(chatId)
                "feedback" -> handleFeedbackPrompt(chatId)
            }
        }
        
        saveLastUpdateId(updateId)
    }
}

fun getUpdates(offset: Long): JSONArray {
    val url = URL("https://api.telegram.org/bot$TOKEN/getUpdates?offset=$offset&timeout=30")
    val conn = url.openConnection() as HttpURLConnection
    val response = conn.inputStream.bufferedReader().readText()
    val json = JSONObject(response)
    return json.optJSONArray("result") ?: JSONArray()
}

fun sendMessage(chatId: Long, text: String, replyMarkup: String? = null) {
    val url = URL("https://api.telegram.org/bot$TOKEN/sendMessage")
    val conn = url.openConnection() as HttpURLConnection
    conn.requestMethod = "POST"
    conn.setRequestProperty("Content-Type", "application/json")
    conn.doOutput = true
    
    val body = JSONObject()
    body.put("chat_id", chatId)
    body.put("text", text)
    if (replyMarkup != null) {
        body.put("reply_markup", JSONObject(replyMarkup))
    }
    
    conn.outputStream.write(body.toString().toByteArray())
    conn.inputStream.close()
}

fun handleStart(chatId: Long) {
    val keyboard = """
    {
        "inline_keyboard": [
            [{"text": "🟢 Проверить сайт", "callback_data": "check"}],
            [{"text": "📝 Оставить отзыв", "callback_data": "feedback"}]
        ]
    }
    """
    sendMessage(chatId, "👋 Привет! Я бот Komorok. Выберите действие:", keyboard)
}

fun handleCheck(chatId: Long) {
    val ok = try {
        val conn = URL(SITE_URL).openConnection() as HttpURLConnection
        conn.connectTimeout = 5000
        conn.readTimeout = 5000
        conn.responseCode == 200
    } catch (e: Exception) {
        false
    }
    sendMessage(chatId, if (ok) "✅ Сайт Komorok работает!" else "❌ Сайт не отвечает!")
}

fun handleFeedbackPrompt(chatId: Long) {
    sendMessage(chatId, "📝 Напишите ваш отзыв о сайте (одним сообщением).")
}

fun handleAdmin(chatId: Long, password: String) {
    if (password.isEmpty()) {
        sendMessage(chatId, "🔒 Используйте: /admin <пароль>")
        return
    }
    
    val hash = hashPassword(password)
    val expectedHash = System.getenv("ADMIN_DOUBLE_HASH") ?: ""
    
    if (hash != expectedHash) {
        sendMessage(chatId, "❌ Неверный пароль!")
        return
    }
    
    // Читаем отзывы
    val feedbacks = try {
        File(FEEDBACK_FILE).readText()
    } catch (e: Exception) {
        "Нет отзывов"
    }
    
    sendMessage(chatId, "📋 Отзывы:\n\n$feedbacks")
}

fun hashPassword(password: String): String {
    val first = MessageDigest.getInstance("SHA-256").digest(password.toByteArray())
        .joinToString("") { "%02x".format(it) }
    return MessageDigest.getInstance("SHA-256").digest(first.toByteArray())
        .joinToString("") { "%02x".format(it) }
}

fun readLastUpdateId(): Long {
    return try {
        File(UPDATE_FILE).readText().trim().toLongOrNull() ?: 0L
    } catch (e: Exception) {
        0L
    }
}

fun saveLastUpdateId(id: Long) {
    File(UPDATE_FILE).writeText(id.toString())
}