from mastodon import Mastodon
spoiler_text = os.environ['cw']
visibility = os.environ['visibility']
client_id = os.environ['clientid.secret']
client_secret = os.environ['clientsecret.secret']
access_token = os.environ['accesstoken.secret']
api_base_url = os.environ['instance']

Mastodon = Mastodon(client_id=client_id,client_secret=client_secret,access_token=access_token,api_base_url=api_base_url)
account = Mastodon.account_verify_credentials()

toots = Mastodon.account_statuses(account)
for toot in toots:
    from time import sleep
    print(toot.id)
    Mastodon.status_delete(toot)
    sleep(5)
next_toots = Mastodon.fetch_next(toots)

while len(next_toots) != 0:
    for toot in next_toots:
        from time import sleep
        print(toot.id)
        sleep(5)
        Mastodon.status_delete(toot)
    print("loop done")
    next_toots = Mastodon.fetch_next(toots)
print("done")