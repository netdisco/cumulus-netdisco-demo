# -*- mode: ruby -*-
# vi: set ft=ruby :

require './vagrant-provision-reboot-waiter-plugin'

cldemo_vagrantfile = File.expand_path('../cldemo-vagrant/Vagrantfile', __FILE__)
eval File.read(cldemo_vagrantfile) if File.exists?(cldemo_vagrantfile)

Vagrant.configure("2") do |config|

  config.vm.define "oob-mgmt-server" do |device|
    device.vm.provision :reboot_waiter
    device.vm.synced_folder ".", "/vagrant"

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
      ansible.groups = {
        "leaves" => ["leaf01","leaf02","leaf03","leaf04"],
        "spines" => ["spine01","spine02"],
        "network:children" => ["leaves","spines"]
      }
      ansible.limit   = "network"
      #ansible.verbose = true
    end

    device.vm.provision :docker do |docker|
      docker.run "netdisco-backend",
        args:  "-e NETDISCO_DB_NAME=cumulus -e NETDISCO_DB_USER=oliver -e NETDISCO_DB_HOST=10.0.2.2",
        image: "netdisco/netdisco:latest-backend"
    end

  end

end
