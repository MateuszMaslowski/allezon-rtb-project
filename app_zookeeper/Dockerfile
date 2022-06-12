FROM debian:bullseye-slim


RUN wget https://dlcdn.apache.org/kafka/3.1.0/kafka_2.13-3.1.0.tgz && \
    tar -xzf kafka_2.13-3.1.0.tgz


CMD cd kafka_2.13-3.1.0 && \
    ./bin/zookeeper-server-start.sh config/zookeeper.properties