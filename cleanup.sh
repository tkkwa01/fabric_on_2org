./host1down.sh
./host2down.sh
./host3down.sh
./host4down.sh


yes |docker swarm leave --force
yes|docker volume prune
yes|docker container prune

