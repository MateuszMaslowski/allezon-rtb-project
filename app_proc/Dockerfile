FROM debian:bullseye-slim

RUN apt-get update && \
	apt-get install -y --no-install-recommends python3 python3-pip

COPY ["requirements.txt", "/tmp/requirements.txt"]

RUN ["pip3", "install", "-r", "/tmp/requirements.txt"]

COPY ["src/", "/opt/app_proc"]

WORKDIR "/opt/app_proc"

CMD ["python3", "main.py"]