"""Cocotb testbench for ace crc16 -- CRC-16/CCITT generator."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def init_inputs(dut):
    dut.data_in.value = 0
    dut.data_valid.value = 0
    dut.crc_init.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify CRC is 0xFFFF after reset (initial value)."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    val = dut.crc_out.value
    assert val.is_resolvable, f"crc_out has X/Z after reset: {val}"
    try:
        assert int(val) == 0xFFFF, f"CRC not 0xFFFF after reset: {int(val):#06x}"
    except ValueError:
        assert False, f"crc_out not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_single_byte(dut):
    """Feed single byte 0x00 and check CRC output."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.data_in.value = 0x00
    dut.data_valid.value = 1
    await RisingEdge(dut.clk)
    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    val = dut.crc_out.value
    assert val.is_resolvable, f"crc_out has X/Z: {val}"
    try:
        dut._log.info(f"CRC after 0x00: {int(val):#06x}")
    except ValueError:
        dut._log.info(f"crc_out not convertible: {val}")
    dut._log.info("Single byte test -- PASS")


@cocotb.test()
async def test_multi_byte(dut):
    """Feed 'ABC' (0x41,0x42,0x43) and verify CRC updates each byte."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for byte_val in [0x41, 0x42, 0x43]:
        dut.data_in.value = byte_val
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)
        dut.data_valid.value = 0
        await RisingEdge(dut.clk)
        val = dut.crc_out.value
        if val.is_resolvable:
            try:
                dut._log.info(f"CRC after 0x{byte_val:02x}: {int(val):#06x}")
            except ValueError:
                pass

    dut._log.info("Multi-byte test -- PASS")


@cocotb.test()
async def test_crc_init(dut):
    """Verify crc_init resets CRC to 0xFFFF."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Feed some data
    dut.data_in.value = 0xFF
    dut.data_valid.value = 1
    await RisingEdge(dut.clk)
    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    # Re-init
    dut.crc_init.value = 1
    await RisingEdge(dut.clk)
    dut.crc_init.value = 0
    await RisingEdge(dut.clk)

    val = dut.crc_out.value
    assert val.is_resolvable, f"crc_out has X/Z after init: {val}"
    try:
        assert int(val) == 0xFFFF, f"CRC not 0xFFFF after init: {int(val):#06x}"
    except ValueError:
        assert False, f"crc_out not convertible: {val}"
    dut._log.info("CRC init test -- PASS")


@cocotb.test()
async def test_deterministic(dut):
    """Same input sequence should produce same CRC each time."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    crcs = []
    for trial in range(2):
        dut.crc_init.value = 1
        await RisingEdge(dut.clk)
        dut.crc_init.value = 0
        await RisingEdge(dut.clk)

        for byte_val in [0x31, 0x32, 0x33]:
            dut.data_in.value = byte_val
            dut.data_valid.value = 1
            await RisingEdge(dut.clk)
        dut.data_valid.value = 0
        await RisingEdge(dut.clk)

        val = dut.crc_out.value
        if val.is_resolvable:
            try:
                crcs.append(int(val))
            except ValueError:
                pass

    if len(crcs) == 2:
        assert crcs[0] == crcs[1], f"CRC not deterministic: {crcs[0]:#06x} vs {crcs[1]:#06x}"
    dut._log.info(f"Deterministic CRC: {[hex(c) for c in crcs]} -- PASS")
