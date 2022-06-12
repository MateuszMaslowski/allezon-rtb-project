sudo docker build $1 -t app_kafka
sudo docker run -d --network=host app_kafka
