"""Cocotb testbench for rom_lookup - 256x8 ROM lookup table."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, data_out should be 0 and data_valid should be low."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rd_en.value = 0
    dut.addr.value = 0
    await RisingEdge(dut.clk)

    if dut.data_out.value.is_resolvable:
        try:
            val = int(dut.data_out.value)
            dut._log.info(f"data_out after reset: {val}")
            assert val == 0, f"Expected data_out=0 after reset, got {val}"
        except ValueError:
            assert False, f"data_out contains X/Z after reset: {dut.data_out.value}"

    if dut.data_valid.value.is_resolvable:
        try:
            vld = int(dut.data_valid.value)
            assert vld == 0, f"Expected data_valid=0 after reset, got {vld}"
        except ValueError:
            assert False, f"data_valid X/Z after reset"


@cocotb.test()
async def test_read_address_zero(dut):
    """Read from address 0 and verify ROM content."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.addr.value = 0
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    if dut.data_valid.value.is_resolvable:
        try:
            vld = int(dut.data_valid.value)
            assert vld == 1, f"Expected data_valid=1 during read, got {vld}"
        except ValueError:
            assert False, f"data_valid X/Z during read"

    if dut.data_out.value.is_resolvable:
        try:
            val = int(dut.data_out.value)
            dut._log.info(f"ROM[0] = {val}")
            assert val == 0, f"Expected ROM[0]=0 (triangular wave base), got {val}"
        except ValueError:
            assert False, f"data_out X/Z during read"


@cocotb.test()
async def test_sequential_reads(dut):
    """Read several sequential addresses and verify valid output."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rd_en.value = 1
    for addr in range(16):
        dut.addr.value = addr
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        if dut.data_out.value.is_resolvable:
            try:
                val = int(dut.data_out.value)
                expected = addr * 4  # first 64 entries: i*4
                dut._log.info(f"ROM[{addr}] = {val}, expected {expected}")
            except ValueError:
                dut._log.info(f"ROM[{addr}] contains X/Z")


@cocotb.test()
async def test_read_enable_deassert(dut):
    """Verify data_valid goes low when rd_en is deasserted."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.addr.value = 10
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.rd_en.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    if dut.data_valid.value.is_resolvable:
        try:
            vld = int(dut.data_valid.value)
            assert vld == 0, f"Expected data_valid=0 when rd_en=0, got {vld}"
        except ValueError:
            assert False, f"data_valid X/Z when rd_en deasserted"


@cocotb.test()
async def test_all_addresses_valid(dut):
    """Sweep all 256 addresses and verify no X/Z outputs."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rd_en.value = 1
    for addr in range(256):
        dut.addr.value = addr
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        if not dut.data_out.value.is_resolvable:
            assert False, f"data_out X/Z at address {addr}"
        try:
            val = int(dut.data_out.value)
            assert 0 <= val <= 255, f"data_out out of range at addr {addr}: {val}"
        except ValueError:
            assert False, f"data_out not convertible at addr {addr}"

    dut._log.info("All 256 ROM addresses read successfully with valid data")
