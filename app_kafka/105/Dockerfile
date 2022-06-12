FROM debian:bullseye-slim

RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get install -y wget && \ 
    apt-get install -y default-jre && \
    apt-get install -y default-jdk


RUN wget https://dlcdn.apache.org/kafka/3.1.0/kafka_2.13-3.1.0.tgz && \
    tar -xzf kafka_2.13-3.1.0.tgz

COPY server.properties kafka_2.13-3.1.0/config/

CMD cd kafka_2.13-3.1.0 && \
    ./bin/kafka-server-start.sh config/server.properties