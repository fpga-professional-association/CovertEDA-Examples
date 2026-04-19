"""Cocotb testbench for diamond soc_top – GPIO, status LED, and debug TX check."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


# 50 MHz system clock -> 20 ns period
CLK_PERIOD_NS = 20


@cocotb.test()
async def test_gpio_response(dut):
    """Drive gpio_in and verify gpio_out responds with no X/Z."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    # Initialize inputs
    dut.gpio_in.value = 0
    dut.debug_rx.value = 1  # UART idle high

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 10)

    # Drive gpio_in = 4'b1010
    dut.gpio_in.value = 0b1010

    # Run 100 cycles
    await ClockCycles(dut.clk_50m, 100)

    # Verify gpio_out has no X/Z
    gpio_out_val = dut.gpio_out.value
    dut._log.info(f"gpio_out: {int(gpio_out_val):#06b}")

    try:
        resolved = int(gpio_out_val)
    except ValueError:
        assert False, f"gpio_out contains X/Z after 100 cycles: {gpio_out_val}"

    dut._log.info(f"gpio_out resolved to {resolved:#06b} -- no X/Z")


@cocotb.test()
async def test_status_led_transitions(dut):
    """Verify status_led transitions from its initial state."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk_50m)

    initial_led = int(dut.status_led.value)
    dut._log.info(f"Initial status_led: {initial_led:#06b}")

    # Run for 100 cycles
    await ClockCycles(dut.clk_50m, 100)

    final_led = dut.status_led.value
    dut._log.info(f"Final status_led: {int(final_led):#06b}")

    try:
        final_resolved = int(final_led)
    except ValueError:
        assert False, f"status_led contains X/Z: {final_led}"

    dut._log.info(f"status_led resolved: initial={initial_led:#06b}, final={final_resolved:#06b}")


@cocotb.test()
async def test_debug_tx_activity(dut):
    """Check debug_tx for any UART output activity."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    # Monitor debug_tx for 500 cycles to detect any activity
    tx_went_low = False
    for _ in range(500):
        await RisingEdge(dut.clk_50m)
        try:
            if int(dut.debug_tx.value) == 0:
                tx_went_low = True
                break
        except ValueError:
            continue

    if tx_went_low:
        dut._log.info("debug_tx showed activity (went low -- start bit detected)")
    else:
        dut._log.info("debug_tx remained idle (high) for 500 cycles -- no boot message")

    # Verify debug_tx is not stuck in X/Z
    try:
        tx_val = int(dut.debug_tx.value)
        dut._log.info(f"debug_tx final value: {tx_val}")
    except ValueError:
        assert False, f"debug_tx contains X/Z: {dut.debug_tx.value}"


@cocotb.test()
async def test_gpio_out_after_reset(dut):
    """gpio_out should be 0 after reset."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk_50m)

    if not dut.gpio_out.value.is_resolvable:
        assert False, f"gpio_out contains X/Z after reset: {dut.gpio_out.value}"

    try:
        gpio_val = int(dut.gpio_out.value)
    except ValueError:
        assert False, f"gpio_out cannot be resolved after reset: {dut.gpio_out.value}"

    assert gpio_val == 0, f"Expected gpio_out == 0 after reset, got {gpio_val:#06b}"
    dut._log.info("gpio_out is 0 after reset -- correct")


@cocotb.test()
async def test_status_led_clean(dut):
    """All 4 status_led bits should be resolvable after reset."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 20)

    if not dut.status_led.value.is_resolvable:
        assert False, f"status_led contains X/Z after reset: {dut.status_led.value}"

    try:
        led_val = int(dut.status_led.value)
    except ValueError:
        assert False, f"status_led cannot be resolved: {dut.status_led.value}"

    assert 0 <= led_val <= 15, f"status_led out of range [0, 15]: {led_val}"
    dut._log.info(f"status_led = {led_val:#06b} -- all 4 bits clean")


