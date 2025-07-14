FROM python:3.10.18-slim-bookworm

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 4044

CMD [ "flask", "run", "--host=0.0.0.0", "--port=4044"]
