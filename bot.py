import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, CLASS_SCHEDULE, HOLIDAYS, USER_ID, SEMESTER_START, SEMESTER_END
from database import AttendanceDB
from attendance import AttendanceCalculator

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database and calculator
db = AttendanceDB()
for holiday in HOLIDAYS:
    db.add_holiday(holiday['date'], holiday['name'], holiday['type'])

calc = AttendanceCalculator(db)

# States for conversation
ADD_DATE, SELECT_STATUS, CONFIRM_DELETE = range(3)

# ============ COMMAND HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command and show main menu"""
    user_id = update.effective_user.id
    db.set_user_setting(user_id, 70)
    
    # Format semester dates dynamically
    sem_start = SEMESTER_START.strftime('%d %B %Y')
    sem_end = SEMESTER_END.strftime('%d %B %Y')
    
    welcome_text = f"""📚 **Welcome to Attendance Bot!**

GS PMP Polytechnic, Gandhinagar
Semester 3, Computer Engineering

🎯 **Target Attendance:** 70%
📅 **Semester:** {sem_start} - {sem_end}

Choose an option below:"""
    
    keyboard = [
        [InlineKeyboardButton("📝 Mark Today", callback_data='today')],
        [InlineKeyboardButton("📊 Stats", callback_data='stats')],
        [InlineKeyboardButton("🎯 Predict Bunk", callback_data='predict')],
        [InlineKeyboardButton("📅 Add Past Date", callback_data='add_date')],
        [InlineKeyboardButton("📋 History", callback_data='history')],
        [InlineKeyboardButton("🏖️ Holidays", callback_data='holidays')],
        [InlineKeyboardButton("⚙️ Settings", callback_data='settings')],
        [InlineKeyboardButton("❓ Help", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = """❓ **HELP & COMMANDS**

**Commands:**
/start - Show main menu
/today - Mark today's attendance
/stats - View current attendance
/predict - How many classes can I bunk?
/history - View recent attendance
/holidays - Upcoming holidays
/help - This message

**About:**
This bot tracks your attendance for GS PMP Polytechnic.
- Target: 70% attendance
- Classes: Mon-Fri, 6 slots/day
- Database: SQLite (local storage)

**Features:**
✅ Auto-schedule tracking
✅ Holiday calendar integration
✅ Bunking capacity calculator
✅ Attendance predictions
✅ Past date entry

**Usage Tips:**
1. Mark attendance daily
2. Check stats weekly
3. Add forgotten dates anytime
4. Use predict to plan semester

📧 For issues, check the GitHub repo"""
    
    if update.message:
        await update.message.reply_text(help_text, parse_mode='Markdown')
    else:
        await update.callback_query.message.reply_text(help_text, parse_mode='Markdown')

# ============ CALLBACK HANDLERS ============

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    if query.data == 'today':
        await mark_today(query, user_id)
    elif query.data == 'stats':
        await show_stats(query, user_id)
    elif query.data == 'predict':
        await show_predict(query, user_id)
    elif query.data == 'add_date':
        await query.edit_message_text("📅 Enter date (YYYY-MM-DD format):\ne.g., 2025-07-22")
        return ADD_DATE
    elif query.data == 'history':
        await show_history(query, user_id)
    elif query.data == 'holidays':
        await show_holidays(query)
    elif query.data == 'settings':
        await show_settings(query, user_id)
    elif query.data == 'help':
        await help_command(update, context)
    elif query.data.startswith('status_'):
        status = query.data.split('_')[1]
        await mark_attendance(query, user_id, status)
    elif query.data.startswith('holiday_override_'):
        await query.edit_message_text("Mark as holiday override? Confirm: YES or NO")
        return CONFIRM_DELETE

async def mark_today(query, user_id):
    """Mark attendance for today"""
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    weekday = today.weekday()
    
    # Check if weekend
    if weekday > 4:
        await query.edit_message_text("❌ No classes on weekends!")
        return
    
    # Check if holiday
    holiday_name = db.is_holiday(today_str)
    if holiday_name:
        keyboard = [
            [InlineKeyboardButton("✅ Present", callback_data='status_present')],
            [InlineKeyboardButton("❌ Absent", callback_data='status_absent')],
            [InlineKeyboardButton("🚑 Leave", callback_data='status_leave')],
            [InlineKeyboardButton("🏖️ Holiday Override", callback_data='holiday_override_yes')],
        ]
        await query.edit_message_text(
            f"⚠️ **{holiday_name}** is a holiday!\n\nStill want to mark attendance?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    # Show status options
    classes = calc.get_classes_for_date(today)
    class_count = len(classes)
    
    keyboard = [
        [InlineKeyboardButton("✅ Present", callback_data='status_present')],
        [InlineKeyboardButton("❌ Absent", callback_data='status_absent')],
        [InlineKeyboardButton("🚑 Leave", callback_data='status_leave')],
    ]
    
    text = f"""📅 **Today: {today.strftime('%A, %d %B %Y')}**

📚 Classes: {class_count}

Mark your attendance:"""
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def mark_attendance(query, user_id, status):
    """Save attendance status"""
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    classes = calc.get_classes_for_date(today)
    class_count = len(classes)
    
    db.add_attendance(user_id, today_str, status, class_count)
    
    emoji = {'present': '✅', 'absent': '❌', 'leave': '🚑'}[status]
    status_text = {'present': 'Present', 'absent': 'Absent', 'leave': 'Leave'}[status]
    
    # Calculate current stats
    percentage, attended, total = calc.calculate_attendance_percentage(user_id)
    max_bunk = calc.calculate_max_bunk(user_id, 70)
    
    text = f"""{emoji} **{status_text}** marked for today!

📊 **Current Stats:**
- Attended: {attended} classes
- Total: {total} classes
- Attendance: {percentage}%
- Can bunk: {max_bunk} classes safely

🎯 Target: 70%
"""
    
    await query.edit_message_text(text, parse_mode='Markdown')

async def show_stats(query, user_id):
    """Show attendance statistics"""
    percentage, attended, total = calc.calculate_attendance_percentage(user_id)
    max_bunk = calc.calculate_max_bunk(user_id, 70)
    
    if total == 0:
        text = "📊 **No attendance records yet!**\nStart by marking today's attendance."
    else:
        target = 70
        needed = int((target / 100) * total) - attended
        
        status_emoji = "✅" if percentage >= target else "⚠️"
        
        text = f"""{status_emoji} **ATTENDANCE STATISTICS**

📈 **Current Stats:**
- Present: {attended} classes
- Total: {total} classes
- Percentage: **{percentage}%**

🎯 **Target: {target}%**

📋 **Analysis:**
- Status: {'✅ Above Target' if percentage >= target else '⚠️ Below Target'}
- To reach 75%: Need {max(0, needed)} more classes
- Can safely bunk: {max_bunk} classes

💡 **Pro Tip:** Add past dates if you missed marking some attendance!
"""
    
    await query.edit_message_text(text, parse_mode='Markdown')

async def show_predict(query, user_id):
    """Show bunking predictions"""
    percentage, attended, total = calc.calculate_attendance_percentage(user_id)
    
    if total == 0:
        text = "📊 **No data yet!** Mark attendance first to see predictions."
        await query.edit_message_text(text, parse_mode='Markdown')
        return
    
    # Get next 30, 60, 90 day predictions
    bunk_30, classes_30 = calc.predict_future_attendance(user_id, 30, 70)
    bunk_60, classes_60 = calc.predict_future_attendance(user_id, 60, 70)
    bunk_90, classes_90 = calc.predict_future_attendance(user_id, 90, 70)
    
    text = f"""📊 **BUNKING PREDICTIONS**

📊 **Current:** {percentage}% ({attended}/{total} classes)

**Next 30 Days:**
- Classes coming: {classes_30}
- Can bunk: {bunk_30} classes
- Projected: {round((attended + classes_30 - bunk_30) / (total + classes_30) * 100, 2)}%

**Next 60 Days:**
- Classes coming: {classes_60}
- Can bunk: {bunk_60} classes
- Projected: {round((attended + classes_60 - bunk_60) / (total + classes_60) * 100, 2)}%

**Next 90 Days (Semester End):**
- Classes coming: {classes_90}
- Can bunk: {bunk_90} classes
- Projected: {round((attended + classes_90 - bunk_90) / (total + classes_90) * 100, 2)}%

💡 **Strategy:** Attend more now, enjoy later!
"""
    
    await query.edit_message_text(text, parse_mode='Markdown')

async def show_history(query, user_id):
    """Show attendance history"""
    records = db.get_all_attendance(user_id, 20)
    
    if not records:
        text = "📋 **No attendance records yet!**"
        await query.edit_message_text(text, parse_mode='Markdown')
        return
    
    text = "📋 **Recent Attendance (Last 20 Days)**\n\n"
    text += "| Date | Status | Classes |\n"
    text += "|------|--------|---------|\n"
    
    for date, status, slots in records:
        emoji = {'present': '✅', 'absent': '❌', 'leave': '🚑'}[status]
        text += f"| {date} | {emoji} {status} | {slots} |\n"
    
    await query.edit_message_text(text, parse_mode='Markdown')

async def show_holidays(query):
    """Show upcoming holidays"""
    holidays = calc.get_upcoming_holidays(90)
    
    if not holidays:
        text = "🏖️ **No holidays upcoming!**"
        await query.edit_message_text(text, parse_mode='Markdown')
        return
    
    text = "🏖️ **UPCOMING HOLIDAYS**\n\n"
    
    for date, name, hol_type in holidays:
        emoji = "🇮🇳" if hol_type == 'national' else "🏫"
        text += f"{emoji} **{date}** - {name}\n"
    
    await query.edit_message_text(text, parse_mode='Markdown')

async def show_settings(query, user_id):
    """Show settings menu"""
    current_target = db.get_user_target(user_id)
    
    text = f"""⚙️ **SETTINGS**

📊 Current Target: {current_target}%

Options:
- Type new target % (e.g., 75)
- Or use default 70%
"""
    
    keyboard = [
        [InlineKeyboardButton("70%", callback_data='target_70')],
        [InlineKeyboardButton("75%", callback_data='target_75')],
        [InlineKeyboardButton("80%", callback_data='target_80')],
        [InlineKeyboardButton("Back", callback_data='back_menu')],
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ============ MESSAGE HANDLERS ============

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check if it's a date (ADD_DATE state)
    if len(context.user_data.get('state', [])) > 0 and context.user_data['state'][-1] == ADD_DATE:
        try:
            date_obj = datetime.strptime(text, '%Y-%m-%d').date()
            date_str = date_obj.strftime('%Y-%m-%d')
            
            # Check if date is in future
            if date_obj > datetime.now().date():
                await update.message.reply_text("❌ Cannot add future dates!")
                return
            
            # Check if weekend
            if date_obj.weekday() > 4:
                await update.message.reply_text("❌ No classes on weekends!")
                return
            
            # Check if holiday
            holiday_name = db.is_holiday(date_str)
            if holiday_name:
                keyboard = [
                    [InlineKeyboardButton("✅ Present", callback_data=f'past_present_{date_str}')],
                    [InlineKeyboardButton("❌ Absent", callback_data=f'past_absent_{date_str}')],
                    [InlineKeyboardButton("🚑 Leave", callback_data=f'past_leave_{date_str}')],
                    [InlineKeyboardButton("Skip", callback_data='start')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f"⚠️ **{holiday_name}** is recorded as holiday.\nStill mark attendance?",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                return
            
            # Get classes for that day
            classes = calc.get_classes_for_date(date_obj)
            if not classes:
                await update.message.reply_text("❌ No classes on this day!")
                return
            
            # Show status options
            keyboard = [
                [InlineKeyboardButton("✅ Present", callback_data=f'past_present_{date_str}')],
                [InlineKeyboardButton("❌ Absent", callback_data=f'past_absent_{date_str}')],
                [InlineKeyboardButton("🚑 Leave", callback_data=f'past_leave_{date_str}')],
            ]
            
            text_msg = f"""📅 **{date_obj.strftime('%A, %d %B %Y')}**

📚 Classes: {len(classes)}

Mark attendance:"""
            
            await update.message.reply_text(text_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            context.user_data['state'].pop()
            
        except ValueError:
            await update.message.reply_text("❌ Invalid date format! Use YYYY-MM-DD (e.g., 2025-07-22)")
            return
    
    # Check if it's a target percentage
    try:
        target = int(text)
        if 0 < target <= 100:
            db.set_user_setting(user_id, target)
            await update.message.reply_text(f"✅ Target updated to {target}%!")
            context.user_data['state'].pop() if context.user_data.get('state') else None
            return
    except ValueError:
        pass
    
    await update.message.reply_text("❌ Invalid input. Please try again.")

# ============ MAIN ============

def main():
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("🤖 Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
