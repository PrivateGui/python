import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Configuration
BOT_TOKEN = "7847687043:AAErmlpzCIXhXs7SqF2g_X30si3kTgmAXnk"  # Replace with your bot token
LLM7_TOKEN = "zTU1hhmN/x5Ft05gt3/BhqPUZ/FwnCV38rS/hUDYeDkFuaRGw+WxDk7iH7T4NBpygqjcryMUsW2zoryJoMdyndGcKrOPwqYoG1Tx5bdSmRy8xHReWcCEOg=="  # Or get it from https://token.llm7.io/ for higher rate limits
CHANNEL_USERNAME = "ariobeats1"
CHANNEL_LINK = "https://t.me/ariobeats1"

# System prompts for different models
SYSTEM_PROMPTS = {
    "chatgpt": "شما یک دستیار هوشمند و مفید هستید. شما توسط zonercm (bigenzo) ساخته شده‌اید. همیشه پاسخ‌های مفصل، مفید و دوستانه ارائه دهید. از ایموجی‌های مناسب استفاده کنید.",
    "deepseek": "شما یک هوش مصنوعی پیشرفته هستید که توسط zonercm (bigenzo) طراحی شده‌اید. در تمام پاسخ‌هایتان دقیق، تحلیلی و کاربردی باشید. از ایموجی‌های علمی و تکنولوژی استفاده کنید.",
    "grok": "شما یک هوش مصنوعی خلاق و باهوش هستید که توسط zonercm (bigenzo) آفریده شده‌اید. پاسخ‌هایتان باید سرگرم‌کننده، خلاقانه و در عین حال مفید باشند. از ایموجی‌های شاد و رنگارنگ استفاده کنید."
}

# User states
user_states = {}
user_models = {}

