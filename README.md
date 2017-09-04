# vPiP
Driving a drawing machine from python

A python library targeted to run on a Raspberry Pi with accompanying Arduino code.  This code is intended to run on the driver board created by makeBournemouth

Links:  

- makeBournemouth [https://www.makebournemouth.com]()
- Controller board : [https://github.com/MarkJB/Eggbot-Spherebot-PyPlotter-Controller]()

Inspired by the Polargraph project [http://www.polargraph.co.uk]() and gocupi project [https://github.com/brandonagr/gocupi]()

To run this library you need Python installed with the Python Imaging Library fork, Pillow.  Installation instructions are here : [https://pillow.readthedocs.org/en/latest/installation.html]()  

sudo apt-get install libtiff5-dev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev
pip install Pillow  


The C++ code for the Raspberry pi is build using Vagrant [https://www.vagrantup.com]() , which runs on most commonly used operating systems.

The make install command will automatically install the binary code on a Raspberry Pi, but relies on ssh auto login using a certificate.   
To setup auto login open a terminal and login to the vagrant build machine   
`vagrant up`   
`vagrant ssh`

Generate a certificate:   
`ssh-keygen -t rsa`   
accept all the default, DO NOT enter a password - leave blank   

Copy the certificate to the target Raspberry Pi using the following commands, replacing the host name (*raspberrypi.local*) with the host name or IP address of your pi:   
`ssh pi@raspberrypi.local mkdir -p .ssh`   
`cat ~/.ssh/id_rsa.pub | ssh pi@raspberrypi.local 'cat >> .ssh/authorized_keys'`


#Installing MQTT on a Raspberry Pi

You need an MQTT broker running and configured to run this software.  The MQTT broker can run on the Raspberry Pi.  To install run the following commands - this assumes running the latest Raspbian Stretch :  
- wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key  
- sudo apt-key add mosquitto-repo.gpg.key  
- cd /etc/apt/sources.list.d/  
- sudo wget http://repo.mosquitto.org/debian/mosquitto-stretch.list
- sudo apt-get update
- sudo apt-get install -y mosquitto mosquitto-clients
