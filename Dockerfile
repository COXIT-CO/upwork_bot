FROM python:3.9 AS build

FROM selenium/standalone-chrome

USER root

COPY --from=build /usr/local/bin /usr/local/bin
RUN rm -rf /usr/local/lib
COPY --from=build /usr/local/lib /usr/local/lib

RUN apt-get update -y
RUN apt-get install cron -y

ADD cronjob /etc/cron.d/cronjob
RUN chmod 0600 /etc/cron.d/cronjob
RUN touch /var/log/cron.log

WORKDIR /app
COPY . .

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
ARG REFRESH_TOKEN
ENV REFRESH_TOKEN ${REFRESH_TOKEN}

RUN pip install -r requirements.txt

EXPOSE 8000

CMD cron && exec python3 -m app