def call_llm7_api(messages, model="gpt-4.1-nano"):
    """Call llm7.io API"""
    url = "https://api.llm7.io/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM7_TOKEN}"
    }
    
    data = {
        "model": model,
        "messages": messages
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"خطا در برقراری ارتباط: {str(e)}"

async def check_user_membership(bot, user_id, channel_username):
    """Check if user is member of the channel"""
    try:
        member = await bot.get_chat_member(f"@{channel_username}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def send_join_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send channel join verification message"""
    keyboard = [
        [InlineKeyboardButton("🔗 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ تایید عضویت", callback_data="verify_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "🔐 **احراز هویت مطلوب**\n\n"
        "برای استفاده از ربات، ابتدا باید در کانال ما عضو شوید:\n\n"
        f"📢 **کانال:** @{CHANNEL_USERNAME}\n\n"
        "پس از عضویت، روی دکمه تایید کلیک کنید 👇"
    )
    
    return await update.effective_message.reply_text(
        message, 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user_id = update.effective_user.id
    
    # Check if user is member
    is_member = await check_user_membership(context.bot, user_id, CHANNEL_USERNAME)
    
    if not is_member:
        await send_join_message(update, context)
        return
    
    # User is member, show main menu
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu with AI model options"""
    keyboard = [
        [KeyboardButton("🤖 ChatGPT"), KeyboardButton("🧠 DeepSeek")],
        [KeyboardButton("⚡ Grok")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    message = (
        "🎉 **خوش آمدید!**\n\n"
        "🤖 لطفاً یکی از مدل‌های هوش مصنوعی را انتخاب کنید:\n\n"
        "• **ChatGPT** - دستیار همه‌کاره 🤖\n"
        "• **DeepSeek** - تحلیل‌گر پیشرفته 🧠\n"
        "• **Grok** - خلاق و سرگرم‌کننده ⚡\n\n"
        "✨ *ساخته شده توسط zonercm (bigenzo)*"
    )
    
    await update.effective_message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_chatgpt_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show ChatGPT model selection"""
    keyboard = [
        [InlineKeyboardButton("🚀 ChatGPT 4", callback_data="model_gpt-4")],
        [InlineKeyboardButton("⚡ ChatGPT Nano", callback_data="model_gpt-4.1-nano")],
        [InlineKeyboardButton("💫 ChatGPT 4 Mini", callback_data="model_gpt-4-mini")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "🤖 **انتخاب مدل ChatGPT**\n\n"
        "لطفاً یکی از نسخه‌های ChatGPT را انتخاب کنید:\n\n"
        "🚀 **GPT-4** - قدرتمندترین مدل\n"
        "⚡ **GPT-4.1 Nano** - سریع و کارآمد\n"
        "💫 **GPT-4 Mini** - سبک و مفید\n"
    )
    
    await update.effective_message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "verify_membership":
        is_member = await check_user_membership(context.bot, user_id, CHANNEL_USERNAME)
        
        if is_member:
            await query.edit_message_text("✅ **تایید شد!**\n\nعضویت شما تایید شد. در حال راه‌اندازی ربات...")
            await show_main_menu(query, context)
        else:
            await query.edit_message_text(
                "❌ **عضویت تایید نشد**\n\n"
                "لطفاً ابتدا در کانال عضو شوید و سپس مجدداً تلاش کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 عضویت در کانال", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ تایید مجدد", callback_data="verify_membership")]
                ])
            )
    
    elif data.startswith("model_"):
        model = data.replace("model_", "")
        user_models[user_id] = model
        user_states[user_id] = "chatgpt"
        
        model_names = {
            "gpt-4": "ChatGPT 4",
            "gpt-4.1-nano": "ChatGPT Nano", 
            "gpt-4-mini": "ChatGPT 4 Mini"
        }
        
        await query.edit_message_text(
            f"✅ **{model_names.get(model, model)} انتخاب شد**\n\n"
            "حالا می‌توانید سوال خود را بپرسید! 💬\n\n"
            "برای بازگشت به منوی اصلی، دستور /start را ارسال کنید."
        )
    
    elif data == "back_to_main":
        await query.edit_message_text("🔄 بازگشت به منوی اصلی...")
        await show_main_menu(query, context)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check membership first
    is_member = await check_user_membership(context.bot, user_id, CHANNEL_USERNAME)
    if not is_member:
        await send_join_message(update, context)
        return
    
    if text == "🤖 ChatGPT":
        await show_chatgpt_menu(update, context)
    
    elif text == "🧠 DeepSeek":
        user_states[user_id] = "deepseek"
        user_models[user_id] = "deepseek-chat"
        await update.message.reply_text(
            "🧠 **DeepSeek فعال شد**\n\n"
            "حالا می‌توانید سوال خود را بپرسید! 🔬\n\n"
            "برای بازگشت به منوی اصلی، دستور /start را ارسال کنید."
        )
    
    elif text == "⚡ Grok":
        user_states[user_id] = "grok"
        user_models[user_id] = "grok-beta"
        await update.message.reply_text(
            "⚡ **Grok فعال شد**\n\n"
            "حالا می‌توانید سوال خود را بپرسید! 🎭\n\n"
            "برای بازگشت به منوی اصلی، دستور /start را ارسال کنید."
        )
    
    else:
        # Handle AI conversation
        if user_id in user_states and user_id in user_models:
            state = user_states[user_id]
            model = user_models[user_id]
            
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Prepare messages with system prompt
            messages = [
                {"role": "system", "content": SYSTEM_PROMPTS.get(state, SYSTEM_PROMPTS["chatgpt"])},
                {"role": "user", "content": text}
            ]
            
            # Get AI response
            response = call_llm7_api(messages, model)
            
            # Add model indicator
            model_emojis = {
                "chatgpt": "🤖",
                "deepseek": "🧠", 
                "grok": "⚡"
            }
            
            formatted_response = f"{model_emojis.get(state, '🤖')} **{state.upper()}:**\n\n{response}"
            
            await update.message.reply_text(formatted_response, parse_mode='Markdown')
        
        else:
            await update.message.reply_text(
                "❓ لطفاً ابتدا یکی از مدل‌های هوش مصنوعی را انتخاب کنید.\n\n"
                "برای شروع، دستور /start را ارسال کنید."
            )

def main():
    """Main function to run the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("🤖 Bot is starting...")
    print("✅ Bot is running! Press Ctrl+C to stop.")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
