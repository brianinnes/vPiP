include defs.mk

# Default target: make program!
all: begin gccversion boardDriver end

begin:
	@echo
	@echo $(MSG_BEGIN)

finished:
	@echo $(MSG_ERRORS_NONE)

end:
	@echo $(MSG_END)
	@echo

boardDriver:
	$(MAKE) -w -C boardDriver all

# Display compiler version information.
gccversion :
	@$(ARM_CC) --version
	@$(ARM_CXX) --version

install: boardDriver
	@echo $(MSG_INSTALLING)
	$(MAKE) -w -C boardDriver install

# Target: clean project.
clean: begin clean_list finished end

clean_list :
	@echo
	@echo $(MSG_CLEANING)
	$(REMOVE) $(TARGET).hex
	$(REMOVE) $(TARGET).eep
	$(REMOVE) $(TARGET).obj
	$(REMOVE) $(TARGET).cof
	$(REMOVE) $(TARGET).elf
	$(REMOVE) $(TARGET).map
	$(REMOVE) $(TARGET).obj
	$(REMOVE) $(TARGET).a90
	$(REMOVE) $(TARGET).sym
	$(REMOVE) $(TARGET).lnk
	$(REMOVE) $(TARGET).lss
	$(REMOVE) $(OBJ)
	$(REMOVE) $(LST)
	$(REMOVE) $(SRC:.c=.s)
	$(REMOVE) $(SRC:.c=.d)
	$(REMOVE) *~
	$(MAKE) -w -C boardDriver clean

# Listing of phony targets.
.PHONY : all gccversion clean clean_list boardDriver \
		install begin finished end
