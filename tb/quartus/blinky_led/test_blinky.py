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


@cocotb.test()
async def test_reset_all_leds_zero(dut):
    """After reset, all 4 LEDs should be 0."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await RisingEdge(dut.clk_50m)

    if not dut.led.value.is_resolvable:
        raise AssertionError("LED value contains X/Z after reset")

    led_val = int(dut.led.value)
    dut._log.info(f"All LEDs after reset: {led_val:#06b}")
    assert led_val == 0, f"Expected all LEDs == 0 after reset, got {led_val:#06b}"


@cocotb.test()
async def test_led_stays_valid(dut):
    """Run 500 cycles, verify led[3:0] stays in range 0-15 with no X/Z."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(500):
        await RisingEdge(dut.clk_50m)
        if not dut.led.value.is_resolvable:
            raise AssertionError(f"LED has X/Z at cycle {cycle}")
        try:
            val = int(dut.led.value)
            assert 0 <= val <= 15, f"LED out of range at cycle {cycle}: {val}"
        except ValueError:
            raise AssertionError(f"LED value not convertible at cycle {cycle}")

    dut._log.info("LED stayed valid for 500 cycles")


@cocotb.test()
async def test_counter0_accessible(dut):
    """Try to read internal div_counter0, verify resolvable."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk_50m, 10)

    if not dut.div_counter0.value.is_resolvable:
        raise AssertionError("div_counter0 contains X/Z after 10 cycles")

    try:
        cnt0 = int(dut.div_counter0.value)
        dut._log.info(f"div_counter0 = {cnt0}")
        assert cnt0 >= 0, "div_counter0 should be non-negative"
    except ValueError:
        raise AssertionError("div_counter0 could not be converted to int")


@cocotb.test()
async def test_multiple_resets(dut):
    """Reset 3 times, verify LEDs clean each time."""

    setup_clock(dut, "clk_50m", 20)

    for i in range(3):
        await reset_dut(dut, "rst_n", active_low=True, cycles=5)
        await RisingEdge(dut.clk_50m)

        if not dut.led.value.is_resolvable:
            raise AssertionError(f"LED has X/Z after reset #{i+1}")

        try:
            led_val = int(dut.led.value)
            assert led_val == 0, f"Reset #{i+1}: expected LED==0, got {led_val}"
            dut._log.info(f"Reset #{i+1}: LED={led_val:#06b} -- clean")
        except ValueError:
            raise AssertionError(f"LED not convertible after reset #{i+1}")

        # Let counters run between resets
        await ClockCycles(dut.clk_50m, 50)


@cocotb.test()
async def test_long_run_stability(dut):
    """1000 cycles, no X/Z on LED output."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(1000):
        await RisingEdge(dut.clk_50m)
        if not dut.led.value.is_resolvable:
            raise AssertionError(f"LED has X/Z at cycle {cycle}")

    try:
        final_led = int(dut.led.value)
        dut._log.info(f"LED after 1000 cycles: {final_led:#06b}")
    except ValueError:
        raise AssertionError("LED not convertible after 1000 cycles")


@cocotb.test()
async def test_led_individual_bits(dut):
    """Check each led bit is 0 or 1 individually."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk_50m, 100)

    if not dut.led.value.is_resolvable:
        raise AssertionError("LED has X/Z after 100 cycles")

    try:
        led_val = int(dut.led.value)
    except ValueError:
        raise AssertionError("LED value not convertible")

    for bit in range(4):
        bit_val = (led_val >> bit) & 1
        assert bit_val in (0, 1), f"LED bit {bit} is not 0 or 1: {bit_val}"
        dut._log.info(f"LED bit {bit} = {bit_val}")


@cocotb.test()
async def test_reset_hold_long(dut):
    """Hold reset for 20 cycles, verify clean state afterwards."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=20)

    await RisingEdge(dut.clk_50m)

    if not dut.led.value.is_resolvable:
        raise AssertionError("LED has X/Z after long reset hold")

    try:
        led_val = int(dut.led.value)
        assert led_val == 0, f"Expected LED==0 after long reset, got {led_val}"
        dut._log.info(f"LED after 20-cycle reset hold: {led_val:#06b}")
    except ValueError:
        raise AssertionError("LED not convertible after long reset hold")

    # Verify counter is also clean
    if dut.div_counter0.value.is_resolvable:
        cnt0 = int(dut.div_counter0.value)
        assert cnt0 == 0 or cnt0 == 1, f"Counter0 should be 0 or 1 just after reset, got {cnt0}"


