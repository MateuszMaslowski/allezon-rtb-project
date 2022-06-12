sudo docker build . -t app_kafka
sudo docker run --network=host app_kafka
