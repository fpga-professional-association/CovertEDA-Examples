"""Cocotb testbench for ace blinky_top.

The counter compares against 26'd50_000_000 - 1 (hardcoded) so the LED will
not actually toggle during a short simulation.  We simply verify reset
behaviour and signal integrity.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_led_after_reset(dut):
    """Verify that the LED is 0 after reset and has no X/Z after running."""

    # Start a 10 ns clock (100 MHz)
    setup_clock(dut, "clk", 10)

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # After reset the LED should be 0
    await RisingEdge(dut.clk)
    led_val = dut.led.value
    dut._log.info(f"LED value after reset: {int(led_val)}")
    assert int(led_val) == 0, f"Expected LED == 0 after reset, got {int(led_val)}"

    # Run for 100 more clock cycles
    await ClockCycles(dut.clk, 100)

    # Verify LED has no X/Z (value should be resolvable to an integer)
    final_led = dut.led.value
    assert not final_led.is_resolvable or int(final_led) in (0, 1), (
        f"LED has unexpected value after 100 cycles: {final_led}"
    )
    assert final_led.is_resolvable, f"LED contains X/Z after 100 cycles: {final_led}"
    dut._log.info(f"LED value after 100 cycles: {int(final_led)}")
