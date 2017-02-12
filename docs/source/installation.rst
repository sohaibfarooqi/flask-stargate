Installation and Running
=========================================

You need to define following Environment Variables:
 - DATABASE_URL = '<yourdburi>'
 - FLASK_APP = wsgi.py
 - FLASK_DEBUG = 'True/False'

Clone the repository:
https://github.com/sohaibfarooqi/stargate.git

Create VirtualEnv:
virtualenv -p "path to python" env
source env/bin/activate

Running:
flask run
