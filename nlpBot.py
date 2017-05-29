from nltk.corpus import stopwords, PlaintextCorpusReader
from nltk.tokenize import word_tokenize
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import sqlite3
import itertools

#Initialize db
conn = sqlite3.connect('sentenceDatabase.db')
c = conn.cursor()
def createTable():
    c.execute('''CREATE TABLE IF NOT EXISTS sentences(username TEXT, sentence TEXT)''')
createTable()

#logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
logger = logging.getLogger(__name__)

#global vars
stop_words = set(stopwords.words("english"))
stop_words.update('[',']',',','"',"'",'(',')', ".")

#Bot Commands
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='I will process your and your friends natural language patterns!')

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def showID(bot, update):
    bot.sendMessage(update.message.chat_id, text=str(update.message.from_user.id))

def showStopWords(bot, update):
    bot.sendMessage(update.message.chat_id, text=str(stop_words))

def saveDataEntry(bot, update):
    conn = sqlite3.connect('sentenceDatabase.db')
    c = conn.cursor()
    sentence = update.message.text
    username = update.message.from_user.username
    c.execute("INSERT INTO sentences (username, sentence) VALUES (? , ?)", (username, sentence.lower()))
    conn.commit()
    c.close()
    conn.close()

def returnDataEntry(bot, update):
    conn = sqlite3.connect('sentenceDatabase.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sentences')
    data = c.fetchall()
    bot.sendMessage(update.message.chat_id, text=str(data))
    c.close()
    conn.close()

def showFreq(bot,update):
    conn = sqlite3.connect('sentenceDatabase.db')
    c = conn.cursor()
    sentenceLists=[]
    user = update.message.from_user.username
    c.execute('SELECT sentence FROM sentences WHERE username=?', (user,))
    data = c.fetchall()
    for i in data:
        sentenceLists.append(i)
    wordsFromSentence = word_tokenize(str(sentenceLists))
    for word in wordsFromSentence:
        wordList = list(word)
        if wordList[0] == "'":
            wordList[0] = ""
        word = "".join(wordList)
    filteredWords = [word for word in wordsFromSentence if not word in stop_words]
    freqFilteredWords = FreqDist(filteredWords)
    bot.sendMessage(update.message.chat_id, text=str(freqFilteredWords.most_common(50)))
    c.close()
    conn.close()

def main():

    #insert your api key here
    updater = Updater(key)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start",start))
    dp.add_handler(CommandHandler("showID",showID))
    dp.add_handler(CommandHandler("showStopWords",showStopWords))
    dp.add_handler(CommandHandler("returnDataEntry", returnDataEntry))
    dp.add_handler(CommandHandler("showFreq",showFreq))
    dp.add_handler(MessageHandler([Filters.text],saveDataEntry))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
