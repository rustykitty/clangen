import shutil
import datetime
import glob
import sys
import os
import os.path

import logging

from scripts.housekeeping.datadir import get_save_dir, get_backups_dir, get_temp_dir

logger = logging.getLogger(__name__)


def make_backup(name):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    shutil.make_archive(
        base_name=get_backups_dir() + f"/{timestamp}_{name}",
        format="zip",
        root_dir=get_save_dir() + f"/{name}",
        logger=logger,
    )

def restore_backup(name, timestamp):
    backup_path = get_backups_dir() + f"/{timestamp}_{name}.zip"
    clan_path = get_save_dir() + f"/{name}"
    temp = get_temp_dir() + "/backup_restore"
    shutil.unpack_archive(backup_path, temp, "zip")

    # delete the old clan path
    if os.path.exists(clan_path):
        shutil.rmtree(clan_path)
    shutil.copytree(temp, clan_path)

def list_backups(name):
    files = glob.glob(get_backups_dir() + f"/*_{name}.zip")
    return [file.lstrip(get_backups_dir() + "/") for file in files]

USAGE = "Usage: backup.py <Clan name> <backup|restore> [options...]"

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print(USAGE)
        return
    clan = args[0]
    if len(args) >= 2:
        subcommand = args[1]
        if subcommand == "backup":
            make_backup(clan)
        elif subcommand == "restore":
            if len(args) == 3:
                restore_backup(args[0], args[2])
            else:
                print(USAGE)
        else:
            print(USAGE)
    else: # 1 arg
        backups = list_backups(clan)
        print("Backups for", clan, f"({len(backups)})")
        for backup in backups:
            print(f"-", backup)

if __name__ == "__main__":
    main()
