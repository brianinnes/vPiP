# vPiP - Broker

This directory contains a vagrant file which runs a Mosquitto broker in a virtual machine.  

The setup creates a certificate authority certificate and the server certificate
to enable secure connections on port 8883 using TLS.

Authentication is enabled with the default credentials:  
- username: mosquitto  
- password: passw0rd  

MQTT client will be able to access the broker using port 8883 on the IP Address of the system running the virtual machine.  

## Using the vagrant file  
To use the vagrant file you need:  
- An up to date installation of [VirtualBox](https://www.virtualbox.org)  
- An up to date installation of [Vagrant](https://www.vagrantup.com)  

On a command line in this directoy you can use the followiug commands:  
- **vagrant up** - Starts the virtual machine (creates it is necessary)
- **vagrant ssh** - ssh into the running virtual machine  
- **vagrant destroy** - stops and deletes the virtual machine  
- **vagrant suspend** - suspends the running virtual machine  
- **vagrant resume** - resume a suspended virtual machine  
- **vagrant halt** - stops a running virtual machine  
