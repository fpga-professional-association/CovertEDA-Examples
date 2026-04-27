# CovertEDA-managed OSS CAD Suite build for spi_slave
# Targets: yosys (synth) -> nextpnr-ecp5 -> ecppack
PROJ    := spi_slave
TOP     := spi_slave
DEVICE  := 25k
PACKAGE := CABGA256
SRC     := src/reg_bank.v \
         src/spi_slave.v \
         src/spi_top.v
LPF     := constraints/spi.lpf

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
