#!/bin/bash

# This script creates necessary directories for the project

if [ -d "input_data" ]; then
  rm -rf input_data
fi  
if [ -d "S3" ]; then
  rm -rf S3
fi

mkdir -p input_data
mkdir -p input_data/accidents
mkdir -p input_data/catalogs

mkdir -p S3
mkdir -p S3/bronze
mkdir -p S3/bronze/accidents
mkdir -p S3/bronze/catalogs
mkdir -p S3/silver
mkdir -p S3/silver/accidents_delta
