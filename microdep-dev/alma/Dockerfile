# Dockerfile to build perfSONAR  node
# To build, cd to folder and run
#
#     docker build --build-arg TYPE=<node-variant> -t perfsonar-<node-variant> ."
#
# where <node-variant> may be "testpoint" og "toolkit" 
#
# To run container with systemd operative in none-priviledge mode (may not work...)  
#   docker run -d --tmpfs /tmp --tmpfs /run -v /sys/fs/cgroup:/sys/fs/cgroup:ro --net=host --name perfsonar-testpoint --rm perfsonar-testpoint
#   docker run -d --tmpfs /tmp --tmpfs /run -v /sys/fs/cgroup:/sys/fs/cgroup:ro --net=host --name perfsonar-toolkit --rm perfsonar-toolkit
#
# ... or in privilede-mode
#   docker run -d --privileged --net=host --name perfsonar-testpoint --rm perfsonar-testpoint
#   docker run -d --privileged --net=host --name perfsonar-toolkit --rm perfsonar-toolkit
#
# Apply pipeworks to give container its own dhcp address (set TYPE to relevant variant):
#
#    TYPE='toolkit|testpoint' && \
#    docker run -d --privileged --net=none --name perfsonar-${TYPE} --rm perfsonar-${TYPE} && \
#    sudo ~/pipework/pipework eth0 perfsonar-${TYPE} dhclient-f U:${TYPE} && \
#    docker exec -it perfsonar-${TYPE} ifconfig eth1 
#


FROM systemd-image-alma:latest
MAINTAINER Otto J Wittner <wittner@sikt.no>

# Fix default locals
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV LC_COLLATE=C
ENV LC_CTYPE=en_US.UTF-8

# ---- D o w n l o a d   a n d   i n s t a l l   p a c k a g e s  ------

# Install the EPEL RPM
RUN dnf install -y epel-release && dnf config-manager --set-enabled crb

# Point Almalinux 9 installation at the perfSONAR main repository
RUN dnf install -y http://software.internet2.edu/rpms/el9/x86_64/latest/packages/perfsonar-repo-0.11-1.noarch.rpm

