RSP1_EXTRAINCDIRS = .
RSP1_CFLAGS = -std=c11 -O3 -Wall -c -fmessage-length=0 \
              -I/opt/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708/arm-rpi-4.9.3-linux-gnueabihf/arm-linux-gnueabihf/sysroot/usr/include \
	            -mabi=aapcs-linux -marm -mfloat-abi=hard -DRPI \
	            $(patsubst %,-I%,$(RSP1_EXTRAINCDIRS))
RSP1_CXXFLAGS = -std=c++0x -O3 -Wall -c -fmessage-length=0 \
 	-mabi=aapcs-linux -marm -mfloat-abi=hard -DRPI \
	-I/opt/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708/arm-rpi-4.9.3-linux-gnueabihf/arm-linux-gnueabihf/include/c++/4.9.3 $(patsubst %,-I%,$(RSP1_EXTRAINCDIRS))
RSP1_ASFLAGS =
RSP1_LDFLAGS = -L /opt/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708/arm-rpi-4.9.3-linux-gnueabihf/lib 

RSP_EXTRAINCDIRS = .
RSP_CFLAGS = -std=c11 -O3 -Wall -c -fmessage-length=0 -I/usr/include/arm-linux-gnueabihf \
	-mabi=aapcs-linux -marm -mfloat-abi=hard -DRPI \
	-I$(RSP_EXTRAINCDIRS)
RSP_CXXFLAGS = -std=c++0x -O3 -Wall -c -fmessage-length=0 \
 	-mabi=aapcs-linux -marm -mfloat-abi=hard -DRPI \
	-I/usr/include/arm-linux-gnueabihf $(patsubst %,-I%,$(RSP_EXTRAINCDIRS))
# RSP_CXXFLAGS = -std=c++0x -O0 -fbuiltin -g -Wall -c -fmessage-length=0 -MMD -MP -I/usr/include/arm-linux-gnueabihf -mcpu=arm1176jzf-s -I$(RSP_EXTRAINCDIRS)
RSP_ASFLAGS =
RSP_LDFLAGS =

ATT_CLOCK = 8000000L
ATT_CFLAGS = -g -Os -w -std=gnu11 \
-funsigned-char -funsigned-bitfields -fpack-struct -fshort-enums \
-ffunction-sections -fdata-sections -MMD -flto \
-DF_CPU=$(ATT_CLOCK) -Wa,-adhlns=$(<:.c=.lst) \
-mmcu=attiny85 -Wl,--gc-sections \
$(patsubst %,-I%,$(ATT_EXTRAINCDIRS))
ATT_CXXFLAGS = -g -Os -w -std=gnu++11 \
-fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics \
-MMD -Wl,--gc-sections \
-DF_CPU=$(ATT_CLOCK) -mmcu=attiny85 \
$(patsubst %,-I%,$(ATT_EXTRAINCDIRS))
ATT_ASFLAGS = -mmcu=attiny85  -x assembler-with-cpp -flto -fuse-linker-plugin \
		$(patsubst %,-I%,$(EXTRAINCDIRS))
ATT_LINKFLAGS = -w -Os \
-mmcu=attiny85 -Xlinker --defsym=__heap_end=0x00
ATT_LDFLAGS = -ffunction-sections -Wl,--gc-sections,-Map=$(TARGET).map,--cref
ATT_HEXSIZE = $(AVR_SIZE) --target=ihex $(TARGET).hex
ATT_ELFSIZE = $(AVR_SIZE) -AC --mcu=attiny85 $(TARGET).elf
ATT_FORMAT = ihex
ATT_AVRDUDE_WRITE_FLASH = -pt85 -U flash:w:$(TARGET).hex:i
ATT_AVRDUDE_WRITE_EEPROM = -pt85 -U eeprom:w:$(TARGET).eep:i
ATT_AVRDUDE_FUSES = -pt85 -D -U lfuse:w:0xe2:m -U hfuse:w:0xdf:m -U efuse:w:0xff:m

ATM_CLOCK = 16000000L
ATM_INCDIRS = /usr/lib/avr/include
ATM_CXXFLAGS = -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions \
               -ffunction-sections -fdata-sections -fno-threadsafe-statics \
							 -MMD -flto -mmcu=atmega328p -DF_CPU=$(ATM_CLOCK) \
							 $(patsubst %,-I%,$(ATM_EXTRAINCDIRS)) \
							 -DARDUINO=10612 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR -D__AVR_ATmega328__
