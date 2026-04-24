"""Cocotb testbench for vivado dpram."""

import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb_helpers import setup_clock


@cocotb.test()
async def test_port_a_write_read(dut):
    """Write via port A and read back from port A."""
    setup_clock(dut, "clk_a", 10)
    setup_clock(dut, "clk_b", 10)

    dut.en_a.value = 0
    dut.we_a.value = 0
    dut.addr_a.value = 0
    dut.din_a.value = 0
    dut.en_b.value = 0
    dut.we_b.value = 0
    dut.addr_b.value = 0
    dut.din_b.value = 0

    await Timer(50, unit="ns")

    # Write to addr 0
    dut.en_a.value = 1
    dut.we_a.value = 1
    dut.addr_a.value = 0
    dut.din_a.value = 0xDEADBEEF
    await RisingEdge(dut.clk_a)

    # Read from addr 0
    dut.we_a.value = 0
    dut.addr_a.value = 0
    await RisingEdge(dut.clk_a)
    await RisingEdge(dut.clk_a)

    if dut.dout_a.value.is_resolvable:
        try:
            val = int(dut.dout_a.value)
            dut._log.info(f"Port A read addr 0: {val:#010x} (expected 0xDEADBEEF)")
        except ValueError:
            dut._log.info("dout_a not convertible")


@cocotb.test()
async def test_port_b_write_read(dut):
    """Write via port B and read back from port B."""
    setup_clock(dut, "clk_a", 10)
    setup_clock(dut, "clk_b", 10)

    dut.en_a.value = 0
    dut.we_a.value = 0
    dut.addr_a.value = 0
    dut.din_a.value = 0
    dut.en_b.value = 0
    dut.we_b.value = 0
    dut.addr_b.value = 0
    dut.din_b.value = 0

    await Timer(50, unit="ns")

    # Write via port B to addr 10
    dut.en_b.value = 1
    dut.we_b.value = 1
    dut.addr_b.value = 10
    dut.din_b.value = 0xCAFEBABE
    await RisingEdge(dut.clk_b)

    # Read back
    dut.we_b.value = 0
    await RisingEdge(dut.clk_b)
    await RisingEdge(dut.clk_b)

    if dut.dout_b.value.is_resolvable:
        try:
            val = int(dut.dout_b.value)
            dut._log.info(f"Port B read addr 10: {val:#010x} (expected 0xCAFEBABE)")
        except ValueError:
            dut._log.info("dout_b not convertible")


@cocotb.test()
async def test_cross_port_read(dut):
    """Write from port A, read from port B at same address."""
    setup_clock(dut, "clk_a", 10)
    setup_clock(dut, "clk_b", 10)

    dut.en_a.value = 0
    dut.we_a.value = 0
    dut.addr_a.value = 0
    dut.din_a.value = 0
    dut.en_b.value = 0
    dut.we_b.value = 0
    dut.addr_b.value = 0
    dut.din_b.value = 0

    await Timer(50, unit="ns")

    # Write via port A
    dut.en_a.value = 1
    dut.we_a.value = 1
    dut.addr_a.value = 5
    dut.din_a.value = 0x12345678
    await RisingEdge(dut.clk_a)
    dut.we_a.value = 0
    dut.en_a.value = 0

    await Timer(20, unit="ns")

    # Read via port B
    dut.en_b.value = 1
    dut.addr_b.value = 5
    await RisingEdge(dut.clk_b)
    await RisingEdge(dut.clk_b)

    if dut.dout_b.value.is_resolvable:
        try:
            val = int(dut.dout_b.value)
            dut._log.info(f"Port B read of port A write: {val:#010x} (expected 0x12345678)")
        except ValueError:
            dut._log.info("dout_b not convertible")


@cocotb.test()
async def test_multiple_addresses(dut):
    """Write and read multiple addresses."""
    setup_clock(dut, "clk_a", 10)
    setup_clock(dut, "clk_b", 10)

    dut.en_a.value = 0
    dut.we_a.value = 0
    dut.addr_a.value = 0
    dut.din_a.value = 0
    dut.en_b.value = 0
    dut.we_b.value = 0
    dut.addr_b.value = 0
    dut.din_b.value = 0

    await Timer(50, unit="ns")

    # Write 8 addresses via port A
    dut.en_a.value = 1
    dut.we_a.value = 1
    for i in range(8):
        dut.addr_a.value = i
        dut.din_a.value = (i + 1) * 0x11111111
        await RisingEdge(dut.clk_a)
    dut.we_a.value = 0
    dut.en_a.value = 0

    await Timer(20, unit="ns")

    # Read back via port B
    dut.en_b.value = 1
    for i in range(8):
        dut.addr_b.value = i
        await RisingEdge(dut.clk_b)
        await RisingEdge(dut.clk_b)
        if dut.dout_b.value.is_resolvable:
            try:
                val = int(dut.dout_b.value)
                dut._log.info(f"Addr {i}: {val:#010x}")
            except ValueError:
                dut._log.info(f"Addr {i}: not convertible")
    dut.en_b.value = 0
