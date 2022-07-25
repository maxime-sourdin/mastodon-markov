from mastodon import Mastodon
from mastodon import Mastodon, StreamListener
from bs4 import BeautifulSoup
import re,os, markovify, json, time, schedule, logging, threading, requests

class Stream(StreamListener):
    def __init__(self): #Héritage
        super(Stream, self).__init__()
        # self.logger = logging.getLogger

    def on_notification(self,notif): #Appelé lorsqu'une notification arrive
        if notif['type'] == 'mention': #Vérifiez si le contenu de la notification est une réponse
            content = notif['status']['content'] #C'est le corps principal de la réponse
            id = notif['status']['account']['username']
            st = notif['status']
            main(content, st, id)

#if not path.exists("clientcred.secret"):
#        print("No clientcred.secret, registering application")
#        client.create_app("ebooks", api_base_url=api_base_url, to_file="cred/clientcred.secret", scopes=scopes)

#if not path.exists("usercred.secret"):
#        print("No usercred.secret, registering application")
#        email = input("Email: ")
#        password = getpass("Password: ")
#        client = Mastodon(client_id="clientcred.secret", api_base_url=api_base_url)
#        client.log_in(email, password, to_file="cred/usercred.secret", scopes=scopes)

def parse_toot(toot):
    if toot.spoiler_text != "": return
    if toot.reblog is not None: return
    if toot.visibility not in ["public", "unlisted"]: return

    soup = BeautifulSoup(toot.content, "html.parser")

    # pull the mentions out
    # for mention in soup.select("span.h-card"):
    #     mention.unwrap()

    # for mention in soup.select("a.u-url.mention"):
    #     mention.unwrap()

    # we will destroy the mentions until we're ready to use them
    # someday turbocat, you will talk to your sibilings
    for mention in soup.select("span.h-card"):
        mention.decompose()

    # make all linebreaks actual linebreaks
    for lb in soup.select("br"):
        lb.insert_after("\n")
        lb.decompose()

    # make each p element its own line because sometimes they decide not to be
    for p in soup.select("p"):
        p.insert_after("\n")
        p.unwrap()

    # keep hashtags in the toots
    for ht in soup.select("a.hashtag"):
        ht.unwrap()

    # unwrap all links (i like the bots posting links)
    for link in soup.select("a"):
        link.insert_after(link["href"])
        link.decompose()

    text = map(lambda a: a.strip(), soup.get_text().strip().split("\n"))

    # next up: store this and patch markovify to take it
    # return {"text": text, "mentions": mentions, "links": links}
    # it's 4am though so we're not doing that now, but i still want the parser updates
    return "\0".join(list(text))

def get_toots(client, id):
    i = 0
    toots = client.account_statuses(id)
    while toots is not None and len(toots) > 0:
        for toot in toots:
            t = parse_toot(toot)
            if t != None:
                yield t
        toots = client.fetch_next(toots)
        i += 1
        if i%10 == 0:
            print(i)

def job():
    logging.info("Background 1 thread running...")
    api_base_url = "https://botsin.space"
    scopes = ["read:statuses", "read:accounts", "read:follows", "write:statuses"]
    spoiler_text = os.environ['cw']
    visibility = os.environ['visibility']
    client_id = os.environ['clientid.secret']
    client_secret = os.environ['clientsecret.secret']
    access_token = os.environ['accesstoken.secret']

    client = Mastodon(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            api_base_url=api_base_url)

    me = client.account_verify_credentials()
    following = client.account_following(me.id)

    with open("/data/corpus.txt", "a") as fp:
        for f in following:
            for t in get_toots(client, f.id):
                fp.write(t + "\n")

    # publishing toot
    with open("/data/corpus.txt") as fp:
        model = markovify.NewlineText(fp.read())
    sentence = None
    # you will make that damn sentence
    while sentence is None:
        sentence = model.make_sentence(tries=100000)
    print("tooting:", model)    
    client.status_post(sentence.replace("\0", "\n"),visibility=visibility,spoiler_text=spoiler_text)

def resp(content,st,id):
    logging.info("Background 1 thread running...")
    api_base_url = "https://botsin.space"
    scopes = ["read:statuses", "read:accounts", "read:follows", "write:statuses"]
    spoiler_text = os.environ['cw']
    visibility = os.environ['visibility']
    client_id = os.environ['clientid.secret']
    client_secret = os.environ['clientsecret.secret']
    access_token = os.environ['accesstoken.secret']

    client = Mastodon(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            api_base_url=api_base_url)

    me = client.account_verify_credentials()
    following = client.account_following(me.id)    
    req = content.rsplit(">")[-2].split("<")[0].strip() #Supprimer les informations supplémentaires du corps de la réponse
    r_date = requests.get(url + "?title=" + req, headers="") #Hit api
    print(req)
    with open("/data/corpus.txt") as fp:
        model = markovify.NewlineText(fp.read())
    sentence = None
    # you will make that damn sentence
    while sentence is None:
        sentence = model.make_sentence(tries=100000)
    print("tooting:", model)    
    client.status_reply(st, sentence.replace("\0", "\n"),id, visibility=visibility,spoiler_text=spoiler_text)
    notif = client.notifications() #Avoir des notifications
    count = 0
    while True:
        if notif[count]['type'] == 'mention':
            if notif[count]['status']['replies_count'] == 0: #Vérifiez si la réponse a déjà été faite
                content = notif[count]['status']['content']
                id = notif[count]['status']['account']['username']
                st = notif[count]['status']
                main(content, st, id)
                count += 1
            else:
                break
        else:
            count += 1
        count += 1
    client.stream_user(Stream())

def run_continuously():
    cease_continuous_run = threading.Event()
    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.info("Main - starting thread")
    schedule.every(3).hours.until(timedelta(hours=12)).do(job)
    schedule.every(1).hours.do(resp)           
    stop_run_continuously = run_continuously()
    logging.info("Main: completed !!")
    time.sleep(5)
    stop_run_continuously.set()
