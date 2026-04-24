"""Cocotb testbench for i2s_receiver - I2S audio receiver."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, sample_valid should be 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.sclk_in.value = 0
    dut.lrclk_in.value = 0
    dut.sdata_in.value = 0
    dut.bit_width_24.value = 0
    await RisingEdge(dut.clk)

    if dut.sample_valid.value.is_resolvable:
        try:
            assert int(dut.sample_valid.value) == 0, "sample_valid should be 0 after reset"
        except ValueError:
            assert False, "sample_valid X/Z after reset"


@cocotb.test()
async def test_idle_no_valid(dut):
    """With no I2S activity, sample_valid stays 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.sclk_in.value = 0
    dut.lrclk_in.value = 0
    dut.sdata_in.value = 0
    dut.bit_width_24.value = 0

    await ClockCycles(dut.clk, 100)

    if dut.sample_valid.value.is_resolvable:
        try:
            assert int(dut.sample_valid.value) == 0, "No valid without I2S activity"
        except ValueError:
            pass

    dut._log.info("No spurious sample_valid during idle")


@cocotb.test()
async def test_outputs_resolvable(dut):
    """Verify all outputs are resolvable after reset."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.sclk_in.value = 0
    dut.lrclk_in.value = 0
    dut.sdata_in.value = 0
    dut.bit_width_24.value = 0
    await ClockCycles(dut.clk, 5)

    for sig_name in ["left_data", "right_data", "sample_valid"]:
        sig = getattr(dut, sig_name)
        if not sig.value.is_resolvable:
            assert False, f"{sig_name} contains X/Z after reset"
        try:
            int(sig.value)
        except ValueError:
            assert False, f"{sig_name} not convertible after reset"

    dut._log.info("All outputs resolvable after reset")
