# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.synced_folder "../panoptes_snmp", "/panoptes_snmp"

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get upgrade -y
    # adding python 3.9 as alternative + snmp for testing
    apt install software-properties-common snmp snmp-mibs-downloader -y
    add-apt-repository ppa:deadsnakes/ppa -y
    apt install -y python3.9 python3.9-distutils python3.9-dev python3.9-venv
    # weighting this as priority 100
    update-alternatives --install /usr/bin/python python /usr/bin/python3.9 100
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 100
    update-alternatives --auto python
    update-alternatives --auto python3

    # snmp daemon for testing
    cp /panoptes_snmp/test_snmpd.conf /etc/snmp/snmpd.conf

    # Back to the normal build
    apt install -y python-is-python3 python3-pip tox
    virtualenv /panoptes_snmp/vagrant_venv --clear
    sudo chmod +x /panoptes_snmp/vagrant_venv/bin/activate
    source /panoptes_snmp/vagrant_venv/bin/activate
    pip install -r /panoptes_snmp/test-requirements.txt

    # Should be able to run the build and tests with;
    # vagrant up
    # vagrant ssh
    # ./panoptes_snmp/tox
  SHELL
end
