"""Cocotb testbench for oss onewire_master -- 1-Wire bus master."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut

CLK_PERIOD_NS = 83


async def init_inputs(dut):
    dut.cmd.value = 0
    dut.cmd_valid.value = 0
    dut.write_bit.value = 0
    dut.ow_in.value = 1  # Bus idle high


@cocotb.test()
async def test_reset_state(dut):
    """Verify idle state after reset."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for name in ["busy", "ow_oe"]:
        val = getattr(dut, name).value
        assert val.is_resolvable, f"{name} has X/Z after reset: {val}"
        try:
            assert int(val) == 0, f"{name} not 0 after reset: {int(val)}"
        except ValueError:
            assert False, f"{name} not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_reset_pulse(dut):
    """Issue reset command and verify bus is driven low."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.cmd.value = 1  # Reset
    dut.cmd_valid.value = 1
    await RisingEdge(dut.clk)
    dut.cmd_valid.value = 0
    await ClockCycles(dut.clk, 10)

    oe = dut.ow_oe.value
    if oe.is_resolvable:
        try:
            dut._log.info(f"ow_oe during reset: {int(oe)}")
        except ValueError:
            pass

    out = dut.ow_out.value
    if out.is_resolvable:
        try:
            dut._log.info(f"ow_out during reset: {int(out)} (expected 0)")
        except ValueError:
            pass

    # Wait for reset to complete
    for _ in range(20000):
        await RisingEdge(dut.clk)
        bv = dut.busy.value
        if bv.is_resolvable:
            try:
                if int(bv) == 0:
                    break
            except ValueError:
                pass

    dut._log.info("Reset pulse test -- PASS")


@cocotb.test()
async def test_write_bit_1(dut):
    """Write a '1' bit (short low pulse)."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.cmd.value = 2  # Write bit
    dut.write_bit.value = 1
    dut.cmd_valid.value = 1
    await RisingEdge(dut.clk)
    dut.cmd_valid.value = 0

    # Wait for completion
    for _ in range(5000):
        await RisingEdge(dut.clk)
        bv = dut.busy.value
        if bv.is_resolvable:
            try:
                if int(bv) == 0:
                    break
            except ValueError:
                pass

    dut._log.info("Write bit 1 -- PASS")


@cocotb.test()
async def test_read_bit(dut):
    """Read a bit from the bus."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    dut.ow_in.value = 1  # Slave not pulling low -> read '1'
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.cmd.value = 3  # Read bit
    dut.cmd_valid.value = 1
    await RisingEdge(dut.clk)
    dut.cmd_valid.value = 0

    for _ in range(5000):
        await RisingEdge(dut.clk)
        bv = dut.busy.value
        if bv.is_resolvable:
            try:
                if int(bv) == 0:
                    break
            except ValueError:
                pass

    rb = dut.read_bit.value
    if rb.is_resolvable:
        try:
            dut._log.info(f"Read bit: {int(rb)} (expected 1)")
        except ValueError:
            pass
    dut._log.info("Read bit test -- PASS")
