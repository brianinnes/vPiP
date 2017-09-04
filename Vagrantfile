# -*- mode: ruby -*-
# vi: set ft=ruby :

#**********************************************************************
# Cross-compile environment for AVR and ARM mcus
#**********************************************************************

def usbfilter_exists(vendor_id, product_id)
  #
  # Determine if a usbfilter with the provided Vendor/Product ID combination
  # already exists on this VM.
  #
  # TODO: Use a more reliable way of retrieving this information.
  #
  # NOTE: The "machinereadable" output for usbfilters is more
  #       complicated to work with (due to variable names including
  #       the numeric filter index) so we don't use it here.
  #
  machine_id_filepath = File.join(".vagrant","machines","default","virtualbox","id")

  if not File.exists? machine_id_filepath
    # VM hasn't been created yet.
    return false
  end

  vm_info = `VBoxManage showvminfo $(<#{machine_id_filepath})`
  filter_match = "VendorId:         #{vendor_id}\nProductId:        #{product_id}\n"
  return vm_info.include? filter_match
end

def better_usbfilter_add(vb, vendor_id, product_id, filter_name)
  #
  # This is a workaround for the fact VirtualBox doesn't provide
  # a way for preventing duplicate USB filters from being added.
  #
  # TODO: Implement this in a way that it doesn't get run multiple
  #       times on each Vagrantfile parsing.
  #
  if not usbfilter_exists(vendor_id, product_id)
    vb.customize ["usbfilter", "add", "0",
                  "--target", :id,
                  "--name", filter_name,
                  "--vendorid", vendor_id,
                  "--productid", product_id
                  ]
  end
end
Vagrant.configure("2") do |config|
  config.vbguest.auto_update = true
  config.vm.network "public_network"
  config.vm.network "private_network", ip: "192.168.50.50"
  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
    v.cpus = 2
    v.customize [
        "storagectl", :id,
        "--name", "SATA Controller",
        "--hostiocache", "on"
    ]
    better_usbfilter_add(v, "1a86", "7523", "Arduino Nano")
    better_usbfilter_add(v, "03eb", "2104", "AAVRISP mkII")
    better_usbfilter_add(v, "0403", "6001", "FTDI TTL232R 3V3")
    better_usbfilter_add(v, "2a03", "0043", "Arduino UNO")
    better_usbfilter_add(v, "16c0", "05dc", "USBasp")
    v.customize ["modifyvm", :id, "--usb", "on"]
    v.customize ["modifyvm", :id, "--usbxhci", "on"]
  end
  config.vm.box = "debian/stretch64"
#--------
# If larger filesystem is needed use the image in the commented out line below
# rather than the debian/jessie64 image
#--------
#  config.vm.box = "wholebits/debian8-64" # Linux ebian-8-64 3.16.0-4-amd64 #1 SMP Debian 3.16.36-1+deb8u2 (2016-10-19) x86_64 GNU/Linux
  config.vm.synced_folder ".", "/vagrant", type: "virtualbox", nfs: true

  config.vm.provision "shell", inline: <<-SHELL
    export ARM6_CROSS_BASE=/opt/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian
    export ARM6_CROSS_BASEx64=${ARM6_CROSS_BASE}-x64
    export ARM6_CROSS_PREFIX=arm-linux-gnueabihf-
    echo "********** Updating and extending base **********"
    apt-get update
    apt-get upgrade -y
    apt-get install -y build-essential curl python-pip python-dev unzip git usbutils
    apt-get install -y libusb-1.0 libusb-dev libelf-dev libftdi-dev
    apt-get install -y avahi-daemon avahi-discover avahi-dnsconfd avahi-utils libnss-mdns
    apt-get install -y libssl-dev autoconf libtool sbuild
    sbuild-adduser $LOGNAME
    `newgrp sbuild`
    sbuild-update --keygen
    echo "********** Installing ARM 7 build tools **********"
# echo "deb http://emdebian.org/tools/debian/ jessie main" >> /etc/apt/sources.list.d/crosstools.list
# curl http://emdebian.org/tools/debian/emdebian-toolchain-archive.key | sudo apt-key add -
    dpkg --add-architecture armhf
    apt-get update
    apt-get install -y crossbuild-essential-armhf
    apt-get install -y libssl-dev:armhf
    echo "********** Installing ARM 6 build tools **********"
    dpkg --add-architecture i386
    apt-get update
    apt-get install -y libstdc++6:i386 libgcc1:i386 zlib1g:i386 libc6:i386
    git clone https://github.com/raspberrypi/tools.git /opt/arm-bcm2708hardfp-linux-gnueabi
    echo "********** Installing AVR build tools **********"
    apt-get install -y gcc-avr binutils-avr avr-libc gdb-avr avrdude
