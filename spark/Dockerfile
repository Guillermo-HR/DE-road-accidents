FROM jupyter/pyspark-notebook:spark-3.5.0

USER ${NB_UID}
COPY requirements.txt /home/jovyan/work/
RUN pip install --no-cache-dir -r /home/jovyan/work/requirements.txt