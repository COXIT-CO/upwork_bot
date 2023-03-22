from slack_bolt import App


def post_slack_message(channel_id, slack_bot_app: App, blocks, encountered_errors):
    response = slack_bot_app.client.chat_postMessage(
        channel=channel_id, blocks=blocks, thread_ts=""
    )
    response_timestamp = response["ts"]
    for err in encountered_errors:
        slack_bot_app.client.chat_postMessage(
            channel=channel_id, text=err, thread_ts=response_timestamp
        )


def build_blocks_given_job_openings(data, origin=None, page=None):
    """given job openings build blocks to show in modal window"""
    blocks = []

    for i, item in enumerate(data):
        if origin == "linkedin" and (True if page is None else page == i):
            for company_data in item:
                title = company_data["company_title"]
                url = company_data["company_url"]
                jobs = company_data["jobs"]
                company_text = f"<{url}|{title}>"
                job_opening_text = ""
                for index, job_data in enumerate(jobs, start=1):
                    job_opening_text += f"\n {' ' * 8}{index}) <{job_data['job_url']}|{job_data['job_title']}>"
                if job_opening_text:
                    company_text += job_opening_text
                    blocks.append(
                        {
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": company_text},
                        }
                    )
                    for _ in range(3):
                        blocks.append({"type": "divider"})
        elif origin == "upwork":
            origin_job_url = item["job_url"]
            origin_job_title = item["job_title"]
            jobs = item["other_opened_jobs"]
            job_opening_text = f"<{origin_job_url}|{origin_job_title}>"
            for index, job in enumerate(jobs, start=1):
                job_opening_text += (
                    f"\n {' ' * 8}{index}) <{job['job_url']}|{job['job_title']}>"
                )
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": job_opening_text},
                }
            )
            for _ in range(3):
                blocks.append({"type": "divider"})
    return blocks


def build_blocks_given_invitations(invitations):
    """given job openings build blocks to show in modal window"""
    blocks = []
    invitation_text = ""
    for index, invitation in enumerate(invitations, start=1):
        link = invitation["link"]
        text = invitation["text"]
        invitation_text += f"{index}) <{link}|{text}>\n"
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": invitation_text}}]
    return blocks
