#!/bin/sh

MINIO_HOST="minio"
MINIO_PORT="9000"
ALIAS="lakehouse_minio_client"

until mc alias set $ALIAS http://$MINIO_HOST:$MINIO_PORT $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD; do
    sleep 1
done

until mc admin user add $ALIAS $MINIO_RW_USER $MINIO_RW_PASSWORD; do
    sleep 1
done

until mc admin user add $ALIAS $MINIO_R_USER $MINIO_R_PASSWORD; do
    sleep 1
done

mc admin policy attach $ALIAS readwrite --user $MINIO_RW_USER
mc admin policy attach $ALIAS readonly --user $MINIO_R_USER

mc mb --ignore-existing $ALIAS/landing
mc mb --ignore-existing $ALIAS/bronze
mc mb --ignore-existing $ALIAS/silver


tail -f /dev/null