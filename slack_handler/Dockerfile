FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

RUN adduser -D zabbix-slack

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./slack_handler.py /app/slack_handler.py

WORKDIR /app

ENV FLASK_APP slack_handler.py

RUN chown -R zabbix-slack:zabbix-slack /app
USER zabbix-slack

EXPOSE 5000

CMD ["gunicorn", "-b", ":5000", "--access-logfile","-", "--error-logfile", "-", "slack_handler:app"]
