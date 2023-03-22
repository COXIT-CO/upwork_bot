import ast
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.absolute()


def write_arg_to_file(arg_name, data_to_write, file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
        with open(file_path, "w") as file:
            lines.append(f"{arg_name}={str(data_to_write)}\n")
            file.writelines(lines)
    except FileNotFoundError:
        pass


def delete_arg_from_file(arg_name, file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
        filtered_lines = [line for line in lines if arg_name not in line]
        with open(file_path, "w") as file:
            file.writelines(filtered_lines)
    except FileNotFoundError:
        pass


def get_arg_value_from_file(arg_name, file_path=f"{ROOT_DIR}/.env"):
    arg_value = {}
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                if arg_name in line:
                    arg_value = line
                    break
    except FileNotFoundError:
        pass
    return arg_value


def write_variables_in_file(file_path, **kwargs):
    VARIABLES = [
        "SLACK_CHANNELS_DATA",
        "SLACK_CHANNEL_ID",
        "SLACK_SIGNING_SECRET",
        "SLACK_BOT_TOKEN",
        "CLIENT_ID",
        "CLIENT_SECRET",
        "CLIENT_EMAIL",
        "CLIENT_PASSWORD",
        "REDIRECT_URI",
        "NOTION_TOKEN",
        "REFRESH_TOKEN",
        "LOGIN_ANSWER",
    ]

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
            for var in VARIABLES.copy():
                for line in lines:
                    if var in line:
                        VARIABLES.remove(var)
    except FileNotFoundError:
        pass

    with open(file_path, "a") as f:
        for var in VARIABLES:
            try:
                f.write(f"{var}={str(kwargs[var])}\n")
            except KeyError:
                pass
