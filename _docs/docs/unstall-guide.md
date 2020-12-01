## Installing dependencies
First or all check that these dependencies are installed:

- Python3.7

  - ```
    python3.7 -V
    pip3.7 -V
    ```

- Virtualenv

  - ```
    virtualenv -h
    ```

- Redis

  - ```
    systemctl status redis.service
    ```

  - ```
    redis-scli> ping
    PONG
    ```

### system proxy

```
export http_proxy=http://proxy.mosreg.ru:8080/
export https_proxy=http://proxy.mosreg.ru:8080/
export no_proxy="localhost, 127.0.0.1"
```

### Install python3.7 and pip3.7 from source

**install dependences**

```
apt update
apt install git wget curl build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev xz-utils libbz2-dev libbz2-dev
```

**download and unpack python 3.7**

```
cd /opt && \
    wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz && \
    tar xvf /opt/Python-3.7.3.tar.xz && \
    rm Python-3.7.3.tar.xz
```

**compile python 3.7**

```
cd /opt/Python-3.7.3/ && \
    ./configure --enable-optimizations
cd /opt/Python-3.7.3/ && \
    make -j 8
```

**install python 3.7**

```
cd /opt/Python-3.7.3/ && \
    make altinstall
```

**check installation of python 3.7 и pip3.7**

```
python3.7 -V
pip3.7 -V
```
### Install Redis from source

**compile Redis db**

```
cd /opt && \
	wget http://download.redis.io/redis-stable.tar.gz && \
	tar xvf /opt/redis-stable.tar.gz && \
	mkdir /opt/redis && \
	cp -r  /opt/redis-stable  /opt/redis && \
	rm /opt/redis-stable.tar.gz && \
	cd redis && \
	make && \
	cp src/redis-cli redis-cli && chmod +x redis-cli && \
	cp src/redis-server redis-server && chmod +x redis-server
```

**configure Redis**

```
cp /opt/analytics-api/doc/config_example/redis.conf /opt/redis/redis.conf

mkdir /opt/redis/log/ && touch /opt/redis/log/log.log
```

*This configuration hosts Redis on localhost: 6379 logs to /opt/redis/log/log.log dumps data to /opt/redis/dump.rdb and creates 1 read only replica of itself. In case of a crash, the data will be replicated and saved to disk.*

**check Redis working state**

```
cd /opt/redis/ && \
	./redis-server redis.conf
```

```
cd /opt/redis/ && \
	./redis-scli

redis-scli> ping
PONG
```

**create systemd service for Redis**

```
vim /etc/systemd/system/redis.service
```

```
[Unit]
Description=redis
After=syslog.target
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=root
WorkingDirectory=/opt/redis/
ExecStart=/opt/redis/redis-server redis.conf

[Install]
WantedBy=multi-user.target

```

**Start redis service**

```
systemctl enable redis
systemctl start  redis
```

## Installing smev-client

**install from deb package**

```
apt purge smev-client
dpkg -i smev-client_<version>_amd64.deb 
```

**configure smev-client**

```
cd /etc/systemd/system
```

1. smev-file-repository-worker.service

   ```
   vi smev-file-repository-worker.service
   ```
   
   configure:
   
   ```
   Environment=http_proxy=""
   Environment=https_proxy=""
   Environment=no_proxy="localhost, 127.0.0.1"
   Environment=POSTGRES_USER=test
   Environment=Environment=POSTGRES_PASSWORD=password
   Environment=POSTGRES_HOST=localhost
   Environment=POSTGRES_PORT=5432
   Environment=POSTGRES_DB=example
   Environment=STORAGE=/app/storage
   Environment=FTP=smev3-n0.test.gosuslugi.ru
   ```

2. smev-file-repository.service

   ```
   vi smev-file-repository.service
   ```

   configure:

   ```
   Environment=http_proxy=""
   Environment=https_proxy=""
   Environment=no_proxy="localhost, 127.0.0.1"
   Environment=POSTGRES_USER=test
   Environment=Environment=POSTGRES_PASSWORD=password
   Environment=POSTGRES_HOST=localhost
   Environment=POSTGRES_PORT=5432
   Environment=POSTGRES_DB=example
   Environment=STORAGE=/app/storage
   Environment=FTP=smev3-n0.test.gosuslugi.ru
   ```

3. smev-record-repository.service

   ```
   vi smev-record-repository.service
   ```

   configure:

   ```
   Environment=http_proxy=""
   Environment=https_proxy=""
   Environment=no_proxy="localhost, 127.0.0.1"
   Environment=POSTGRES_USER=test
   Environment=Environment=POSTGRES_PASSWORD=password
   Environment=POSTGRES_HOST=localhost
   Environment=POSTGRES_PORT=5432
   Environment=POSTGRES_DB=example
   ```

4. smev-connector.service

   ```
   vi smev-connector.service
   ```

   configure:

   ```
   Environment=http_proxy=""
   Environment=https_proxy=""
   Environment=no_proxy="localhost, 127.0.0.1"
   ```

5. smev-plugins.service

   ```
   vi smev-plugins.service
   ```

   configure:

   ```
   Environment=http_proxy=""
   Environment=https_proxy=""
   Environment=no_proxy="localhost, 127.0.0.1"
   ```

**run smev-client**

```
systemctl enable smev-file-repository.service
systemctl enable smev-file-repository-worker.service
systemctl enable smev-json2xml.service
systemctl enable smev-record-repository.service
systemctl enable smev-connector.service
systemctl enable smev-plugins.service

systemctl srart smev-file-repository.service
systemctl srart smev-file-repository-worker.service
systemctl srart smev-json2xml.service
systemctl srart smev-record-repository.service
systemctl srart smev-connector.service
systemctl srart smev-plugins.service
```
