FROM python:3.9
WORKDIR /usr/src/app


#registry: cdk-hnb659fds-container-assets-764573855117-us-east-1 
ENV SPARK_HOME=/usr/local/lib/python3.9/site-packages/pyspark
RUN mkdir -p ~/.aws
RUN mkdir -p "${SPARK_HOME}/jars"
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt update && apt-get install -y curl awscli vim libsnappy-dev openjdk-11-jdk mlocate docker
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# # https://medium.com/attest-product-and-technology/how-to-install-pyspark-locally-connecting-to-aws-s3-redshift-55488e87d4cd
# RUN rm ${SPARK_HOME}/jars/guava*.jar 
# RUN curl -s https://repo1.maven.org/maven2/com/google/guava/guava/23.1-jre/guava-23.1-jre.jar                                 --output "${SPARK_HOME}"/jars/guava-23.1-jre.jar 
# RUN curl -s https://repo1.maven.org/maven2/org/apache/spark/spark-hadoop-cloud_2.12/3.3.0/spark-hadoop-cloud_2.12-3.3.0.jar   --output "${SPARK_HOME}"/jars/spark-hadoop-cloud_2.12-3.3.0.jar
# RUN curl -s https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.1026/aws-java-sdk-bundle-1.11.1026.jar      --output "${SPARK_HOME}"/jars/aws-java-sdk-bundle-1.11.1026.jar
# RUN curl -s https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.2/hadoop-aws-3.3.2.jar                            --output "${SPARK_HOME}"/jars/hadoop-aws-3.3.2.jar
# RUN curl -s https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client/3.3.2/hadoop-client-3.3.0.jar                      --output "${SPARK_HOME}"/jars/hadoop-client-3.3.2.jar
# RUN updatedb

# ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
# ENV PATH=$PATH:$JAVA_HOME:$JAVA_HOME/bin:$SPARK_HOME
# ENV PYTHONPATH=/usr/local/lib/python3.8/site-packages/:usr/src/app:/usr/local/lib/python3.9/site-packages/pyspark/python/lib

# RUN mkdir -p ~/.aws
# RUN echo "" > ~/.aws/credentials

COPY ./app.py app.py 




