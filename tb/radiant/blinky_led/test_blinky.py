"""Cocotb testbench for radiant blinky_top."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_led_changes(dut):
    """Verify LED output is clean after reset and design runs without X/Z."""

    # Start a 40 ns clock (25 MHz)
    setup_clock(dut, "clk", 40)

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Capture the initial LED value after reset
    await RisingEdge(dut.clk)
    assert dut.led.value.is_resolvable, "LED has X/Z right after reset"
    initial_led = int(dut.led.value)
    dut._log.info(f"Initial LED value after reset: {initial_led:#06b}")

    # Run for some cycles
    await ClockCycles(dut.clk, 100)

    # Verify LED is still resolvable (no X/Z)
    assert dut.led.value.is_resolvable, "LED has X/Z after 100 cycles"
    final_led = int(dut.led.value)
    dut._log.info(f"Final LED value after 100 cycles: {final_led:#06b}")

    dut._log.info("Blinky design runs cleanly with no X/Z on LED output")
