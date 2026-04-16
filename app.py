import os
from flask import Flask, render_template_string, request
import feedparser
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = "8625470192:AAGCLRkQzxgXJCrOdz9RQPXz6TMvlQz716I"
CHANNEL = "@kuponbazz"

bot = Bot(token=TOKEN)
app = Flask(__name__)

feeds = [
    "https://www.haberturk.com/rss/spor.xml",
    "https://www.fotomac.com.tr/rss/anasayfa.xml"
]

news_cache = []

def fetch_news():
    global news_cache
    news_cache = []
    try:
        for url in feeds:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                news_cache.append({
                    "title": entry.title,
                    "link": entry.link
                })
    except Exception as e:
        print("Haber çekme hatası:", e)

def send_news(title, link):
    try:
        msg = f"🔥 *{title}*\n\nDetay 👇\n{link}"
        bot.send_message(chat_id=CHANNEL, text=msg, parse_mode="Markdown")
    except Exception as e:
        print("Telegram gönderme hatası:", e)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        index = int(request.form["index"])
        if index < len(news_cache):
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

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
