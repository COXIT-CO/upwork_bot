# Upwork_bot
[![CodeFactor](https://www.codefactor.io/repository/github/coxit-co/upwork_bot/badge?s=f80a00123d45808c5c0b6d8cff8fab3e607b160c)](https://www.codefactor.io/repository/github/coxit-co/upwork_bot)
[![buddy pipeline](https://app.buddy.works/soleskevych/upwork-bot/pipelines/pipeline/338573/badge.svg?token=00f56263ddf955f429925817a0fc038c807db2c528fbf0704c14a05c05ceaa31 "buddy pipeline")](https://app.buddy.works/soleskevych/upwork-bot/pipelines/pipeline/338573)

# What does this bot do?
A bot is integration of Slack, Upwork and Notion platforms to automate new projects seeking. Once or more times a day notion table notes are iterated through to get project links. Having them requests to Upwork API are made to get full necessary info about job: title, other opened jobs by client and their titles. If new projects appeared comparing with previous such iteration, which is figured out by quering and comparing database entries, bot sends message in Slack through Slack bot

# Architecture notes
Project consists of separate logical parts:
- *app* - flask app itself composing all other parts. **Also it manages read/write transactions from/to SQLite database**
- *slack* part responsible for integration with Slack platform. **In schema/models directory you will find two ORM classes matching tables in database**
- *notion* part serves notion tables notes extraction namely extraction job links
- *upwork* part provides access to work with Upwork API
- *tests* is test coverage for entire project

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
