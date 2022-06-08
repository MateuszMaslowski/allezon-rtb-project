sudo docker build -t app_aero $1
sudo docker run --network=host --privileged app_aero
