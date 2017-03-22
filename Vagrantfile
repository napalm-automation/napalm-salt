# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
#
# Settings for veos VMs
def v_configs(num_images, oct, prefix)
  images = []
  for image_id in 1..num_images
    images << {
      :number => image_id,
      :name   => "%s%s" % [prefix, image_id],
      :ip     => "192.168.50.%d%d" % [oct, image_id],
    }
  end
  return images
end

veos_confs = v_configs(1, 1, 'veos')
vsrx_confs = v_configs(0, 2, 'vsrx')

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provider "virtualbox" do |vb|
      vb.memory = 2048
  end
  vsrx_confs.each do |vsrx_conf|
    config.vm.define vsrx_conf[:name] do |vsrx_config|
        vsrx_config.vm.box = "juniper/ffp-12.1X47-D20.7"
        vsrx_config.vm.host_name = "vsrx1"
        vsrx_config.vm.network "private_network", ip: vsrx_conf[:ip]
    end
  end
  veos_confs.each do |veos_conf|
    config.vm.define veos_conf[:name] do |eos_config|
      eos_config.vm.box = "vEOS-lab-4.16.9M"
      eos_config.vm.network "private_network", ip: veos_conf[:ip], auto_config: false
      eos_config.vm.provider "virtualbox" do |vb|
        vb.customize ["modifyvm", :id, "--memory", 2048]
      end
      eos_config.vm.provision 'shell' do |s|
        s.inline = <<-SHELL
          FastCli -p 15 -c "configure
          hostname $2
          interface Et1
          no switchport
          ip add ${1}/24
          ip route 0.0.0.0/0 10.0.2.2
          end
          copy running-config startup-config"
        SHELL
        s.args = [veos_conf[:ip], veos_conf[:name]]
      end
    end
  end
  config.vm.define :master do |master_config|
    master_config.vm.box = "ubuntu/trusty64"
    master_config.vm.host_name = 'saltmaster.local'
    master_config.vm.network "private_network", ip: "192.168.50.10"
	master_config.vm.synced_folder "saltstack", "/srv"
    master_config.vm.provision :salt do |salt|
      salt.master_config = "saltstack/etc/master"
      salt.minion_config = "saltstack/etc/master.minion"
      salt.master_key = "saltstack/keys/master_minion.pem"
      salt.master_pub = "saltstack/keys/master_minion.pub"
      salt.minion_key = "saltstack/keys/master_minion.pem"
      salt.minion_pub = "saltstack/keys/master_minion.pub"
      salt.seed_master = {
                            "master" => "saltstack/keys/master_minion.pub"
                         }
      salt.install_type = "git"
      salt.install_args = "develop"
      salt.install_master = true
      salt.no_minion = false
      salt.verbose = true
      salt.colorize = true
      salt.bootstrap_options = "-P -c /tmp"
      # Uncomment below line to use custom git repo for salt instead of saltstack
      #salt.bootstrap_options = "-P -c /tmp -g git@github.com:your-user/salt.git"
      salt.run_highstate = true
    end
  end
end
