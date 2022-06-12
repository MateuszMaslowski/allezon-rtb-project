sudo docker build $1 -t app_zookeeper
sudo docker run --network=host app_zookeeper


