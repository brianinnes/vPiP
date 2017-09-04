# This file contains local definitions for your environment
# It is in the .gitignore file, so changes will not be written back to git
#

# Raspberry Pi - this section defines the target Raspberry Pi
# If the RPI_HOST is not defined the install will not be attempted
# ssh auto login must be configured between the compile system and TARGET
# Raspberry Pi and the user and directory must exist
RSP_USER = pi
RSP_HOST = bi-rasp3b1.local
RSP_DIRECTORY = /home/pi

RSP1_USER = pi
RSP1_HOST = bi-raspZero4.local
RSP1_DIRECTORY = /home/pi

# ATMega and ATTiny - this section defines the target programmers for AVR
# If the ATx_AVRDUDE_PORT is not defined the install will not be attempted
# You may need to add additional devices to the Vagrantfile for your local
# environment to work.
ATT_AVRDUDE_PROGRAMMER = avrispmkII
ATT_AVRDUDE_PORT = usb
ATT_EXTRA_FLAGS =

ATM_AVRDUDE_PROGRAMMER = arduino
ATM_AVRDUDE_PORT = /dev/ttyUSBnano
ATM_EXTRA_FLAGS = -b 57600
