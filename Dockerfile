FROM python:3.7-slim

COPY requirements .
RUN pip install -r requirements

RUN apt update -y \
 && apt upgrade -y
RUN apt install -y cron
RUN (crontab -l 2>/dev/null; echo "1 0 * * * /app/update.sh") | crontab -

WORKDIR /app
COPY . .

CMD [ "python" ]