ATM_LINKFLAGS = -w -Os \
							 -mmcu=atmega328p -Xlinker --defsym=__heap_end=0x00
ATM_LDFLAGS = -ffunction-sections -Wl,--gc-sections,-Map=$(TARGET).map,--cref
ATM_FORMAT = ihex
ATM_AVRDUDE_WRITE_FLASH = -patmega328p -D -U flash:w:$(TARGET).hex:i

##
# RaspberryPi 1 (ARM6) rules
##

rsp1Release/%.lss: rspRelease/%
	@echo
	@echo $(MSG_EXTENDED_LISTING) $@
	$(AR6_OBJDUMP) -h -S $< > $@

rsp1Release/%.sym: rspRelease/%
	@echo
	@echo $(MSG_SYMBOL_TABLE) $@
	$(AR6_NM) -n $< > $@

.SECONDARY : $(RSP1_TARGET)
.PRECIOUS : $(AR6_OBJS)
$(RSP1_TARGET): $(AR6_OBJS)
	@echo
	@echo $(MSG_LINKING) $@
	$(AR6_CXX) $(AR6_OBJS) $(ARCHIVES) --output $@ $(RSP1_LDFLAGS)

rsp1Release/%.o:%.c
	@echo
	@echo $(MSG_COMPILING) $<
	$(AR6_CC) -c $(RSP1_CFLAGS) $< -o $@

rsp1Release/%.o:%.cpp
	@echo
	@echo $(MSG_COMPILING) $<
	$(AR6_CXX) -c $(RSP1_CXXFLAGS) $< -o $@

rsp1Release/%.s:%.c
	$(AR6_CC) -S $(RSP1_CFLAGS) $< -o $@

rsp1Release/%.o : %.S
	@echo
	@echo $(MSG_ASSEMBLING) $<
	$(AR6_CC) -c $(RSP1_ASFLAGS) $< -o $@

rsp1Release/%.d: %.c
		set -e; $(AR6_CC) -MM $(RSP1_CFLAGS) $< \
	| sed 's,\(.*\)\.o[ :]*,\1.o \1.d : ,g' > $@; \
	[ -s $@ ] || rm -f $@

##
# RaspberryPi 2 (ARM 7)rules
##

rspRelease/%.lss: rspRelease/%
	@echo
	@echo $(MSG_EXTENDED_LISTING) $@
	$(ARM_OBJDUMP) -h -S $< > $@

rspRelease/%.sym: rspRelease/%
	@echo
	@echo $(MSG_SYMBOL_TABLE) $@
	$(ARM_NM) -n $< > $@

.SECONDARY : $(RSP_TARGET)
.PRECIOUS : $(ARM_OBJS)
$(RSP_TARGET): $(ARM_OBJS)
	@echo
	@echo $(MSG_LINKING) $@
	$(ARM_CXX) $(ARM_OBJS) $(ARCHIVES) --output $@ $(RSP_LDFLAGS)

rspRelease/%.o:%.c
	@echo
	@echo $(MSG_COMPILING) $<
	$(ARM_CC) -c $(RSP_CFLAGS) $< -o $@

rspRelease/%.o:%.cpp
	@echo
	@echo $(MSG_COMPILING) $<
	$(ARM_CXX) -c $(RSP_CXXFLAGS) $< -o $@

rspRelease/%.s:%.c
	$(ARM_CC) -S $(RSP_CFLAGS) $< -o $@

rspRelease/%.o : %.S
	@echo
	@echo $(MSG_ASSEMBLING) $<
	$(ARM_CC) -c $(RSP_ASFLAGS) $< -o $@

rspRelease/%.d: %.c
		set -e; $(ARM_CC) -MM $(RSP_CFLAGS) $< \
	| sed 's,\(.*\)\.o[ :]*,\1.o \1.d : ,g' > $@; \
	[ -s $@ ] || rm -f $@

##
# ATTINY 85 rules
##

# Create final output files (.hex, .eep) from ELF output file.
attRelease/%.hex: attRelease/%.elf
	@echo
	@echo $(MSG_FLASH) $@
	$(AVR_STRIP) $< -o $<.stripped
	$(AVR_OBJCOPY) -O $(ATT_FORMAT) -R .eeprom $<.stripped $@

