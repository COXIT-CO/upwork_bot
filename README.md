# Upwork_bot
[![CodeFactor](https://www.codefactor.io/repository/github/coxit-co/upwork_bot/badge?s=f80a00123d45808c5c0b6d8cff8fab3e607b160c)](https://www.codefactor.io/repository/github/coxit-co/upwork_bot)
[![buddy pipeline](https://app.buddy.works/soleskevych/upwork-bot/pipelines/pipeline/338573/badge.svg?token=00f56263ddf955f429925817a0fc038c807db2c528fbf0704c14a05c05ceaa31 "buddy pipeline")](https://app.buddy.works/soleskevych/upwork-bot/pipelines/pipeline/338573)

# What does this bot do?
A bot is integration of Slack, Notion, Upwork and Linkedin platforms to automate new projects seeking. Once or more times a day notion table notes are iterated through to get project links. Having them requests to Upwork API are made or LinkedIn companied scraping is done to get full necessary info about job and company jobs. If new projects appeared comparing with previous such iteration, which is figured out by quering and comparing database entries, bot sends message in Slack through Slack bot

# Architecture notes
Project consists of separate logical parts:
- *app* - the head part of application composing all other ones. Contains ```__main__.py``` script running flask server.
- *cron_jobs* - folder with cron jobs scripts
- *db_schema* - consists of models and controllers to store job in database (and interview invitations for Upwork)
- *helpers* - scripts used by different parts of application 
- *notion* - has script scraping notion table by provided url
- *slack* - responsible for integration with Slack platform. **In schema/models directory you will find two ORM classes matching tables in database**
- *upwork* part provides access to work with Upwork API
- *tests* is test coverage for entire project

# How to run the app?
Before running the application you need to do a lot of underlying work, so you might want to skip run for now untill you set up all right. So go to https://github.com/COXIT-CO/upwork_bot/blob/issue_47/README.md#setup

Execute following lines in your terminal:

```git clone https://github.com/COXIT-CO/upwork_bot.git``` or ```git clone git@github.com:COXIT-CO/upwork_bot.git```
```
cd upwork_bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker build --build-arg CLIENT_ID='<your_client_id>' --build-arg CLIENT_SECRET='<your_client_secret>' --build-arg CLIENT_EMAIL='<your_client_email>' --build-arg CLIENT_PASSWORD='<your_client_password>' --build-arg REDIRECT_URI='<your_client_redirect_url>' --build-arg SLACK_BOT_TOKEN='<your_slack_bot_token>' --build-arg SLACK_SIGNING_SECRET='<your_slack_signing_secret>' --build-arg NOTION_TOKEN='<your_notion_token>' --build-arg REFRESH_TOKEN='<your_refresh_token>' --build-arg LOGIN_ANSWER='<your_login_answer>' -t upwork_bot .
docker run -p 8000:8000 upwork_bot
```

# Setup

*!!! Worth mentioning that notion table scraping + slack message send is done with cron jobs*

# Requirements
Python 3.9

Run `pip install -r requirements.txt` to install all required libraries.

Upwork account, with given credentials from Upwork API.

# Notion setup
Visit [link](https://developers.notion.com/docs/create-a-notion-integration#step-1-create-an-integration) and do first 2 steps.

Pay attention at ```.env.samples``` file in project root. Create the same one with ```.env``` name and populate it with your notion token.


# Upwork API setup
You need to have valid upwork account and then you can request access to Upwork's API in order to integrate Upwork's features with their website and/or internal systems.

For more detailed instruction read : 
1. Request an API key - https://support.upwork.com/hc/en-us/articles/115015857647-Request-an-API-Key
2. Upwork API Documentation - https://developers.upwork.com/

# Slack API setup
Firstly, you need to have workspace in Slack app.

After that, visit https://api.slack.com/, create your app and connect to your workspace.

# Start
When you clone this repository and want to start program:
first what you need to do is to run 'setup.py' file with parameters:

`-hst`: Flask host

`-prt`: Flask port

`-cid`: Upwork client id

`-csc`: Upwork client secret

`-at` : Upwork access token

`-eat`: Upwork token expires at

`-ein`: Upwork token expires in

`-rt` : Upwork refresh token

`-tt` : Upwork token type

`-sbt`: Slack bot token

`-sss`: Slack signing secret

`-swu`: Slack webhook url

Example:
- python setup.py -hst 127.0.0.1 -prt 5000 -cid your_secret_data_here -csc your_secret_data_here -at your_secret_data_here -eat your_secret_data_here -ein your_secret_data_here -rt your_secret_data_here -tt your_secret_data_here -sbt your_secret_data_here -sss your_secret_data_here -swu https://hooks.slack.com/services/your_secret_url


As a result, `settings.ini` file will be created with all your data inside. So next time you don't have to input all parameters.


# Run The Script
After a successful settings.ini file creation, you should run `main.py` file. 
And start to use bot!
