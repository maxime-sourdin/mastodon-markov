from mastodon import Mastodon
from bs4 import BeautifulSoup
import re,os, markovify, json, random, time, datetime, signal, schedule
from typing import Any, Optional, Union
from schedule import every, repeat, run_pending

class MastodonConfigurationError(Exception):
    pass

def parse_toot(toot):
    try: 
        if client.ratelimit_remaining > 10:
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
            print(time.strftime("%H:%M:%S"), " - Remaining requests:", client.ratelimit_remaining)        
            return
        else:
            print(time.strftime("%H:%M:%S"), " - Low remaining requests:", client.ratelimit_remaining)          
            time.sleep(120)            
    except:
        print(time.strftime("%H:%M:%S"), " - Failed to parse toots!")
        print(time.strftime("%H:%M:%S"), " - Remaining requests:", client.ratelimit_remaining)          

def get_toots(client, id):
    if client.ratelimit_remaining > 10:
        i = 0
        toots = client.account_statuses(id,only_media=False,pinned=False,exclude_replies=False, limit="1")
        while toots is not None and len(toots) > 1:
            for toot in toots:
                t = parse_toot(toot)
                if t != None:
                    yield t
            toots = client.fetch_next(toots)
            i += 1
            print(time.strftime("%H:%M:%S"), " - Getting toots (",i,")")
            print(time.strftime("%H:%M:%S"), " - Remaining requests:", client.ratelimit_remaining)          
            return
    else:
        print(time.strftime("%H:%M:%S"), " - Low remaining requests:", client.ratelimit_remaining)          

def write_toot(client):    
    i = 0       
    # Get toots and store it on file
    with open(corpus_location, "a") as fp:
        for f in following:
            for t in get_toots(client, f.id):
                fp.write(t + "\n")
                i += 1                        
                print(time.strftime("%H:%M:%S"), "- Saving toots (",i,")")
                print(time.strftime("%H:%M:%S"), " - Remaining requests:", client.ratelimit_remaining)                  
                return

def job(client):
    if client.ratelimit_remaining > 10:            
        with open(corpus_location) as fp:
            model = markovify.NewlineText(fp.read())
            sentence = None               
            while sentence is None:
                sentence = model.make_short_sentence(tries=tries, max_chars=max_chars, min_chars=min_chars)
                sentence = sentence.replace("\0", "\n")                  
                status = client.status_post(sentence, visibility = visibility, spoiler_text=spoiler_text)
                print(time.strftime("%H:%M:%S"), " - Next line you're going to say:" "", sentence, "")
                print(time.strftime("%H:%M:%S"), " - Remaining request:", client.ratelimit_remaining)  
                return
    else:
        print(time.strftime("%H:%M:%S"), " - Low remaining requests:", client.ratelimit_remaining)          
        time.sleep(120)  
        
def answer(client):
    if client.ratelimit_remaining > 10:            
        notifications = client.notifications()
        for notification in notifications:            
            n_id = notification["id"]
            n_acct = notification.account.acct
            if notification.type == "mention":
                with open(corpus_location) as fp:
                    model = markovify.NewlineText(fp.read())
                    sentence = None               
                    while sentence is None:
                        sentence = model.make_short_sentence(tries=tries, max_chars=max_chars, min_chars=min_chars)
                        reply = sentence.replace("\0", "\n")                  
                        status = client.status_reply(notification.status,reply, in_reply_to_id = n_id, visibility = visibility, spoiler_text=spoiler_text)
                        client.notifications_dismiss(n_id)
                        print("Notification", n_id, "from", n_acct, "treated")
                        print("Next line you're going to say:" "", reply, "")
                        print(time.strftime("%H:%M:%S"), " - Remaining requests:", client.ratelimit_remaining)  
                        return
    else:
        print(time.strftime("%H:%M:%S"), " - Low remaining requests:", client.ratelimit_remaining)          
        time.sleep(120)
                        
if __name__ == "__main__":
    print(time.strftime("%H:%M:%S"), "- Bot started !")
    client_secret: Union[str, Any] = os.environ.get("client_secret", default=None)
    client_id: Union[str, Any] = os.environ.get("client_id", default=None)
    access_token: Union[str, Any] = os.environ.get("access_token", default=None)
    api_base_url: Union[str, Any] = os.environ.get("api_base_url", default="https://botsin.space") 
    spoiler_text: Union[str, Any] = os.environ.get("spoiler_text", default="markov bot: test")
    visibility: Union[str, Any] = os.environ.get("visibility", default="private")
    frequency= int(os.environ.get("frequency", default="1"))
    corpus_location: Union[str, Any] = os.environ.get("corpus_location", default="data/corpus.txt")
    tries = int(os.environ.get("tries", default="10000"))
    max_chars = int(os.environ.get("max_chars", default="500"))
    min_chars = int(os.environ.get("max_chars", default="5"))
    if client_secret is None or client_id is None or access_token is None:
        raise MastodonConfigurationError
    else:
        client = Mastodon(client_id=client_id,client_secret=client_secret,access_token=access_token,api_base_url=api_base_url)
        me = client.account_verify_credentials()
        following = client.account_following(me.id)
        schedule.every(frequency).hours.do(job, client)
        schedule.every().minutes.do(answer, client)
        schedule.every(24).hours.do(write_toot, client)
        while True:
            run_pending()
            time.sleep(1)