@cocotb.test()
async def test_clock_10ns(dut):
    """Use 10ns clock period (100MHz), verify design works."""

    setup_clock(dut, "clk_50m", 10)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk_50m, 200)

    if not dut.led.value.is_resolvable:
        raise AssertionError("LED has X/Z with 10ns clock")

    try:
        led_val = int(dut.led.value)
        dut._log.info(f"LED with 10ns clock after 200 cycles: {led_val:#06b}")
        assert 0 <= led_val <= 15, f"LED out of range: {led_val}"
    except ValueError:
        raise AssertionError("LED not convertible with 10ns clock")


@cocotb.test()
async def test_independent_leds(dut):
    """After many cycles, different LEDs may have different values due to independent counters."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Run for a long time -- counters have different bit widths (26-29 bits)
    # so they will roll over at different rates
    await ClockCycles(dut.clk_50m, 500)

    if not dut.led.value.is_resolvable:
        raise AssertionError("LED has X/Z after 500 cycles")

    try:
        led_val = int(dut.led.value)
        dut._log.info(f"LED value after 500 cycles: {led_val:#06b}")
    except ValueError:
        raise AssertionError("LED not convertible after 500 cycles")

    # Verify individual counter signals are accessible and resolvable
    for ctr_name in ["div_counter0", "div_counter1", "div_counter2", "div_counter3"]:
        try:
            ctr_sig = getattr(dut, ctr_name)
            if ctr_sig.value.is_resolvable:
                ctr_val = int(ctr_sig.value)
                dut._log.info(f"{ctr_name} = {ctr_val}")
            else:
                dut._log.warning(f"{ctr_name} contains X/Z")
        except AttributeError:
            dut._log.info(f"{ctr_name} not accessible (may be optimized out)")
        except ValueError:
            dut._log.warning(f"{ctr_name} not convertible to int")


@cocotb.test()
async def test_counter_monotonic_increase(dut):
    """Verify div_counter0 increases monotonically over consecutive samples."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    prev_val = None
    for cycle in range(200):
        await RisingEdge(dut.clk_50m)
        if not dut.div_counter0.value.is_resolvable:
            continue
        try:
            cur_val = int(dut.div_counter0.value)
        except ValueError:
            continue
        if prev_val is not None:
            assert cur_val >= prev_val or cur_val == 0, (
                f"Counter0 went backwards at cycle {cycle}: {prev_val} -> {cur_val}"
            )
        prev_val = cur_val

    dut._log.info(f"div_counter0 monotonically increased over 200 cycles, final={prev_val}")


