sudo docker build -t my-proxy .
sudo docker run -d --network=host --privileged my-proxy
