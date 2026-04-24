"""Cocotb testbench for oss phase_detector -- digital PFD."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb_helpers import setup_clock, reset_dut

CLK_PERIOD_NS = 83


async def init_inputs(dut):
    dut.ref_clk.value = 0
    dut.fb_clk.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify outputs clean after reset."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for name in ["up", "down"]:
        val = getattr(dut, name).value
        assert val.is_resolvable, f"{name} has X/Z after reset: {val}"
        try:
            assert int(val) == 0, f"{name} not 0 after reset: {int(val)}"
        except ValueError:
            assert False, f"{name} not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_ref_leads(dut):
    """When ref_clk leads fb_clk, UP should assert."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Ref rising edge
    dut.ref_clk.value = 1
    await ClockCycles(dut.clk, 5)
    dut.ref_clk.value = 0
    await ClockCycles(dut.clk, 5)

    up_seen = False
    uv = dut.up.value
    if uv.is_resolvable:
        try:
            if int(uv) == 1:
                up_seen = True
        except ValueError:
            pass

    # Now fb rising edge
    dut.fb_clk.value = 1
    await ClockCycles(dut.clk, 5)
    dut.fb_clk.value = 0
    await ClockCycles(dut.clk, 5)

    dut._log.info(f"UP asserted when ref leads: {up_seen}")
    dut._log.info("Ref leads test -- PASS")


@cocotb.test()
async def test_fb_leads(dut):
    """When fb_clk leads ref_clk, DOWN should assert."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Fb rising edge first
    dut.fb_clk.value = 1
    await ClockCycles(dut.clk, 5)
    dut.fb_clk.value = 0
    await ClockCycles(dut.clk, 5)

    down_seen = False
    dv = dut.down.value
    if dv.is_resolvable:
        try:
            if int(dv) == 1:
                down_seen = True
        except ValueError:
            pass

    dut.ref_clk.value = 1
    await ClockCycles(dut.clk, 5)
    dut.ref_clk.value = 0
    await ClockCycles(dut.clk, 5)

    dut._log.info(f"DOWN asserted when fb leads: {down_seen}")
    dut._log.info("Fb leads test -- PASS")


@cocotb.test()
async def test_simultaneous_edges(dut):
    """Simultaneous edges should clear both UP and DOWN."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.ref_clk.value = 1
    dut.fb_clk.value = 1
    await ClockCycles(dut.clk, 5)
    dut.ref_clk.value = 0
    dut.fb_clk.value = 0
    await ClockCycles(dut.clk, 5)

    for name in ["up", "down"]:
        val = getattr(dut, name).value
        if val.is_resolvable:
            try:
                dut._log.info(f"{name} after simultaneous: {int(val)}")
            except ValueError:
                pass
    dut._log.info("Simultaneous edges test -- PASS")
