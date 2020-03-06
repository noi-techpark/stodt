cron
echo Switching to new host '$HOST'
sed -e 's%http://localhost:5000%'$HOST'%g' www/index.html
python /code/app.py
