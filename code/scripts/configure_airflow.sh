#!/bin/bash

pip install apache-airflow-providers-amazon

sleep 10
airflow db migrate

airflow users create \
    --username $_AF_USER \
    --password $_AF_PASS \
    --firstname $_AF_FNAME \
    --lastname $_AF_LNAME \
    --role Admin \
    --email $_AF_EMAIL || true
    
airflow scheduler & airflow webserver