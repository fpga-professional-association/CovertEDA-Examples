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


@cocotb.test()
async def test_led_zero_sync_reset(dut):
    """After synchronous reset, led should be 0."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    # Synchronous reset needs a few extra clock edges
    await ClockCycles(dut.clk, 5)
    await RisingEdge(dut.clk)

    led_val = dut.led.value
    assert led_val.is_resolvable, f"LED has X/Z after sync reset: {led_val}"
    try:
        assert int(led_val) == 0, f"Expected LED==0 after sync reset, got {int(led_val)}"
    except ValueError:
        assert False, f"LED not convertible after sync reset: {led_val}"
    dut._log.info("LED==0 after synchronous reset -- PASS")


@cocotb.test()
async def test_led_binary(dut):
    """Run 500 cycles and verify led is always 0 or 1."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 3)

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
    setup_clock(dut, "clk", CLK_PERIOD_NS)

    for attempt in range(3):
        await reset_dut(dut, "rst_n", active_low=True, cycles=5)
        await ClockCycles(dut.clk, 5)
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
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 3)

    for cycle in range(1000):
        await RisingEdge(dut.clk)
        val = dut.led.value
        if not val.is_resolvable:
            assert False, f"LED has X/Z at cycle {cycle}: {val}"
    dut._log.info("No X/Z on LED for 1000 cycles -- PASS")


@cocotb.test()
async def test_reset_hold(dut):
    """Hold reset for 20 cycles and verify clean release."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await reset_dut(dut, "rst_n", active_low=True, cycles=20)
    await ClockCycles(dut.clk, 5)
    await RisingEdge(dut.clk)

    led_val = dut.led.value
    assert led_val.is_resolvable, f"LED has X/Z after 20-cycle reset: {led_val}"
    try:
        assert int(led_val) == 0, f"LED not 0 after long reset: {int(led_val)}"
    except ValueError:
        assert False, f"LED not convertible after long reset: {led_val}"
    dut._log.info("20-cycle reset hold clean -- PASS")


@cocotb.test()
async def test_different_clock(dut):
    """Use a 40ns clock and verify led stays valid."""
    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 5)

    for cycle in range(200):
        await RisingEdge(dut.clk)
        val = dut.led.value
        if not val.is_resolvable:
            assert False, f"LED has X/Z at cycle {cycle} with 40ns clock: {val}"
    dut._log.info("40ns clock: LED clean for 200 cycles -- PASS")


@cocotb.test()
async def test_reset_mid_run(dut):
    """Reset at cycle 300 and verify clean recovery."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 3)

    # Run 300 cycles
    await ClockCycles(dut.clk, 300)

    # Assert reset mid-run
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 5)
    await RisingEdge(dut.clk)

    led_val = dut.led.value
    assert led_val.is_resolvable, f"LED has X/Z after mid-run reset: {led_val}"
    try:
        assert int(led_val) == 0, f"LED not 0 after mid-run reset: {int(led_val)}"
    except ValueError:
        assert False, f"LED not convertible after mid-run reset: {led_val}"

    await ClockCycles(dut.clk, 50)
    final = dut.led.value
    assert final.is_resolvable, f"LED has X/Z after recovery: {final}"
    dut._log.info("Mid-run reset at cycle 300 and recovery clean -- PASS")


@cocotb.test()
async def test_led_check_every_50(dut):
    """Sample led every 50 cycles for 500 cycles, ensure always resolvable."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 3)

    for i in range(10):
        await ClockCycles(dut.clk, 50)
        val = dut.led.value
        assert val.is_resolvable, f"LED has X/Z at sample {i} (cycle {(i+1)*50}): {val}"
        try:
            assert int(val) in (0, 1), f"LED not binary at sample {i}: {int(val)}"
        except ValueError:
            assert False, f"LED not convertible at sample {i}: {val}"
    dut._log.info("LED resolvable at every 50-cycle sample for 500 cycles -- PASS")


@cocotb.test()
async def test_no_x_at_any_point(dut):
    """Continuous monitoring for X/Z on led over 500 cycles."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 3)

    x_count = 0
    for cycle in range(500):
        await RisingEdge(dut.clk)
        val = dut.led.value
        if not val.is_resolvable:
            x_count += 1
            if x_count > 5:
                assert False, f"LED has persistent X/Z (count={x_count}) at cycle {cycle}: {val}"

    assert x_count == 0, f"LED had X/Z on {x_count} cycles out of 500"
    dut._log.info(f"No X/Z detected in 500 continuous cycles -- PASS")