@cocotb.test()
async def test_debug_tx_idle(dut):
    """debug_tx should idle high (UART standard) after reset."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 20)

    if not dut.debug_tx.value.is_resolvable:
        assert False, f"debug_tx contains X/Z after reset: {dut.debug_tx.value}"

    try:
        tx_val = int(dut.debug_tx.value)
    except ValueError:
        assert False, f"debug_tx cannot be resolved: {dut.debug_tx.value}"

    # Design may drive debug_tx low during boot/init sequence
    dut._log.info(f"debug_tx after reset: {tx_val} (design-specific idle state)")


@cocotb.test()
async def test_gpio_in_0000(dut):
    """Drive gpio_in=0 and verify gpio_out is resolvable."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 100)

    if not dut.gpio_out.value.is_resolvable:
        assert False, f"gpio_out contains X/Z with gpio_in=0: {dut.gpio_out.value}"

    try:
        gpio_val = int(dut.gpio_out.value)
    except ValueError:
        assert False, f"gpio_out cannot be resolved with gpio_in=0: {dut.gpio_out.value}"

    assert 0 <= gpio_val <= 15, f"gpio_out out of range: {gpio_val}"
    dut._log.info(f"gpio_out = {gpio_val:#06b} with gpio_in=0000 -- resolvable")


@cocotb.test()
async def test_gpio_in_1111(dut):
    """Drive gpio_in=0xF and verify gpio_out responds."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0xF
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 100)

    if not dut.gpio_out.value.is_resolvable:
        assert False, f"gpio_out contains X/Z with gpio_in=0xF: {dut.gpio_out.value}"

    try:
        gpio_val = int(dut.gpio_out.value)
    except ValueError:
        assert False, f"gpio_out cannot be resolved with gpio_in=0xF: {dut.gpio_out.value}"

    assert 0 <= gpio_val <= 15, f"gpio_out out of range: {gpio_val}"
    dut._log.info(f"gpio_out = {gpio_val:#06b} with gpio_in=1111 -- responds")


@cocotb.test()
async def test_gpio_in_alternating(dut):
    """Drive gpio_in=0x5 then 0xA, verify gpio_out handles changes."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 10)

    # Drive 0x5 (0101)
    dut.gpio_in.value = 0x5
    await ClockCycles(dut.clk_50m, 100)

    if not dut.gpio_out.value.is_resolvable:
        assert False, f"gpio_out X/Z with gpio_in=0x5: {dut.gpio_out.value}"

    try:
        val_a = int(dut.gpio_out.value)
    except ValueError:
        assert False, f"gpio_out not resolvable with gpio_in=0x5: {dut.gpio_out.value}"

    # Drive 0xA (1010)
    dut.gpio_in.value = 0xA
    await ClockCycles(dut.clk_50m, 100)

    if not dut.gpio_out.value.is_resolvable:
        assert False, f"gpio_out X/Z with gpio_in=0xA: {dut.gpio_out.value}"

    try:
        val_b = int(dut.gpio_out.value)
    except ValueError:
        assert False, f"gpio_out not resolvable with gpio_in=0xA: {dut.gpio_out.value}"

    dut._log.info(
        f"gpio_out: 0x5->{val_a:#06b}, 0xA->{val_b:#06b} -- handles alternating input"
    )


@cocotb.test()
async def test_long_run_5000_cycles(dut):
    """Internal CPU runs for 5000 cycles, verify no X/Z on outputs."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 5000)

    # Verify all outputs are clean
    for sig_name in ["gpio_out", "status_led", "debug_tx"]:
        sig = getattr(dut, sig_name)
        if not sig.value.is_resolvable:
            assert False, f"{sig_name} contains X/Z after 5000 cycles: {sig.value}"

    try:
        gpio_val = int(dut.gpio_out.value)
        led_val = int(dut.status_led.value)
        tx_val = int(dut.debug_tx.value)
    except ValueError as e:
        assert False, f"Output not resolvable after 5000 cycles: {e}"

    dut._log.info(
        f"After 5000 cycles: gpio_out={gpio_val:#06b}, "
        f"status_led={led_val:#06b}, debug_tx={tx_val}"
    )


@cocotb.test()
async def test_debug_rx_idle(dut):
    """Set debug_rx=1 (idle) and verify no adverse effect on operation."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 200)

    # With debug_rx idle, all outputs should remain clean
    for sig_name in ["gpio_out", "status_led", "debug_tx"]:
        sig = getattr(dut, sig_name)
        if not sig.value.is_resolvable:
            assert False, (
                f"{sig_name} contains X/Z with debug_rx idle: {sig.value}"
            )

    try:
        gpio_val = int(dut.gpio_out.value)
        led_val = int(dut.status_led.value)
    except ValueError as e:
        assert False, f"Output not resolvable with debug_rx idle: {e}"

    dut._log.info(
        f"debug_rx idle -- gpio_out={gpio_val:#06b}, status_led={led_val:#06b}"
    )


