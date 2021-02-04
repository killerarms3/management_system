# management_system

1. migrate
```
$ python manage.py makemigrations
$ python manage.py migrate
```
2. loaddata
- 有資料就跑以下指令
```
$ python manage.py loaddata --app accounts > db/accounts.json
$ python manage.py loaddata --app auth > db/auth.json
$ python manage.py loaddata --app customer > db/customer
$ python manage.py loaddata --app customer > db/customer.json
$ python manage.py loaddata --app contract > db/contract.json
$ python manage.py loaddata --app experiment > db/experiment.json
$ python manage.py loaddata --app product > db/product.json
$ python manage.py loaddata --app project > db/project.json
$ python manage.py loaddata --app language > db/language.json
$ python manage.py loaddata --app history > db/history.json
```
- 沒資料就跑以下指令
```
$ python LoadLanguageCode.py -i db/default_codes.yaml
```
3. add crontab
```
$ python manage.py crontab add
```
4. apache2
- 把`management_system`移動到`/var/www/html`下
```
$ sudo mv management_system /var/www/html
```
- 把`management_system_apache2.conf`移動到`/etc/apache2/sites-available`下
```
$ sudo mv management_system_apache2.conf /etc/apache2/sites-available
```
- 啟用
```
$ sudo a2ensite management_system_apache2
```
- reload apache2
```
$ sudo service apache2 reload
```
