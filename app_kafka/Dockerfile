FROM debian:bullseye-slim


RUN wget https://dlcdn.apache.org/kafka/3.1.0/kafka_2.13-3.1.0.tgz && \
    tar -xzf kafka_2.13-3.1.0.tgz

COPY $1/server.properties kafka_2.13-3.1.0/config/

CMD cd kafka_2.13-3.1.0 && \
    ./bin/kafka-server-start.sh config/server.properties