#/bin/sh
source activate MeasMan
rm MeasurementManagement/migrations/*.py
rm db.sqlite3
python manage.py migrate
py.test
