import os
import telebot
import requests

TOKEN = "8718571147:AAFOSWu-vm_k0USxnEpwa1UwfOrNzZsQKhU"
GROQ_API_KEY = "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"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! အသံဖိုင် (သို့) Voice ပို့ပေးပါက စာသားအဖြစ် ပြောင်းပေးပါမည်။")

@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice(message):
    try:
        bot.reply_to(message, "🎙️ အသံဖိုင်ကို စစ်ဆေးနေပါသည်...")

        # Voice လား၊ Audio လား စစ်ပြီး file_id ယူခြင်း
        if message.voice:
            file_info = bot.get_file(message.voice.file_id)
            file_ext = "voice.ogg"
        elif message.audio:
            file_info = bot.get_file(message.audio.file_id)
            file_ext = "audio.mp3"
        else:
            bot.reply_to(message, "⚠️ ကျေးဇူးပြု၍ မှန်ကန်သော အသံဖိုင် (Voice / Audio) ကို ပို့ပေးပါ။")
            return

        downloaded_file = bot.download_file(file_info.file_path)

        with open(file_ext, "wb") as f:
            f.write(downloaded_file)

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        
        with open(file_ext, "rb") as audio_file:
            files = {"file": (file_ext, audio_file, "audio/ogg")}
            data = {"model": "whisper-large-v3"}
            
            response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            transcript = response.json().get("text", "စာသားအဖြစ် ပြောင်းလဲ၍ မရပါ။")
            bot.reply_to(message, f"📝 **ပြောင်းလဲထားသော စာသား:**\n\n{transcript}", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ အမှားအယွင်းရှိပါသည်: {response.text}")

        if os.path.exists(file_ext):
            os.remove(file_ext)

    except Exception as e:
        bot.reply_to(message, f"⚠️ ချို့ယွင်းချက်ရှိပါသည်: {str(e)}")

print("Bot စတင် အလုပ်လုပ်နေပါပြီ...")
bot.infinity_polling()
