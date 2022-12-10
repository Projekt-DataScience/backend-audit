FROM python:3.10-bullseye

COPY ./app /app
COPY ./helper_scripts/generate_recurrent_audits.py /opt/generate_recurrent_audits.py

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000:8000

RUN pip install -r /app/requirements.txt
RUN echo "* 0 * * * bash -c 'python3 /opt/generate_recurrent_audits.py'" >> /etc/cron.d/generate_recurrent_audits

CMD [ "python", "main.py" ]