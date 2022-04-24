FROM python:3.8.12-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update -y
# RUN apt-get install -y python3 python3-pip 
RUN apt-get install -y tk
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "lib/gui.py" ]
ENTRYPOINT [ "python3" ]