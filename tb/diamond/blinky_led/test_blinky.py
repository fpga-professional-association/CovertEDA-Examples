"""Cocotb testbench for diamond blinky_top – basic reset and liveness check.

The design uses a localparam PRESCALE_VAL = 25_000_000 which cannot be
overridden via Verilog parameter override (-P).  Instead we verify the
post-reset state and confirm the design is alive (no X/Z) after 100 cycles.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, led_out should be 4'b0001."""

    # Start a 40 ns clock (25 MHz)
    setup_clock(dut, "clk", 40)

    # Reset (active-low reset_n)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    await RisingEdge(dut.clk)
    led_val = int(dut.led_out.value)
    dut._log.info(f"LED value after reset: {led_val:#06b}")

    assert led_val == 0b0001, (
        f"Expected led_out == 4'b0001 after reset, got {led_val:#06b}"
    )


@cocotb.test()
async def test_no_xz_after_100_cycles(dut):
    """Run 100 clock cycles and verify led_out contains no X or Z values."""

    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk, 100)

    led_val = dut.led_out.value
    dut._log.info(f"LED value after 100 cycles: {int(led_val):#06b}")

    # Check for X/Z by verifying the value resolves to an integer
    try:
        resolved = int(led_val)
    except ValueError:
        assert False, f"led_out contains X or Z after 100 cycles: {led_val}"

    assert resolved >= 0, f"led_out has unexpected value: {resolved}"
    dut._log.info("Design is alive -- no X/Z detected on led_out")
