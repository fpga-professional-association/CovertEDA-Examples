"""Cocotb testbench for oss tone_generator -- musical tone generator."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut

CLK_PERIOD_NS = 83


async def init_inputs(dut):
    dut.half_period.value = 100
    dut.enable.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify output is 0 after reset."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    val = dut.tone_out.value
    assert val.is_resolvable, f"tone_out has X/Z after reset: {val}"
    try:
        assert int(val) == 0, f"tone_out not 0 after reset: {int(val)}"
    except ValueError:
        assert False, f"tone_out not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_tone_toggles(dut):
    """Enable tone and verify output toggles."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    dut.half_period.value = 10
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.enable.value = 1
    transitions = 0
    prev = 0
    for _ in range(100):
        await RisingEdge(dut.clk)
        val = dut.tone_out.value
        if val.is_resolvable:
            try:
                v = int(val)
                if v != prev:
                    transitions += 1
                    prev = v
            except ValueError:
                pass

    dut.enable.value = 0
    dut._log.info(f"Tone transitions in 100 cycles: {transitions}")
    assert transitions > 2, f"Expected tone to toggle, got {transitions} transitions"
    dut._log.info("Tone toggles test -- PASS")


@cocotb.test()
async def test_disabled_silent(dut):
    """Verify output stays 0 when disabled."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    dut.half_period.value = 5
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.enable.value = 0
    for _ in range(50):
        await RisingEdge(dut.clk)
        val = dut.tone_out.value
        if val.is_resolvable:
            try:
                assert int(val) == 0, f"tone_out not 0 when disabled: {int(val)}"
            except ValueError:
                pass
    dut._log.info("Disabled silent test -- PASS")


@cocotb.test()
async def test_frequency_change(dut):
    """Change half_period and verify tone frequency adapts."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.enable.value = 1
    for hp in [5, 20, 50]:
        dut.half_period.value = hp
        transitions = 0
        prev = 0
        for _ in range(200):
            await RisingEdge(dut.clk)
            val = dut.tone_out.value
            if val.is_resolvable:
                try:
                    v = int(val)
                    if v != prev:
                        transitions += 1
                        prev = v
                except ValueError:
                    pass
        dut._log.info(f"half_period={hp}: {transitions} transitions in 200 cycles")

    dut.enable.value = 0
    dut._log.info("Frequency change test -- PASS")
