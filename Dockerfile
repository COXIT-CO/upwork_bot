# # FROM python:3.9
# FROM alpeware/chrome-headless-trunk

# # Update the package repository and install Google Chrome
# ENV TZ=Europe/Kiev
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# RUN apt-get update && apt-get install -y wget && \
#     wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
#     apt-get install ./google-chrome-stable_current_amd64.deb -y
# # apt-get -fy install && \
# # dpkg -i google-chrome-stable_current_amd64.deb

# RUN apt-get -y install cron

# WORKDIR /app

# # Copy the contents of the local directory to the container
# COPY . .

# RUN set -xe \
#     && apt-get update -y \
#     && apt-get install python3-pip -y
# RUN pip3 install --upgrade pip -y

# # RUN apt-get install python3 python3-pip -y
# # # RUN pip3 install --upgrade pip
# # RUN pip3 install -r requirements.txt

# ARG CLIENT_ID
# ENV CLIENT_ID ${CLIENT_ID}
# ARG CLIENT_SECRET
# ENV CLIENT_SECRET ${CLIENT_SECRET}
# ARG CLIENT_EMAIL
# ENV CLIENT_EMAIL ${CLIENT_EMAIL}
# ARG CLIENT_PASSWORD
# ENV CLIENT_PASSWORD ${CLIENT_PASSWORD}
# ARG REDIRECT_URI
# ENV REDIRECT_URI ${REDIRECT_URI}
# ARG SLACK_BOT_TOKEN
# ENV SLACK_BOT_TOKEN ${SLACK_BOT_TOKEN}
# ARG SLACK_SIGNING_SECRET
# ENV SLACK_SIGNING_SECRET ${SLACK_SIGNING_SECRET}
# ARG NOTION_TOKEN
# ENV NOTION_TOKEN ${NOTION_TOKEN}
# ARG SLACK_CHANNEL_ID
# ENV SLACK_CHANNEL_ID ${SLACK_CHANNEL_ID}
# ARG REFRESH_TOKEN
# ENV REFRESH_TOKEN ${REFRESH_TOKEN}

# EXPOSE 8000

# CMD python3 -m app
# # -ci 1c3cc82d1b899a9ee1e44681f1c43514 -cs fe9bec427ad322bf -rt oauth2v2_bd8f2b9864d2180db76ac696372dc4fa -sbt xoxb-4630409558228-4629770434357-7xWPI0AP7HpoYKXshfLOH2XX -sss 5863439f405cea0ca9498fdc1011e94f -nt secret_o1kyubNpJ5XKD5pSVq8OLmq8KC2F64wAAa1GVWdczyQ























FROM python:3.9
# FROM alpeware/chrome-headless-trunk

# Update the package repository and install Google Chrome
ENV TZ=Europe/Kiev
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# RUN apt-get update && apt-get install -y wget && \
#     wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
#     apt-get install ./google-chrome-stable_current_amd64.deb -y
# apt-get -fy install && \
# dpkg -i google-chrome-stable_current_amd64.deb

RUN apt-get update
RUN apt-get -y install cron

WORKDIR /app

# Copy the contents of the local directory to the container
COPY . .

# RUN set -xe \
#     && apt-get update -y \
#     && apt-get install python3-pip -y
# RUN pip3 install --upgrade pip -y

# RUN apt-get install python3 python3-pip -y
# # RUN pip3 install --upgrade pip
RUN pip install -r requirements.txt

ARG CLIENT_ID
ENV CLIENT_ID ${CLIENT_ID}
ARG CLIENT_SECRET
ENV CLIENT_SECRET ${CLIENT_SECRET}
ARG CLIENT_EMAIL
ENV CLIENT_EMAIL ${CLIENT_EMAIL}
ARG CLIENT_PASSWORD
ENV CLIENT_PASSWORD ${CLIENT_PASSWORD}
ARG REDIRECT_URI
ENV REDIRECT_URI ${REDIRECT_URI}
ARG SLACK_BOT_TOKEN
ENV SLACK_BOT_TOKEN ${SLACK_BOT_TOKEN}
ARG SLACK_SIGNING_SECRET
ENV SLACK_SIGNING_SECRET ${SLACK_SIGNING_SECRET}
ARG NOTION_TOKEN
ENV NOTION_TOKEN ${NOTION_TOKEN}
ARG SLACK_CHANNEL_ID
ENV SLACK_CHANNEL_ID ${SLACK_CHANNEL_ID}
ARG REFRESH_TOKEN
ENV REFRESH_TOKEN ${REFRESH_TOKEN}

EXPOSE 8000

CMD python3 -m app
# -ci 1c3cc82d1b899a9ee1e44681f1c43514 -cs fe9bec427ad322bf -rt oauth2v2_bd8f2b9864d2180db76ac696372dc4fa -sbt xoxb-4630409558228-4629770434357-7xWPI0AP7HpoYKXshfLOH2XX -sss 5863439f405cea0ca9498fdc1011e94f -nt secret_o1kyubNpJ5XKD5pSVq8OLmq8KC2F64wAAa1GVWdczyQ