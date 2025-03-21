FROM python:3.13.1

RUN mkdir /metall_roll

WORKDIR /metall_roll

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x /metall_roll/docker/*.sh

