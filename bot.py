import os
from telethon import TelegramClient, events, Button
from dotenv import load_dotenv
import random
import aiohttp

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Store game state
game_states = {}

# Create the client
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send a message when the command /start is issued."""
    buttons = [
        [Button.text("📸 إرسال صورة"), Button.text("🎮 ألعاب")],
        [Button.text("ℹ️ مساعدة")]
    ]
    await event.respond(
        'مرحباً! 👋\n'
        'أنا بوت متعدد المهام. اختر من القائمة أدناه ما تريد القيام به.',
        buttons=buttons
    )

@client.on(events.NewMessage(pattern='/help'))
async def help_command(event):
    """Send a message when the command /help is issued."""
    help_text = """
الأوامر المتاحة:
/start - بدء المحادثة
/help - عرض هذه المساعدة
/photo - إرسال صورة عشوائية
/game - بدء لعبة

يمكنك أيضاً استخدام الأزرار في القائمة الرئيسية للوصول إلى هذه الميزات.
"""
    await event.respond(help_text)

@client.on(events.NewMessage(pattern='/photo'))
async def send_photo(event):
    """Send a random photo with caption."""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://picsum.photos/400/300") as response:
            if response.status == 200:
                photo = await response.read()
                await event.respond("صورة عشوائية جميلة! 🎨", file=photo)
            else:
                await event.respond("عذراً، حدث خطأ أثناء تحميل الصورة.")

@client.on(events.NewMessage(pattern='/game'))
async def start_game(event):
    """Start a simple number guessing game."""
    buttons = [
        [
            Button.inline("1", b"guess_1"),
            Button.inline("2", b"guess_2"),
            Button.inline("3", b"guess_3")
        ],
        [
            Button.inline("4", b"guess_4"),
            Button.inline("5", b"guess_5"),
            Button.inline("6", b"guess_6")
        ]
    ]
    
    # Store random number in game state
    chat_id = event.chat_id
    game_states[chat_id] = random.randint(1, 6)
    
    await event.respond(
        "لنلعب لعبة تخمين الأرقام! 🎲\nاخترت رقماً من 1 إلى 6. هل يمكنك تخمينه؟",
        buttons=buttons
    )

@client.on(events.CallbackQuery())
async def button_callback(event):
    """Handle button callbacks."""
    if event.data.startswith(b"guess_"):
        chat_id = event.chat_id
        if chat_id not in game_states:
            await event.respond("عذراً، انتهت اللعبة. استخدم /game للبدء من جديد.")
            return
            
        guess = int(event.data.split(b"_")[1])
        correct = game_states[chat_id]
        
        if guess == correct:
            await event.respond("🎉 أحسنت! لقد خمنت الرقم الصحيح!")
        else:
            await event.respond(f"❌ للأسف خطأ! الرقم الصحيح كان {correct}")
        
        # Clear game state
        del game_states[chat_id]

@client.on(events.NewMessage())
async def handle_text(event):
    """Handle text messages and keyboard buttons."""
    text = event.raw_text
    
    if text == "📸 إرسال صورة":
        await send_photo(event)
    elif text == "ℹ️ مساعدة":
        await help_command(event)
    elif text == "🎮 ألعاب":
        await start_game(event)

def main():
    """Start the bot."""
    print("البوت يعمل الآن...")
    client.run_until_disconnected()

if __name__ == '__main__':
    main()
