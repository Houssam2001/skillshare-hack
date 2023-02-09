from immune import immune
immune()

# telegram bot
# https://t.me/SkillshareHecker_Bot

import logging, os, requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import pyshorteners
shtn = pyshorteners.Shortener()


cookie = os.environ['cookie']
pk = os.environ['pk']
account_id = os.environ['brightcove_account_id']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)
def start(i, ctx):
  i.message.reply_text("Just give me the course URL.")
def help(i, ctx):
  i.message.reply_text("Just give me the course URL.")

def sendcourse(i, ctx):
  chatid = i.effective_chat.id
  if "skillshare.com/classes/" in i.message.text:
    ctx.bot.send_message(chat_id=chatid, text=f"<b>Gimme a moment.</b>", parse_mode="HTML")
    cid = demistifyurl(i.message.text)
    ccc = getcourse(cid)
    title = ccc[0]
    names = ccc[1]
    links = ccc[2]
    # ctx.bot.send_message(chat_id=chatid, text=f"<code>{title}</code>", parse_mode="HTML")
    msg=f"""<code>{title}</code>\n\n"""
    ctx.bot.send_message(chat_id=chatid, text=msg, parse_mode="HTML")    
    for num, q in enumerate(names):
      msg = f"<code>{num+1}.</code> <b>{q}</b> \n {links[num]}\n\n"
      ctx.bot.send_message(chat_id=chatid, text=msg, parse_mode="HTML")      
  else:
    i.message.reply_text("I can sense it's not a valid URL.")

def getcourse(id):
  url = f'https://api.skillshare.com/classes/{id}'
  data = requests.get(url, headers={'cookie': cookie}).json()
  vid_names = []
  vid_links = []
  def getvid(video_id, account_id):
    fetch = f'https://edge.api.brightcove.com/playback/v1/accounts/{account_id}/videos/{video_id}'
    vidjson = requests.get(fetch, headers={'Accept': 'application/json;pk='+pk}).json()
    if vidjson['sources'][6]['container'] == 'MP4' and 'src' in vidjson['sources'][6]:
      url = vidjson['sources'][6]['src']
    else:
      url = vidjson['sources'][1]['src']
    return url
  for i in data['_embedded']['sessions']['_embedded']['sessions']:
    video_id = i['video_hashed_id'].split(':')[1] if 'video_hashed_id' in i and i['video_hashed_id'] else None
    vid_names.append(i['title'])
    vid_links.append(shtn.isgd.short(getvid(video_id, account_id)))
  return [data['title'], vid_names, vid_links]

def error(i, ctx): logger.warning(f'Update {i} caused error {ctx.error}')

def demistifyurl(url): return url.split("?")[0].rsplit("/",1)[-1]

updater = Updater(os.environ['token'], use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(MessageHandler(Filters.text, sendcourse))
dp.add_error_handler(error)
updater.start_polling()
updater.idle()