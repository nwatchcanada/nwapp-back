# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "centos/8"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  # config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 8001, host: 8080

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"
  config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: [".git/", "env", ".env", "centos_env"]

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Automount the shared folder.
  #   vb.automount = true
  #
  #   # Customize the amount of memory on the VM:
  #   vb.memory = "1024"
  # end

  # View the documentation for the provider you are using for more
  # information on available options.

  # Enable provisioning with a shell script. Additional provisioners such as
  # Ansible, Chef, Docker, Puppet and Salt are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
    #########################################################################
    # INSTALLATION AND CONFIGURAITON OF THE NEIGBHOURHOOD WATCH APP PROJECT #
    #########################################################################
    #--------------------------------------------#
    # STEP 1: SYSTEM AND ASSOCIATED DEPENDENCIES #
    #--------------------------------------------#
    yum install -y epel-release
    yum -y update
    yum -y install wget;
    yum -y install nginx
    yum -y install gcc openssl-devel bzip2-devel libffi-devel
    setsebool httpd_can_network_connect on -P

    #------------------#
    # STEP 2: PYTHON 3 #
    #------------------#
    # Special thanks to https://tecadmin.net/install-python-3-7-on-centos/
    # PYTHON
    cd /usr/src
    wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz
    tar xzf Python-3.7.4.tgz
    cd Python-3.7.4
    sudo ./configure --enable-optimizations
    sudo make altinstall
    python3.7 -V
    rm /usr/src/Python-3.7.4.tgz

    # PIP
    yum -y install python3-pip
    curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
    python3 get-pip.py
    rm get-pip.py
    ln -s /usr/local/bin/pip3.6 /bin/pip3.6
    pip3.6 install --upgrade pip

    # VIRTUALENV
    pip3.6 install virtualenv
    ln -s /usr/local/bin/virtualenv /bin/virtualenv

    #---------------------#
    # STEP 3: POSTGRES 12 #
    #---------------------#
    # The following instructions were taken from [this article](https://linuxconfig.org/how-to-install-postgres-on-redhat-8) and [this article](https://computingforgeeks.com/how-to-install-postgresql-12-on-centos-7/).

    # INSTALL
    yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm
    dnf -qy module disable postgresql
    dnf -y install postgresql12 postgresql12-server  postgresql12-contrib postgresql12-devel

    # INSTALL POSTGIS
    # Special thanks via https://computingforgeeks.com/how-to-install-postgis-on-centos-8-linux/
    yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm
    dnf -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
    dnf config-manager --set-enabled PowerTools
    dnf -qy module disable postgresql
    yum -y install postgis30_12
    dnf -y install gdal30 gdal30-devel

    # Enable PostgreSQL server to listen on all available networks.
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /var/lib/pgsql/12/data/postgresql.conf

    # Enable MD5-encrypted password authentication.
    sed -i "s/ident/md5/" /var/lib/pgsql/12/data/pg_hba.conf

    # INITIALIZE
    /usr/pgsql-12/bin/postgresql-12-setup initdb
    systemctl enable --now postgresql-12
    systemctl status postgresql-12

    # SETUP DATABASE
    # (Look in the project configuration)
    #su postgres -c "psql -c \"CREATE ROLE vagrant SUPERUSER LOGIN PASSWORD 'vagrant'\" "
    sudo su postgres -c "psql -c \"drop database nwapp_db\" "
    sudo su postgres -c "psql -c \"create database nwapp_db\" "
    sudo su postgres nwapp_db -c "psql -c \"CREATE USER vagrant WITH PASSWORD '123password'\" "
    sudo su postgres nwapp_db -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE nwapp_db to vagrant;\" "
    sudo su postgres nwapp_db -c "psql -c \"ALTER USER vagrant CREATEDB;\" "
    sudo su postgres nwapp_db -c "psql -c \"ALTER ROLE vagrant SUPERUSER;\" "
    sudo su postgres nwapp_db -c "psql -c \"CREATE EXTENSION postgis;\" "

    #---------------#
    # STEP 4: REDIS #
    #---------------#
    yum -y install redis
    systemctl start redis
    systemctl enable redis

    #-----------------#
    # STEP 5: WEB-APP #
    #-----------------#
    yum -y install python3-devel postgresql-devel

    cd /vagrant
    virtualenv -p python3.6 centos_env
    source centos_env/bin/activate

    # bugfix
    export PATH=/usr/pgsql-12/bin/:$PATH
    pip install psycopg2
    export PATH=/usr/gdal30/bin/:$PATH
    pip install GDAL==3.0.4

    pip install -r requirements.txt

    cd scripts/
    ./setup_credentials.sh
    cd ../

    sed -i "s/from django.utils.six import text_type/from six import text_type/" /vagrant/centos_env/lib/python3.6/site-packages/rest_framework_msgpack/parsers.py

    python manage.py makemigrations;
    python manage.py migrate_schemas --executor=multiprocessing;
    python manage.py init_app;
    python manage.py setup_oauth2;
    python manage.py create_shared_user "bart@mikasoftware.com" "123password" "Bart" "Mika"; # Please change your password!
    python manage.py create_shared_organization london \
           "Neighbourhood Watch London" \
           "NWatch App" \
           "This is our main tenant organization" \
           "Canada" \
           "London" \
           "Ontario" \
           "200" \
           "Centre" \
           "23" \
           "1" \
           "" \
           "" \
           "N6J4X4" \
           "America/Toronto" \
           "https://www.coplogic.ca/dors/en/filing/selectincidenttype?dynparam=1584326750929" \
           "42.983611" \
           "-81.249722" \
           "13";

    echo "Vagrant environment has been setup, to access the developer environment please run the following command to login:"
    echo "vagrant ssh"
    echo ""
    echo "Afterwords startup the server"
    echo "cd /vagrant"
    echo "source centos_env/bin/activate"
    echo "cd nwapp"
    echo "python3 manage.py runserver 0.0.0.0:8001"
    echo ""
    echo "In your browser, access the site via: http://localhost:8080"
  SHELL
end
