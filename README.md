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

# Update SNMP and LLDP config

SSH to the oob-mgmt-server node then enable SNMP and amend LLDP config on
all devices:

    vagrant ssh oob-mgmt-server
    git clone ttps://github.com/netdisco/cumulus-netdisco-demo.git
    cd cumulus-netdisco-demo
    ansible-playbook deploy.yml

# Deploy Netdisco from Docker

Finally amend the oob-mgmt-server node to run the Netdisco backend docker container,
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

# Caveats

You will need to run the web frontend on your workstation.

So far, SNMP::Info is not doing a good job with the Cumulus platform. This
will not be hard to fix.
