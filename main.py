from mastodon import Mastodon, StreamListener
from bs4 import BeautifulSoup
import re,os, markovify, json, threading, random, time, datetime

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
    return "\0".join(list(text))

def get_toots(client, id):
    i = 0
    toots = client.account_statuses(id)
    while toots is not None and len(toots) > 0:
        for toot in toots:
            print(toot)
            t = parse_toot(toot)
            if t != None:
                yield t
        toots = client.fetch_next(toots)
        i += 1
        if i%10 == 0:
            print(i)

def job(client):
    scopes = ["read:statuses", "read:accounts", "read:follows", "write:statuses"]
    if os.stat('/data/corpus.txt').st_size == 0:
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

    print("Bot shitposting...")  
    client.status_post(sentence.replace("\0", "\n"),visibility=visibility,spoiler_text=spoiler_text)

def reply(client):
    replies = [line.strip().replace("\\n", "\n")
               for line in open("/data/corpus.txt").readlines()]
    notifications = client.notifications()

    for notification in notifications:    
        n_id = notification["id"]
        n_acct = notification.account.acct
        if notification.type == "mention":
            random.shuffle(replies)
            reply = replies[0]
            time.sleep(15)
            status = client.status_reply(notification.status,reply, in_reply_to_id = n_id, visibility = visibility)
        print("Bot responds to mention...")
        client.notifications_clear()
        client.notifications()
        
if __name__ == "__main__":
    api_base_url = "https://botsin.space"
    scopes = ["read:statuses", "read:accounts", "read:follows", "write:statuses", "read:notifications", "write:notifications"]
    spoiler_text = os.environ['cw']
    visibility = os.environ['visibility']
    client_id = os.environ['clientid.secret']
    client_secret = os.environ['clientsecret.secret']
    access_token = os.environ['accesstoken.secret']
    sleep_duration = os.environ['sleep_duration']
    sleep_duration=float(sleep_duration)
    client = Mastodon(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            api_base_url=api_base_url)
    me = client.account_verify_credentials()
    following = client.account_following(me.id)
    while True:
        reply(client)
    while True:
        if os.stat('/data/corpus.txt').st_size == 0:
            job(client)
        time.sleep(sleep_duration)
