# Mastodon Markov

## FR

### Comment ça marche ?
#### Pour générer du texte
Le bot se connecte à son compte mastodon, récupére ses followers, récupére leurs toots et ensuite les stocke dans un corpus (dans /data/corpus.txt).
Ensuite, il fait un beau mélange et hop ça donne un bout de texte généré, qui est ensuite publié.

#### Pour répondre aux mentions
Le bot récupére toutes ses notifications, filtre aux mentions, remelange un peu de texte du corpus, et hop ensuite il répond, et vide les notifications.

### Comment créer une appli pour le bot ?
Je vous renvoie à ce [tutoriel](https://botwiki.org/resource/tutorial/how-to-make-a-mastodon-botsin-space-app-bot/) . 
Attention, il faut bien donner au bot les droits **write** et **read** .

### Comment ça déploie
#### Via un Helm Chart
J'ai fourni (https://github.com/maxime-sourdin/mastodon-markov/blob/main/helm.zip)[un exemple zippé dans le repo]. Rien ne fonctionne en root sur le helm chart.

#### Via Docker-Compose
Vous trouverez le (https://github.com/maxime-sourdin/mastodon-markov/blob/main/docker-compose.yml)[docker-compose.yml] dans le repo, pensez à bien build votre image de votre côté, la mienne n'est pas publique.
	
### Précisions
Vous pouvez régler la visibilité des toots, le temps entre chaque toot et le ContentWarning dans les variables.

## EN

### How does it work?
#### To generate text
The bot connects to his mastodon account, gets his followers, gets their toots and then stores them in a corpus (in /data/corpus.txt).
Then, he makes a nice mix and hop it gives a piece of text generated, which is then published.

#### To answer to mentions
The bot gets all its notifications, filters the mentions, mixes a bit of text from the corpus, and then it replies, and empties the notifications.

### How to create an application for the bot ?
I refer you to this [tutorial](https://botwiki.org/resource/tutorial/how-to-make-a-mastodon-botsin-space-app-bot/). 
Be careful, you have to give the bot the **write** and **read** rights.

### How to deploy it
#### Via a Helm Chart
I have provided (https://github.com/maxime-sourdin/mastodon-markov/blob/main/helm.zip)[a zipped example in the repo].

Nothing is running in root on the helm chart.

#### Via Docker-Compose
You can find the (https://github.com/maxime-sourdin/mastodon-markov/blob/main/docker-compose.yml)[docker-compose.yml] in the repo, remember to build your own image, mine is not public.
	
### Precisions
You can set the visibility of toots, the time between each toot and the ContentWarning in the variables.