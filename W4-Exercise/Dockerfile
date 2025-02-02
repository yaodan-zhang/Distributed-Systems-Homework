FROM python:latest
RUN apt-get update && apt-get install -y \
python3-dev \
libldap2-dev \
libssl-dev \
ldap-utils \
libsasl2-dev
RUN pip3 install python-ldap
RUN pip3 install dnspython
RUN pip3 install jupyterlab
CMD ["jupyter-lab", "--allow-root", "--ip", "0.0.0.0"]