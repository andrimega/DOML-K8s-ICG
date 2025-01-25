FROM debian:10.12-slim

RUN apt-get update && apt-get install -y \
  procps curl apt-transport-https gnupg2 inotify-tools python-docker && \
  curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add - && \
  echo "deb https://packages.wazuh.com/4.x/apt/ stable main" | tee /etc/apt/sources.list.d/wazuh.list && \
  apt-get update &&  \
  apt-get install -y lsb-release && \
  rm -rf /var/lib/apt/lists/*

RUN curl -so wazuh-agent-4.2.5.deb https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.2.5-1_amd64.deb && dpkg -i ./wazuh-agent-4.2.5.deb

COPY entrypoint.sh /entrypoint.sh
COPY ossec.conf /var/ossec/etc/

ENTRYPOINT ["bash","entrypoint.sh"]