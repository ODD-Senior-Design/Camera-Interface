#!/bin/bash
sudo docker build -t camera-interface . && sudo docker tag camera-interface eliteabhi/camera-interface:latest && sudo docker push eliteabhi/camera-interface:latest
sudo docker compose up -d
