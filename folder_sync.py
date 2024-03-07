import os
import shutil
import hashlib
import argparse
import logging
from pathlib import Path
import time


def setup_logger(log_file_path):
    """Set up logging to both console and file."""
    logger = logging.getLogger("folder_sync")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    if log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def calculate_md5(path):
    if path.is_file():
        hash_md5 = hashlib.md5()
        with open(path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    else:
        return None  # Return None for directories


def synchronize_folders(source_path, replica_path, interval_seconds, log_file_path):
    source = Path(source_path)
    replica = Path(replica_path)
    logger = setup_logger(log_file_path)

    while True:
        source_paths = {
            (Path(root) / item).resolve(): calculate_md5(Path(root) / item)
            for root, dirs, items in os.walk(source)
            for item in dirs + items
        }

        # Delete files and folders in replica not present in source
        for replica_item in replica.rglob("*"):
            source_item = source / os.path.relpath(replica_item, replica)

            if not source_item.exists():
                if replica_item.is_file():
                    replica_item.unlink()
                    logger.info(f"Deleted file: {replica_item}")
                elif replica_item.is_dir():
                    shutil.rmtree(replica_item)
                    logger.info(f"Deleted folder: {replica_item}")

        # Sync new and modified files and folders from source to replica
        for source_path, source_hash in source_paths.items():
            replica_path = replica / os.path.relpath(source_path, source)

            if source_path.is_file() and (
                not replica_path.exists() or source_hash != calculate_md5(replica_path)
            ):
                shutil.copy2(source_path, replica_path)
                logger.info(f"Copied: {source_path} -> {replica_path}")
            elif source_path.is_dir() and not replica_path.exists():
                shutil.copytree(source_path, replica_path)
                logger.info(f"Created folder: {replica_path}")

        time.sleep(interval_seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Periodically synchronize two folders."
    )
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument(
        "interval_seconds", type=int, help="Synchronization interval in seconds"
    )
    parser.add_argument(
        "--log_file", default="./log.txt", help="Path to the log file (optional)"
    )

    args = parser.parse_args()

    synchronize_folders(
        args.source_folder, args.replica_folder, args.interval_seconds, args.log_file
    )