#
#   Create the udev rules to ensure devices have a know name for make rules
#   and ensure correct permissions are set to allow vagrant user to access the devices
#
    usermod -a -G dialout vagrant
    cat > /etc/udev/avrisp.rules <<- "EOF"
SUBSYSTEM!="usb", ACTION!="add", GOTO="avrisp_end"
# Atmel Corp. JTAG ICE mkII
ATTR{idVendor}=="03eb", ATTR{idProduct}=="2103", MODE="660", GROUP="dialout"
# Atmel Corp. AVRISP mkII
ATTR{idVendor}=="03eb", ATTR{idProduct}=="2104", MODE="660", GROUP="dialout"
# Atmel Corp. Dragon
ATTR{idVendor}=="03eb", ATTR{idProduct}=="2107", MODE="660", GROUP="dialout"
# USBasp
ATTR{idVendor}=="16c0", ATTR{idProduct}=="05dc", MODE="660", GROUP="dialout"


LABEL="avrisp_end"
EOF
    cat > /etc/udev/links.rules <<- "EOF"
SUBSYSTEM!="usb", ACTION!="add", GOTO="links_end"
# QinHeng Electronics CH340 nano
SUBSYSTEM=="tty", SUBSYSTEMS=="usb", DRIVERS=="usb", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="660", SYMLINK+="ttyUSBnano"
# FTDI 3v3 tty cable
SUBSYSTEM=="tty", SUBSYSTEMS=="usb", DRIVERS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="660", SYMLINK+="ttyUSBftdi"
# Arduino UNO
SUBSYSTEM=="tty", SUBSYSTEMS=="usb", DRIVERS=="usb", ATTRS{idVendor}=="2a03", ATTRS{idProduct}=="0043", MODE="660", SYMLINK+="ttyUSBuno"

LABEL="links_end"
EOF
    cd /etc/udev/rules.d
    ln ../avrisp.rules 10-avrisp.rules
    ln ../links.rules 10-links.rules
    systemctl restart udev
    udevadm control --reload-rules; udevadm trigger
    cd /tmp
    echo "********** Installing Paho MQTT C library **********"
    git clone https://github.com/openssl/openssl.git
    git clone https://github.com/eclipse/paho.mqtt.c.git
    git clone  https://github.com/eclipse/paho.mqtt.cpp.git
    cd openssl
    git checkout tags/OpenSSL_1_0_2k
    export cross=${ARM6_CROSS_BASEx64}/bin/${ARM6_CROSS_PREFIX}
    ./Configure linux-armv4 --prefix=${ARM6_CROSS_BASE}/arm-linux-gnueabihf shared
    make CC="${cross}gcc" AR="${cross}ar r" RANLIB="${cross}ranlib"
    make CC="${cross}gcc" AR="${cross}ar r" RANLIB="${cross}ranlib" install_sw
    echo "********** Installing Paho MQTT C library **********"
    cd ../paho.mqtt.c
