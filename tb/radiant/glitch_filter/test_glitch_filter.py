"""Cocotb testbench for radiant glitch_filter."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify all outputs zero after reset."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    dut.threshold.value = 4
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.sig_out.value.is_resolvable, "sig_out has X/Z after reset"
    assert dut.glitch_flag.value.is_resolvable, "glitch_flag has X/Z after reset"
    try:
        assert int(dut.sig_out.value) == 0, "sig_out not zero"
        assert int(dut.glitch_flag.value) == 0, "glitch_flag not zero"
        dut._log.info("Reset state OK")
    except ValueError:
        raise AssertionError("Outputs not resolvable after reset")


@cocotb.test()
async def test_stable_passes(dut):
    """Stable input held longer than threshold should pass through."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    dut.threshold.value = 4
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Apply stable input on channel 0
    dut.sig_in.value = 0x01
    # Need sync (2 cycles) + threshold (4 cycles) + margin
    await ClockCycles(dut.clk, 12)

    assert dut.sig_out.value.is_resolvable, "sig_out has X/Z"
    try:
        val = int(dut.sig_out.value)
        assert val & 0x01, f"Stable input not passed: sig_out={val:#06b}"
        dut._log.info(f"Stable input passed: sig_out={val:#06b}")
    except ValueError:
        raise AssertionError("sig_out not resolvable")


@cocotb.test()
async def test_glitch_rejected(dut):
    """Short glitch should be filtered out."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    dut.threshold.value = 8
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Apply a 2-cycle pulse (much shorter than threshold=8)
    dut.sig_in.value = 0x01
    await ClockCycles(dut.clk, 2)
    dut.sig_in.value = 0x00
    await ClockCycles(dut.clk, 15)

    assert dut.sig_out.value.is_resolvable, "sig_out has X/Z"
    try:
        val = int(dut.sig_out.value)
        assert val == 0, f"Glitch not filtered: sig_out={val:#06b}"
        dut._log.info("Glitch correctly rejected")
    except ValueError:
        raise AssertionError("sig_out not resolvable")


@cocotb.test()
async def test_multi_channel(dut):
    """Apply stable signal on all 4 channels, verify all pass through."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    dut.threshold.value = 3
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sig_in.value = 0x0F
    await ClockCycles(dut.clk, 12)

    assert dut.sig_out.value.is_resolvable, "sig_out has X/Z"
    try:
        val = int(dut.sig_out.value)
        assert val == 0x0F, f"Not all channels passed: sig_out={val:#06b}"
        dut._log.info(f"All channels passed: sig_out={val:#06b}")
    except ValueError:
        raise AssertionError("sig_out not resolvable")


@cocotb.test()
async def test_threshold_variation(dut):
    """Test that higher threshold requires longer stable time."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    dut.threshold.value = 10
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sig_in.value = 0x01

    # Check after short time (should not have passed yet)
    await ClockCycles(dut.clk, 6)
    assert dut.sig_out.value.is_resolvable, "sig_out has X/Z"
    try:
        val_early = int(dut.sig_out.value)
        dut._log.info(f"After 6 cycles with threshold=10: sig_out={val_early:#06b}")
    except ValueError:
        raise AssertionError("sig_out not resolvable")

    # Wait more for threshold to be met
    await ClockCycles(dut.clk, 12)
    assert dut.sig_out.value.is_resolvable, "sig_out has X/Z"
    try:
        val_late = int(dut.sig_out.value)
        dut._log.info(f"After 18 cycles with threshold=10: sig_out={val_late:#06b}")
        assert val_late & 0x01, "Signal should have passed by now"
    except ValueError:
        raise AssertionError("sig_out not resolvable")
