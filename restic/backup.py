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

def handler(asdf,fdsa):
    os.remove(LOCKFILE)
    print("---cleanup---")
    sleep(5000)
    exit(1)


# Backup-parameters
RESTIC = '/usr/bin/restic'
RESTIC_EXCLUDE = '/etc/restic/exclude.txt'

os.environ['RESTIC_PASSWORD'] = credentials.RESTIC_PASSWORD

def handleBackup():
    print(os.system(RESTIC + ' -r ' + credentials.RESTIC_REPOSITORY + ' --verbose backup / --exclude-caches --exclude-file '
            + RESTIC_EXCLUDE))
    #    raise RuntimeError("faiiiiiiiiilllll")
    #print(subprocess.check_output("echo","foo"))

def handleDelete():

    #execute
    print("foo")


# Handly Python
if __name__ == "__main__":

    #catchSignals = set(signal.Signals) - {signal.SIGKILL, signal.SIGINT}
    #for sig in catchSignals:
   # signal.signal(signal.SIGINT, handler) not working since subprocess is only stopped
#    signal.signal(signal.SIGKILL, handler)

    parser = argparse.ArgumentParser(description='Borg-Backup script')
    parser.add_argument('--backup', action="store_true")
    parser.add_argument('--forget', action="store_true")

    args = parser.parse_args()

    if args.backup:
        # backup
        handleBackup()
        
        # check back on athq-monitoring
        headers = {
                'Content-type': 'application/json',
                }
        data = '{ "service: "backup_kathi_laptop", "token" : ' + credentials.ATHQ_SECRET_TOKEN + ' , "info" : "backup successful", "status" : "OK" }'
        response = requests.post('https://async-icinga.athq.de/', headers=headers, data=data)

    if args.forget:
        handleDelete()
    print("DONE")
