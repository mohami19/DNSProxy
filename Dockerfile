FROM python:3-alpine

ADD src/dns_proxy.py .

ADD src/setting.json .

RUN pip install redis datetime

CMD ["python","./dns_proxy.py"]