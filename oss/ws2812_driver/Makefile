# CovertEDA-managed OSS CAD Suite build for ws2812_driver
# Targets: yosys (synth) -> nextpnr-ecp5 -> ecppack
PROJ    := ws2812_driver
TOP     := ws2812_top
DEVICE  := 25k
PACKAGE := CABGA256
SRC     := src/color_rom.v \
         src/gamma_lut.v \
         src/ws2812_top.v \
         src/ws2812_tx.v
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
