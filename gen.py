import markovify, json, time, os
from mastodon import Mastodon

spoiler_text = os.environ['cw']
visibility = os.environ['visibility']
api_base_url = "https://botsin.space"

client = Mastodon(
        client_id="cred/clientcred.secret",
        access_token="cred/usercred.secret",
        api_base_url=api_base_url)

with open("corpus.txt") as fp:
    model = markovify.NewlineText(fp.read())

print("tooting")
sentence = None
# you will make that damn sentence
while sentence is None:
    sentence = model.make_sentence(tries=100000)
client.status_post(sentence.replace("\0", "\n"),visibility=visibility,spoiler_text=spoiler_text)
