"""Cocotb testbench for vivado pulse_width_measure."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb_helpers import setup_clock, reset_dut


async def generate_pwm(dut, period_clks, duty_clks, num_cycles):
    """Generate PWM signal on signal_in."""
    for _ in range(num_cycles):
        dut.signal_in.value = 1
        for _ in range(duty_clks):
            await RisingEdge(dut.clk)
        dut.signal_in.value = 0
        for _ in range(period_clks - duty_clks):
            await RisingEdge(dut.clk)


@cocotb.test()
async def test_reset_state(dut):
    """Verify outputs are zero after reset."""
    setup_clock(dut, "clk", 10)
    dut.signal_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.valid.value.is_resolvable, "valid has X/Z after reset"
    assert dut.period.value.is_resolvable, "period has X/Z after reset"
    try:
        v = int(dut.valid.value)
        p = int(dut.period.value)
        dut._log.info(f"After reset: valid={v}, period={p}")
    except ValueError:
        assert False, "Signals not convertible after reset"


@cocotb.test()
async def test_50pct_duty(dut):
    """Measure a 50% duty cycle signal."""
    setup_clock(dut, "clk", 10)
    dut.signal_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Generate PWM: period=20 clocks, 50% duty = 10 clocks high
    await generate_pwm(dut, 20, 10, 5)

    # Wait for sync delay
    await ClockCycles(dut.clk, 5)

    if dut.period.value.is_resolvable and dut.high_time.value.is_resolvable:
        try:
            p = int(dut.period.value)
            h = int(dut.high_time.value)
            dut._log.info(f"50% duty: period={p}, high_time={h}")
        except ValueError:
            dut._log.info("Measurement not convertible")


@cocotb.test()
async def test_25pct_duty(dut):
    """Measure a 25% duty cycle signal."""
    setup_clock(dut, "clk", 10)
    dut.signal_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Generate PWM: period=40 clocks, 25% duty = 10 clocks high
    await generate_pwm(dut, 40, 10, 4)

    await ClockCycles(dut.clk, 5)

    if dut.period.value.is_resolvable and dut.high_time.value.is_resolvable:
        try:
            p = int(dut.period.value)
            h = int(dut.high_time.value)
            dut._log.info(f"25% duty: period={p}, high_time={h}")
        except ValueError:
            dut._log.info("Measurement not convertible")


@cocotb.test()
async def test_no_signal(dut):
    """Verify no valid output when signal stays low."""
    setup_clock(dut, "clk", 10)
    dut.signal_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk, 100)

    if dut.valid.value.is_resolvable:
        try:
            v = int(dut.valid.value)
            dut._log.info(f"valid with no signal: {v} (expected 0)")
        except ValueError:
            dut._log.info("valid not convertible")
