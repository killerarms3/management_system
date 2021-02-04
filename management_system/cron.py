import subprocess
import os
from django.conf import settings
import sys
from datetime import datetime
from django.core import management
import gzip


def backup():
    now = datetime.today().strftime('%Y%m%d')
    if not os.path.exists(os.path.join(settings.BASE_DIR, 'backup')):
        os.makedirs(os.path.join(settings.BASE_DIR, 'backup'))
    backup_f = os.path.join(settings.BASE_DIR, 'backup', 'backup_'+now+'.gz')
    management.call_command('dumpdata', output=os.path.join(settings.BASE_DIR, 'db', 'backup.json'))
    with gzip.open(backup_f, 'wb') as out_f:
        with open(os.path.join(settings.BASE_DIR, 'db', 'backup.json'), 'rb') as in_f:
            out_f.writelines(in_f)



