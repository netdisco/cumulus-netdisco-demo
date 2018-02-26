# A quick hack to allow rebooting of a Vagrant VM during provisioning.
# from https://github.com/exratione/vagrant-provision-reboot
# ----------------------------------------------------------------------------

require 'vagrant'

class RebootPlugin < Vagrant.plugin('2')
  name 'Reboot Waiter Plugin'

  provisioner 'reboot_waiter' do

    class RebootProvisioner < Vagrant.plugin('2', :provisioner)
      def initialize(machine, config)
        super(machine, config)
      end

      def configure(root_config)
        super(root_config)
      end

      def provision
        options = {}
        options[:provision_ignore_sentinel] = false
        @machine.action(:reload, options)
        begin
          sleep 10
        end until @machine.communicate.ready?
      end

      def cleanup
        super
      end
    end
    RebootProvisioner

  end
end
