# CovertEDA-managed OSS CAD Suite build for logic_analyzer
# Targets: yosys (synth) -> nextpnr-ecp5 -> ecppack
PROJ    := logic_analyzer
TOP     := logic_analyzer
DEVICE  := 25k
PACKAGE := CABGA256
SRC     := src/logic_analyzer.v
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
