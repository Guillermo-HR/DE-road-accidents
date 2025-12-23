#! /bin/bash

if [ -d "input_data" ]; then
  rm -rf input_data
fi  
if [ -d "S3" ]; then
  sudo rm -rf S3
fi