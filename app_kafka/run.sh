sudo docker build $1 -t app_kafka
sudo docker run --network=host app_kafka
