FROM ubuntu

RUN apt-get update
RUN apt install -y python3 python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install zimply

COPY . .
CMD [ "python3", "extract.py" ]

LABEL version="1.0"

LABEL NAME="mrdotiendat/zimserver:latest"

EXPOSE 9454

