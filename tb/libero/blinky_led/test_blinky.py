"""Cocotb testbench for libero blinky_top.

The counter compares against a hardcoded 25_000_000 - 1, so we cannot
override it for fast simulation.  We simply verify the reset state and
that the design runs cleanly for a number of cycles without X/Z on the
LED output.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state_and_clean_run(dut):
    """Verify led==0 after reset and no X/Z after 100 clock cycles."""

    # Start a 20 ns clock (50 MHz)
    setup_clock(dut, "clk", 20)

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Check LED is 0 after reset
    await RisingEdge(dut.clk)
    led_val = dut.led.value
    dut._log.info(f"LED value after reset: {int(led_val)}")
    assert int(led_val) == 0, f"Expected led==0 after reset, got {int(led_val)}"

    # Run for 100 clock cycles
    await ClockCycles(dut.clk, 100)

    # Verify LED has no X/Z (the value should be resolvable to an integer)
    final_led = dut.led.value
    try:
        final_int = int(final_led)
    except ValueError:
        assert False, f"LED contains X/Z after 100 cycles: {final_led}"

    dut._log.info(f"LED value after 100 cycles: {final_int} (no X/Z)")