# Clean cache and update 
RUN dnf clean all && rm -rf /var/cache/dnf/* && dnf -y update

# Install management packages
RUN dnf install -y --allowerasing coreutils man-db nano emacs git patch openssh-clients net-tools iputils traceroute tcpdump curl bind-utils unzip gnupg

# Fiks tcpdump issue for priveledge mode
RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump
RUN ln -s /usr/bin/tcpdump /usr/sbin/tcpdump

# Install and explicitly init postgres (since initialisation seems to not happen "by it self") 
#
# Based on a Dockerfile at
# https://raw.githubusercontent.com/zokeber/docker-postgresql/master/Dockerfile
# and
# https://raw.githubusercontent.com/perfsonar/perfsonar-testpoint-docker/master/systemd/Dockerfile

RUN dnf install -y postgresql-server

# Set the environment variables
ENV PGDATA /var/lib/pgsql/data

# Initialize the database
RUN su - postgres -c "/usr/bin/pg_ctl init"

# Change own user
RUN chown -R postgres:postgres /var/lib/pgsql/data/*

#Start postgresql and install perfSONAR
ARG TYPE
RUN mkdir -p /var/run/postgresql && chown postgres.postgres /var/run/postgresql \
    && su - postgres -c "/usr/bin/pg_ctl -D /var/lib/pgsql/data start -w -t 120" \
    && dnf install -y perfsonar-$TYPE

# Clean up 
RUN dnf clean all && rm -rf /var/cache/dnf/* && dnf -y update

# Add Opensearch dashboards ("Kibana")
RUN if [ "$TYPE" = "toolkit" ]; then \
       dnf -y install opensearch-dashboards && systemctl enable opensearch-dashboards.service ; \
    fi
# Add Grafana visualisation server    
COPY etc/grafana.repo /etc/yum.repos.d/grafana.repo
RUN dnf -y install wget && wget -q -O gpg.key https://rpm.grafana.com/gpg.key && sudo rpm --import gpg.key
RUN if [ "$TYPE" = "toolkit" ]; then \
           dnf -y update && dnf -y install grafana; \
           systemctl enable grafana-server.service; \
    fi

# Add Rabbit message queue packages
RUN dnf -y install centos-release-rabbitmq-38 && dnf -y update
RUN dnf -y install rabbitmq-server python3-pika && systemctl enable rabbitmq-server.service 

# Add packages required by microdep analytics.
#   - qstream-gap-ana dependencies:
RUN dnf -y install perl-App-cpanminus perl-DateTime perl-JSON-XS perl-File-ShareDir-Install perl-Test-Exception perl-AnyEvent perl-ExtUtils-MakeMaker perl-version perl-Readonly perl-namespace-clean perl-Devel-GlobalDestruction perl-File-ShareDir perl-List-MoreUtils perl-Class-Data-Inheritable perl-Test-Simple perl-Test-Deep perl-YAML-LibYAML wget
RUN cpanm Statistics::Basic
RUN cpanm AnyEvent::RabbitMQ
RUN dnf -y install perl-ExtUtils-MakeMaker perl-Test-Simple
RUN cpanm Statistics::LineFit
#  - trace_event_reader dependencies
RUN dnf -y install python3-mysqlclient gcc python3-devel
RUN pip3 install multidict typing_extensions yarl async_timeout idna_ssl aiosignal cchardet charset_normalizer attrs
RUN pip3 install geoip2
COPY etc/microdep/GeoLite2-ASN.mmdb /usr/share/GeoIP/

# Fetch css, js and other source-files for Microdep
COPY microdep/server/script/*  /usr/lib/perfsonar/microdep-map/
COPY microdep/server/script/microdep-map.js  /usr/lib/perfsonar/microdep-map/
RUN  mkdir -p /usr/lib/perfsonar/microdep-map/js
RUN if [ "$TYPE" = "toolkit" ]; then \
       wget -P /usr/lib/perfsonar/microdep-map/js/ -i /usr/lib/perfsonar/microdep-map/list-of-external-sources.txt; \
    fi
# Add jquery libs
RUN dnf -y install js-jquery.noarch js-jquery-ui.noarch
RUN ln -s /usr/share/javascript/jquery/latest /usr/lib/perfsonar/microdep-map/jquery
RUN ln -s /usr/share/javascript/jquery-ui /usr/lib/perfsonar/microdep-map/jquery-ui


# ----  E n d   d o w n l o a d s   a n d   p a c k a g e   i n s t a l l   ----

# POSTGRES
# Reconfigure prefsonar Postgres DB (start db server first)
RUN mkdir -p /var/run/postgresql && chown postgres.postgres /var/run/postgresql \
    && su - postgres -c "/usr/bin/pg_ctl -D /var/lib/pgsql/data start -w -t 120" \
    && /usr/libexec/pscheduler/internals/db-update \
    && /usr/libexec/pscheduler/internals/db-change-password

# Rsyslog
# Note: need to modify default rsyslog configuration to work with Docker, 
# as described here: http://www.projectatomic.io/blog/2014/09/running-syslog-within-a-docker-container/
# (relevant for Centos7, but also for almalinux 9?)
COPY perfsonar-testpoint-docker/rsyslog/rsyslog.conf /etc/rsyslog.conf
COPY perfsonar-testpoint-docker/rsyslog/listen.conf /etc/rsyslog.d/listen.conf
COPY perfsonar-testpoint-docker/rsyslog/python-pscheduler.conf /etc/rsyslog.d/python-pscheduler.conf
COPY perfsonar-testpoint-docker/rsyslog/owamp-syslog.conf /etc/rsyslog.d/owamp-syslog.conf

# Make ntdp stay root and stop attempting to update system clock
#RUN sed -i 's|-u ntp:ntp ||g' /usr/lib/systemd/system/ntpd.service
#RUN echo "disable kernel" >> /etc/ntp.conf

# Make pscheduler services more tolerant to restart failures
RUN sed -i 's|Restart=always|Restart=always\nStartLimitBurst=1000\nStartLimitIntervalSec=30|g' /usr/lib/systemd/system/pscheduler-archiver.service
RUN sed -i 's|Restart=always|Restart=always\nStartLimitBurst=1000\nStartLimitIntervalSec=30|g' /usr/lib/systemd/system/pscheduler-runner.service
RUN sed -i 's|Restart=always|Restart=always\nStartLimitBurst=1000\nStartLimitIntervalSec=30|g' /usr/lib/systemd/system/pscheduler-scheduler.service
RUN sed -i 's|Restart=always|Restart=always\nStartLimitBurst=1000\nStartLimitIntervalSec=30|g' /usr/lib/systemd/system/pscheduler-ticker.service

# Reduce range for owamp and twamp test-ports (to more easy enable docker port mapping)
RUN sed -i 's|testports 8760-9960|testports 8760-8800|g' /etc/owamp-server/owamp-server.conf
RUN sed -i 's|testports 18760-19960|testports 18760-18800|g' /etc/twamp-server/twamp-server.conf

# Add lookup service configs 
COPY etc/lsregistrationdaemon.conf*  /etc/perfsonar/

# Add service to apply host specific config
COPY etc/hostspecific-conf.service /usr/lib/systemd/system/
RUN systemctl enable hostspecific-conf.service

RUN if [ "$TYPE" = "toolkit" ]; then \
# Fix JNA and temp-file issue with Opensearch and Logstash,
       sed -i 's|${OPENSEARCH_TMPDIR}|/var/log/opensearch|g' /etc/opensearch/jvm.options; \
       sed -i 's|#-Djava.io.tmpdir=$HOME|-Djava.io.tmpdir=/var/log/logstash|g' /etc/logstash/jvm.options; \
# Go easy on java heap size
       sed -i 's|-Xms7g|-Xms2g|g' /etc/opensearch/jvm.options; \
       sed -i 's|-Xmx7g|-Xms4g|g' /etc/opensearch/jvm.options; \
# Increase startup timeout and add auto restart for Opensearch
       sed -i 's|TimeoutStartSec=75|TimeoutStartSec=600\nRestart=on-failure\nRestartSec=10s|g' /usr/lib/systemd/system/opensearch.service; \
# Fix template error for Logstash
#       cp /usr/share/logstash/vendor/local_gems/022abded/logstash-output-opensearch/lib/logstash/outputs/opensearch/templates/ecs-disabled/1x.json /usr/share/logstash/vendor/local_gems/022abded/logstash-output-opensearch/lib/logstash/outputs/opensearch/templates/ecs-disabled/2x.json; \
# Fix SSL problems with proxy towards Opensearch
       cp /etc/opensearch/node.pem /etc/opensearch/both.pem; \
       sed 's|PRI|RSA PRI|g' /etc/opensearch/node-key.pem >> /etc/opensearch/both.pem; \
       sed -i 's|ProxyPass|    SSLProxyVerify none\n    SSLProxyCheckPeerCN off\n    SSLProxyCheckPeerName off\n    SSLProxyCheckPeerExpire off\n    SSLProxyMachineCertificateFile /etc/opensearch/both.pem\n    ProxyPass|' /etc/httpd/conf.d/apache-opensearch.conf; \
# Fix access to local resources when external port mapping alters urls
       sed -i 's|Listen 443 https|Listen 443 https\nListen 4435 https\nListen 4436 https|' /etc/httpd/conf.d/ssl.conf; \
       sed -i 's|_default_:443|_default_:443 _default_:4435 _default_:4436|' /etc/httpd/conf.d/ssl.conf; \
       sed -i 's|Listen 80|Listen 80\nListen 8085\nListen 8086|' /etc/httpd/conf/httpd.conf; \
       sed -i 's|\*:80|\*:80 \*:8085 \*:8086|' /etc/httpd/conf.d/apache-toolkit_web_gui.conf; \
# Prepare script to re-config Opensearch security plugin to reconfig password
       sed -e 's|kirk|admin|g' -e 's|sudo|sudo OPENSEARCH_JAVA_HOME=/usr/share/opensearch/jdk|g' /securityadmin_demo.sh > /usr/local/sbin/securityadmin.sh; \
       chmod +x /usr/local/sbin/securityadmin.sh; \
# Set management gui user/password to admin/notadminnono
       dnf -y install httpd-tools && htpasswd -c -b /etc/perfsonar/toolkit/psadmin.htpasswd admin notadminnono ; \
    fi
# Add service to run (re)run password setup for opensearch
COPY etc/opensearch/opensearch-security-admin.service /usr/lib/systemd/system/
RUN systemctl enable opensearch-security-admin.service

#
#  M i c r o d e p - i n - p e r f s o n a r   a d d i t i o n s
#

# Add subsession support for powstream 
COPY owamp/owamp/owamp/powstream/powstream /usr/bin/powstream
COPY pscheduler/pscheduler-latencybg-subcount.patch-with-runtime-paths /usr/libexec/pscheduler
RUN cd /usr/libexec/pscheduler && patch -up1 < pscheduler-latencybg-subcount.patch-with-runtime-paths


# Add default tests (only for toolkit)
COPY etc/psconfig/pscheduler.d/* /etc/perfsonar/psconfig/pscheduler.d/
RUN if [ "$TYPE" = "testpoint" ]; then \
       rm -r /etc/perfsonar/psconfig; \
    fi
# Publish psconfig file for microdep tests
RUN if [ "$TYPE" = "tootlkit" ]; then \
       dnf install -y perfsonar-psconfig-publisher; \
       psconfig publish --pretty /etc/perfsonar/psconfig/pscheduler.d/microdep-tests.json; \
    fi

# Add some Rabbitmq and Opensearch debugging tools
COPY bin/rabbitmq-consume.py /usr/local/bin
COPY bin/consume.pl /usr/local/bin 
COPY bin/json2table.pl /usr/local/bin
COPY bin/opensearch-query.sh /usr/local/bin

# Fix host address, username and password for Opensearch dashboard ("Kibana")
RUN if [ "$TYPE" = "toolkit" ]; then \
       sed -i 's/# server.host: "localhost"/server.host: "0.0.0.0"/' /etc/opensearch-dashboards/opensearch_dashboards.yml; \
       USER=`awk -F " " '{print $1}' /etc/perfsonar/opensearch/opensearch_login` && sed -i "s|opensearch.username: kibanaserver|opensearch.username: $USER|g" /etc/opensearch-dashboards/opensearch_dashboards.yml; \
       PASSWD=`awk -F " " '{print $2}' /etc/perfsonar/opensearch/opensearch_login` && sed -i "s|opensearch.password: kibanaserver|opensearch.password: $PASSWD|g" /etc/opensearch-dashboards/opensearch_dashboards.yml; \
    fi

#  A d d   M i c r o d e p   m a p   w e b   G U I
# Add http config and html+js+ccs stuff
COPY etc/httpd/apache-microdep-gui.conf /etc/httpd/conf.d
RUN ln -s /usr/lib/perfsonar/microdep-map /root
RUN cd /usr/lib/perfsonar/microdep-map/; ln -s microdep-map.html index.html
# Fix cross origin mess and missing/obsolite/missplaced css, js and other source-files
# Moved to download/install: RUN mkdir /usr/lib/perfsonar/microdep-map/js
# Moved to download/install: RUN wget -P /usr/lib/perfsonar/microdep-map/js/ -i /usr/lib/perfsonar/microdep-map/list-of-external-sources.txt
RUN sed -i \
    -e 's|src=\".*jquery.*min\.js\"|src=\"jquery/jquery.min.js\"|' \
    -e 's|src=\".*jquery-ui.*min\.js\"|src=\"jquery-ui/jquery-ui.min.js"|' \
    -e 's|href=\".*jquery-ui.*min\.css\"|href=\"jquery-ui/jquery-ui.min.css\"|' \
    -e 's|<link rel="stylesheet" href="/uninett-bootstrap-theme/css/bootstrap.min.css">||' \
    -e 's|<link rel="stylesheet" href="/uninett-theme/css/uninett.css">||' \
    -e 's|; @import url("/styles.css");||' \
    -e 's|https://.*\(/.*\.js"\)|js\1|' \
    -e 's|https://.*\(/.*\.css"\)|js\1|' \
    -e 's|//.*\(/.*\.js"\)|js\1|' \
    -e 's|//.*\(/.*\.css"\)|js\1|' \
    -e 's|/js/ajax-loader.gif|"js/ajax-loader.gif"|' \
    -e 's|/js\.gml|js|' \
    -e 's|favicon.ico|/toolkit/favicon.ico|'    /usr/lib/perfsonar/microdep-map/microdep-map.html
RUN mv /usr/lib/perfsonar/microdep-map/stats.js /usr/lib/perfsonar/microdep-map/js/
RUN mv /usr/lib/perfsonar/microdep-map/ajax-loader.gif /usr/lib/perfsonar/microdep-map/js/
COPY etc/microdep/marker-*.png /usr/lib/perfsonar/microdep-map/js/images/
# Fiks some perl libs
RUN sed -i 's|::Simple||' /usr/lib/perfsonar/microdep-map/microdep-config.cgi
RUN sed -i "s|YAML|YAML::XS|g" /usr/lib/perfsonar/microdep-map/yaml-to-json.cgi
# Add and adjust to support global/Dragonlab topology (and remove Uninett topology)
RUN sed -i 's|/var/lib/microdep|/usr/lib/perfsonar/microdep-map|' /usr/lib/perfsonar/microdep-map/microdep-config.yml
COPY etc/microdep/dragonlab*.json /usr/lib/perfsonar/microdep-map/dragonlab/
# Init Microdep config db
RUN if [ "$TYPE" = "toolkit" ]; then \
        mkdir -p /usr/lib/perfsonar/microdep-map/mp-dragonlab/etc/; \
        /usr/lib/perfsonar/microdep-map/microdep-psconfig-load.pl -c --db /usr/lib/perfsonar/microdep-map/mp-dragonlab/etc/microdep.db /etc/perfsonar/psconfig/pscheduler.d/microdep-tests.json; \
    fi

# Fix credentials ++ for accessing Opensearch
RUN if [ "$TYPE" = "toolkit" ]; then \
        USER=`awk -F " " '{print $1}' /etc/perfsonar/opensearch/opensearch_login` ;\
        PASSWD=`awk -F " " '{print $2}' /etc/perfsonar/opensearch/opensearch_login` ; \
        sed -i "s|http://admin:no+nz+br|https://$USER:$PASSWD|g" /usr/lib/perfsonar/microdep-map/elastic-get-date-type.pl; \
        sed -i "s|curl -X POST|curl -X POST --insecure|g" /usr/lib/perfsonar/microdep-map/elastic-get-date-type.pl; \
    fi

#   A d d   T r a c e t r e e   w e b   G U I 
# Add http config and html+js+ccs stuff
#COPY etc/httpd/apache-tracetree-gui.conf /etc/httpd/conf.d
#COPY pstracetree/*  /usr/lib/perfsonar/tracetree/
#RUN ln -s /usr/lib/perfsonar/tracetree /root
#RUN cd /usr/lib/perfsonar/tracetree/; ln -s ls.html index.html
COPY pstracetree/rpmbuild/RPMS/noarch/perfsonar-tracetree-5.1.0-alfa1.el9.noarch.rpm /root
RUN if [ "$TYPE" = "toolkit" ]; then \
        dnf install -y /root/perfsonar-tracetree-5.1.0-alfa1.el9.noarch.rpm; \
    fi	 

#   A d d   M i c r o d e p   a n a l y t i c s 
#    Gap analytics
#    (qstream-gap-ana is avaiable from https://scm.uninett.no/iou/microdep)
COPY bin/qstream-gap-ana /usr/local/bin
COPY etc/microdep/perfsonar-microdep-gap-ana.service /usr/lib/systemd/system/
RUN systemctl enable perfsonar-microdep-gap-ana.service

#    Traceroute analytics
COPY bin/create_new_db.sh /usr/local/bin
# POSTGRES
RUN mkdir -p /var/run/postgresql && chown postgres.postgres /var/run/postgresql \
    && su - postgres -c "/usr/bin/pg_ctl -D /var/lib/pgsql/data start -w -t 120" \
    && create_new_db.sh -t postgres -d routingmonitor
COPY bin/trace_event_reader.py /usr/local/bin
COPY etc/microdep/perfsonar-microdep-trace-ana.service /usr/lib/systemd/system/
RUN systemctl enable perfsonar-microdep-trace-ana.service

COPY etc/logstash/microdep /usr/lib/perfsonar/logstash/pipeline/microdep
RUN if [ "$TYPE" = "toolkit" ]; then \
       #  Make Logstash feed analytic results to Opensearch
       echo -e "- path.config: /usr/lib/perfsonar/logstash/pipeline/microdep/*.conf\n  pipeline.id: microdep" >> /etc/logstash/pipelines.yml; \
       # Add microdep index pattern to pscheduler user ... but this require opensearch to run...
       #sed -i "s|- 'pscheduler_\*'|- 'pscheduler_\*'\n      - 'dragonlab\*'|" opensearch/opensearch-security/roles.yml; \
       #sed -i "s|- 'pscheduler\*'|- 'pscheduler\*'\n      - 'dragonlab\*'|" opensearch/opensearch-security/roles.yml; \
       #/usr/share/opensearch/plugins/opensearch-security/tools/securityadmin.sh -f /etc/opensearch/opensearch-security/roles.yml -icl -nhnv -cert /etc/opensearch/admin.pem -cacert /etc/opensearch/root-ca.pem -key /etc/opensearch/admin-key.pem -t config
       # ... substitute in user+passwd instead
       USER=`awk -F " " '{print $1}' /etc/perfsonar/opensearch/opensearch_login` && sed -i "s|\${opensearch_admin_user}|$USER|g" /usr/lib/perfsonar/logstash/pipeline/microdep/03-microdep-outputs.conf; \
       PASSWD=`awk -F " " '{print $2}' /etc/perfsonar/opensearch/opensearch_login` && sed -i "s|\${opensearch_admin_password}|$PASSWD|g" /usr/lib/perfsonar/logstash/pipeline/microdep/03-microdep-outputs.conf; \
       mkdir -p /var/lib/logstash/microdep && chmod 777 /var/lib/logstash/microdep; \
    fi

# Add services which restart microdep services at 23:59 every evening to trigger output of daily summary reports.
COPY etc/microdep/perfsonar-microdep-restart.service /usr/lib/systemd/system/
COPY etc/microdep/perfsonar-microdep-restart.timer /usr/lib/systemd/system/
RUN systemctl enable perfsonar-microdep-restart.timer

# Add link to Microdep in web gui sidebar
COPY etc/httpd/sidebar.html.patch /root
RUN if [ "$TYPE" = "toolkit" ]; then \
      patch -u /usr/lib/perfsonar/web-ng/templates/components/sidebar.html -i /root/sidebar.html.patch; \
    fi

# http web (use 443 instead!)
EXPOSE 80  
# https web
EXPOSE 443
# Opensearch (use https://<hostname>:443/opensearch/ instead)
#EXPOSE 9200
# Opensearch Dashboard   
EXPOSE 5601
# Grafana   
EXPOSE 3000   

# Run systemd as in "parent"-image
CMD ["/lib/systemd/systemd"]
