import os
from flask import Flask, render_template_string, request
import feedparser
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
import snscrape.modules.twitter as sntwitter

TOKEN = os.getenv("8625470192:AAGCLRkQzxgXJCrOdz9RQPXz6TMvlQz716I")
CHANNEL = "@kuponbazz"

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Haber siteleri
feeds = [
    "https://www.haberturk.com/rss/spor.xml",
    "https://www.fotomac.com.tr/rss/anasayfa.xml"
]

# X hesapları
accounts = [
    "FabrizioRomano",
    "TransferNewsTR"
]

news_cache = []
sent = set()

def fetch_news():
    global news_cache
    news_cache = []

    # RSS haberleri
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            news_cache.append({
                "title": entry.title,
                "link": entry.link
            })

    # X (Twitter) haberleri
    for user in accounts:
        try:
            for tweet in sntwitter.TwitterUserScraper(user).get_items():
                if len(news_cache) > 20:
                    break

                if tweet.content not in sent:
                    news_cache.append({
                        "title": tweet.content,
                        "link": tweet.url
                    })
                    sent.add(tweet.content)
        except:
            pass

def send_news(title, link):
    msg = f"🔥 *{title}*\n\nDetay 👇\n{link}"
    bot.send_message(chat_id=CHANNEL, text=msg, parse_mode="Markdown")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        index = int(request.form["index"])
        item = news_cache[index]
        send_news(item["title"], item["link"])

    html = """
    <h2>Futbol Haber Paneli</h2>
    <form method="post">
    {% for n in news %}
        <p>{{n.title}}</p>
        <button name="index" value="{{loop.index0}}">Gönder</button>
        <hr>
    {% endfor %}
    </form>
    """
    return render_template_string(html, news=news_cache)

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_news, 'interval', minutes=30)
scheduler.start()

fetch_news()

PORT = int(os.getenv("PORT", 5000))
app.run(host="0.0.0.0", port=PORT)
