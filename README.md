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
Before running the application you need to do a lot of underlying work, so you might want to omit this section as for now and go forward to [Setup](https://github.com/COXIT-CO/upwork_bot/blob/issue_47/README.md#setup) one. As soon as you are done with it, go back here.

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

During platforms setup you will obtain a lot of credentials needed to build docker container. I will pay your attention on every credential you need to posess

<h3>Notion</h3>

First of all you have to have a populated notion table with 2 required fields: **Project Name** and **Link**. Other fields won't be considered. Here is how my table with linkedin jobs looks like:

![image](https://user-images.githubusercontent.com/85521093/227469505-f94641cc-0262-429a-950c-c960990a1168.png)

!!! Here in **Project Name** field you should paste a link on a company you want to track. It match pattern **https://www.linkedin.com/company/** + company name. E.g. **https://www.linkedin.com/company/returnbear/**. Any query parameters or additions must be removed

and respectively Upwork:

![image](https://user-images.githubusercontent.com/85521093/227469708-8e6dfb22-99e1-4979-a2cd-8faa1025d099.png)

!!! Here in **Project Name** field you should paste a link on a job you are tracking and want to receive updates on every opened job the client of this one has posted. It match pattern **https://www.upwork.com/jobs/** + job key. E.g. **https://www.upwork.com/jobs/~01ae4de5c88f60bee4**. Any query parameters or additions must be removed.

Now you need to obtain access token and connect it to this table:
1. Go to (https://www.notion.so/my-integrations)[https://www.notion.so/my-integrations] and create new integration. Give it random name. It populate fields as shown below:

![image](https://user-images.githubusercontent.com/85521093/227472099-0678a5a9-b6aa-49a5-ac00-ce63ccfeaa9f.png)

**As a result you will have a secret we need for docker build stage**

![image](https://user-images.githubusercontent.com/85521093/227472469-0ffa6f3e-baa4-4de3-b134-a21d27688514.png)

Now got to your notion table and connect this integration:

![image](https://user-images.githubusercontent.com/85521093/227473329-7f62a908-a80b-4b83-ba07-75be8165f5ea.png)

Fine! We set up Notion. Moving forward

<h3>Slack</h3>

Establishing Slack to work is way much harder. But let's do it following instructions:

1. First of all you might want to create slack app, so visit [link](https://api.slack.com/apps?new_app) and:
Here you see a navigation bar, I will refer to its items as text enclosed in double qoutes

![image](https://user-images.githubusercontent.com/85521093/227484615-07ebf8f9-4458-4d7c-9071-dc38be89b288.png)

2. Once you've come with working app we need to set it right:
    - Go to "Interactivity & Shortcuts" and toggle on the switch. In the **Request URL** field you should paste you domain name + '/slack/interactive'. E.g. **https://8f76-91-214-209-68.eu.ngrok.io/slack/interactive** (I use ngrok for local development):
    - 
    ![image](https://user-images.githubusercontent.com/85521093/227486545-332d2515-2e8f-4f72-a7a8-4ceeff1cd145.png)

    - Go to "Slash Commands". Here we need to create 2 commands: **/subscribe_upwork** and **/subscribe_linkedin**. For each command the **Request URL** field should be your domain name + **/slack/<command_name>**. E.g. **https://8f76-91-214-209-68.eu.ngrok.io/slack/subscribe_upwork** and **https://8f76-91-214-209-68.eu.ngrok.io/slack/subscribe_linkedin**:

    ![image](https://user-images.githubusercontent.com/85521093/227488296-7f3e9866-17b8-4bea-bdcc-f24a3a26e620.png) ![image](https://user-images.githubusercontent.com/85521093/227488440-82fcfa06-2474-4366-ba40-dadbca4e73e4.png)
    
    - Go to "Event Subscriptions". Toogle on the switch. In **Request URL** field paste your domain name + **/slack/events**. Then scroll a bit down and reproduce next subscriptions:
    - 
    ![image](https://user-images.githubusercontent.com/85521093/227489695-a82cbc34-cb5f-46c5-bee4-53bd2b1a620c.png)

    - Go to "App Home" and just switch on everything as shown here:
    
    ![image](https://user-images.githubusercontent.com/85521093/227490016-f655444a-8648-432c-ba6c-d195a1670a7e.png) ![image](https://user-images.githubusercontent.com/85521093/227490122-4a6fc00e-9683-4760-9b32-d68c7db6ab39.png)
    
    - Go to "OAuth & Permissions". Scroll a bit down and set these scopes:
    
    ![image](https://user-images.githubusercontent.com/85521093/227491304-0aea0187-0a67-4abb-80f0-44aba9fa8c55.png) ![image](https://user-images.githubusercontent.com/85521093/227491357-1e625662-ba05-41ac-bd7c-3995c5592835.png)

    - Go to "Basic Information" and generate App Level Token:
    
    ![image](https://user-images.githubusercontent.com/85521093/227491804-34e1447c-f392-4b7f-935d-13f829a3cb95.png)
    
    giving it **connections:write** scope:
    
    ![image](https://user-images.githubusercontent.com/85521093/227492094-3d9366c5-6d27-40d4-baaa-0a89d230887b.png)
    
    Now install your app to workspace:
    
    ![image](https://user-images.githubusercontent.com/85521093/227492363-6fabd049-7bdd-48fb-8eca-6fcfa4cb68e4.png)

Now go to "Oauth & Permissions" and copy **Bot User OAuth Token**:

![image](https://user-images.githubusercontent.com/85521093/227492962-44f1f3ea-fe0f-436f-9b61-c82a261540f1.png)

**We need it for docker build stage**. On "Basic Information" copy "Signing Secret":

![image](https://user-images.githubusercontent.com/85521093/227493707-83d3807f-71a6-4a4b-a3ef-d0bf861c44f7.png)

**We need it for docker build stage as well**

<h3>Upwork</h3>

For Upwork we need to obtain 6 credentials: **CLIENT_ID**, **CLIENT_SECRET**, **CLIENT_EMAIL**, **CLIENT_PASSWORD**, **REDIRECT_URI** and **REFRESH_TOKEN**. First 5 of them you should get from a client. I will tell how to get last one. I helpers folder you see module called **get_upwork_access_token.py**. For this time you should log in Upwork, go to terminal and execute ```python get_upwork_access_token.py```:

![image](https://user-images.githubusercontent.com/85521093/227498050-6d296c1c-bf89-4786-bc33-69f1d86001e1.png)

As you can see we need to visit a link. There you need to grant press "Grant Access" button in case the window with poped up. Now you see the link has been dynamically changed, so copy it and paste back in terminal, then press Return key and you will get a dictionary with **refresh_token** field:

![image](https://user-images.githubusercontent.com/85521093/227498487-b52ada53-b88e-4fbf-9c8e-b3449f544e46.png)

That's exactly what we need



Congrats!!! We finished with setuping our platrorms. As for now you have to posess 3 credentials 





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
