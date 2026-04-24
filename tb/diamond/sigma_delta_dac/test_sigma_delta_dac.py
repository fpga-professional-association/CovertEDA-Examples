"""Cocotb testbench for sigma_delta_dac - 1-bit sigma-delta DAC."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, dout should be 0."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.din.value = 0
    dut.din_valid.value = 0
    await RisingEdge(dut.clk)

    if dut.dout.value.is_resolvable:
        try:
            assert int(dut.dout.value) == 0, "dout should be 0 after reset"
        except ValueError:
            assert False, "dout X/Z after reset"


@cocotb.test()
async def test_zero_input_low_density(dut):
    """With din=0, output should be mostly 0 (low pulse density)."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.din.value = 0
    dut.din_valid.value = 1
    await RisingEdge(dut.clk)
    dut.din_valid.value = 0

    ones = 0
    total = 500
    for _ in range(total):
        await RisingEdge(dut.clk)
        if dut.dout.value.is_resolvable:
            try:
                ones += int(dut.dout.value)
            except ValueError:
                pass

    density = ones / total
    dut._log.info(f"Zero input: pulse density = {density:.3f} ({ones}/{total})")
    assert density < 0.1, f"Expected low density for zero input, got {density:.3f}"


@cocotb.test()
async def test_max_input_high_density(dut):
    """With din=0xFFFF, output should be mostly 1 (high pulse density)."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.din.value = 0xFFFF
    dut.din_valid.value = 1
    await RisingEdge(dut.clk)
    dut.din_valid.value = 0

    ones = 0
    total = 500
    for _ in range(total):
        await RisingEdge(dut.clk)
        if dut.dout.value.is_resolvable:
            try:
                ones += int(dut.dout.value)
            except ValueError:
                pass

    density = ones / total
    dut._log.info(f"Max input: pulse density = {density:.3f} ({ones}/{total})")
    assert density > 0.9, f"Expected high density for max input, got {density:.3f}"


@cocotb.test()
async def test_mid_input_half_density(dut):
    """With din=0x8000, output should be ~50% density."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.din.value = 0x8000
    dut.din_valid.value = 1
    await RisingEdge(dut.clk)
    dut.din_valid.value = 0

    ones = 0
    total = 1000
    for _ in range(total):
        await RisingEdge(dut.clk)
        if dut.dout.value.is_resolvable:
            try:
                ones += int(dut.dout.value)
            except ValueError:
                pass

    density = ones / total
    dut._log.info(f"Mid input: pulse density = {density:.3f} ({ones}/{total})")
    assert 0.3 < density < 0.7, f"Expected ~50% density for mid input, got {density:.3f}"
