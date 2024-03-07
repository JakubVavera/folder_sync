# Folder Synchronization Script

This Python script enables one-way synchronization of two folders: a source folder and a replica folder. The synchronization is performed periodically.

## Features

- One-way synchronization: Updates the content of the replica folder to exactly match the source folder.
- Periodic synchronization: The script runs at specified intervals to keep the folders synchronized.
- Logging: File creation, copying, and removal operations are logged to both the console and a log file.

## Usage

```bash
python folder_sync.py source_folder replica_folder interval_seconds --log_file log_file_path
