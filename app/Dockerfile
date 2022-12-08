FROM python:3.10-bullseye

COPY . /app

WORKDIR /app

EXPOSE 8000:8000

RUN pip install -r /app/requirements.txt

CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--reload" ]