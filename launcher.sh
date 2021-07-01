#!/bin/bash

sudo docker ps -a -q  --filter ancestor=covid19
sudo docker rmi covid19 --force && sudo docker-compose build && sudo docker-compose up -d