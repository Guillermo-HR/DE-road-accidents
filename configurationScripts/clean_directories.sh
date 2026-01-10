#! /bin/bash

if [ -d "S3" ]; then
  sudo rm -rf S3
fi

if [ -d "airflow/logs" ]; then
  sudo rm -rf airflow/logs
fi