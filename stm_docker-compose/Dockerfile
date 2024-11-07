FROM ubuntu:20.04

USER root
RUN touch /etc/apt/apt.conf.d/99verify-peer.conf | echo >>/etc/apt/apt.conf.d/99verify-peer.conf "Acquire { https::Verify-Peer false }"
RUN echo "deb [arch=amd64 trusted=yes] https://raw.githubusercontent.com/SolaceLabs/apt-stm/master stm main" | tee  /etc/apt/sources.list.d/solace-stm-test.list
RUN apt-get update
RUN apt-get install stm 

RUN stm config init

ADD Test-Banking root/.stm/feeds/Test-Banking
COPY test-banking-0.1.0.json tmp/test-banking-0.1.0.json
COPY stm-cli-config.json root/.stm/stm-cli-config.json

CMD ["tail", "-f"]