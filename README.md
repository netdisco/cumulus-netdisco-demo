# Introduction

This repository  is a demo for using Netdisco in a
[Cumulus](https://cumulusnetworks.com/products/cumulus-vx/) VX
[Network](https://github.com/CumulusNetworks/cldemo-vagrant).

# Network Build

You can start up a [reference
topology](https://github.com/CumulusNetworks/cldemo-config-mlag) for Cumulus
VX which includes two spine switches, four leaf switches (two pairs running
MLAG), and four servers dual-connected to the leaf switches.

# Update SNMP and LLDP config

Then ssh to the oob-mgmt-server node and clone this repo and run the Ansible
configuration to update all switches to enable SNMP and amend LLDP config.

# Deploy Netdisco from Docker

Finally you can reboot the oob-mgmt-server node to run Netdisco backend
connected to a database server on your worktation. See the sample Vagrantfile
included, which can be copied to `~/.vagrant.d/` before destorying and
restarting the oob-mgmt-server.

You will need to edit the Vagrantfile to change the settings for your
database, and possible add others. See the
[documentation](https://github.com/netdisco/netdisco/wiki/Environment-Variables)
page for available options.

# Caveats

You will need to run the web frontend on your workstation.

So far, SNMP::Info is not doing a good job with the Cumulus platform. This
should not be hard to fix.