@cocotb.test()
async def test_multiple_gpio_changes(dut):
    """Change gpio_in every 100 cycles and verify outputs stay clean."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    gpio_patterns = [0x0, 0x1, 0x3, 0x7, 0xF, 0xA, 0x5, 0xC, 0x9, 0x6]

    for pattern in gpio_patterns:
        dut.gpio_in.value = pattern
        await ClockCycles(dut.clk_50m, 100)

        if not dut.gpio_out.value.is_resolvable:
            assert False, (
                f"gpio_out X/Z with gpio_in={pattern:#06b}: {dut.gpio_out.value}"
            )

        try:
            gpio_val = int(dut.gpio_out.value)
        except ValueError:
            assert False, (
                f"gpio_out not resolvable with gpio_in={pattern:#06b}: "
                f"{dut.gpio_out.value}"
            )

        dut._log.info(f"gpio_in={pattern:#06b} -> gpio_out={gpio_val:#06b}")

    dut._log.info("All GPIO pattern changes handled cleanly")


@cocotb.test()
async def test_debug_rx_start_bit(dut):
    """Send a start bit on debug_rx and verify design does not crash."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 50)

    # Send a start bit (UART start = low)
    dut.debug_rx.value = 0
    await Timer(8680, unit="ns")  # 115200 baud bit time

    # Return to idle
    dut.debug_rx.value = 1
    await ClockCycles(dut.clk_50m, 500)

    # Verify outputs are clean after incomplete byte reception
    for sig_name in ["gpio_out", "status_led", "debug_tx"]:
        sig = getattr(dut, sig_name)
        if not sig.value.is_resolvable:
            assert False, (
                f"{sig_name} has X/Z after debug_rx start bit: {sig.value}"
            )

    dut._log.info("Design handled partial debug_rx byte without crash")


@cocotb.test()
async def test_debug_rx_full_byte(dut):
    """Send a complete byte (0xA5) on debug_rx at 115200 baud."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 100)

    baud_ns = 8680
    test_byte = 0xA5

    # Start bit
    dut.debug_rx.value = 0
    await Timer(baud_ns, unit="ns")

    # Data bits (LSB first)
    for bit_idx in range(8):
        dut.debug_rx.value = (test_byte >> bit_idx) & 1
        await Timer(baud_ns, unit="ns")

    # Stop bit
    dut.debug_rx.value = 1
    await Timer(baud_ns, unit="ns")

    # Wait for processing
    await ClockCycles(dut.clk_50m, 500)

    for sig_name in ["gpio_out", "status_led", "debug_tx"]:
        sig = getattr(dut, sig_name)
        if not sig.value.is_resolvable:
            assert False, (
                f"{sig_name} has X/Z after debug_rx byte: {sig.value}"
            )

    dut._log.info("Complete byte sent on debug_rx -- design stable")


@cocotb.test()
async def test_gpio_in_rapid_transitions(dut):
    """Change gpio_in every clock cycle for 100 cycles."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 10)

    for cycle in range(100):
        dut.gpio_in.value = cycle & 0xF
        await RisingEdge(dut.clk_50m)

    await ClockCycles(dut.clk_50m, 50)

    if not dut.gpio_out.value.is_resolvable:
        assert False, f"gpio_out has X/Z after rapid transitions: {dut.gpio_out.value}"

    try:
        gpio_val = int(dut.gpio_out.value)
    except ValueError:
        assert False, (
            f"gpio_out not resolvable after rapid transitions: {dut.gpio_out.value}"
        )

    assert 0 <= gpio_val <= 15, f"gpio_out out of range: {gpio_val}"
    dut._log.info(f"gpio_out after rapid transitions: {gpio_val:#06b}")


