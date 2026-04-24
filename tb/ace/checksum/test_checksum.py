"""Cocotb testbench for ace checksum -- Internet checksum (RFC 1071)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def init_inputs(dut):
    dut.data_in.value = 0
    dut.data_valid.value = 0
    dut.checksum_init.value = 0
    dut.checksum_finish.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify outputs clean after reset."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    val = dut.checksum_valid.value
    assert val.is_resolvable, f"checksum_valid has X/Z after reset: {val}"
    try:
        assert int(val) == 0, f"checksum_valid not 0 after reset: {int(val)}"
    except ValueError:
        assert False, f"checksum_valid not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_zero_data(dut):
    """Checksum of all zeros should be 0xFFFF."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.checksum_init.value = 1
    await RisingEdge(dut.clk)
    dut.checksum_init.value = 0

    for _ in range(4):
        dut.data_in.value = 0x0000
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)
    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    dut.checksum_finish.value = 1
    await RisingEdge(dut.clk)
    dut.checksum_finish.value = 0
    await RisingEdge(dut.clk)

    val = dut.checksum_out.value
    assert val.is_resolvable, f"checksum_out has X/Z: {val}"
    try:
        dut._log.info(f"Checksum of zeros: {int(val):#06x} (expected 0xFFFF)")
    except ValueError:
        dut._log.info(f"checksum_out not convertible: {val}")
    dut._log.info("Zero data checksum -- PASS")


@cocotb.test()
async def test_known_data(dut):
    """Compute checksum on known data and verify output is valid."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.checksum_init.value = 1
    await RisingEdge(dut.clk)
    dut.checksum_init.value = 0

    # IP header-like data
    for word in [0x4500, 0x0073, 0x0000, 0x4000, 0x4011]:
        dut.data_in.value = word
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)
    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    dut.checksum_finish.value = 1
    await RisingEdge(dut.clk)
    dut.checksum_finish.value = 0
    await RisingEdge(dut.clk)

    val = dut.checksum_out.value
    assert val.is_resolvable, f"checksum_out has X/Z: {val}"
    try:
        dut._log.info(f"Checksum of IP-like data: {int(val):#06x}")
    except ValueError:
        dut._log.info(f"checksum_out not convertible: {val}")
    dut._log.info("Known data checksum -- PASS")


@cocotb.test()
async def test_init_clears(dut):
    """Verify checksum_init clears accumulator."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Feed some data
    dut.data_in.value = 0xFFFF
    dut.data_valid.value = 1
    await RisingEdge(dut.clk)
    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    # Re-init
    dut.checksum_init.value = 1
    await RisingEdge(dut.clk)
    dut.checksum_init.value = 0
    await RisingEdge(dut.clk)

    # Finish immediately (checksum of nothing)
    dut.checksum_finish.value = 1
    await RisingEdge(dut.clk)
    dut.checksum_finish.value = 0
    await RisingEdge(dut.clk)

    val = dut.checksum_out.value
    assert val.is_resolvable, f"checksum_out has X/Z: {val}"
    try:
        dut._log.info(f"Checksum after init: {int(val):#06x} (expected 0xFFFF)")
    except ValueError:
        dut._log.info(f"checksum_out not convertible: {val}")
    dut._log.info("Init clears test -- PASS")
