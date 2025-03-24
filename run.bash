#! /bin/bash -

cd /home/haasrr/repos/helpdesk
source .venv/bin/activate
python3 manage.py runsslserver csciauto1.etsu.edu:8000 --certificate certs/server.crt --key certs/server.key --settings=helpdesk.settings_prod
