# -*- mode: ruby -*-
# vi: set ft=ruby :

require './lib/reboot-waiter-plugin'

cldemo_vagrantfile = File.expand_path('../cldemo-vagrant/Vagrantfile', __FILE__)
eval File.read(cldemo_vagrantfile) if File.exists?(cldemo_vagrantfile)

Vagrant.configure("2") do |config|

  config.vm.define "oob-mgmt-server", primary: true do |device|
    device.vm.provision :reboot_waiter
    device.vm.synced_folder ".", "/vagrant"

    device.vm.provision :shell , inline: "cp /vagrant/provisioning/ansible.cfg /etc/ansible/"

    device.vm.provision :ansible_local do |ansible|
      ansible.compatibility_mode = "2.0"
      ansible.provisioning_path = "/vagrant/cldemo-config-mlag"
      ansible.playbook = "deploy.yml"
      ansible.inventory_path = "ansible-inventory"
      ansible.limit   = "all"
      #ansible.verbose = true
    end

    device.vm.provision :ansible_local do |ansible|
      ansible.compatibility_mode = "2.0"
      ansible.playbook = "provisioning/playbook.yml"
      ansible.inventory_path = "provisioning/ansible-inventory"
      ansible.limit   = "all"
      #ansible.verbose = true
    end

    device.vm.provision :docker do |docker|
      docker.run "netdisco-backend",
        args:  "-e NETDISCO_DB_NAME=cumulus -e NETDISCO_DB_USER=oliver -e NETDISCO_DB_HOST=10.0.2.2",
        image: "netdisco/netdisco:latest-backend"
    end
  end

  config.vm.define "internet", autostart: false
  config.vm.define "exit01",   autostart: false
  config.vm.define "exit02",   autostart: false
  config.vm.define "edge01",   autostart: false

  # do not start this automatically, so that the network can boot first
  # otherwise the server will not be able to reach the devices.
  config.vm.define "oob-mgmt-server", autostart: false

end
