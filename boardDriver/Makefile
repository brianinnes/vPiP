CXXSRC = boardDriver.cpp async_client.cpp client.cpp iclient_persistence.cpp message.cpp token.cpp topic.cpp vpipController.cpp
ARM_OBJS    = $(CXXSRC:%.cpp=rspRelease/%.o)
AR6_OBJS    = $(CXXSRC:%.cpp=rsp1Release/%.o)
RSP_TARGET = rspRelease/boardDriver
RSP1_TARGET = rsp1Release/boardDriver

include ../rules.mk
include ../local.mk

RSP_EXTRAINCDIRS = . /usr/local/include ../paho.mqtt.cpp/src
RSP_LDFLAGS += -L/usr/local/lib/arm-linux-gnueabihf-gcc -L../paho.mqtt.cpp/lib_arm -lpaho-mqtt3as -lssl -lcrypto -lstdc++ -lpaho-mqttpp3
RSP1_EXTRAINCDIRS = . /usr/local/include ../paho.mqtt.cpp/src
RSP1_LDFLAGS += -L/usr/local/lib/arm6-linux-gnueabihf-gcc -L${ARM6_CROSS_BASE}/arm-linux-gnueabihf/lib -lpaho-mqttpp3 -lpaho-mqtt3as -lssl -lcrypto -lstdc++ -lrt

all: directories $(RSP_TARGET) $(RSP_TARGET).lss $(RSP_TARGET).sym $(RSP1_TARGET) $(RSP1_TARGET).lss $(RSP1_TARGET).sym

directories:
	$(MKDIR) rspRelease
	$(MKDIR) rsp1Release

install:
ifdef RSP_HOST
	- scp $(RSP_TARGET) $(RSP_USER)@$(RSP_HOST):$(RSP_DIRECTORY)/$(notdir $(RSP_TARGET))
	- scp /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqttpp3.so $(RSP_USER)@$(RSP_HOST):$(RSP_DIRECTORY)
	- scp /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3a.so $(RSP_USER)@$(RSP_HOST):$(RSP_DIRECTORY)
	- scp /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3as.so $(RSP_USER)@$(RSP_HOST):$(RSP_DIRECTORY)
	- scp /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3c.so $(RSP_USER)@$(RSP_HOST):$(RSP_DIRECTORY)
	- scp /usr/local/lib/arm-linux-gnueabihf-gcc/libpaho-mqtt3cs.so $(RSP_USER)@$(RSP_HOST):$(RSP_DIRECTORY)
	- ssh $(RSP_USER)@$(RSP_HOST) sudo mv libpaho-mqttpp3.so /usr/local/lib
	- ssh $(RSP_USER)@$(RSP_HOST) sudo mv libpaho-mqtt3a.so /usr/local/lib
	- ssh $(RSP_USER)@$(RSP_HOST) sudo mv libpaho-mqtt3as.so /usr/local/lib
	- ssh $(RSP_USER)@$(RSP_HOST) sudo mv libpaho-mqtt3c.so /usr/local/lib
	- ssh $(RSP_USER)@$(RSP_HOST) sudo mv libpaho-mqtt3cs.so /usr/local/lib
	- ssh $(RSP_USER)@$(RSP_HOST) sudo chown root:staff /usr/local/lib/libpaho-mqttpp3.so
	- ssh $(RSP_USER)@$(RSP_HOST) sudo chown root:staff /usr/local/lib/libpaho-mqtt3a.so
	- ssh $(RSP_USER)@$(RSP_HOST) sudo chown root:staff /usr/local/lib/libpaho-mqtt3as.so
	- ssh $(RSP_USER)@$(RSP_HOST) sudo chown root:staff /usr/local/lib/libpaho-mqtt3c.so
	- ssh $(RSP_USER)@$(RSP_HOST) sudo chown root:staff /usr/local/lib/libpaho-mqtt3cs.so
	- ssh $(RSP_USER)@$(RSP_HOST) sudo ldconfig
endif
ifdef RSP1_HOST
	- scp $(RSP1_TARGET) $(RSP1_USER)@$(RSP1_HOST):$(RSP1_DIRECTORY)/$(notdir $(RSP1_TARGET))
	- scp /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqttpp3.so $(RSP1_USER)@$(RSP1_HOST):$(RSP1_DIRECTORY)
#	- scp ${ARM6_CROSS_BASE}/arm-linux-gnueabihf/lib/libssl.so $(RSP1_USER)@$(RSP1_HOST):$(RSP1_DIRECTORY)
#	- scp ${ARM6_CROSS_BASE}/arm-linux-gnueabihf/lib/libcrypto.so $(RSP1_USER)@$(RSP1_HOST):$(RSP1_DIRECTORY)
	- scp /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3a.so $(RSP1_USER)@$(RSP1_HOST):$(RSP1_DIRECTORY)
	- scp /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3as.so $(RSP1_USER)@$(RSP1_HOST):$(RSP1_DIRECTORY)
	- scp /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3c.so $(RSP1_USER)@$(RSP1_HOST):$(RSP1_DIRECTORY)
	- scp /usr/local/lib/arm6-linux-gnueabihf-gcc/libpaho-mqtt3cs.so $(RSP1_USER)@$(RSP1_HOST):$(RSP1_DIRECTORY)
#	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo mv libssl.so /usr/local/lib
#	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo mv libcrypto.so /usr/local/lib
	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo mv libpaho-mqttpp3.so /usr/local/lib
	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo mv libpaho-mqtt3a.so /usr/local/lib
	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo mv libpaho-mqtt3as.so /usr/local/lib
	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo mv libpaho-mqtt3c.so /usr/local/lib
	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo mv libpaho-mqtt3cs.so /usr/local/lib
#	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo chown root:staff /usr/local/lib/libssl.so
#	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo chown root:staff /usr/local/lib/libcrypto.so
	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo chown root:staff /usr/local/lib/libpaho-mqttpp3.so
	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo chown root:staff /usr/local/lib/libpaho-mqtt3a.so
	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo chown root:staff /usr/local/lib/libpaho-mqtt3as.so
	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo chown root:staff /usr/local/lib/libpaho-mqtt3c.so
	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo chown root:staff /usr/local/lib/libpaho-mqtt3cs.so
	- ssh $(RSP1_USER)@$(RSP1_HOST) sudo ldconfig

endif

# Target: clean project.
clean:
	@echo
	@echo $(MSG_CLEANING)
	$(REMOVE) -r rspRelease
	$(REMOVE) -r rsp1Release

.PHONY : directories clean install
