"""Cocotb testbench for oss ir_decoder -- NEC IR remote decoder."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut

CLK_PERIOD_NS = 83


async def init_inputs(dut):
    dut.ir_in.value = 1  # Idle high


@cocotb.test()
async def test_reset_state(dut):
    """Verify outputs clean after reset."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for name in ["data_valid", "error"]:
        val = getattr(dut, name).value
        assert val.is_resolvable, f"{name} has X/Z after reset: {val}"
        try:
            assert int(val) == 0, f"{name} not 0 after reset: {int(val)}"
        except ValueError:
            assert False, f"{name} not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_idle_no_decode(dut):
    """No data_valid when IR line stays idle (high)."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for _ in range(100):
        await RisingEdge(dut.clk)
        dv = dut.data_valid.value
        if dv.is_resolvable:
            try:
                assert int(dv) == 0, "data_valid asserted during idle"
            except ValueError:
                pass
    dut._log.info("Idle no decode -- PASS")


@cocotb.test()
async def test_short_pulse_error(dut):
    """Short pulse (not 9ms leader) should not trigger decode."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Short pulse: 100us (much shorter than 9ms leader)
    dut.ir_in.value = 0
    await ClockCycles(dut.clk, 1200)  # ~100us
    dut.ir_in.value = 1
    await ClockCycles(dut.clk, 1000)

    dv = dut.data_valid.value
    if dv.is_resolvable:
        try:
            assert int(dv) == 0, "data_valid on short pulse"
        except ValueError:
            pass
    dut._log.info("Short pulse no decode -- PASS")
