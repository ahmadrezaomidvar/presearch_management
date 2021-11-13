from subprocess import Popen, PIPE
import json
from pathlib import Path
import argparse
import time

def load_user_list(root):
    user_list = Path(root).joinpath('user_list.json')

    with open(str(user_list)) as json_file:
        user_list = json.load(json_file)

    return user_list

def get_args():

        parser = argparse.ArgumentParser(description="This script run main.py for each user listed in user_list individually",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("--root", type=str, help="root to chrome")
        args = parser.parse_args()

        return args

def main():
    args = get_args()
    root = args.root

    user_list = load_user_list(root)
    for user, password in user_list.items():
        Popen(f"gnome-terminal -- python main.py --user_name {user} --password {password} --root {root}", stdout=PIPE, stderr=True, shell=True)
        time.sleep(10)



if __name__ == "__main__":
    main()