#    make
#    make install
    install -m 644   src/MQTTAsync.h /usr/local/include
    install -m 644   src/MQTTClient.h /usr/local/include
    install -m 644   src/MQTTClientPersistence.h /usr/local/include
    CC_ORG=$CC
    export CC=/usr/bin/arm-linux-gnueabihf-gcc
    make clean
    make
    [[ -d /usr/local/lib/arm-linux-gnueabihf-gcc ]] || mkdir -p /usr/local/lib/arm-linux-gnueabihf-gcc
    install -m 644  build/output/libpaho-mqtt3c.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc
    install -m 644  build/output/libpaho-mqtt3cs.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc
    install -m 644  build/output/libpaho-mqtt3a.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc
    install -m 644  build/output/libpaho-mqtt3as.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc
    install  build/output/MQTTVersion /usr/local/bin/arm-linux-gnueabihf-gcc
    ln -s libpaho-mqtt3c.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3c.so
    ln -s libpaho-mqtt3cs.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3cs.so
    ln -s libpaho-mqtt3a.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3a.so
    ln -s libpaho-mqtt3as.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3as.so
    ln -s libpaho-mqtt3c.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3c.so.1
    ln -s libpaho-mqtt3cs.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3cs.so.1
    ln -s libpaho-mqtt3a.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3a.so.1
    ln -s libpaho-mqtt3as.so.1.0 /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3as.so.1
    export CC=${ARM6_CROSS_BASEx64}/bin/${ARM6_CROSS_PREFIX}gcc
    make clean
    cross_arm6=${ARM6_CROSS_BASE}/arm-linux-gnueabihf
    make prefix=${cross_arm6} CFLAGS+=-I${cross_arm6}/include LDFLAGS+=-L${cross_arm6}/lib/
    mkdir /usr/local/lib/arm6-linux-gnueabihf-gcc
    install -m 644  build/output/libpaho-mqtt3c.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc
    install -m 644  build/output/libpaho-mqtt3cs.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc
    install -m 644  build/output/libpaho-mqtt3a.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc
    install -m 644  build/output/libpaho-mqtt3as.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc
    install  build/output/MQTTVersion /usr/local/bin/arm6-linux-gnueabihf-gcc
    ln -s libpaho-mqtt3c.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3c.so
    ln -s libpaho-mqtt3cs.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3cs.so
    ln -s libpaho-mqtt3a.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3a.so
    ln -s libpaho-mqtt3as.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3as.so
    ln -s libpaho-mqtt3c.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3c.so.1
    ln -s libpaho-mqtt3cs.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3cs.so.1
    ln -s libpaho-mqtt3a.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3a.so.1
    ln -s libpaho-mqtt3as.so.1.0 /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3as.so.1
    export CC=$CC_ORG
    echo "******************************************************"
    echo "********** Installing Paho MQTT C++ library **********"
    echo "******************************************************"
    echo "********** ARM7 **********"
    cd ../paho.mqtt.cpp
    if [ -d lib_arm ]; then
      rm -rf lib_arm
    fi
    if [ -d lab_arm6 ]; then
      rm -rf lib_arm6
    fi
    mkdir lib_arm
    mkdir lib_arm6
#    make
#    mv lib lib_x86_64
#    make clean
    CC_ORG=$CC
    CXX_ORG=$CXX
    LD_LIBRARY_PATH_ORG=$LD_LIBRARY_PATH
    export CC=/usr/bin/arm-linux-gnueabihf-gcc
    export CXX=/usr/bin/arm-linux-gnueabihf-g++
    make DEVELOP=DEVELOP SSL=SSL INC_DIR="/usr/local/include src" LIB_DIR=lib_arm dump
    make DEVELOP=DEVELOP SSL=SSL INC_DIR="/usr/local/include src" LIB_DIR=lib_arm
    install -m 644  lib_arm/libpaho-mqttpp3.so.0.5.0 /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqttpp3.so.0.5.0
    ln -s libpaho-mqttpp3.so.0.5.0 /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqttpp3.so.0
    ln -s libpaho-mqttpp3.so.0.5.0 /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqttpp3.so
    export CC=${ARM6_CROSS_BASEx64}/bin/${ARM6_CROSS_PREFIX}gcc
    export CXX=${ARM6_CROSS_BASEx64}/bin/${ARM6_CROSS_PREFIX}g++
    export LD_LIBRARY_PATH=${ARM6_CROSS_BASE}/arm-linux-gnueabihf/lib
    ./bootstrap
    ./configure --host=arm-linux-gnueabihf --with-ssl CXXFLAGS="-I/usr/local/include -I${ARM6_CROSS_BASE}/arm-linux-gnueabihf/include" LDFLAGS="-L${ARM6_CROSS_BASE}/arm-linux-gnueabihf/lib -L/usr/local/lib/arm6-linux-gnueabihf-gcc" CFLAGS="-I/usr/local/include -I${ARM6_CROSS_BASE}/arm-linux-gnueabihf/include" CPPFLAGS="-I/usr/local/include -I${ARM6_CROSS_BASE}/arm-linux-gnueabihf/include" --libdir=${PWD}/lib_arm6
    make install
    export CC=$CC
    export CXX=$CXX
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH_ORG
    install -m 644  lib_arm6/libpaho-mqttpp3.so.0.5.0 /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqttpp3.so.0.5.0
    ln -s libpaho-mqttpp3.so.0.5.0 /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqttpp3.so.0
    ln -s libpaho-mqttpp3.so.0.5.0 /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqttpp3.so
    export CC=$CC_ORG
    echo "********** Building project **********"
    cd /vagrant/boardDriver
    git clone https://github.com/nlohmann/json.git
    cd ..
    make all
  SHELL
end
