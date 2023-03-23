from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.absolute()


def write_arg_to_file(arg_name, data_to_write, file_path):
    try:
        with open(file_path, "r") as f:
            pass
    except FileNotFoundError:
        with open(file_path, "w") as f:
            pass

    with open(file_path, "r") as file:
        lines = file.readlines()
    for i, line in enumerate(lines):
        if arg_name in line:
            lines[i] = f"{arg_name}={data_to_write}\n"
            break
    else:
        lines.append(f"{arg_name}={data_to_write}\n")
    if len(lines) == 0:
        lines = [f"{arg_name}={data_to_write}\n"]

    with open(file_path, "w") as f:
        f.writelines(lines)


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
