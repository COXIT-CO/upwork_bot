# FROM python:3.10.0-alpine AS build
# COPY requirements.txt .
# RUN pip install -r requirements.txt
# # RUN echo `ls /usr/local/lib/python3.10/site-packages`
# RUN echo `which python`
# RUN python --version

# FROM alpeware/chrome-headless-trunk

# RUN rm -rf "/usr/bin/*python*"

# ENV PATH=/usr/local/lib:/usr/local/bin:${PATH}

# RUN rm -rf "/usr/local/lib/*"

# RUN echo `ls /usr/local/bin`

# COPY --from=build /usr/local/bin/python /usr/local/bin
# COPY --from=build /usr/local/lib /usr/local/lib

# RUN which python
# RUN /usr/local/bin/python --version



# WORKDIR /app
# COPY . .
# RUN echo `ls /usr/local/lib`

# # Update the package repository and install Google Chrome
# # ENV TZ=Europe/Kiev
# # RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# # RUN apt-get update && apt-get install -y wget && \
# #     wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
# #     apt-get install ./google-chrome-stable_current_amd64.deb -y
# # apt-get -fy install && \
# # dpkg -i google-chrome-stable_current_amd64.deb

# RUN apt-get update -y
# RUN echo `which python3`
# RUN apt-get -y install cron


# # RUN set -xe \
# #     && apt-get update -y \
# #     && apt-get install python3-pip -y

# # RUN apt-get install python3 python3-pip -y
# # RUN pip3 install --upgrade pip

# # RUN pip install -r requirements.txt

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

# # WORKDIR /app
# # RUN docker images
# # COPY --from=build /app/dist /app

# CMD python -m app
# # -ci 1c3cc82d1b899a9ee1e44681f1c43514 -cs fe9bec427ad322bf -rt oauth2v2_bd8f2b9864d2180db76ac696372dc4fa -sbt xoxb-4630409558228-4629770434357-7xWPI0AP7HpoYKXshfLOH2XX -sss 5863439f405cea0ca9498fdc1011e94f -nt secret_o1kyubNpJ5XKD5pSVq8OLmq8KC2F64wAAa1GVWdczyQ























# FROM python:3.9
# # FROM alpeware/chrome-headless-trunk

# # Update the package repository and install Google Chrome
# ENV TZ=Europe/Kiev
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# # RUN apt-get update && apt-get install -y wget && \
# #     wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
# #     apt-get install ./google-chrome-stable_current_amd64.deb -y
# # apt-get -fy install && \
# # dpkg -i google-chrome-stable_current_amd64.deb

# RUN apt-get update
# RUN apt-get -y install cron
# RUN apt install nano
# ENV EDITOR=/usr/bin/nano

# WORKDIR /app

# # Copy the contents of the local directory to the container
# COPY . .

# # RUN set -xe \
# #     && apt-get update -y \
# #     && apt-get install python3-pip -y
# # RUN pip3 install --upgrade pip -y

# # RUN apt-get install python3 python3-pip -y
# # # RUN pip3 install --upgrade pip
# RUN pip install -r requirements.txt


# ADD root.sh /root/root.sh
# RUN chmod 0644 /root/root.sh

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

# CMD ["cron", "-f", "&&", "python3", "-m", "app"]
# # # -ci 1c3cc82d1b899a9ee1e44681f1c43514 -cs fe9bec427ad322bf -rt oauth2v2_bd8f2b9864d2180db76ac696372dc4fa -sbt xoxb-4630409558228-4629770434357-7xWPI0AP7HpoYKXshfLOH2XX -sss 5863439f405cea0ca9498fdc1011e94f -nt secret_o1kyubNpJ5XKD5pSVq8OLmq8KC2F64wAAa1GVWdczyQ



























# FROM python:3.9

# RUN apt-get update
# RUN apt-get -y install cron

# WORKDIR /app

# COPY . .

# RUN pip install -r requirements.txt

# # Add crontab file in the cron directory
# ADD crontab /etc/cron.d/hello-cron

# # Give execution rights on the cron job
# RUN chmod 0644 /etc/cron.d/hello-cron

# RUN crontab /etc/cron.d/hello-cron

# ENTRYPOINT ["cron", "-f"]

# # Create the log file to be able to run tail
# # RUN touch /var/log/cron.log

# # EXPOSE 8000

# # ARG CLIENT_ID
# # ENV CLIENT_ID ${CLIENT_ID}
# # ARG CLIENT_SECRET
# # ENV CLIENT_SECRET ${CLIENT_SECRET}
# # ARG CLIENT_EMAIL
# # ENV CLIENT_EMAIL ${CLIENT_EMAIL}
# # ARG CLIENT_PASSWORD
# # ENV CLIENT_PASSWORD ${CLIENT_PASSWORD}
# # ARG REDIRECT_URI
# # ENV REDIRECT_URI ${REDIRECT_URI}
# # ARG SLACK_BOT_TOKEN
# # ENV SLACK_BOT_TOKEN ${SLACK_BOT_TOKEN}
# # ARG SLACK_SIGNING_SECRET
# # ENV SLACK_SIGNING_SECRET ${SLACK_SIGNING_SECRET}
# # ARG NOTION_TOKEN
# # ENV NOTION_TOKEN ${NOTION_TOKEN}
# # ARG REFRESH_TOKEN
# # ENV REFRESH_TOKEN ${REFRESH_TOKEN}

# # CMD (cron -f &) && exec python3 -m app

# # CMD "cron", "&&", "python3 -m app"]



























FROM python:3.9
WORKDIR /app

RUN apt-get update -y
RUN apt-get install cron -y

ADD cronjob /etc/cron.d/cronjob
RUN chmod 0600 /etc/cron.d/cronjob
RUN touch /var/log/cron.log

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

# RUN chmod +x ./run.sh
# ENTRYPOINT /bin/sh ./run.sh

EXPOSE 8000

CMD cron && exec python3 -m app

# RUN echo "* * * * * python /app/cron-jobs/test.py" >> /etc/crontab

# CMD cron && tail -f /dev/null

# Add crontab file in the cron directory
# ADD crontab /etc/cron.d/hello-cron

# # Give execution rights on the cron job
# RUN chmod 0644 /etc/cron.d/hello-cron

# RUN crontab /etc/cron.d/hello-cron

# ENTRYPOINT ["cron", "-f"]

# Create the log file to be able to run tail
# RUN touch /var/log/cron.log

# EXPOSE 8000

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
# ARG REFRESH_TOKEN
# ENV REFRESH_TOKEN ${REFRESH_TOKEN}

# CMD (cron -f &) && exec python3 -m app

# CMD "cron", "&&", "python3 -m app"]