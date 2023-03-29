#!/usr/bin/python3

''' Strongly guided by the bash-script-version of @Thomas_Preisner '''

from os.path import exists
import os
import signal
import argparse
import subprocess
import requests
import credentials

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
    command = os.system(RESTIC + ' -r ' + credentials.RESTIC_REPOSITORY + ' --verbose backup / --exclude-caches --exclude-file ' + RESTIC_EXCLUDE)

    if command == 0:
        # check back on athq-monitoring
        headers = {
                'Content-type': 'application/json',
                }
        data = { "service": "backup_kathi_laptop", 
                 "token" : credentials.ATHQ_SECRET_TOKEN,
                 "info" : "backup successful",
                 "status" : "OK" }
        response = requests.post('https://async-icinga.atlantishq.de/', headers=headers, json=data)

    print("Done - success")


def handleDelete():
    #execute
    print("todo --IMPLEMENT ME--")


# Handly Python
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Borg-Backup script')
    parser.add_argument('--backup', action="store_true")
    parser.add_argument('--forget', action="store_true")

    args = parser.parse_args()

    if (not args.backup and not args.forget):
        raise Exception("ABORT - no parameter specified (--backup, --forget)")

    if args.backup:
        # backup
        handleBackup()
        
    if args.forget:
        handleDelete()
