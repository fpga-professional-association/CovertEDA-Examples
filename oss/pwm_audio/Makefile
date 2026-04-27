# CovertEDA-managed OSS CAD Suite build for pwm_audio
# Targets: yosys (synth) -> nextpnr-ecp5 -> ecppack
PROJ    := pwm_audio
TOP     := audio_top
DEVICE  := 25k
PACKAGE := CABGA256
SRC     := src/audio_top.v \
         src/pwm_dac.v \
         src/sample_rom.v
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
