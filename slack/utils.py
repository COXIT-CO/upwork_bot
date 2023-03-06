def build_blocks_given_job_openings(job_openings):
    """given job openings build blocks to show in modal window"""
    blocks = []
    for job_opening in job_openings:
        origin_job_url = job_opening["job_url"]
        origin_job_title = job_opening["job_title"]
        job_opening_text = f"<{origin_job_url}|{origin_job_title}>"
        for index, other_opened_job in enumerate(
            job_opening["other_opened_jobs"], start=1
        ):
            job_opening_text += f"\n {' ' * 8}{index}) <{other_opened_job['job_url']}|{other_opened_job['job_title']}>"
        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": job_opening_text}}
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


def build(current_job_url, current_job_title):
    return f"<{current_job_url}|{current_job_title}>"


def write_variables_in_file(file_path, **kwargs):
    VARIABLES = ['NOTION_TABLE_URL', 'SLACK_CHANNEL_ID', 'SLACK_SIGNING_SECRET', 'SLACK_BOT_TOKEN', 'CLIENT_ID', 'CLIENT_SECRET', 'CLIENT_EMAIL', 'CLIENT_PASSWORD', 'REDIRECT_URI', 'NOTION_TOKEN', 'REFRESH_TOKEN', 'LOGIN_ANSWER']

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for var in VARIABLES.copy():
                for line in lines:
                    if var in line:
                        VARIABLES.remove(var)
    except FileNotFoundError:
        pass
        
    with open(file_path, 'a') as f:
        for var in VARIABLES:
            f.write(f'{var}={kwargs[var]}\n')
