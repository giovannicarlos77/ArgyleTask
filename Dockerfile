FROM python:3.10-slim-buster

COPY . /task
WORKDIR /task

RUN  apt-get update \
  && apt-get install -y wget \
  && apt-get install -y gnupg2 \
  && apt-get install -y curl \
  && rm -rf /var/lib/apt/lists/*

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

ENTRYPOINT [ "python3", "main.py" ]