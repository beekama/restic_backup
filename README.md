# Backup using Restic
## Prerequisites
- python3
- restic
## Create Restic Repository
Create a restic repository as described in their [documentation](https://restic.readthedocs.io/en/latest/030_preparing_a_new_repo.html#sftp). <br>
The script uses SFTP so in my case the command looks like this: <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
```restic -r sftp:foo:/srv/restic-repo init```
## Credentials
For my credentials i use a separate file 'credentials.py' located in the same directory as the backup-script. <br>
The file contains the following variables: <br>
- RESTIC_REPOSITORY
- RESTIC_PASSWORD
- ATHQ_SECRET_TOKEN (optional for awesome monitoring created by [FAUSheppy](https://github.com/FAUSheppy/icinga-webhook-gateway)
## Run 
For example as crontab entry: <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
```0 3 * * * /PATH/TO/backup.py --backup```
