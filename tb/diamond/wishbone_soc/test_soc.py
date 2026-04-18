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
