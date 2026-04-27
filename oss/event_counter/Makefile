# CovertEDA-managed OSS CAD Suite build for event_counter
# Targets: yosys (synth) -> nextpnr-ecp5 -> ecppack
PROJ    := event_counter
TOP     := event_counter
DEVICE  := 25k
PACKAGE := CABGA256
SRC     := src/event_counter.v
LPF     :=

.PHONY: all clean
all: build/$(PROJ).bit

build/$(PROJ).bit: build/$(PROJ).config
	ecppack --bit $@ $<

build/$(PROJ).config: build/$(PROJ).json
	nextpnr-ecp5 --$(DEVICE) --package $(PACKAGE) --json $< --textcfg $@ $(if $(LPF),--lpf $(LPF))

build/$(PROJ).json: $(SRC)
	@mkdir -p build
	yosys -p "synth_ecp5 -top $(TOP) -json $@" $(SRC)

clean:
	rm -rf build
