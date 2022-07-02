FROM debian:bullseye-slim

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get update && \
	apt-get install -y --no-install-recommends python3 python3-pip && \
	add-apt-repository ppa:pypy/ppa && \
	apt update && \
	apt install pypy3


COPY ["requirements.txt", "/tmp/requirements.txt"]

RUN ["pip3", "install", "-r", "/tmp/requirements.txt"]

COPY ["src/", "/opt/app_server"]

WORKDIR "/opt/app_server"

ENTRYPOINT ["pypy", "-m", "uvicorn", "--host", "0.0.0.0", "--workers", "30", "main:app"]