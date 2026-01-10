#! /bin/bash

if [ ! -d "airflow/logs" ]; then
  mkdir -p airflow/logs
  chmod 777 airflow/logs
fi