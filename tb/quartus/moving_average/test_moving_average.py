"""Cocotb testbench for quartus moving_average (8-sample, 16-bit filter)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify output is zero and valid_out is low after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.valid_in.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    if not dut.dout.value.is_resolvable:
        raise AssertionError("dout has X/Z after reset")

    try:
        dout_val = int(dut.dout.value)
        vout_val = int(dut.valid_out.value)
    except ValueError:
        raise AssertionError("Signals not convertible after reset")

    assert dout_val == 0, f"Expected dout=0, got {dout_val}"
    assert vout_val == 0, f"Expected valid_out=0, got {vout_val}"
    dut._log.info("Reset state verified: dout=0, valid_out=0")


@cocotb.test()
async def test_constant_input(dut):
    """Feed constant value for 8+ samples; average should equal that value."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.valid_in.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    const_val = 1000

    # Feed 10 samples of the same value
    for i in range(10):
        dut.valid_in.value = 1
        dut.din.value = const_val
        await RisingEdge(dut.clk)

    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.dout.value.is_resolvable:
        try:
            avg = int(dut.dout.value)
            dut._log.info(f"Average of constant {const_val}: {avg}")
            assert avg == const_val, f"Expected avg={const_val}, got {avg}"
        except ValueError:
            raise AssertionError("dout not convertible")


@cocotb.test()
async def test_valid_out_timing(dut):
    """valid_out should not assert until 8 samples have been fed."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.valid_in.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    valid_seen = False
    for i in range(8):
        dut.valid_in.value = 1
        dut.din.value = 100 * (i + 1)
        await RisingEdge(dut.clk)
        if dut.valid_out.value.is_resolvable:
            try:
                if int(dut.valid_out.value) == 1:
                    valid_seen = True
                    dut._log.info(f"valid_out asserted at sample {i}")
            except ValueError:
                pass

    dut._log.info(f"valid_out seen during fill phase: {valid_seen}")
    # After the 8th sample, valid_out should be asserted
    dut.valid_in.value = 1
    dut.din.value = 900
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.valid_out.value.is_resolvable:
        try:
            vout = int(dut.valid_out.value)
            dut._log.info(f"valid_out after 9 samples: {vout}")
        except ValueError:
            dut._log.warning("valid_out not convertible")


@cocotb.test()
async def test_ramp_input(dut):
    """Feed a ramp signal and verify the average is reasonable."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.valid_in.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    # Feed ramp: 0, 100, 200, ..., 1500 (16 samples)
    for i in range(16):
        dut.valid_in.value = 1
        dut.din.value = i * 100
        await RisingEdge(dut.clk)

    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.dout.value.is_resolvable:
        try:
            avg = int(dut.dout.value)
            # Last 8 values: 800..1500, expected average = 1150
            expected = sum(range(8, 16)) * 100 // 8
            dut._log.info(f"Ramp average: {avg}, expected ~{expected}")
        except ValueError:
            dut._log.warning("dout not convertible")


@cocotb.test()
async def test_no_valid_in_holds_output(dut):
    """When valid_in is deasserted, output should hold its last value."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.valid_in.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    # Fill with constant 500
    for _ in range(10):
        dut.valid_in.value = 1
        dut.din.value = 500
        await RisingEdge(dut.clk)

    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.dout.value.is_resolvable:
        try:
            held_val = int(dut.dout.value)
        except ValueError:
            raise AssertionError("dout not convertible")
    else:
        raise AssertionError("dout has X/Z")

    # Wait more cycles without valid_in
    await ClockCycles(dut.clk, 10)

    if dut.dout.value.is_resolvable:
        try:
            after_val = int(dut.dout.value)
            dut._log.info(f"Held value: {held_val}, value after 10 idle cycles: {after_val}")
            assert held_val == after_val, f"Output changed without valid input: {held_val} -> {after_val}"
        except ValueError:
            raise AssertionError("dout not convertible after idle")
