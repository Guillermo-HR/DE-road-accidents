#!/bin/sh

MINIO_HOST="minio"
MINIO_PORT="9000"
ALIAS="lakehouse_minio_client"

until mc alias set $ALIAS http://$MINIO_HOST:$MINIO_PORT $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD; do
    sleep 1
done

mc mb --ignore-existing $ALIAS/landing
mc mb --ignore-existing $ALIAS/bronze
mc mb --ignore-existing $ALIAS/silver

echo "--- Buckets on the system: ---"
mc ls $ALIAS

tail -f /dev/null