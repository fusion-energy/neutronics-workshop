xhost local:root
sudo docker run --net=host -it --rm -v /tmp/.X11-unix:/tmp/.X11-unix -v $PWD:/openmc_workshop -e DISPLAY=unix$DISPLAY --privileged openmcworkshop/tasks:latest
