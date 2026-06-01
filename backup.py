import shutil
import datetime

import logging

from scripts.housekeeping.datadir import get_save_dir, get_backups_dir

logger = logging.getLogger(__name__)


def make_backup(name):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    shutil.make_archive(
        base_name=get_backups_dir() + f"/{timestamp}_{name}",
        format="zip",
        root_dir=get_save_dir() + f"/{name}",
        logger=logger,
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        make_backup(sys.argv[1])
    else:
        print("Usage: backup.py <Clan name>")
