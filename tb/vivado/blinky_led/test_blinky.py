"""Cocotb testbench for vivado blinky_top."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_led_changes(dut):
    """Verify LED output is clean after reset and design runs without X/Z."""

    # Start a 10 ns clock (100 MHz)
    setup_clock(dut, "clk_in", 10)

    # Drive btn_in to 0 (no buttons pressed)
    dut.btn_in.value = 0

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Capture the initial LED value after reset
    await RisingEdge(dut.clk_in)
    assert dut.led_out.value.is_resolvable, "led_out has X/Z right after reset"
    initial_led = int(dut.led_out.value)
    dut._log.info(f"Initial LED value after reset: {initial_led:#06b}")

    # Run for some cycles
    await ClockCycles(dut.clk_in, 100)

    # Verify LED is still resolvable (no X/Z)
    assert dut.led_out.value.is_resolvable, "led_out has X/Z after 100 cycles"
    final_led = int(dut.led_out.value)
    dut._log.info(f"Final LED value after 100 cycles: {final_led:#06b}")

    dut._log.info("Blinky design runs cleanly with no X/Z on LED output")
