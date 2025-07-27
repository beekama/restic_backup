#!/usr/bin/python3

''' Strongly guided by the bash-script-version of @Thomas_Preisner '''

from os.path import exists
import os
import signal
import argparse
import subprocess
import requests
import credentials
import sys
import datetime

# Ensure backup runs only once at a time
LOCKFILE = '/run/restic-backup.lock'
if (exists(LOCKFILE)):
    print("backup already running. Aborting this job now ...")
    exit(0)

# Backup-parameters
RESTIC = '/usr/bin/restic'
RESTIC_EXCLUDE = '/etc/restic/exclude.txt'

os.environ['RESTIC_PASSWORD'] = credentials.RESTIC_PASSWORD

def handleBackup():
    backup_command = [
        RESTIC,
        '-r', credentials.RESTIC_REPOSITORY,
        '--verbose',
        'backup',
        '/',
        '--exclude-caches',
        '--exclude-file', RESTIC_EXCLUDE
    ]
    result = subprocess.run(backup_command, capture_output=True, text=True)

    if result.returncode != 0:
        print("Backup command failed", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return

    snapshot_command = [
        RESTIC,
        '-r', credentials.RESTIC_REPOSITORY,
        'snapshots',
        '--json'
    ]

    snapshot_result = subprocess.run(snapshot_command, capture_output=True, text=True)

    if snapshot_result.returncode != 0:
        print("Failed to list snapshots", file=sys.stderr)
        print(snapshot_result.stderr, file=sys.stderr)
        return

    try:
        import json
        snapshots = json.loads(snapshot_result.stdout)
        latest_snapshot = max(snapshots, key=lambda s: s['time'])
        snapshot_time = datetime.datetime.fromisoformat(latest_snapshot['time'].replace("Z", "+00:00"))

        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - snapshot_time

        if delta.total_seconds() > 300: # 5minuten
            print("No recent snapshot found after backup. Possible failure.", file=sys.stderr)
            return

    except Exception as e:
        print("Error parsing snapshots or validating latest backup:", e, file=sys.stderr)
        return

    # Backup successful -> monitoring
    headers = {
        'Content-type': 'application/json',
    }
    data = { "service": credentials.ATHQ_SERVICE,
             "token" : credentials.ATHQ_SECRET_TOKEN,
             "info" : "backup successful",
             "status" : "OK"
    }
    try:
        response = requests.post('https://async-icinga.atlantishq.de/report', headers=headers, json=data)
        if not (200 <= response.status_code < 300):
            print(f"Error: Failed to upload status to Icinga (Status Code: {response.status_code})", file=sys.stderr)
        else:
            print("===== DONE SUCCESS =====")
    except request.RequestException as e:
        print(f"Error: Unable to reach monitoring endpoint: {e}", file=sys.stderr)


# Handly Python
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Borg-Backup script')
    parser.add_argument('--backup', action="store_true")

    args = parser.parse_args()

    if (not args.backup):
        raise Exception("ABORT - no parameter specified (--backup)")

    if args.backup:
        # backup
        handleBackup()
