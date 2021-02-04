#!/bin/bash
NOW=$(date +"%Y%m%d")
FILE="backup_$NOW.tgz"

echo "Dumping data to ./db"
python manage.py dumpdata accounts > db/accounts.json
python manage.py dumpdata auth > db/auth.json
python manage.py dumpdata customer > db/customer
python manage.py dumpdata customer > db/customer.json
python manage.py dumpdata contract > db/contract.json
python manage.py dumpdata experiment > db/experiment.json
python manage.py dumpdata product > db/product.json
python manage.py dumpdata project > db/project.json
python manage.py dumpdata language > db/language.json
python manage.py dumpdata history > db/history.json

echo "Backing up data to backup/backup_$NOW.tgz file, please wait..."
mkdir -p backup
tar zcvf backup/$FILE db



