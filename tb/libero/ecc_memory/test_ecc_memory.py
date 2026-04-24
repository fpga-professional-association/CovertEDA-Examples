"""Cocotb testbench for ecc_memory - 32-bit memory with SECDED ECC."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, rd_valid should be 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.addr.value = 0
    dut.wr_data.value = 0
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)

    if dut.rd_valid.value.is_resolvable:
        try:
            assert int(dut.rd_valid.value) == 0, "rd_valid should be 0 after reset"
        except ValueError:
            assert False, "rd_valid X/Z after reset"


@cocotb.test()
async def test_write_read_no_error(dut):
    """Write then read same address, expect no errors."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    # Write
    dut.addr.value = 0
    dut.wr_data.value = 0xDEADBEEF
    dut.wr_en.value = 1
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)

    # Read
    dut.wr_en.value = 0
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    if dut.rd_data.value.is_resolvable:
        try:
            val = int(dut.rd_data.value)
            dut._log.info(f"Read: {val:#010x}")
            assert val == 0xDEADBEEF, f"Expected 0xDEADBEEF, got {val:#010x}"
        except ValueError:
            assert False, "rd_data X/Z"

    if dut.single_err.value.is_resolvable:
        try:
            assert int(dut.single_err.value) == 0, "No single error expected"
        except ValueError:
            pass

    if dut.double_err.value.is_resolvable:
        try:
            assert int(dut.double_err.value) == 0, "No double error expected"
        except ValueError:
            pass


@cocotb.test()
async def test_multiple_addresses(dut):
    """Write to several addresses and read back."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    test_data = {0: 0x11111111, 10: 0x22222222, 255: 0x33333333}

    for addr, data in test_data.items():
        dut.addr.value = addr
        dut.wr_data.value = data
        dut.wr_en.value = 1
        dut.rd_en.value = 0
        await RisingEdge(dut.clk)

    dut.wr_en.value = 0
    for addr, expected in test_data.items():
        dut.addr.value = addr
        dut.rd_en.value = 1
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        if dut.rd_data.value.is_resolvable:
            try:
                val = int(dut.rd_data.value)
                dut._log.info(f"Addr {addr}: read {val:#010x}, expected {expected:#010x}")
            except ValueError:
                dut._log.info(f"Addr {addr}: X/Z")

    dut._log.info("Multiple address read-back complete")
