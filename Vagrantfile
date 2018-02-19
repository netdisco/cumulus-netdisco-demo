# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.provision :shell, privileged: false, :inline => <<-cldemo_bootstrap
git clone https://github.com/cumulusnetworks/cldemo-vagrant
cldemo_bootstrap
#cd cldemo-vagrant
#vagrant up oob-mgmt-server oob-mgmt-switch leaf01 leaf02 leaf03 leaf04 spine01 spine02 server01 server02 server03 server04

  cldemo_vagrantfile = File.expand_path('../cldemo-vagrant/Vagrantfile', __FILE__)
  eval File.read(cldemo_vagrantfile) if File.exists?(cldemo_vagrantfile)

  config.vm.define "oob-mgmt-server" do |device|

    device.vm.provision :shell,
      name: "git clone cldemo-config-mlag",
      privileged: false,
      inline: "cd /tmp && git clone https://github.com/cumulusnetworks/cldemo-config-mlag"
    end

    device.vm.provision :ansible_local do |ansible|
      ansible.provisioning_path = "/tmp/cldemo-config-mlag"
      ansible.playbook = "deploy.yml"
      ansible.inventory_path = "ansible-inventory"
      ansible.limit   = "all"
      ansible.verbose = true
    end

    device.vm.provision :ansible_local do |ansible|
      ansible.playbook = "provisioning/playbook.yml"
      ansible.groups = {
        "leaves" => ["leaf01","leaf02","leaf03","leaf04"],
        "spines" => ["spine01","spine02"],
        "network:children" => ["leaves","spines"]
      }
      ansible.limit   = "network"
      ansible.verbose = true
    end

    device.vm.provision :docker do |docker|
      docker.run "netdisco-backend",
        args:  "-e NETDISCO_DB_NAME=cumulus -e NETDISCO_DB_USER=oliver -e NETDISCO_DB_HOST=10.0.2.2",
        image: "netdisco/netdisco:latest-backend"
    end

  end

end
