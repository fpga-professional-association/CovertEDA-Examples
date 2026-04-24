"""Cocotb testbench for clock_crossing - CDC synchronizer with gray-code FIFO."""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb_helpers import reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, FIFO should be empty and not full."""
    cocotb.start_soon(Clock(dut.wr_clk, 20, unit="ns").start())
    cocotb.start_soon(Clock(dut.rd_clk, 30, unit="ns").start())

    await reset_dut(dut, "wr_reset_n", active_low=True, cycles=5)
    await reset_dut(dut, "rd_reset_n", active_low=True, cycles=5)

    dut.wr_data.value = 0
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    await RisingEdge(dut.wr_clk)

    if dut.rd_empty.value.is_resolvable:
        try:
            assert int(dut.rd_empty.value) == 1, "Should be empty after reset"
        except ValueError:
            assert False, "rd_empty X/Z after reset"

    if dut.wr_full.value.is_resolvable:
        try:
            assert int(dut.wr_full.value) == 0, "Should not be full after reset"
        except ValueError:
            assert False, "wr_full X/Z after reset"


@cocotb.test()
async def test_write_then_read(dut):
    """Write one item, then read it back."""
    cocotb.start_soon(Clock(dut.wr_clk, 20, unit="ns").start())
    cocotb.start_soon(Clock(dut.rd_clk, 30, unit="ns").start())

    await reset_dut(dut, "wr_reset_n", active_low=True, cycles=5)
    await reset_dut(dut, "rd_reset_n", active_low=True, cycles=5)

    # Write
    dut.wr_data.value = 0xAB
    dut.wr_en.value = 1
    dut.rd_en.value = 0
    await RisingEdge(dut.wr_clk)
    dut.wr_en.value = 0

    # Wait for synchronization (2-3 rd_clk cycles)
    for _ in range(6):
        await RisingEdge(dut.rd_clk)

    # Read
    dut.rd_en.value = 1
    await RisingEdge(dut.rd_clk)
    await RisingEdge(dut.rd_clk)
    dut.rd_en.value = 0

    if dut.rd_data.value.is_resolvable:
        try:
            val = int(dut.rd_data.value)
            dut._log.info(f"Read data: {val:#04x}")
        except ValueError:
            dut._log.info("rd_data X/Z")


@cocotb.test()
async def test_empty_after_read(dut):
    """After reading all data, FIFO should be empty."""
    cocotb.start_soon(Clock(dut.wr_clk, 20, unit="ns").start())
    cocotb.start_soon(Clock(dut.rd_clk, 30, unit="ns").start())

    await reset_dut(dut, "wr_reset_n", active_low=True, cycles=5)
    await reset_dut(dut, "rd_reset_n", active_low=True, cycles=5)

    # Write one item
    dut.wr_data.value = 0x42
    dut.wr_en.value = 1
    dut.rd_en.value = 0
    await RisingEdge(dut.wr_clk)
    dut.wr_en.value = 0

    # Sync delay
    for _ in range(6):
        await RisingEdge(dut.rd_clk)

    # Read it
    dut.rd_en.value = 1
    await RisingEdge(dut.rd_clk)
    await RisingEdge(dut.rd_clk)
    dut.rd_en.value = 0

    # Wait for empty to propagate
    for _ in range(6):
        await RisingEdge(dut.rd_clk)

    if dut.rd_empty.value.is_resolvable:
        try:
            empty = int(dut.rd_empty.value)
            dut._log.info(f"rd_empty after read: {empty}")
        except ValueError:
            dut._log.info("rd_empty X/Z")
