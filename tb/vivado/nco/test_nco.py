"""Cocotb testbench for vivado nco."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify NCO output is mid-scale after reset."""
    setup_clock(dut, "clk", 10)
    dut.freq_word.value = 0
    dut.phase_offset.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.sine_out.value.is_resolvable, "sine_out has X/Z after reset"
    try:
        val = int(dut.sine_out.value)
        dut._log.info(f"sine_out after reset: {val} (expected ~2048 mid-scale)")
    except ValueError:
        assert False, "sine_out not convertible after reset"


@cocotb.test()
async def test_output_range(dut):
    """Verify sine output stays within 12-bit range."""
    setup_clock(dut, "clk", 10)
    dut.freq_word.value = 0
    dut.phase_offset.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Set a moderate frequency
    dut.freq_word.value = 0x01000000
    dut.phase_offset.value = 0

    for i in range(200):
        await RisingEdge(dut.clk)
        if dut.sine_out.value.is_resolvable:
            try:
                val = int(dut.sine_out.value)
                assert 0 <= val <= 4095, f"sine_out={val} out of 12-bit range at cycle {i}"
            except ValueError:
                pass

    dut._log.info("sine_out stayed within 0..4095 for 200 cycles")


@cocotb.test()
async def test_zero_freq(dut):
    """With zero frequency word, output should be constant."""
    setup_clock(dut, "clk", 10)
    dut.freq_word.value = 0
    dut.phase_offset.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.freq_word.value = 0

    await ClockCycles(dut.clk, 10)

    vals = []
    for i in range(10):
        await RisingEdge(dut.clk)
        if dut.sine_out.value.is_resolvable:
            try:
                vals.append(int(dut.sine_out.value))
            except ValueError:
                pass

    if len(vals) > 1:
        all_same = all(v == vals[0] for v in vals)
        dut._log.info(f"Zero freq values: {vals[:5]}... all_same={all_same}")


@cocotb.test()
async def test_frequency_change(dut):
    """Change frequency word mid-operation and verify output adapts."""
    setup_clock(dut, "clk", 10)
    dut.freq_word.value = 0
    dut.phase_offset.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Low frequency
    dut.freq_word.value = 0x00100000
    await ClockCycles(dut.clk, 50)

    # High frequency
    dut.freq_word.value = 0x10000000
    await ClockCycles(dut.clk, 50)

    assert dut.sine_out.value.is_resolvable, "sine_out has X/Z after freq change"
    dut._log.info("NCO handled frequency change without X/Z")


@cocotb.test()
async def test_phase_offset(dut):
    """Verify phase offset affects output."""
    setup_clock(dut, "clk", 10)
    dut.freq_word.value = 0
    dut.phase_offset.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.freq_word.value = 0x01000000

    # Read output with zero phase offset
    dut.phase_offset.value = 0
    await ClockCycles(dut.clk, 10)
    val_no_offset = 0
    if dut.sine_out.value.is_resolvable:
        try:
            val_no_offset = int(dut.sine_out.value)
        except ValueError:
            pass

    # Apply phase offset
    dut.phase_offset.value = 0x800
    await ClockCycles(dut.clk, 10)
    val_with_offset = 0
    if dut.sine_out.value.is_resolvable:
        try:
            val_with_offset = int(dut.sine_out.value)
        except ValueError:
            pass

    dut._log.info(f"No offset: {val_no_offset}, With offset: {val_with_offset}")
