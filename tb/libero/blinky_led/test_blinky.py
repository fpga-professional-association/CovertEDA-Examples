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


@cocotb.test()
async def test_rapid_reset_toggle(dut):
    """Toggle reset on/off every 2 cycles for 20 iterations, verify no X/Z."""
    setup_clock(dut, "clk", 20)

    for i in range(20):
        dut.rst_n.value = 0
        await ClockCycles(dut.clk, 2)
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 2)

    # After rapid toggling, allow settling
    await ClockCycles(dut.clk, 10)
    led_val = dut.led.value
    if not led_val.is_resolvable:
        assert False, f"LED has X/Z after rapid reset toggling: {led_val}"
    try:
        v = int(led_val)
    except ValueError:
        assert False, f"LED not convertible after rapid reset toggling: {led_val}"
    dut._log.info(f"Rapid reset toggle: led={v}, no X/Z after 20 rapid toggles")


@cocotb.test()
async def test_clock_period_40ns(dut):
    """Use a slower 40ns clock (25 MHz) and verify clean operation."""
    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk, 200)

    led_val = dut.led.value
    if not led_val.is_resolvable:
        assert False, f"LED has X/Z with 40ns clock: {led_val}"
    try:
        final_int = int(led_val)
    except ValueError:
        assert False, f"LED not convertible with 40ns clock: {led_val}"
    assert final_int in (0, 1), f"LED has unexpected value {final_int} with 40ns clock"
    dut._log.info(f"LED with 40ns clock after 200 cycles: {final_int}")


@cocotb.test()
async def test_reset_single_cycle(dut):
    """Apply reset for only 1 cycle, verify design handles minimal reset."""
    setup_clock(dut, "clk", 20)

    await reset_dut(dut, "rst_n", active_low=True, cycles=1)

    await ClockCycles(dut.clk, 10)
    led_val = dut.led.value
    if not led_val.is_resolvable:
        assert False, f"LED has X/Z after 1-cycle reset: {led_val}"
    try:
        v = int(led_val)
    except ValueError:
        assert False, f"LED not convertible after 1-cycle reset: {led_val}"
    assert v in (0, 1), f"LED has unexpected value {v} after 1-cycle reset"
    dut._log.info(f"Single-cycle reset: led={v}, clean operation")


@cocotb.test()
async def test_led_no_glitch_on_reset_release(dut):
    """Sample led on consecutive cycles around reset release, verify no X/Z."""
    setup_clock(dut, "clk", 20)

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)

    # Release reset and sample every cycle for 10 cycles
    dut.rst_n.value = 1
    for cycle in range(10):
        await RisingEdge(dut.clk)
        led_val = dut.led.value
        if not led_val.is_resolvable:
            assert False, f"LED has X/Z at cycle {cycle} after reset release: {led_val}"
        try:
            v = int(led_val)
        except ValueError:
            assert False, f"LED not convertible at cycle {cycle} after reset release: {led_val}"
        dut._log.info(f"Cycle {cycle} post-release: led={v}")

    dut._log.info("No glitch detected around reset release boundary")


@cocotb.test()
async def test_led_constant_during_short_window(dut):
    """Verify led does not toggle within 50 consecutive cycles (counter far from threshold)."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk, 100)

    # Record led for 50 consecutive cycles
    values = []
    for _ in range(50):
        await RisingEdge(dut.clk)
        led_val = dut.led.value
        if not led_val.is_resolvable:
            assert False, f"LED has X/Z during short window: {led_val}"
        try:
            values.append(int(led_val))
        except ValueError:
            assert False, f"LED not convertible during short window: {led_val}"

    # LED should remain constant since 50 cycles << 25M threshold
    assert len(set(values)) == 1, (
        f"LED changed within 50-cycle window (unexpected given 25M threshold): {values}"
    )
    dut._log.info(f"LED constant at {values[0]} for 50 consecutive cycles as expected")


@cocotb.test()
async def test_stress_2000_cycles(dut):
    """Stress test: run 2000 cycles and verify led is always resolvable."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    x_count = 0
    for cycle in range(2000):
        await RisingEdge(dut.clk)
        led_val = dut.led.value
        if not led_val.is_resolvable:
            x_count += 1

    assert x_count == 0, f"LED had X/Z on {x_count} of 2000 cycles"
    dut._log.info("Stress test: 2000 cycles with zero X/Z occurrences")
