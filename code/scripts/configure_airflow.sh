#! /bin/bash

if [ ! -d "dags" ]; then
  mkdir dags
  chmod 777 dags
fi

if [ ! -d "logs" ]; then
  mkdir logs
  chmod 777 logs
fi

if [ ! -d "plugins" ]; then
  mkdir plugins
  chmod 777 plugins
fi