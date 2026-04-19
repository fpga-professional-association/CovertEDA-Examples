"""Cocotb testbench for ace histogram -- 256-bin histogram calculator."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def init_inputs(dut):
    dut.data_in.value = 0
    dut.data_valid.value = 0
    dut.clear.value = 0
    dut.read_addr.value = 0
    dut.read_en.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify outputs are zero after reset."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    val = dut.read_valid.value
    assert val.is_resolvable, f"read_valid has X/Z after reset: {val}"
    try:
        assert int(val) == 0, f"read_valid not 0 after reset: {int(val)}"
    except ValueError:
        assert False, f"read_valid not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_single_increment(dut):
    """Insert one value and read back count=1."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.data_in.value = 42
    dut.data_valid.value = 1
    await RisingEdge(dut.clk)
    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    dut.read_addr.value = 42
    dut.read_en.value = 1
    await RisingEdge(dut.clk)
    dut.read_en.value = 0
    await RisingEdge(dut.clk)

    val = dut.read_count.value
    assert val.is_resolvable, f"read_count has X/Z: {val}"
    try:
        assert int(val) == 1, f"Expected count=1 for bin 42, got {int(val)}"
    except ValueError:
        assert False, f"read_count not convertible: {val}"
    dut._log.info("Single increment -- PASS")


@cocotb.test()
async def test_multiple_increments(dut):
    """Insert same value 5 times and verify count=5."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for _ in range(5):
        dut.data_in.value = 100
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)
    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    dut.read_addr.value = 100
    dut.read_en.value = 1
    await RisingEdge(dut.clk)
    dut.read_en.value = 0
    await RisingEdge(dut.clk)

    val = dut.read_count.value
    assert val.is_resolvable, f"read_count has X/Z: {val}"
    try:
        assert int(val) == 5, f"Expected count=5 for bin 100, got {int(val)}"
    except ValueError:
        assert False, f"read_count not convertible: {val}"
    dut._log.info("Multiple increments -- PASS")


@cocotb.test()
async def test_clear_bins(dut):
    """Insert values, clear, verify count=0."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for _ in range(3):
        dut.data_in.value = 200
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)
    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    dut.clear.value = 1
    await RisingEdge(dut.clk)
    dut.clear.value = 0
    await RisingEdge(dut.clk)

    dut.read_addr.value = 200
    dut.read_en.value = 1
    await RisingEdge(dut.clk)
    dut.read_en.value = 0
    await RisingEdge(dut.clk)

    val = dut.read_count.value
    assert val.is_resolvable, f"read_count has X/Z after clear: {val}"
    try:
        assert int(val) == 0, f"Expected count=0 after clear, got {int(val)}"
    except ValueError:
        assert False, f"read_count not convertible: {val}"
    dut._log.info("Clear bins -- PASS")
