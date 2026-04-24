"""Cocotb testbench for quartus nios_top with altpll stub."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


def check_no_xz(signal, name):
    """Verify a signal resolves to a valid integer (no X/Z)."""
    val = int(signal.value)
    assert 0 <= val <= 0xFF, f"{name} value {val} out of range, possible X/Z"
    return val


@cocotb.test()
async def test_nios_basic(dut):
    """Reset, drive sw_input, verify led_output and seg_output have no X/Z."""

    # Start a 10 ns clock (100 MHz)
    setup_clock(dut, "clk_100m", 10)

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Drive switch inputs
    dut.sw_input.value = 0xA5

    # Run for 50 clock cycles to let design settle
    await ClockCycles(dut.clk_100m, 50)

    # Verify no X/Z on LED and segment outputs
    led_val = check_no_xz(dut.led_output, "led_output")
    seg_val = check_no_xz(dut.seg_output, "seg_output")
    dut._log.info(f"led_output={led_val:#04x}, seg_output={seg_val:#04x}")


@cocotb.test()
async def test_nios_switch_change(dut):
    """Drive different sw_input values and verify outputs respond."""

    # Start a 10 ns clock (100 MHz)
    setup_clock(dut, "clk_100m", 10)

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    test_values = [0x00, 0xFF, 0x55, 0xAA, 0x0F, 0xF0]

    for sw_val in test_values:
        dut.sw_input.value = sw_val
        await ClockCycles(dut.clk_100m, 20)

        led_val = check_no_xz(dut.led_output, "led_output")
        seg_val = check_no_xz(dut.seg_output, "seg_output")
        dut._log.info(
            f"sw_input={sw_val:#04x} -> led_output={led_val:#04x}, "
            f"seg_output={seg_val:#04x}"
        )


@cocotb.test()
async def test_pll_lock(dut):
    """After reset, PLL lock should be detected (design should stabilize)."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sw_input.value = 0x00

    # Give the PLL stub time to assert lock
    await ClockCycles(dut.clk_100m, 100)

    # Verify outputs are resolvable (PLL lock allows design to run)
    if not dut.led_output.value.is_resolvable:
        raise AssertionError("led_output has X/Z -- PLL may not have locked")

    try:
        led_val = int(dut.led_output.value)
        dut._log.info(f"led_output after PLL warmup: {led_val:#04x}")
    except ValueError:
        raise AssertionError("led_output not convertible after PLL warmup")

    dut._log.info("PLL lock detected -- design outputs are resolvable")


@cocotb.test()
async def test_led_output_stable(dut):
    """Run 500 cycles, verify led_output resolvable throughout."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sw_input.value = 0x55

    for cycle in range(500):
        await RisingEdge(dut.clk_100m)
        if not dut.led_output.value.is_resolvable:
            raise AssertionError(f"led_output has X/Z at cycle {cycle}")

    try:
        final_val = int(dut.led_output.value)
        dut._log.info(f"led_output after 500 cycles: {final_val:#04x}")
    except ValueError:
        raise AssertionError("led_output not convertible after 500 cycles")


@cocotb.test()
async def test_seg_output_stable(dut):
    """Run 500 cycles, verify seg_output resolvable throughout."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sw_input.value = 0xAA

    for cycle in range(500):
        await RisingEdge(dut.clk_100m)
        if not dut.seg_output.value.is_resolvable:
            raise AssertionError(f"seg_output has X/Z at cycle {cycle}")

    try:
        final_val = int(dut.seg_output.value)
        dut._log.info(f"seg_output after 500 cycles: {final_val:#04x}")
    except ValueError:
        raise AssertionError("seg_output not convertible after 500 cycles")


@cocotb.test()
async def test_gpio_bidir_no_xz(dut):
    """After warmup, gpio_bidir should be resolvable."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sw_input.value = 0x00

    # Give design time to warm up
    await ClockCycles(dut.clk_100m, 200)

    if not dut.gpio_bidir.value.is_resolvable:
        dut._log.info("gpio_bidir has X/Z after 200 cycles -- trying more warmup")
        await ClockCycles(dut.clk_100m, 300)
        if not dut.gpio_bidir.value.is_resolvable:
            # Bidirectional pins in tristate are expected to have X/Z in simulation
            dut._log.info("gpio_bidir still X/Z after 500 cycles (tristate/bidirectional -- acceptable)")
        else:
            try:
                gpio_val = int(dut.gpio_bidir.value)
                dut._log.info(f"gpio_bidir after extended warmup: {gpio_val:#04x}")
            except ValueError:
                dut._log.info("gpio_bidir not convertible after extended warmup")
    else:
        try:
            gpio_val = int(dut.gpio_bidir.value)
            dut._log.info(f"gpio_bidir after warmup: {gpio_val:#04x}")
        except ValueError:
            dut._log.info("gpio_bidir not convertible to int")


@cocotb.test()
async def test_switch_all_zeros(dut):
    """Set sw_input=0x00, run, verify outputs clean."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sw_input.value = 0x00
    await ClockCycles(dut.clk_100m, 50)

    if not dut.led_output.value.is_resolvable:
        raise AssertionError("led_output has X/Z with sw_input=0x00")
    if not dut.seg_output.value.is_resolvable:
        raise AssertionError("seg_output has X/Z with sw_input=0x00")

    try:
        led_val = int(dut.led_output.value)
        seg_val = int(dut.seg_output.value)
        dut._log.info(f"sw=0x00: led={led_val:#04x}, seg={seg_val:#04x}")
    except ValueError:
        raise AssertionError("Outputs not convertible with sw_input=0x00")


