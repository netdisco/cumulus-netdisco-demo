#!/bin/bash

sudo apt-get -y install libdbd-pg-perl libsnmp-perl libssl-dev libio-socket-ssl-perl curl

curl -L https://cpanmin.us/ | perl - --notest --local-lib ~/perl5 App::Netdisco

mkdir ~/bin
ln -s ~/perl5/bin/{localenv,netdisco-*} ~/bin/

mkdir ~/environments
cp ~/perl5/lib/perl5/auto/share/dist/App-Netdisco/environments/deployment.yml ~/environments
chmod 600 ~/environments/deployment.yml

curl -sL https://api.github.com/repos/netdisco/netdisco-mibs/releases/latest | \
  grep browser_download_url | xargs printf "curl -sL %s\n" | tail -1 | \
  sh | tar -zx
mv netdisco-mibs-* netdisco-mibs

(crontab -l 2>/dev/null; echo "@reboot NETDISCO_DB_HOST=10.0.2.2 ~/bin/netdisco-backend start") | crontab -
