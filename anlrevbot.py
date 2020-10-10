import logging
import re
import csv
from datetime import timedelta
from anlquiz import Question, Quiz, create_quiz
from openpyxl import load_workbook
import configparser as cfg
workb = load_workbook("anlrev questions.xlsx")

from telegram import ReplyKeyboardMarkup, User, Sticker, StickerSet
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence)

# Define read config function
def read_token(config):
    parser = cfg.ConfigParser()
    parser.read(config)
    return parser.get('creds','token')

# Define Bot Token
config = 'config.cfg'
TOKEN = read_token(config)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define Conversation states
CHOOSE_MOD, CHOOSE_NUMQ, ASKING, CHECKING, RATING = range(5)

# Define custom keyboards

anl_keyboard =[['ANL303', 'ANL305', 'ANL321']]

anl_mods = ReplyKeyboardMarkup(anl_keyboard, one_time_keyboard=True)

num_keyboard = [['10', '15', '20']]

num = ReplyKeyboardMarkup(num_keyboard, one_time_keyboard=True)

ready_keyboard = [['Yes', 'No']]

ready = ReplyKeyboardMarkup(ready_keyboard, one_time_keyboard=True)

answer_keyboard = [['A', 'B', 'C'],
                  ['Skip'],
                  ['Quit']]
answer = ReplyKeyboardMarkup(answer_keyboard, one_time_keyboard=True)

rate_keyboard = [['1 \n(Bad)', '2 \n(Poor)'],
                ['3 \n(Decent)', '4 \n(Good)'],
                ['5 \n(Great)']]

rate = ReplyKeyboardMarkup(rate_keyboard, one_time_keyboard=True)

# Define Sticker objects for result memes lol
smart = Sticker("CAADAQADpQADj7KDCfIKqAyRIYxZFgQ", 512, 291, False)
disappoint = Sticker("CAADAQADrQEAAphGpgi7YIB3m1Z86xYE", 512, 361, False)

#Create persistence object
user_persistence = PicklePersistence(filename="userid")

# Define callback functions in Conversation Handler

# Start function that takes handles /start command
def start(update, context):
    context.user_data['id'] = update.message.from_user.id
    first_name = update.message.from_user.first_name
    context.user_data['name'] = first_name
    context.chat_data['date'] = update.message.date
    update.message.reply_text(
        f"Hello {first_name}, welcome to the ANL Revision bot!\n"
        "Which module would you like to revise?",
        reply_markup=anl_mods)

    return CHOOSE_MOD

# Function  to store module name
def receive_mod(update,context):
    module = update.message.text
    context.chat_data['module'] = module
    update.message.reply_text(
        f"You have chosen to revise {module}\n"
        f'How many questions?',
        reply_markup=num)

    return CHOOSE_NUMQ

# Function to initialize quiz
def receive_num(update, context):
    module = context.chat_data['module']
    num_q = int(update.message.text)
    context.chat_data['num_q'] = num_q
    update.message.reply_text(
        f"You have chosen {num_q} questions \n")
    this_Quiz = Quiz(module, num_q, workb)
    context.chat_data['quiz'] = this_Quiz
    update.message.reply_text(
        'Start quiz?',
        reply_markup=ready)

    return ASKING

def receive_rating(update, context):
    rated = int(update.message.text[0])
    context.user_data['rating'] = rated
    user_id = context.user_data['id']
    row = [user_id, rated]
    with open('anlbotrating.csv', mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(row)
    csv_file.close()

    update.message.reply_text("Thank you for your feedback!")
    update.message.reply_text("All the best for your papers!\nType /start to try again")
    return ConversationHandler.END

# Function to ask questions
def ask_q(update, context):
    this_Quiz = context.chat_data['quiz']
    num_q = context.chat_data['num_q']
    if this_Quiz.q_counter < num_q:
        update.message.reply_text(
        f"Question {this_Quiz.q_counter+1}.\n"
        f"{this_Quiz.ask()}\n\n"
        f"{this_Quiz.show_choices()}",
        reply_markup=answer)
        result = CHECKING
    else:
        result = done(update, context)
    return result

# Function to check user answer
def check_ans(update, context):
    user_ans = update.message.text
    this_Quiz = context.chat_data['quiz']
    if user_ans.upper() == this_Quiz.show_answer():
        result = "That is correct!"
        this_Quiz.user_score +=1
    else:
        result = f"Sorry, that is not correct, the correct answer is {this_Quiz.show_answer()}"
    this_Quiz.q_counter += 1
    context.chat_data['score'] = this_Quiz.user_score
    update.message.reply_text(
        f"{result} \n")
    return ask_q(update, context)

# Function to handle skip input
def skip(update, context):
    this_Quiz = context.chat_data['quiz']
    update.message.reply_text(
        f"Skipped question, the correct answer is {this_Quiz.show_answer()}")
    this_Quiz.q_counter += 1
    return ask_q(update, context)

# Function to handle quit input and end of quiz
def done(update, context):
    # Define variables to be captured
    user_id = context.user_data['id']
    first_name = context.user_data['name']
    module = context.chat_data['module']
    num_q = context.chat_data['num_q']
    this_Quiz = context.chat_data['quiz']
    chat_date = context.chat_data['date']
    adjusted_date = chat_date + timedelta(hours=8)
    if this_Quiz.q_counter == 0:
        update.message.reply_text("Goodbye, type /start to try again")
        return ConversationHandler.END
    else:
        r_score = context.chat_data['score']
        t_score = r_score/this_Quiz.q_counter
        # Write variables to csv file
        row = [user_id, first_name, module, num_q, r_score, adjusted_date]
        with open('anlbotdata.csv', mode='a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(row)
        csv_file.close()

        # Display results of quiz to user
        update.message.reply_text(f"End of Quiz\nYour score is {r_score}/{this_Quiz.q_counter}\n")
        if r_score == 0:
            update.message.reply_text("https://www.wikihow.com/Embrace-Failure")
        elif 0 < t_score <= 0.5:
            update.message.reply_sticker(disappoint)
        elif t_score <= 0.8:
            update.message.reply_sticker(smart)
        else:
            update.message.reply_text("https://college.harvard.edu/admissions/apply")
    try:
        rated = context.user_data['rating']
        update.message.reply_text(f"You have already rated this bot")
        update.message.reply_text("All the best for your papers!\nType /start to try again")
    except:
        update.message.reply_text(
            "Please take a moment to rate this bot:",
        reply_markup=rate)
        return RATING

    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(TOKEN, persistence=user_persistence, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={

            CHOOSE_MOD: [MessageHandler(Filters.regex(re.compile(r'^(ANL303|ANL305|ANL321)$', re.I)), receive_mod)],

            CHOOSE_NUMQ :[MessageHandler(Filters.regex('^(10|15|20)$'), receive_num)],


            ASKING: [MessageHandler(Filters.regex(re.compile(r'^(Yes)$', re.I)), ask_q),
                     MessageHandler(Filters.regex(re.compile(r'^(No)$', re.I)), done)],


            CHECKING: [MessageHandler(Filters.regex(re.compile(r'^(A|B|C|)$',re.I)), check_ans),
                        MessageHandler(Filters.regex(re.compile(r'^(Skip)$', re.I)), skip),
                        MessageHandler(Filters.regex(re.compile(r'^(Quit)$', re.I)), done)],

            RATING: [MessageHandler(Filters.regex('^(1|2|3|4|5)'), receive_rating)]
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()