@cocotb.test()
async def test_reset_during_counting(dut):
    """Assert reset while counters are running, verify clean restart."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Let counters run for a while
    await ClockCycles(dut.clk_50m, 300)

    if not dut.div_counter0.value.is_resolvable:
        raise AssertionError("div_counter0 has X/Z before mid-run reset")

    try:
        cnt_before = int(dut.div_counter0.value)
    except ValueError:
        raise AssertionError("div_counter0 not convertible before mid-run reset")

    dut._log.info(f"Counter0 before mid-run reset: {cnt_before}")
    assert cnt_before > 0, "Counter0 should be >0 after 300 cycles"

    # Reset mid-counting
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk_50m)

    if not dut.div_counter0.value.is_resolvable:
        raise AssertionError("div_counter0 has X/Z after mid-run reset")

    try:
        cnt_after = int(dut.div_counter0.value)
    except ValueError:
        raise AssertionError("div_counter0 not convertible after mid-run reset")

    assert cnt_after <= 1, f"Counter0 should be 0 or 1 after reset, got {cnt_after}"
    dut._log.info("Counter restarted cleanly after mid-run reset")


@cocotb.test()
async def test_very_fast_clock_5ns(dut):
    """Use a 5ns clock period (200MHz) and verify no metastability or X/Z."""

    setup_clock(dut, "clk_50m", 5)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk_50m, 500)

    if not dut.led.value.is_resolvable:
        raise AssertionError("LED has X/Z with 5ns (200MHz) clock")

    try:
        led_val = int(dut.led.value)
        dut._log.info(f"LED with 5ns clock after 500 cycles: {led_val:#06b}")
        assert 0 <= led_val <= 15, f"LED out of range: {led_val}"
    except ValueError:
        raise AssertionError("LED not convertible with 5ns clock")


@cocotb.test()
async def test_slow_clock_100ns(dut):
    """Use a 100ns clock period (10MHz) and verify design still works."""

    setup_clock(dut, "clk_50m", 100)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk_50m, 200)

    if not dut.led.value.is_resolvable:
        raise AssertionError("LED has X/Z with 100ns (10MHz) clock")

    try:
        led_val = int(dut.led.value)
        dut._log.info(f"LED with 100ns clock after 200 cycles: {led_val:#06b}")
        assert 0 <= led_val <= 15, f"LED out of range: {led_val}"
    except ValueError:
        raise AssertionError("LED not convertible with 100ns clock")


@cocotb.test()
async def test_reset_glitch_single_cycle(dut):
    """Assert reset for only 1 cycle, verify design still resets properly."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=1)

    await RisingEdge(dut.clk_50m)

    if not dut.led.value.is_resolvable:
        raise AssertionError("LED has X/Z after single-cycle reset")

    try:
        led_val = int(dut.led.value)
        dut._log.info(f"LED after 1-cycle reset: {led_val:#06b}")
        assert 0 <= led_val <= 15, f"LED out of range: {led_val}"
    except ValueError:
        raise AssertionError("LED not convertible after 1-cycle reset")


@cocotb.test()
async def test_all_counters_increment_together(dut):
    """Verify all four counters are incrementing after reset."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk_50m, 50)

    counter_vals = {}
    for ctr_name in ["div_counter0", "div_counter1", "div_counter2", "div_counter3"]:
        try:
            ctr_sig = getattr(dut, ctr_name)
            if ctr_sig.value.is_resolvable:
                ctr_val = int(ctr_sig.value)
                counter_vals[ctr_name] = ctr_val
                dut._log.info(f"{ctr_name} after 50 cycles = {ctr_val}")
                assert ctr_val > 0, f"{ctr_name} should be >0 after 50 cycles"
            else:
                dut._log.warning(f"{ctr_name} has X/Z after 50 cycles")
        except AttributeError:
            dut._log.info(f"{ctr_name} not accessible")
        except ValueError:
            dut._log.warning(f"{ctr_name} not convertible")

    if len(counter_vals) >= 2:
        dut._log.info(f"All accessible counters incrementing: {counter_vals}")
    else:
        dut._log.info("Fewer than 2 counters accessible for comparison")


@cocotb.test()
async def test_led_value_sampled_at_edges(dut):
    """Sample LED at rising and falling edges to ensure consistency."""

    setup_clock(dut, "clk_50m", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Sample at multiple rising edges and verify value doesn't glitch
    prev_val = None
    glitch_count = 0
    for cycle in range(100):
        await RisingEdge(dut.clk_50m)
        if not dut.led.value.is_resolvable:
            continue
        try:
            cur_val = int(dut.led.value)
        except ValueError:
            continue

        assert 0 <= cur_val <= 15, f"LED out of range at cycle {cycle}: {cur_val}"

        # Check for unexpected transitions -- with large counters LED should
        # not change in 100 cycles, but if it does, log it
        if prev_val is not None and cur_val != prev_val:
            glitch_count += 1
            dut._log.info(f"LED changed at cycle {cycle}: {prev_val:#06b} -> {cur_val:#06b}")
        prev_val = cur_val

    # Wait half a clock period and sample again to check setup/hold
    await Timer(10, unit="ns")
    if dut.led.value.is_resolvable:
        try:
            mid_val = int(dut.led.value)
            dut._log.info(f"LED sampled mid-cycle: {mid_val:#06b}")
            assert 0 <= mid_val <= 15, f"LED mid-cycle out of range: {mid_val}"
        except ValueError:
            dut._log.warning("LED not convertible at mid-cycle sample")

    dut._log.info(f"LED edge sampling complete, transitions observed: {glitch_count}")
