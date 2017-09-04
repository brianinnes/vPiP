export MAKEFLAGS += --no-builtin-rules

export REMOVE = rm -f
export COPY = cp
export SHELL = sh
export MKDIR = mkdir -p

#AVR Tools
export AVR_CC = avr-gcc
export AVR_CXX = avr-g++
export AVR_AR = avr-ar
export AVR_OBJCOPY = avr-objcopy
export AVR_OBJDUMP = avr-objdump
export AVR_SIZE = avr-size
export AVR_STRIP = avr-strip
export ARV_NM = avr-nm
# Programming support using avrdude.
export AVRDUDE = avrdude


#ARM6 Tools
#export ARM6_CROSS_BASE=/opt/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708/arm-rpi-4.9.3-linux-gnueabihf
export ARM6_CROSS_BASE=/opt/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian
export ARM6_CROSS_BASEx64=/opt/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64
export ARM6_CROSS_PREFIX=arm-linux-gnueabihf-
export AR6_CC = ${ARM6_CROSS_BASE}/bin/${ARM6_CROSS_PREFIX}gcc
export AR6_CXX = ${ARM6_CROSS_BASE}/bin/${ARM6_CROSS_PREFIX}g++
export AR6_AR = ${ARM6_CROSS_BASE}/bin/${ARM6_CROSS_PREFIX}ar
export AR6_OBJCOPY = ${ARM6_CROSS_BASE}/bin/${ARM6_CROSS_PREFIX}objcopy
export AR6_OBJDUMP = ${ARM6_CROSS_BASE}/bin/${ARM6_CROSS_PREFIX}objdump
export AR6_SIZE = ${ARM6_CROSS_BASE}/bin/${ARM6_CROSS_PREFIX}size
export AR6_STRIP = ${ARM6_CROSS_BASE}/bin/${ARM6_CROSS_PREFIX}strip
export AR6_NM = ${ARM6_CROSS_BASE}/bin/${ARM6_CROSS_PREFIX}nm

#ARM7 Tools
export ARM_CC = /usr/bin/arm-linux-gnueabihf-gcc
export ARM_CXX = /usr/bin/arm-linux-gnueabihf-g++
export ARM_AR = /usr/bin/arm-linux-gnueabihf-ar
export ARM_OBJCOPY = /usr/bin/arm-linux-gnueabihf-objcopy
export ARM_OBJDUMP = /usr/bin/arm-linux-gnueabihf-objdump
export ARM_SIZE = /usr/bin/arm-linux-gnueabihf-size
export ARM_STRIP = /usr/bin/arm-linux-gnueabihf-strip
export ARM_NM = /usr/bin/arm-linux-gnueabihf-nm

# List any extra directories to look for include files here.
#     Each directory must be seperated by a space.
# EXTRAINCDIRS = $(CURDIR) $(CURDIR)/nrf24l01 /usr/lib/avr/include

#AVRDUDE_WRITE_FLASH = -U flash:w:$(TARGET).hex
#AVRDUDE_WRITE_EEPROM = -U eeprom:w:$(TARGET).eep

#export AVRDUDE_FLAGS = -p $(MCU) -P $(AVRDUDE_PORT) -c $(AVRDUDE_PROGRAMMER)

#HEXSIZE = $(SIZE) --target=$(FORMAT) $(TARGET).hex
#ELFSIZE = $(SIZE) -AC --mcu=$(MCU) $(TARGET).elf

# Define Messages
# English
export MSG_ERRORS_NONE = Errors- none
export MSG_BEGIN = -------- begin --------
export MSG_END = --------  end  --------
export MSG_SIZE_BEFORE = Size before-
export MSG_SIZE_AFTER = Size after-
export MSG_COFF = Converting to AVR COFF-
export MSG_EXTENDED_COFF = Converting to AVR Extended COFF-
export MSG_FLASH = Creating load file for Flash-
export MSG_EEPROM = Creating load file for EEPROM-
export MSG_EXTENDED_LISTING = Creating Extended Listing-
export MSG_SYMBOL_TABLE = Creating Symbol Table-
export MSG_LINKING = Linking-
export MSG_COMPILING = Compiling-
export MSG_ASSEMBLING = Assembling-
export MSG_CLEANING = Cleaning project-
export MSG_INSTALLING = Installing binaries
