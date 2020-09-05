FROM ubuntu

RUN apt-get update && apt-get -y install python3-pip && apt-get -y install python3 && apt-get -y install gunicorn


WORKDIR /opt/app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5050

CMD gunicorn3 --workers=3 --threads=2 --bind=0.0.0.0:5050 app:app