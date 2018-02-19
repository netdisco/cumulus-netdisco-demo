# IMPORTANT NOTE

This is a work in progress, and probably broken if this note is still in the README.

# Introduction

This repository  is a demo for using Netdisco in a
[Cumulus](https://cumulusnetworks.com/products/cumulus-vx/) VX
[Network](https://github.com/CumulusNetworks/cldemo-vagrant).

# Network Build

Start up the MLAG [reference
topology](https://github.com/CumulusNetworks/cldemo-config-mlag) for Cumulus
VX, which includes an OOB management server and switch,
two spine routers, four leaf routers (in MLAG pairs),
and four servers dual-connected to upstream leaf switches.

You may need to install dependencies on your workstation such as virtualbox
and Vagrant - the respective websites have click-install packages.

# Deploy Netdisco from Docker

Amend the oob-mgmt-server node to run the Netdisco backend docker container,
connecting to a database on your worktation.

See the sample Vagrantfile in this repository, which can be copied to
`~/.vagrant.d/` before destroying and
restarting the oob-mgmt-server.

    # on your workstation
    mkdir ~/.vagrant.d
    cp cumulus-netdisco-demo/vagrant.d/Vagrantfile !$
    vagrant destroy oob-mgmt-server
    vagrant up oob-mgmt-server --provision

You will probably need to edit the Vagrantfile to change the settings for your
database, at least. See the
[documentation](https://github.com/netdisco/netdisco/wiki/Environment-Variables)
page for available options. Leave the DB Host set to
10.0.2.2 as this is usually what Vagrant assigns to your workstation's NAT.

# Update SNMP and LLDP config

SSH to the oob-mgmt-server node then enable SNMP and amend LLDP config on
all devices:

    vagrant ssh oob-mgmt-server
    git clone https://github.com/netdisco/cumulus-netdisco-demo.git
    cd cumulus-netdisco-demo
    ansible-playbook deploy.yml

# Access Netdisco Backend

Should you wish to visit the backend docker container:

    vagrant ssh oob-mgmt-server
    docker exec -it netdisco-backend sh

The Netdisco configuration is in `./environments` as usual.

# Caveats

You will need to run the web frontend on your workstation. Obviously, this does
not share configuration with the backend docker container running on oob-mgm-server.

So far, SNMP::Info is not doing a good job with the Cumulus platform. This
will not be hard to fix.
