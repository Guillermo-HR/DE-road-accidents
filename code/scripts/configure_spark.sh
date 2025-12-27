#!/bin/bash

pip install --upgrade pip

pip install -r /home/iceberg/notebooks/requirements.txt

jupyter lab \
  --ip=0.0.0.0 \
  --port=8888 \
  --no-browser \
  --allow-root \
  --NotebookApp.token='' \
  --notebook-dir=/home/iceberg/notebooks/scripts