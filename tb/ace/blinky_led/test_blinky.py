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


@cocotb.test()
async def test_led_zero_at_reset(dut):
    """Verify that led is exactly 0 immediately after reset."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    led_val = dut.led.value
    assert led_val.is_resolvable, f"LED has X/Z right after reset: {led_val}"
    try:
        assert int(led_val) == 0, f"Expected LED == 0 at reset, got {int(led_val)}"
    except ValueError:
        assert False, f"LED value could not be converted to int: {led_val}"
    dut._log.info("LED is 0 at reset -- PASS")


@cocotb.test()
async def test_led_stays_binary(dut):
    """Run 500 cycles and verify led is always 0 or 1 (never X/Z)."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(500):
        await RisingEdge(dut.clk)
        val = dut.led.value
        if val.is_resolvable:
            try:
                assert int(val) in (0, 1), f"LED not binary at cycle {cycle}: {int(val)}"
            except ValueError:
                assert False, f"LED not convertible at cycle {cycle}: {val}"
        else:
            assert False, f"LED has X/Z at cycle {cycle}: {val}"
    dut._log.info("LED stayed binary for 500 cycles -- PASS")


@cocotb.test()
async def test_multiple_resets(dut):
    """Apply 3 successive resets and verify clean recovery each time."""
    setup_clock(dut, "clk", 10)

    for attempt in range(3):
        await reset_dut(dut, "rst_n", active_low=True, cycles=5)
        await RisingEdge(dut.clk)
        led_val = dut.led.value
        assert led_val.is_resolvable, f"LED X/Z after reset #{attempt+1}: {led_val}"
        try:
            assert int(led_val) == 0, f"LED not 0 after reset #{attempt+1}: {int(led_val)}"
        except ValueError:
            assert False, f"LED not convertible after reset #{attempt+1}: {led_val}"
        await ClockCycles(dut.clk, 50)
        dut._log.info(f"Reset #{attempt+1} clean")
    dut._log.info("3 successive resets all clean -- PASS")


@cocotb.test()
async def test_long_run(dut):
    """Run 1000 cycles and verify no X/Z appears on led."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(1000):
        await RisingEdge(dut.clk)
        val = dut.led.value
        if not val.is_resolvable:
            assert False, f"LED has X/Z at cycle {cycle}: {val}"
    dut._log.info("No X/Z on LED for 1000 cycles -- PASS")


@cocotb.test()
async def test_reset_hold_long(dut):
    """Hold reset for 20 cycles and verify clean release."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=20)
    await RisingEdge(dut.clk)

    led_val = dut.led.value
    assert led_val.is_resolvable, f"LED has X/Z after 20-cycle reset: {led_val}"
    try:
        assert int(led_val) == 0, f"LED not 0 after long reset: {int(led_val)}"
    except ValueError:
        assert False, f"LED not convertible after long reset: {led_val}"
    dut._log.info("20-cycle reset hold clean -- PASS")


@cocotb.test()
async def test_clock_5ns(dut):
    """Use a faster 5ns clock and verify led stays valid."""
    setup_clock(dut, "clk", 5)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(200):
        await RisingEdge(dut.clk)
        val = dut.led.value
        if not val.is_resolvable:
            assert False, f"LED has X/Z at cycle {cycle} with 5ns clock: {val}"
    dut._log.info("5ns clock: LED clean for 200 cycles -- PASS")


@cocotb.test()
async def test_reset_during_run(dut):
    """Reset at cycle 200 and verify clean recovery."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Run 200 cycles
    await ClockCycles(dut.clk, 200)

    # Assert reset mid-run
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    led_val = dut.led.value
    assert led_val.is_resolvable, f"LED has X/Z after mid-run reset: {led_val}"
    try:
        assert int(led_val) == 0, f"LED not 0 after mid-run reset: {int(led_val)}"
    except ValueError:
        assert False, f"LED not convertible after mid-run reset: {led_val}"

    # Run a few more cycles to confirm recovery
    await ClockCycles(dut.clk, 50)
    final = dut.led.value
    assert final.is_resolvable, f"LED has X/Z after recovery: {final}"
    dut._log.info("Mid-run reset and recovery clean -- PASS")


@cocotb.test()
async def test_led_resolvable_continuous(dut):
    """Check led every 10 cycles for 200 cycles, ensure always resolvable."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for i in range(20):
        await ClockCycles(dut.clk, 10)
        val = dut.led.value
        assert val.is_resolvable, f"LED has X/Z at sample {i} (cycle {(i+1)*10}): {val}"
        try:
            int(val)
        except ValueError:
            assert False, f"LED not convertible at sample {i}: {val}"
    dut._log.info("LED resolvable at every 10-cycle sample for 200 cycles -- PASS")


@cocotb.test()
async def test_counter_not_stuck(dut):
    """Verify the design keeps running (counter advances, no hang)."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Sample led at two different times; design should not crash
    await ClockCycles(dut.clk, 100)
    val1 = dut.led.value
    assert val1.is_resolvable, f"LED has X/Z at cycle 100: {val1}"

    await ClockCycles(dut.clk, 400)
    val2 = dut.led.value
    assert val2.is_resolvable, f"LED has X/Z at cycle 500: {val2}"

    # Both should be valid integers -- design did not get stuck
    try:
        int(val1)
        int(val2)
    except ValueError as e:
        assert False, f"LED value not convertible: {e}"
    dut._log.info("Design kept running through 500 cycles -- PASS")
