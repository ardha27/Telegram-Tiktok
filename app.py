from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO
import requests
from douyin_tiktok_scraper.scraper import Scraper
import logging

logging.getLogger().setLevel(logging.CRITICAL)

api = Scraper()
TOKEN = '6328020589:AAFnIjw-7dtEKYmiSAS6IO3T-tGeYo7ScpE'
BOT_USERNAME = '@ManukaAI_Bot'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, im Manuka')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Please type something so i can respond')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is custom command')

async def hybrid_parsing(url: str) -> dict:
    try:
        # Hybrid parsing(Douyin/TikTok URL)
        result = await api.hybrid_parsing(url)

        video = result["video_data"]["nwm_video_url_HQ"]
        music = result["music"]["play_url"]["uri"]
        caption = result["desc"]

        print("Video URL:", video)
        print("Play URL:", music)
        print("Caption:", caption)
        
        response_video = requests.get(video)

        if response_video.status_code == 200:
            video_stream = BytesIO(response_video.content)
        else:
            print(f"Failed to download MP4. Status code: {response_video.status_code}")

        
    except Exception as e:
        print(f'An error occurred: {str(e)}')
        return None

    return video_stream, music, caption

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
        else:
            return
    elif message_type == 'private':
        if "tiktok.com" in text:

            result = await hybrid_parsing(text)

            if result:
                video = result[0]
                music = result[1]
                caption = result[2]
                text = "Sound:\n" + music + "\n\n" + "Caption:\n" + caption

                await update.message.reply_video(video=InputFile(video), caption=text)
            else:
                await update.message.reply_text("Please send only TikTok URL")
        else:
            await update.message.reply_text("Please send a TikTok URL")
            return

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)


