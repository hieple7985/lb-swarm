#!/usr/bin/env bash

currentPath=$(pwd)

#build trigger
cd $currentPath
cd trigger

docker build -t mrdotiendat/trigger:latest .

#build downloader
cd $currentPath
cd downloader

docker build -t mrdotiendat/downloader:latest .

#build extractor
cd $currentPath
cd extractor

docker build -t mrdotiendat/extractor:latest .

#build uploader
cd $currentPath
cd uploader

docker build -t mrdotiendat/uploader:latest .

#build httpserver
cd $currentPath
cd httpserver

npm install && npm run build 

docker build -t mrdotiendat/httpserver:latest .

#run docker-compose
cd $currentPath

echo "y" | docker system prune 
docker-compose down
docker-compose up -d
