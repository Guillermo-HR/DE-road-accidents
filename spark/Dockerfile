FROM jupyter/pyspark-notebook:spark-3.5.0

USER root

ENV HADOOP_AWS_VERSION=3.3.4
ENV AWS_JAVA_SDK_VERSION=1.12.500

RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/${HADOOP_AWS_VERSION}/hadoop-aws-${HADOOP_AWS_VERSION}.jar -P /usr/local/spark/jars/ && \
    wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/${AWS_JAVA_SDK_VERSION}/aws-java-sdk-bundle-${AWS_JAVA_SDK_VERSION}.jar -P /usr/local/spark/jars/

USER ${NB_UID}

COPY requirements.txt /home/jovyan/work/
RUN pip install --no-cache-dir -r /home/jovyan/work/requirements.txt