sudo docker build . -t app_proc
sudo docker run --network=host app_proc
