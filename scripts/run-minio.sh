#!/usr/bin/env bash


docker stop minio
docker rm minio
docker run -d \
   -p 9000:9000 \
   -p 9090:9090 \
   --name minio \
   -v $PWD/minio-storage:/data \
   -e "MINIO_ROOT_USER=LIBREPROPERTY" \
   -e "MINIO_ROOT_PASSWORD=LIBREPROPERTY" \
   quay.io/minio/minio server /data --console-address ":9090"
