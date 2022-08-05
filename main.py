from mastodon import Mastodon, StreamListener
from bs4 import BeautifulSoup
import re,os, markovify, json, threading, random, time, datetime, threading, signal

def parse_toot(toot):
    try: 
        if toot.spoiler_text != "": return
        if toot.reblog is not None: return
        if toot.visibility not in ["public", "unlisted"]: return
        soup = BeautifulSoup(toot.content, "html.parser")
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
        return "\0".join(list(text))
        print(time.strftime("%H:%M:%S"), " - Parsing toots...") 
    except:
        print(time.strftime("%H:%M:%S"), " - Failed to parse toots!") 
        pid = os.getpid()
        os.kill(pid, signal.SIGTERM)

def get_toots(client, id):
    try: 
        i = 0
        toots = client.account_statuses(id,only_media=False,pinned=False,exclude_replies=True)
        while toots is not None and len(toots) > 0:
            for toot in toots:
                t = parse_toot(toot)
                if t != None:
                    yield t
            toots = client.fetch_next(toots)
            i += 1
            print(time.strftime("%H:%M:%S"), " - Getting toots (", i, "...)") 
    except:
        print(time.strftime("%H:%M:%S"), " - Failed to get toots!") 

def writetoot(client):
    try:
        i = 0
        while True:         
            # Get toots and store it on file
            with open(corpus_location, "a") as fp:
                for f in following:
                    for t in get_toots(client, f.id):
                        fp.write(t + "\n")
                        i += 1                        
                        print(today, "- Saving toots (", i, ")...")
    except:
        print(time.strftime("%H:%M:%S"), " - Failed to save toots!") 

def job(client):
    try: 
        while True:    
            # publishing toot
            with open(corpus_location) as fp:
                model = markovify.NewlineText(fp.read())
                sentence = None
                while sentence is None:
                    sentence = model.make_sentence(tries=1000000000)  
                status = client.status_post(sentence.replace("\0", "\n"),visibility=visibility,spoiler_text=spoiler_text)
                print(time.strftime("%H:%M:%S"), "- Publishing.... (every", sleep_duration, "s)")
                time.sleep(sleep_duration)
    except:
        print("Toot generation failed !") 
        pid = os.getpid()
        os.kill(pid, signal.SIGTERM)

def reply(client):
    try:
        while True:
                notifications = client.notifications()
                for notification in notifications:            
                    n_id = notification["id"]
                    n_acct = notification.account.acct
                    if notification.type == "mention":
                        with open(corpus_location) as fp:
                            model = markovify.NewlineText(fp.read())
                            sentence = None               
                            while sentence is None:
                                sentence = model.make_sentence(tries=10000000)
                                reply = sentence.replace("\0", "\n")                  
                                status = client.status_reply(notification.status,reply, in_reply_to_id = n_id, visibility = visibility, spoiler_text=spoiler_text)
                                client.notifications_dismiss(n_id)
                                print("notif", n_id, "treated")
                                print(time.strftime("%H:%M:%S"), "- sleeping 60 seconds...")
                                time.sleep(60)
    except:
        print(time.strftime("%H:%M:%S"), "- Reply failed !")
        pid = os.getpid()
        os.kill(pid, signal.SIGTERM)

def getCurrentMemoryUsage():
    # From: https://stackoverflow.com/a/48397534
    ''' Memory usage in kB '''
    with open('/proc/self/status') as f:
        memusage = f.read().split('VmRSS:')[1].split('\n')[0][:-3]
    return int(memusage.strip())

if __name__ == "__main__":
    spoiler_text = os.environ['cw']
    visibility = os.environ['visibility']
    client_id = os.environ['clientid.secret']
    client_secret = os.environ['clientsecret.secret']
    access_token = os.environ['accesstoken.secret']
    sleep_duration = os.environ['sleep_duration']    
    corpus_location = os.environ['corpus_location']
    api_base_url = os.environ['instance']    
    sleep_duration=float(sleep_duration)
    client = Mastodon(client_id=client_id,client_secret=client_secret,access_token=access_token,api_base_url=api_base_url)
    me = client.account_verify_credentials()
    following = client.account_following(me.id) 
    # threading
    get = threading.Thread(target=writetoot, args=(client,))     
    answer = threading.Thread(target=reply, args=(client,))
    generate = threading.Thread(target=job, args=(client,))
    get.start()
    answer.start()
    generate.start()
    generate.join()
    answer.join()
    get.join()