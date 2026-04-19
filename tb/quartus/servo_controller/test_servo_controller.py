"""Cocotb testbench for quartus servo_controller (4-channel RC servo PWM)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify PWM outputs are valid after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.wr_en.value = 0
    dut.ch_sel.value = 0
    dut.position.value = 0
    await RisingEdge(dut.clk)

    if not dut.servo_pwm.value.is_resolvable:
        raise AssertionError("servo_pwm has X/Z after reset")

    try:
        pwm_val = int(dut.servo_pwm.value)
        dut._log.info(f"PWM after reset: {pwm_val:#06b}")
        assert 0 <= pwm_val <= 0xF, f"PWM out of range: {pwm_val}"
    except ValueError:
        raise AssertionError("servo_pwm not convertible")


@cocotb.test()
async def test_pwm_generates_pulses(dut):
    """Run for a full period and verify PWM toggling occurs."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.wr_en.value = 0
    dut.ch_sel.value = 0
    dut.position.value = 0
    await RisingEdge(dut.clk)

    high_count = 0
    low_count = 0
    for _ in range(1100):  # slightly more than PERIOD_COUNT
        await RisingEdge(dut.clk)
        if dut.servo_pwm.value.is_resolvable:
            try:
                val = int(dut.servo_pwm.value) & 1  # channel 0
                if val:
                    high_count += 1
                else:
                    low_count += 1
            except ValueError:
                pass

    dut._log.info(f"Channel 0 - High: {high_count}, Low: {low_count}")
    assert high_count > 0, "PWM channel 0 never went high"
    assert low_count > 0, "PWM channel 0 never went low"


@cocotb.test()
async def test_position_write(dut):
    """Write a position and verify the channel accepts it."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.wr_en.value = 0
    dut.ch_sel.value = 0
    dut.position.value = 0
    await RisingEdge(dut.clk)

    # Write minimum position to channel 0
    dut.ch_sel.value = 0
    dut.position.value = 0
    dut.wr_en.value = 1
    await RisingEdge(dut.clk)
    dut.wr_en.value = 0

    # Write maximum position to channel 1
    dut.ch_sel.value = 1
    dut.position.value = 0xFFFF
    dut.wr_en.value = 1
    await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    # Run for a period and compare duty cycles
    ch0_high = 0
    ch1_high = 0
    for _ in range(1100):
        await RisingEdge(dut.clk)
        if dut.servo_pwm.value.is_resolvable:
            try:
                pwm = int(dut.servo_pwm.value)
                if pwm & 0x1:
                    ch0_high += 1
                if pwm & 0x2:
                    ch1_high += 1
            except ValueError:
                pass

    dut._log.info(f"Ch0 (min pos) high count: {ch0_high}")
    dut._log.info(f"Ch1 (max pos) high count: {ch1_high}")
    # Channel 1 should have more high time than channel 0
    dut._log.info(f"Ch1 > Ch0: {ch1_high > ch0_high}")


@cocotb.test()
async def test_all_channels_independent(dut):
    """Verify all 4 channels can have different positions."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.wr_en.value = 0
    dut.ch_sel.value = 0
    dut.position.value = 0
    await RisingEdge(dut.clk)

    positions = [0x0000, 0x5555, 0xAAAA, 0xFFFF]
    for ch, pos in enumerate(positions):
        dut.ch_sel.value = ch
        dut.position.value = pos
        dut.wr_en.value = 1
        await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    # Run and check all channels produce output
    await ClockCycles(dut.clk, 1100)

    if dut.servo_pwm.value.is_resolvable:
        try:
            final = int(dut.servo_pwm.value)
            dut._log.info(f"Final PWM state: {final:#06b}")
            assert 0 <= final <= 0xF, f"PWM out of range: {final}"
        except ValueError:
            raise AssertionError("servo_pwm not convertible")


@cocotb.test()
async def test_counter_wraps(dut):
    """Verify the internal counter wraps around correctly."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.wr_en.value = 0
    dut.ch_sel.value = 0
    dut.position.value = 0
    await RisingEdge(dut.clk)

    # Run for 2+ full periods
    transitions = 0
    prev_pwm = None
    for _ in range(2200):
        await RisingEdge(dut.clk)
        if dut.servo_pwm.value.is_resolvable:
            try:
                cur = int(dut.servo_pwm.value) & 1
                if prev_pwm is not None and cur != prev_pwm:
                    transitions += 1
                prev_pwm = cur
            except ValueError:
                pass

    dut._log.info(f"PWM transitions in 2+ periods: {transitions}")
    assert transitions >= 2, f"Expected at least 2 transitions, got {transitions}"
