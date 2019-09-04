FROM docker.io/bigstepinc/jupyter_bdl:2.4.1-11
ARG PIP_PACKAGES
ENV PIP_PACKAGES=${PIP_PACKAGES:-'seaborn'}
ARG OS_PACKAGES
ENV OS_PACKAGES=${OS_PACKAGES:-'vim'}
ARG API_KEY
ENV API_KEY=${API_KEY}
ARG API_ENDPOINT
ENV API_ENDPOINT=${API_ENDPOINT}

COPY . .
RUN pip install $PIP_PACKAGES && \
    apt-get install --no-install-recommends -y $OS_PACKAGES && \
    mkdir /root/.docker && \
    cp /kaniko/.docker/config.json /root/.docker/config.json && \
    chsh -s /bin/bash && cd && \
    wget https://repo.lentiq.com/bdl_client_python_1.0.0.tar.gz && \
    tar -xzvf bdl_client_python_1.0.0.tar.gz && \
    rm -rf /opt/bdl_client_python_1.0.0.tar.gz && \
    cd ./bdl_client_python && \
    pip install . && cd /

ENTRYPOINT ["python ./entrypoint.py $API_KEY $API_ENDPOINT"]