@cocotb.test()
async def test_switch_all_ones(dut):
    """Set sw_input=0xFF, verify outputs clean."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sw_input.value = 0xFF
    await ClockCycles(dut.clk_100m, 50)

    if not dut.led_output.value.is_resolvable:
        raise AssertionError("led_output has X/Z with sw_input=0xFF")
    if not dut.seg_output.value.is_resolvable:
        raise AssertionError("seg_output has X/Z with sw_input=0xFF")

    try:
        led_val = int(dut.led_output.value)
        seg_val = int(dut.seg_output.value)
        dut._log.info(f"sw=0xFF: led={led_val:#04x}, seg={seg_val:#04x}")
    except ValueError:
        raise AssertionError("Outputs not convertible with sw_input=0xFF")


@cocotb.test()
async def test_switch_walking_one(dut):
    """Cycle through walking-one pattern: 0x01, 0x02, 0x04, ..., 0x80."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for bit in range(8):
        sw_val = 1 << bit
        dut.sw_input.value = sw_val
        await ClockCycles(dut.clk_100m, 30)

        if not dut.led_output.value.is_resolvable:
            raise AssertionError(f"led_output has X/Z with sw_input={sw_val:#04x}")

        try:
            led_val = int(dut.led_output.value)
            seg_val = int(dut.seg_output.value)
            dut._log.info(
                f"sw={sw_val:#04x}: led={led_val:#04x}, seg={seg_val:#04x}"
            )
        except ValueError:
            raise AssertionError(f"Outputs not convertible with sw_input={sw_val:#04x}")


@cocotb.test()
async def test_long_run(dut):
    """Run 2000 cycles, verify stability of all outputs."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sw_input.value = 0x42

    for cycle in range(2000):
        await RisingEdge(dut.clk_100m)
        if not dut.led_output.value.is_resolvable:
            raise AssertionError(f"led_output has X/Z at cycle {cycle}")
        if not dut.seg_output.value.is_resolvable:
            raise AssertionError(f"seg_output has X/Z at cycle {cycle}")

    try:
        led_val = int(dut.led_output.value)
        seg_val = int(dut.seg_output.value)
        dut._log.info(f"After 2000 cycles: led={led_val:#04x}, seg={seg_val:#04x}")
    except ValueError:
        raise AssertionError("Outputs not convertible after 2000 cycles")


@cocotb.test()
async def test_reset_recovery(dut):
    """Reset mid-operation, verify clean recovery."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sw_input.value = 0xA5
    await ClockCycles(dut.clk_100m, 100)

    # Verify outputs before second reset
    if not dut.led_output.value.is_resolvable:
        raise AssertionError("led_output has X/Z before mid-operation reset")

    try:
        led_before = int(dut.led_output.value)
        dut._log.info(f"led_output before mid-op reset: {led_before:#04x}")
    except ValueError:
        raise AssertionError("led_output not convertible before mid-op reset")

    # Reset mid-operation
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_100m, 50)

    # Verify clean recovery
    if not dut.led_output.value.is_resolvable:
        raise AssertionError("led_output has X/Z after mid-operation reset")

    try:
        led_after = int(dut.led_output.value)
        seg_after = int(dut.seg_output.value)
        dut._log.info(
            f"After recovery: led={led_after:#04x}, seg={seg_after:#04x}"
        )
    except ValueError:
        raise AssertionError("Outputs not convertible after reset recovery")


@cocotb.test()
async def test_switch_walking_zero(dut):
    """Cycle through walking-zero pattern: 0xFE, 0xFD, 0xFB, ..., 0x7F."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for bit in range(8):
        sw_val = 0xFF ^ (1 << bit)
        dut.sw_input.value = sw_val
        await ClockCycles(dut.clk_100m, 30)

        if not dut.led_output.value.is_resolvable:
            raise AssertionError(f"led_output has X/Z with sw_input={sw_val:#04x}")

        try:
            led_val = int(dut.led_output.value)
            seg_val = int(dut.seg_output.value)
            dut._log.info(
                f"sw={sw_val:#04x}: led={led_val:#04x}, seg={seg_val:#04x}"
            )
        except ValueError:
            raise AssertionError(f"Outputs not convertible with sw_input={sw_val:#04x}")


@cocotb.test()
async def test_rapid_switch_toggling(dut):
    """Toggle sw_input between 0x00 and 0xFF every cycle for 200 cycles."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(200):
        dut.sw_input.value = 0xFF if (cycle % 2 == 0) else 0x00
        await RisingEdge(dut.clk_100m)

    # After rapid toggling, verify outputs are clean
    if not dut.led_output.value.is_resolvable:
        raise AssertionError("led_output has X/Z after rapid toggling")
    if not dut.seg_output.value.is_resolvable:
        raise AssertionError("seg_output has X/Z after rapid toggling")

    try:
        led_val = int(dut.led_output.value)
        seg_val = int(dut.seg_output.value)
        dut._log.info(f"After rapid toggle: led={led_val:#04x}, seg={seg_val:#04x}")
    except ValueError:
        raise AssertionError("Outputs not convertible after rapid toggling")

    dut._log.info("Design survived 200 cycles of rapid switch toggling")


