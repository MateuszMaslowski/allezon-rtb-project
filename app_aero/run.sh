sudo cp $1/aerospike.conf /etc/aerospike/
sudo systemctl stop aerospike
sudo systemctl start aerospike
sudo systemctl status aerospike

