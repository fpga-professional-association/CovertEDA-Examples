"""Cocotb testbench for quartus blinky_top (hardcoded counter values)."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_led_after_reset(dut):
    """Verify LEDs are 0 after reset and counters increment without X/Z."""

    # Start a 20 ns clock (50 MHz)
    setup_clock(dut, "clk_50m", 20)

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # After reset, all LEDs should be off
    await RisingEdge(dut.clk_50m)
    led_val = int(dut.led.value)
    dut._log.info(f"LED value after reset: {led_val:#06b}")
    assert led_val == 0, f"Expected led==0 after reset, got {led_val:#06b}"

    # Run for 100 clock cycles -- counters are huge so LEDs stay 0,
    # but we verify the design doesn't crash and outputs stay valid.
    await ClockCycles(dut.clk_50m, 100)

    final_led = int(dut.led.value)
    dut._log.info(f"LED value after 100 cycles: {final_led:#06b}")

    # Verify no X or Z on led by checking that the value resolves to an integer.
    # cocotb raises an exception if the value contains X/Z when calling int(),
    # so reaching this point already confirms no X/Z.  Do an explicit range check.
    assert 0 <= final_led <= 0xF, (
        f"LED value {final_led} is out of range, possible X/Z"
    )

    # Verify counters are incrementing by checking internal signals
    cnt0 = int(dut.div_counter0.value)
    dut._log.info(f"div_counter0 after 100 cycles: {cnt0}")
    assert cnt0 > 0, "Counter0 should have incremented from 0"
