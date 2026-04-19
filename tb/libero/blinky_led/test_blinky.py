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


@cocotb.test()
async def test_led_zero_after_reset(dut):
    """Verify led==0 immediately after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await RisingEdge(dut.clk)
    led_val = dut.led.value
    if not led_val.is_resolvable:
        assert False, f"LED is X/Z after reset: {led_val}"
    assert int(led_val) == 0, f"Expected led==0 after reset, got {int(led_val)}"
    dut._log.info("LED is 0 after reset as expected")


@cocotb.test()
async def test_led_resolvable_500_cycles(dut):
    """Run 500 cycles, check every 50 that led is resolvable."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for i in range(10):
        await ClockCycles(dut.clk, 50)
        led_val = dut.led.value
        if not led_val.is_resolvable:
            assert False, f"LED has X/Z at cycle {(i + 1) * 50}: {led_val}"
        dut._log.info(f"Cycle {(i + 1) * 50}: led={int(led_val)}, resolvable")

    dut._log.info("LED was resolvable at every 50-cycle checkpoint over 500 cycles")


@cocotb.test()
async def test_multiple_resets(dut):
    """Apply 3 resets and verify led==0 after each."""
    setup_clock(dut, "clk", 20)

    for reset_num in range(3):
        await reset_dut(dut, "rst_n", active_low=True, cycles=5)
        await RisingEdge(dut.clk)

        led_val = dut.led.value
        if not led_val.is_resolvable:
            assert False, f"LED is X/Z after reset #{reset_num + 1}: {led_val}"
        assert int(led_val) == 0, (
            f"Expected led==0 after reset #{reset_num + 1}, got {int(led_val)}"
        )
        dut._log.info(f"Reset #{reset_num + 1}: led==0 confirmed")

        # Run some cycles between resets
        await ClockCycles(dut.clk, 50)


@cocotb.test()
async def test_led_binary_value(dut):
    """Verify led is always 0 or 1 (never 2+) over 200 cycles."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(200):
        await RisingEdge(dut.clk)
        led_val = dut.led.value
        if not led_val.is_resolvable:
            assert False, f"LED has X/Z at cycle {cycle}: {led_val}"
        try:
            v = int(led_val)
        except ValueError:
            assert False, f"LED not convertible at cycle {cycle}: {led_val}"
        assert v in (0, 1), f"LED has unexpected value {v} at cycle {cycle}"

    dut._log.info("LED was always 0 or 1 over 200 cycles")


@cocotb.test()
async def test_long_run_1000(dut):
    """Verify no X/Z after 1000 cycles."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk, 1000)

    led_val = dut.led.value
    if not led_val.is_resolvable:
        assert False, f"LED has X/Z after 1000 cycles: {led_val}"
    try:
        final_int = int(led_val)
    except ValueError:
        assert False, f"LED not convertible after 1000 cycles: {led_val}"

    dut._log.info(f"LED value after 1000 cycles: {final_int} (no X/Z)")


@cocotb.test()
async def test_reset_hold_extended(dut):
    """Hold reset for 50 cycles and verify clean state."""
    setup_clock(dut, "clk", 20)

    # Hold reset for 50 cycles (much longer than normal)
    await reset_dut(dut, "rst_n", active_low=True, cycles=50)

    await RisingEdge(dut.clk)
    led_val = dut.led.value
    if not led_val.is_resolvable:
        assert False, f"LED has X/Z after extended reset: {led_val}"
    assert int(led_val) == 0, f"Expected led==0 after extended reset, got {int(led_val)}"

    # Run a few cycles to confirm clean operation
    await ClockCycles(dut.clk, 20)
    led_val = dut.led.value
    if not led_val.is_resolvable:
        assert False, f"LED has X/Z after post-reset run: {led_val}"
    dut._log.info(f"Extended reset: led={int(led_val)}, clean operation confirmed")


@cocotb.test()
async def test_clock_10ns(dut):
    """Use 10ns clock period and verify led is clean over 200 cycles."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk, 200)

    led_val = dut.led.value
    if not led_val.is_resolvable:
        assert False, f"LED has X/Z with 10ns clock: {led_val}"
    try:
        final_int = int(led_val)
    except ValueError:
        assert False, f"LED not convertible with 10ns clock: {led_val}"

    dut._log.info(f"LED with 10ns clock after 200 cycles: {final_int}")


@cocotb.test()
async def test_led_stability(dut):
    """Verify led stays at 0 when counter threshold is too large to reach."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Run for 300 cycles -- counter threshold is 25M, so led won't toggle
    led_values = []
    for _ in range(300):
        await RisingEdge(dut.clk)
        led_val = dut.led.value
        if not led_val.is_resolvable:
            assert False, f"LED has X/Z during stability test: {led_val}"
        try:
            led_values.append(int(led_val))
        except ValueError:
            assert False, f"LED not convertible during stability test: {led_val}"

    # Since 300 cycles << 25M threshold, led should remain at 0
    assert all(v == 0 for v in led_values), (
        "LED toggled unexpectedly within 300 cycles (threshold is 25M)"
    )
    dut._log.info("LED stayed at 0 for 300 cycles as expected (counter threshold not reached)")


@cocotb.test()
async def test_reset_during_run(dut):
    """Run 200 cycles, apply reset, verify recovery."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Run for 200 cycles
    await ClockCycles(dut.clk, 200)

    # Apply a mid-run reset
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await RisingEdge(dut.clk)
    led_val = dut.led.value
    if not led_val.is_resolvable:
        assert False, f"LED has X/Z after mid-run reset: {led_val}"
    assert int(led_val) == 0, f"Expected led==0 after mid-run reset, got {int(led_val)}"

    # Run 50 more cycles to verify clean operation
    await ClockCycles(dut.clk, 50)
    led_val = dut.led.value
    if not led_val.is_resolvable:
        assert False, f"LED has X/Z after recovery: {led_val}"
    try:
        final_int = int(led_val)
    except ValueError:
        assert False, f"LED not convertible after recovery: {led_val}"

    dut._log.info(f"Mid-run reset recovery: led={final_int}, clean operation")
