"""Cocotb testbench for i2s_transmitter - I2S audio transmitter."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, ready should be high and outputs idle."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.left_data.value = 0
    dut.right_data.value = 0
    dut.sample_valid.value = 0
    dut.bit_width_24.value = 0
    await RisingEdge(dut.clk)

    if dut.ready.value.is_resolvable:
        try:
            assert int(dut.ready.value) == 1, "ready should be 1 after reset"
        except ValueError:
            assert False, "ready X/Z after reset"

    if dut.sdata.value.is_resolvable:
        try:
            assert int(dut.sdata.value) == 0, "sdata should be 0 after reset"
        except ValueError:
            assert False, "sdata X/Z after reset"


@cocotb.test()
async def test_ready_goes_low(dut):
    """When sample is loaded, ready should go low."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.bit_width_24.value = 0
    dut.left_data.value = 0x00AA00
    dut.right_data.value = 0x005500
    dut.sample_valid.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.sample_valid.value = 0

    if dut.ready.value.is_resolvable:
        try:
            val = int(dut.ready.value)
            dut._log.info(f"ready after sample load: {val}")
            assert val == 0, "ready should go low when transmitting"
        except ValueError:
            assert False, "ready X/Z after sample load"


@cocotb.test()
async def test_sclk_toggles(dut):
    """Verify sclk toggles during transmission."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.bit_width_24.value = 0
    dut.left_data.value = 0xABCD00
    dut.right_data.value = 0x123400
    dut.sample_valid.value = 1
    await RisingEdge(dut.clk)
    dut.sample_valid.value = 0

    sclk_transitions = 0
    prev_sclk = 0
    for _ in range(200):
        await RisingEdge(dut.clk)
        if dut.sclk.value.is_resolvable:
            try:
                cur = int(dut.sclk.value)
                if cur != prev_sclk:
                    sclk_transitions += 1
                prev_sclk = cur
            except ValueError:
                pass

    dut._log.info(f"SCLK transitions observed: {sclk_transitions}")
    assert sclk_transitions > 0, "SCLK should toggle during transmission"


@cocotb.test()
async def test_ready_returns_high(dut):
    """After transmitting both channels, ready should go high again."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.bit_width_24.value = 0
    dut.left_data.value = 0xFF0000
    dut.right_data.value = 0x00FF00
    dut.sample_valid.value = 1
    await RisingEdge(dut.clk)
    dut.sample_valid.value = 0

    # Wait enough cycles for 16-bit stereo transmission
    ready_seen = False
    for _ in range(500):
        await RisingEdge(dut.clk)
        if dut.ready.value.is_resolvable:
            try:
                if int(dut.ready.value) == 1:
                    ready_seen = True
                    break
            except ValueError:
                pass

    assert ready_seen, "ready never returned high after transmission"
    dut._log.info("Transmission complete - ready returned high")
