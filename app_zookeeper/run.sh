sudo docker build . -t app_zookeeper
sudo docker run -d --network=host app_zookeeper