attRelease/%.eep: attRelease/%.elf
	@echo
	@echo $(MSG_EEPROM) $@
	- $(AVR_OBJCOPY) -j .eeprom --set-section-flags=.eeprom="alloc,load" \
	--change-section-lma .eeprom=0 -O $(ATT_FORMAT) $< $@

attRelease/%.lss: attRelease/%.elf
	@echo
	@echo $(MSG_EXTENDED_LISTING) $@
	$(AVR_OBJDUMP) -h -S $< > $@

attRelease/%.sym: attRelease/%.elf
	@echo
	@echo $(MSG_SYMBOL_TABLE) $@
	avr-nm -n $< > $@

.SECONDARY : $(TARGET).elf
.PRECIOUS : $(AVR_OBJS)
attRelease/%.elf: $(AVR_OBJS)
	@echo
	@echo $(MSG_LINKING) $@
	$(AVR_CC) $(ATT_LINKFLAGS) $(AVR_OBJS) $(ARCHIVES) --output $@ $(ATT_LDFLAGS)

attRelease/%.o:%.c
	@echo
	@echo $(MSG_COMPILING) $<
	$(AVR_CC) -c $(ATT_CFLAGS) $< -o $@

attRelease/%.o: %.cpp
	@echo
	@echo $(MSG_COMPILING) $<
	$(AVR_CXX) -c $(ATT_CXXFLAGS) $< -o $@

attRelease/%.s : %.c
	$(AVR_CC) -S $(ATT_CXXFLAGS) $< -o $@

attRelease/%.o : %.S
	@echo
	@echo $(MSG_ASSEMBLING) $<
	$(AVR_CC) -c $(ATT_ASFLAGS) $< -o $@

attRelease/%.d: %.c
		set -e; $(AVR_CC) -MM $(ATT_CFLAGS) $< \
	| sed 's,\(.*\)\.o[ :]*,\1.o \1.d : ,g' > $@; \
	[ -s $@ ] || rm -f $@


##
# AT MEGA (ARDUINO) rules
##

# Create final output files (.hex, .eep) from ELF output file.
atmRelease/%.hex: atmRelease/%.elf
	@echo
	@echo $(MSG_FLASH) $@
	$(AVR_STRIP) $< -o $<.stripped
	$(AVR_OBJCOPY) -O $(ATM_FORMAT) -R .eeprom $<.stripped $@

atmRelease/%.eep: atmRelease/%.elf
	@echo
	@echo $(MSG_EEPROM) $@
	- $(AVR_OBJCOPY) -j .eeprom --set-section-flags=.eeprom="alloc,load" \
	--change-section-lma .eeprom=0 -O $(FORMAT) $< $@

atmRelease/%.lss: atmRelease/%.elf
	@echo
	@echo $(MSG_EXTENDED_LISTING) $@
	$(AVR_OBJDUMP) -h -S $< > $@

atmRelease/%.sym: atmRelease/%.elf
	@echo
	@echo $(MSG_SYMBOL_TABLE) $@
	avr-nm -n $< > $@

.SECONDARY : $(TARGET).elf
.PRECIOUS : $(AVR_OBJS)
atmRelease/%.elf: $(AVR_OBJS)
	@echo
	@echo $(MSG_LINKING) $@
	$(AVR_CC) $(ATM_LINKFLAGS) $(AVR_OBJS) $(ARCHIVES) --output $@ $(ATM_LDFLAGS)

atmRelease/%.o:%.c
	@echo
	@echo $(MSG_COMPILING) $<
	$(AVR_CC) -c $(CFLAGS) $< -o $@

atmRelease/%.o: %.cpp
	@echo
	@echo $(MSG_COMPILING) $<
	$(AVR_CXX) -c $(ATM_CXXFLAGS) $< -o $@

atmRelease/%.s : %.c
	$(AVR_CC) -S $(CXXFLAGS) $< -o $@

atmRelease/%.o : %.S
	@echo
	@echo $(MSG_ASSEMBLING) $<
	$(AVR_CC) -c $(ALL_ASFLAGS) $< -o $@

atmRelease/%.d: %.c
		set -e; $(AVR_CC) -MM $(ALL_CFLAGS) $< \
	| sed 's,\(.*\)\.o[ :]*,\1.o \1.d : ,g' > $@; \
	[ -s $@ ] || rm -f $@
