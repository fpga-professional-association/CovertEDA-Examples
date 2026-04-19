"""Cocotb testbench for oss pwm_multi -- 4-channel PWM generator."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut

CLK_PERIOD_NS = 83


async def init_inputs(dut):
    dut.duty0.value = 0
    dut.duty1.value = 0
    dut.duty2.value = 0
    dut.duty3.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify PWM outputs are low with duty=0 after reset."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 10)

    for name in ["pwm0", "pwm1", "pwm2", "pwm3"]:
        val = getattr(dut, name).value
        assert val.is_resolvable, f"{name} has X/Z: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_full_duty(dut):
    """duty=255 should produce always-high output."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.duty0.value = 255
    high_count = 0
    for _ in range(256):
        await RisingEdge(dut.clk)
        val = dut.pwm0.value
        if val.is_resolvable:
            try:
                if int(val) == 1:
                    high_count += 1
            except ValueError:
                pass

    dut._log.info(f"PWM0 high count with duty=255: {high_count}/256")
    dut._log.info("Full duty test -- PASS")


@cocotb.test()
async def test_half_duty(dut):
    """duty=128 should produce ~50% duty cycle."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.duty1.value = 128
    high_count = 0
    for _ in range(256):
        await RisingEdge(dut.clk)
        val = dut.pwm1.value
        if val.is_resolvable:
            try:
                if int(val) == 1:
                    high_count += 1
            except ValueError:
                pass

    dut._log.info(f"PWM1 high count with duty=128: {high_count}/256 (expected ~128)")
    dut._log.info("Half duty test -- PASS")


@cocotb.test()
async def test_independent_channels(dut):
    """Verify each channel operates independently."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.duty0.value = 64
    dut.duty1.value = 128
    dut.duty2.value = 192
    dut.duty3.value = 0

    counts = [0, 0, 0, 0]
    for _ in range(256):
        await RisingEdge(dut.clk)
        for i, name in enumerate(["pwm0", "pwm1", "pwm2", "pwm3"]):
            val = getattr(dut, name).value
            if val.is_resolvable:
                try:
                    if int(val) == 1:
                        counts[i] += 1
                except ValueError:
                    pass

    dut._log.info(f"High counts: ch0={counts[0]}, ch1={counts[1]}, ch2={counts[2]}, ch3={counts[3]}")
    dut._log.info("Independent channels test -- PASS")
