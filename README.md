# Mastodon Markov

Inspired by [Jess3Jane](https://github.com/Jess3Jane/mastodon-ebooks)

## How does it work?
### To generate text
The bot connects to his mastodon account, gets his followers, gets their toots and then stores them in a corpus (in /data/corpus.txt).
Then, it makes a nice mix and hop it gives a piece of text generated, which is then published.

### To answer to mentions
The bot gets all its notifications, filters the mentions, mixes a bit of text from the corpus, and then it replies, and empties the notifications.

## How to create an application for the bot ?
I refer you to this [tutorial](https://botwiki.org/resource/tutorial/how-to-make-a-mastodon-botsin-space-app-bot/). 
Be careful, you have to give the bot the **write** and **read** rights.

## How to deploy it

### Needed Variables

Used variables ------- Mastodon.py variables ------- Default value

- client_secret -> client_secret
- client_id -> client_id
- access_token -> access_token
- instance -> api_base_url -> default: [https://botsin.space](https://botsin.space)
- cw -> spoiler_text -> default: "markov bot: test"
- visiblity -> visiblity -> default: "private"
- sleep_duration -> sleep_duration -> default: "14400"
- corpus_location -> corpus_location -> default: "data/corpus.txt"
- tries -> tries -> default: "10000"
- max_chars -> max_chars -> default: "500"
- min_chars -> min_chars -> default: "5"

### Via a Helm Chart
I have provided [a zipped example in the repo](https://github.com/maxime-sourdin/mastodon-markov/blob/main/helm.zip).

Nothing is running in root on the helm chart.

### Via Docker-Compose
You can find the [docker-compose.yml](https://github.com/maxime-sourdin/mastodon-markov/blob/main/docker-compose.yml) in the repo, remember to build your own image, mine is not public.
	
## Precisions
You can set the visibility of toots, the time between each toot and the Content Warning in the variables.