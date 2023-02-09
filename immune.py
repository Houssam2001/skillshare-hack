#######################
#   HeckerNoHecking   #
#######################


# including all necessary modules
import requests, os
from flask import Flask, render_template, request, redirect, url_for
from threading import Thread


app = Flask('')

cookie = os.environ['cookie']
pk = os.environ['pk']
account_id = os.environ['brightcove_account_id']

@app.route('/<id>')
def getcourse(id):
  if id!="favicon.ico":
    with open("logs.txt", "a") as file: file.write(f"ID - {id}\n")
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
    vid_links.append(getvid(video_id, account_id))
  
  for i in range(len(vid_names)):
    print(f'{i+1} - {vid_names[i]} {vid_links[i]}')

  # return vid_links[2]
  return render_template('download.html', title=data['title'], thumb=data['image_huge'], vid_links=vid_links, vid_names=vid_names)


@app.route('/heck', methods=['POST'])
def heckURL():
  # print(request.form['url'])
  # with open("laas.txt", "a") as file: file.write(f"URL - {request.form['url']}\n")
  if request.method == 'POST':
    url = request.form['url']
    if url.startswith('https://www.skillshare.com/'):
      id = url.split('/')[-1].split("?")[0]
      return redirect(url_for('getcourse', id=id))
    else:
      return -1


@app.route('/')
def howto():
  return render_template('index.html')

@app.route('/play')
def play():
  return render_template('play.html')

def run():
  app.run(host='0.0.0.0', port=8080)

def immune():
    t = Thread(target=run)
    t.start()