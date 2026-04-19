"""Cocotb testbench for oss blinky_top.

The counter compares against 24'd12_000_000 (hardcoded) so the LED will
not actually toggle during a short simulation.  We verify reset behaviour
and signal integrity.  Note: this design uses synchronous reset
(always @(posedge clk) with if (!rst_n)).
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles, FallingEdge
from cocotb_helpers import setup_clock, reset_dut


# ~12 MHz iCE40 clock -> 83 ns period
CLK_PERIOD_NS = 83


@cocotb.test()
async def test_led_after_reset(dut):
    """Verify that the LED is 0 after reset and has no X/Z after running."""

    # Start a 83 ns clock (~12 MHz, iCE40 frequency)
    setup_clock(dut, "clk", CLK_PERIOD_NS)

    # Synchronous reset requires clock edges, so use enough cycles
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Allow a few clock edges for the synchronous reset to take effect
    await ClockCycles(dut.clk, 3)

    # After reset the LED should be 0
    await RisingEdge(dut.clk)
    led_val = dut.led.value
    dut._log.info(f"LED value after reset: {int(led_val)}")
    assert int(led_val) == 0, f"Expected LED == 0 after reset, got {int(led_val)}"

    # Run for 100 more clock cycles
    await ClockCycles(dut.clk, 100)

    # Verify LED has no X/Z (value should be resolvable to an integer)
    final_led = dut.led.value
    assert final_led.is_resolvable, f"LED contains X/Z after 100 cycles: {final_led}"
    assert int(final_led) in (0, 1), (
        f"LED has unexpected value after 100 cycles: {final_led}"
    )
    dut._log.info(f"LED value after 100 cycles: {int(final_led)}")
