FROM python

RUN mkdir -p /opt/app

WORKDIR /opt/app

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 5050

CMD python3 app.py