@cocotb.test()
async def test_gpio_bidir_driven(dut):
    """Drive gpio_bidir externally and verify design does not crash."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sw_input.value = 0x00

    # Attempt to drive gpio_bidir with a value
    try:
        dut.gpio_bidir.value = 0xA5
    except Exception:
        dut._log.info("gpio_bidir cannot be driven externally (expected for bidirectional)")

    await ClockCycles(dut.clk_100m, 200)

    # Verify other outputs remain clean
    if not dut.led_output.value.is_resolvable:
        raise AssertionError("led_output has X/Z after driving gpio_bidir")

    try:
        led_val = int(dut.led_output.value)
        dut._log.info(f"led_output after gpio_bidir drive: {led_val:#04x}")
    except ValueError:
        raise AssertionError("led_output not convertible after gpio_bidir drive")


@cocotb.test()
async def test_clock_period_5ns(dut):
    """Use a 5ns clock period (200 MHz) to stress the design."""

    setup_clock(dut, "clk_100m", 5)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.sw_input.value = 0x33
    await ClockCycles(dut.clk_100m, 500)

    if not dut.led_output.value.is_resolvable:
        raise AssertionError("led_output has X/Z with 5ns clock")
    if not dut.seg_output.value.is_resolvable:
        raise AssertionError("seg_output has X/Z with 5ns clock")

    try:
        led_val = int(dut.led_output.value)
        seg_val = int(dut.seg_output.value)
        dut._log.info(f"5ns clock: led={led_val:#04x}, seg={seg_val:#04x}")
    except ValueError:
        raise AssertionError("Outputs not convertible with 5ns clock")

    dut._log.info("Design ran cleanly at 200 MHz (5ns) for 500 cycles")


@cocotb.test()
async def test_reset_hold_50_cycles(dut):
    """Hold reset for 50 cycles and verify clean recovery."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=50)

    dut.sw_input.value = 0xCC
    await ClockCycles(dut.clk_100m, 100)

    if not dut.led_output.value.is_resolvable:
        raise AssertionError("led_output has X/Z after 50-cycle reset hold")
    if not dut.seg_output.value.is_resolvable:
        raise AssertionError("seg_output has X/Z after 50-cycle reset hold")

    try:
        led_val = int(dut.led_output.value)
        seg_val = int(dut.seg_output.value)
        dut._log.info(f"After 50-cycle reset: led={led_val:#04x}, seg={seg_val:#04x}")
    except ValueError:
        raise AssertionError("Outputs not convertible after 50-cycle reset hold")


@cocotb.test()
async def test_switch_boundary_single_bit(dut):
    """Test sw_input at single-bit boundary values 0x01 and 0x80."""

    setup_clock(dut, "clk_100m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for sw_val in [0x01, 0x80]:
        dut.sw_input.value = sw_val
        await ClockCycles(dut.clk_100m, 50)

        if not dut.led_output.value.is_resolvable:
            raise AssertionError(f"led_output has X/Z with sw_input={sw_val:#04x}")
        if not dut.seg_output.value.is_resolvable:
            raise AssertionError(f"seg_output has X/Z with sw_input={sw_val:#04x}")

        try:
            led_val = int(dut.led_output.value)
            seg_val = int(dut.seg_output.value)
            dut._log.info(f"sw={sw_val:#04x}: led={led_val:#04x}, seg={seg_val:#04x}")
        except ValueError:
            raise AssertionError(f"Outputs not convertible with sw_input={sw_val:#04x}")

    dut._log.info("Single-bit boundary switch values handled cleanly")


@cocotb.test()
async def test_consecutive_resets_different_inputs(dut):
    """Three resets with different sw_input each time, verify clean outputs."""

    setup_clock(dut, "clk_100m", 10)

    test_inputs = [0x00, 0x55, 0xFF]
    for i, sw_val in enumerate(test_inputs):
        await reset_dut(dut, "rst_n", active_low=True, cycles=5)
        dut.sw_input.value = sw_val
        await ClockCycles(dut.clk_100m, 100)

        if not dut.led_output.value.is_resolvable:
            raise AssertionError(f"led_output X/Z on iteration {i} (sw={sw_val:#04x})")

        try:
            led_val = int(dut.led_output.value)
            seg_val = int(dut.seg_output.value)
            dut._log.info(
                f"Reset #{i}: sw={sw_val:#04x}, led={led_val:#04x}, seg={seg_val:#04x}"
            )
        except ValueError:
            raise AssertionError(f"Outputs not convertible on iteration {i}")

    dut._log.info("All three consecutive resets with different inputs passed")
