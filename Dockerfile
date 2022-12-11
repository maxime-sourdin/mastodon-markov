FROM proxy-docker.sourdin.ovh/python:3.9.16-alpine3.17
WORKDIR /ebooks/
USER root
RUN apk update \
    && apk upgrade \
    && apk --no-cache add bash py3-pip shadow\
    && useradd -m worker \
    && chown -R worker:worker /ebooks
USER 1000
COPY --chown=worker:worker main.py /ebooks/main.py
COPY --chown=worker:worker clean.py /ebooks/clean.py
ENV PATH $PATH:$HOME/.local/bin
RUN pip3 install --no-cache-dir Mastodon.py markovify beautifulsoup4 schedule