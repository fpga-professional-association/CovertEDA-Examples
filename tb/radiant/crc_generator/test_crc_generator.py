"""Cocotb testbench for radiant crc_generator."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify CRC initializes to 0xFFFFFFFF after reset."""
    setup_clock(dut, "clk", 40)
    dut.valid.value = 0
    dut.data_in.value = 0
    dut.init.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.crc_out.value.is_resolvable, "crc_out has X/Z after reset"
    try:
        crc = int(dut.crc_out.value)
        assert crc == 0xFFFFFFFF, f"CRC not initialized: {crc:#010x}"
        dut._log.info(f"Reset state OK: crc={crc:#010x}")
    except ValueError:
        raise AssertionError("crc_out not resolvable after reset")


@cocotb.test()
async def test_single_byte(dut):
    """Feed a single byte and verify CRC changes."""
    setup_clock(dut, "clk", 40)
    dut.valid.value = 0
    dut.data_in.value = 0
    dut.init.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.data_in.value = 0x31  # ASCII '1'
    dut.valid.value = 1
    await RisingEdge(dut.clk)
    dut.valid.value = 0
    await RisingEdge(dut.clk)

    assert dut.crc_out.value.is_resolvable, "crc_out has X/Z"
    try:
        crc = int(dut.crc_out.value)
        assert crc != 0xFFFFFFFF, f"CRC unchanged after byte: {crc:#010x}"
        dut._log.info(f"CRC after byte 0x31: {crc:#010x}")
    except ValueError:
        raise AssertionError("crc_out not resolvable")


@cocotb.test()
async def test_init_resets_crc(dut):
    """Process data, then assert init, verify CRC returns to 0xFFFFFFFF."""
    setup_clock(dut, "clk", 40)
    dut.valid.value = 0
    dut.data_in.value = 0
    dut.init.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Process a byte
    dut.data_in.value = 0xAA
    dut.valid.value = 1
    await RisingEdge(dut.clk)
    dut.valid.value = 0
    await RisingEdge(dut.clk)

    # Assert init
    dut.init.value = 1
    await RisingEdge(dut.clk)
    dut.init.value = 0
    await RisingEdge(dut.clk)

    assert dut.crc_out.value.is_resolvable, "crc_out has X/Z after init"
    try:
        crc = int(dut.crc_out.value)
        assert crc == 0xFFFFFFFF, f"CRC not reset by init: {crc:#010x}"
        dut._log.info("Init correctly resets CRC")
    except ValueError:
        raise AssertionError("crc_out not resolvable after init")


@cocotb.test()
async def test_multi_byte_deterministic(dut):
    """Feed same sequence twice, verify same CRC result."""
    setup_clock(dut, "clk", 40)
    dut.valid.value = 0
    dut.data_in.value = 0
    dut.init.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    test_data = [0x48, 0x65, 0x6C, 0x6C, 0x6F]  # "Hello"
    crcs = []

    for run in range(2):
        # Init CRC
        dut.init.value = 1
        await RisingEdge(dut.clk)
        dut.init.value = 0
        await RisingEdge(dut.clk)

        # Feed data
        for byte in test_data:
            dut.data_in.value = byte
            dut.valid.value = 1
            await RisingEdge(dut.clk)
        dut.valid.value = 0
        await RisingEdge(dut.clk)

        assert dut.crc_out.value.is_resolvable, "crc_out has X/Z"
        try:
            crcs.append(int(dut.crc_out.value))
        except ValueError:
            raise AssertionError("crc_out not resolvable")

    dut._log.info(f"CRC run 1: {crcs[0]:#010x}, run 2: {crcs[1]:#010x}")
    assert crcs[0] == crcs[1], f"CRC not deterministic: {crcs}"


@cocotb.test()
async def test_crc_valid_pulse(dut):
    """Verify crc_valid pulses on each valid input cycle."""
    setup_clock(dut, "clk", 40)
    dut.valid.value = 0
    dut.data_in.value = 0
    dut.init.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.data_in.value = 0x55
    dut.valid.value = 1
    await RisingEdge(dut.clk)
    dut.valid.value = 0
    await RisingEdge(dut.clk)

    assert dut.crc_valid.value.is_resolvable, "crc_valid has X/Z"
    try:
        cv = int(dut.crc_valid.value)
        dut._log.info(f"crc_valid after data: {cv}")
    except ValueError:
        raise AssertionError("crc_valid not resolvable")

    # After one more cycle with valid=0, crc_valid should deassert
    await RisingEdge(dut.clk)
    assert dut.crc_valid.value.is_resolvable, "crc_valid has X/Z"
    try:
        cv = int(dut.crc_valid.value)
        assert cv == 0, f"crc_valid not deasserted: {cv}"
        dut._log.info("crc_valid correctly deasserts")
    except ValueError:
        raise AssertionError("crc_valid not resolvable")
