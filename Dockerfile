FROM ubuntu:20.04

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "./run_tests.py" ]