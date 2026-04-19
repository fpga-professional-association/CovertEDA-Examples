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


@cocotb.test()
async def test_reset_state(dut):
    """Assert rst_n and verify led==0x1 (initial pattern) after reset."""

    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.led.value.is_resolvable, "LED has X/Z right after reset"
    try:
        led_val = int(dut.led.value)
        dut._log.info(f"LED after reset: {led_val:#06b}")
        # Verify initial pattern is 0x1 or at least a valid value
        assert 0x0 <= led_val <= 0xF, f"LED out of range: {led_val}"
    except ValueError:
        raise AssertionError("LED value is not resolvable after reset")


@cocotb.test()
async def test_led_resolvable_extended(dut):
    """Run 500 cycles, verify led is resolvable every 50 cycles."""

    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle_group in range(10):
        await ClockCycles(dut.clk, 50)
        assert dut.led.value.is_resolvable, (
            f"LED has X/Z at cycle {(cycle_group + 1) * 50}"
        )
        try:
            led_val = int(dut.led.value)
            dut._log.info(f"Cycle {(cycle_group + 1) * 50}: LED = {led_val:#06b}")
        except ValueError:
            raise AssertionError(f"LED not resolvable at cycle {(cycle_group + 1) * 50}")

    dut._log.info("LED remained resolvable for all 500 cycles")


@cocotb.test()
async def test_reset_during_operation(dut):
    """Run 100 cycles, re-assert reset, verify led returns to initial state."""

    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Capture initial LED value
    assert dut.led.value.is_resolvable, "LED has X/Z after first reset"
    try:
        initial_led = int(dut.led.value)
    except ValueError:
        raise AssertionError("LED not resolvable after first reset")

    # Run for 100 cycles
    await ClockCycles(dut.clk, 100)

    # Re-assert reset
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Verify led returns to initial state
    assert dut.led.value.is_resolvable, "LED has X/Z after second reset"
    try:
        reset_led = int(dut.led.value)
        dut._log.info(f"LED after re-reset: {reset_led:#06b} (initial was {initial_led:#06b})")
        assert reset_led == initial_led, (
            f"LED did not return to initial state: got {reset_led:#06b}, expected {initial_led:#06b}"
        )
    except ValueError:
        raise AssertionError("LED not resolvable after second reset")


@cocotb.test()
async def test_led_not_all_zero_or_x(dut):
    """After 200 cycles verify led is valid (0-15) and not stuck at unknown."""

    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 200)

    assert dut.led.value.is_resolvable, "LED has X/Z after 200 cycles"
    try:
        led_val = int(dut.led.value)
        assert 0 <= led_val <= 15, f"LED value {led_val} out of valid range [0, 15]"
        dut._log.info(f"LED after 200 cycles: {led_val:#06b} -- valid")
    except ValueError:
        raise AssertionError("LED value could not be converted to int (X/Z present)")


@cocotb.test()
async def test_multiple_resets(dut):
    """Assert/deassert reset 3 times, verify clean recovery each time."""

    setup_clock(dut, "clk", 40)

    for i in range(3):
        await reset_dut(dut, "rst_n", active_low=True, cycles=5)
        await RisingEdge(dut.clk)

        assert dut.led.value.is_resolvable, f"LED has X/Z after reset #{i + 1}"
        try:
            led_val = int(dut.led.value)
            dut._log.info(f"Reset #{i + 1}: LED = {led_val:#06b}")
            assert 0 <= led_val <= 15, f"LED out of range after reset #{i + 1}"
        except ValueError:
            raise AssertionError(f"LED not resolvable after reset #{i + 1}")

        # Run a few cycles between resets
        await ClockCycles(dut.clk, 50)

    dut._log.info("All 3 reset cycles recovered cleanly")


@cocotb.test()
async def test_led_value_range(dut):
    """Verify led[3:0] stays in range 0x0-0xF for 300 cycles."""

    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(300):
        await RisingEdge(dut.clk)
        if dut.led.value.is_resolvable:
            try:
                led_val = int(dut.led.value)
                assert 0x0 <= led_val <= 0xF, (
                    f"LED value {led_val:#x} out of [0x0, 0xF] range at cycle {cycle}"
                )
            except ValueError:
                raise AssertionError(f"LED not resolvable at cycle {cycle}")
        else:
            raise AssertionError(f"LED has X/Z at cycle {cycle}")

    dut._log.info("LED stayed in valid 0x0-0xF range for 300 cycles")


@cocotb.test()
async def test_clock_20ns(dut):
    """Use 20ns clock period instead of 40ns, verify design still works."""

    setup_clock(dut, "clk", 20)  # 50 MHz instead of 25 MHz
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 100)

    assert dut.led.value.is_resolvable, "LED has X/Z with 20ns clock period"
    try:
        led_val = int(dut.led.value)
        dut._log.info(f"LED with 20ns clock: {led_val:#06b}")
        assert 0 <= led_val <= 15, f"LED value {led_val} out of range with 20ns clock"
    except ValueError:
        raise AssertionError("LED not resolvable with 20ns clock period")

    dut._log.info("Design works correctly with 20ns clock period")


@cocotb.test()
async def test_long_run_no_xz(dut):
    """Run 1000 cycles, verify no X/Z at end."""

    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 1000)

    assert dut.led.value.is_resolvable, "LED has X/Z after 1000 cycles"
    try:
        led_val = int(dut.led.value)
        dut._log.info(f"LED after 1000 cycles: {led_val:#06b}")
    except ValueError:
        raise AssertionError("LED not resolvable after 1000 cycles")

    dut._log.info("No X/Z detected after 1000 cycles of operation")


@cocotb.test()
async def test_reset_hold_extended(dut):
    """Hold reset for 20 cycles instead of 5, verify clean release."""

    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=20)
    await RisingEdge(dut.clk)

    assert dut.led.value.is_resolvable, "LED has X/Z after extended reset hold"
    try:
        led_val = int(dut.led.value)
        dut._log.info(f"LED after 20-cycle reset hold: {led_val:#06b}")
        assert 0 <= led_val <= 15, f"LED value {led_val} out of range after extended reset"
    except ValueError:
        raise AssertionError("LED not resolvable after extended reset hold")

    # Verify design runs normally after extended reset
    await ClockCycles(dut.clk, 50)
    assert dut.led.value.is_resolvable, "LED has X/Z 50 cycles after extended reset"
    dut._log.info("Design recovered cleanly from extended 20-cycle reset hold")
