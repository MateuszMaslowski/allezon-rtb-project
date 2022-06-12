sudo docker build . -t app_server
sudo docker run -d --network=host app_server

