$ sudo apt-get install python-dev supervisor build-essential libffi-dev

$ sudo mkdir /var/log/core
$ sudo chmod 777 -Rf /var/log/core

$ sudo mkdir /usr/local/core
$ sudo chown -R $USER: /usr/local/core
$ sudo chmod 777 -Rf /usr/local/core

$ git clone git clone git@git.innfinision.net:ali.hallaji/core_services.git

$ cd /usr/local/core

$ sudo pip install --upgrade pip

$ sudo pip install -r requirements/table_requirements.txt

$ sudo pip install -r requirements.txt


$ sudo ln -s /usr/local/core/config/core_services.conf /etc/supervisor/conf.d

$ sudo /etc/init.d/supervisor restart
