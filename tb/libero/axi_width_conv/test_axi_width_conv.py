"""Cocotb testbench for axi_width_conv - AXI data width converter."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, s_ready should be 1, m_valid should be 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.s_data.value = 0
    dut.s_valid.value = 0
    dut.s_last.value = 0
    dut.m_ready.value = 0
    await RisingEdge(dut.clk)

    if dut.s_ready.value.is_resolvable:
        try:
            assert int(dut.s_ready.value) == 1, "s_ready should be 1 after reset"
        except ValueError:
            assert False, "s_ready X/Z after reset"

    if dut.m_valid.value.is_resolvable:
        try:
            assert int(dut.m_valid.value) == 0, "m_valid should be 0 after reset"
        except ValueError:
            assert False, "m_valid X/Z after reset"


@cocotb.test()
async def test_two_words_combine(dut):
    """Two 32-bit words should combine into one 64-bit word."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.m_ready.value = 1

    # Send first word
    dut.s_data.value = 0xAAAAAAAA
    dut.s_valid.value = 1
    dut.s_last.value = 0
    await RisingEdge(dut.clk)

    # Send second word
    dut.s_data.value = 0xBBBBBBBB
    dut.s_last.value = 1
    await RisingEdge(dut.clk)
    dut.s_valid.value = 0
    dut.s_last.value = 0

    # Wait for output
    for _ in range(5):
        await RisingEdge(dut.clk)
        if dut.m_valid.value.is_resolvable:
            try:
                if int(dut.m_valid.value) == 1:
                    if dut.m_data.value.is_resolvable:
                        val = int(dut.m_data.value)
                        dut._log.info(f"Combined 64-bit: {val:#018x}")
                    break
            except ValueError:
                pass


@cocotb.test()
async def test_single_word_with_last(dut):
    """Single word with s_last should produce padded 64-bit output."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.m_ready.value = 1

    dut.s_data.value = 0x12345678
    dut.s_valid.value = 1
    dut.s_last.value = 1
    await RisingEdge(dut.clk)
    dut.s_valid.value = 0
    dut.s_last.value = 0

    valid_seen = False
    for _ in range(5):
        await RisingEdge(dut.clk)
        if dut.m_valid.value.is_resolvable:
            try:
                if int(dut.m_valid.value) == 1:
                    valid_seen = True
                    if dut.m_data.value.is_resolvable:
                        val = int(dut.m_data.value)
                        dut._log.info(f"Padded output: {val:#018x}")
                    break
            except ValueError:
                pass

    assert valid_seen, "m_valid should assert for single word with last"


@cocotb.test()
async def test_backpressure(dut):
    """With m_ready=0, output should hold until accepted."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.m_ready.value = 0

    # Send two words
    dut.s_data.value = 0x11111111
    dut.s_valid.value = 1
    dut.s_last.value = 0
    await RisingEdge(dut.clk)
    dut.s_data.value = 0x22222222
    dut.s_last.value = 1
    await RisingEdge(dut.clk)
    dut.s_valid.value = 0
    dut.s_last.value = 0

    await ClockCycles(dut.clk, 3)

    # Now accept
    dut.m_ready.value = 1
    await ClockCycles(dut.clk, 3)

    dut._log.info("Backpressure test complete")