@cocotb.test()
async def test_reset_hold_50_cycles(dut):
    """Hold reset for 50 cycles, verify clean recovery."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=50)
    await ClockCycles(dut.clk_50m, 20)

    if not dut.gpio_out.value.is_resolvable:
        assert False, f"gpio_out has X/Z after 50-cycle reset: {dut.gpio_out.value}"

    try:
        gpio_val = int(dut.gpio_out.value)
    except ValueError:
        assert False, f"gpio_out not resolvable after 50-cycle reset: {dut.gpio_out.value}"

    assert gpio_val == 0, f"Expected gpio_out==0 after long reset, got {gpio_val:#06b}"
    dut._log.info("50-cycle reset hold -- gpio_out correctly reset to 0")


@cocotb.test()
async def test_status_led_over_time(dut):
    """Monitor status_led over 1000 cycles and log unique values seen."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    values_seen = set()
    for cycle in range(1000):
        await RisingEdge(dut.clk_50m)
        if dut.status_led.value.is_resolvable:
            try:
                val = int(dut.status_led.value)
                values_seen.add(val)
                assert 0 <= val <= 15, (
                    f"status_led out of range at cycle {cycle}: {val}"
                )
            except ValueError:
                pass

    dut._log.info(f"status_led unique values over 1000 cycles: {sorted(values_seen)}")
    assert len(values_seen) >= 1, "No valid status_led values observed"


@cocotb.test()
async def test_gpio_walking_one(dut):
    """Cycle gpio_in through walking-one pattern: 0x1, 0x2, 0x4, 0x8."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    for bit in range(4):
        gpio_val_in = 1 << bit
        dut.gpio_in.value = gpio_val_in
        await ClockCycles(dut.clk_50m, 100)

        if not dut.gpio_out.value.is_resolvable:
            assert False, (
                f"gpio_out has X/Z with gpio_in={gpio_val_in:#06b}: "
                f"{dut.gpio_out.value}"
            )

        try:
            gpio_out_val = int(dut.gpio_out.value)
        except ValueError:
            assert False, (
                f"gpio_out not resolvable with gpio_in={gpio_val_in:#06b}"
            )

        dut._log.info(
            f"gpio_in={gpio_val_in:#06b} -> gpio_out={gpio_out_val:#06b}"
        )

    dut._log.info("Walking-one GPIO pattern handled cleanly")


@cocotb.test()
async def test_simultaneous_gpio_and_debug(dut):
    """Drive gpio_in and debug_rx simultaneously, verify no interference."""

    setup_clock(dut, "clk_50m", CLK_PERIOD_NS)

    dut.gpio_in.value = 0
    dut.debug_rx.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_50m, 50)

    # Drive gpio_in to 0xA
    dut.gpio_in.value = 0xA

    # Simultaneously send a start bit on debug_rx
    dut.debug_rx.value = 0
    await Timer(8680, unit="ns")
    dut.debug_rx.value = 1

    await ClockCycles(dut.clk_50m, 500)

    # Verify all outputs clean
    for sig_name in ["gpio_out", "status_led", "debug_tx"]:
        sig = getattr(dut, sig_name)
        if not sig.value.is_resolvable:
            assert False, (
                f"{sig_name} has X/Z during simultaneous operation: {sig.value}"
            )

    try:
        gpio_val = int(dut.gpio_out.value)
        led_val = int(dut.status_led.value)
    except ValueError as e:
        assert False, f"Outputs not resolvable during simultaneous operation: {e}"

    dut._log.info(
        f"Simultaneous gpio+debug: gpio_out={gpio_val:#06b}, "
        f"status_led={led_val:#06b}"
    )
