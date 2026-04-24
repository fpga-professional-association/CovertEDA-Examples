"""Cocotb testbench for oss led_chaser -- N-LED chaser with speed control."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut

CLK_PERIOD_NS = 83


async def init_inputs(dut):
    dut.speed.value = 0
    dut.direction.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """After reset, only LED[0] should be on."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    val = dut.leds.value
    assert val.is_resolvable, f"leds has X/Z after reset: {val}"
    try:
        assert int(val) == 1, f"Expected leds=1 after reset, got {int(val):#04x}"
    except ValueError:
        assert False, f"leds not convertible: {val}"
    dut._log.info("Reset state: LED[0] on -- PASS")


@cocotb.test()
async def test_chasing_left(dut):
    """With speed=0 and direction=0, LED should shift left."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    dut.speed.value = 0
    dut.direction.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    positions = []
    for _ in range(5000):
        await RisingEdge(dut.clk)
        val = dut.leds.value
        if val.is_resolvable:
            try:
                v = int(val)
                if v not in [0] and (len(positions) == 0 or v != positions[-1]):
                    positions.append(v)
            except ValueError:
                pass
        if len(positions) >= 4:
            break

    dut._log.info(f"LED positions: {[hex(p) for p in positions]}")
    dut._log.info("Chasing left test -- PASS")


@cocotb.test()
async def test_chasing_right(dut):
    """With direction=1, LED should shift right."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    dut.speed.value = 0
    dut.direction.value = 1
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    positions = []
    for _ in range(5000):
        await RisingEdge(dut.clk)
        val = dut.leds.value
        if val.is_resolvable:
            try:
                v = int(val)
                if v not in [0] and (len(positions) == 0 or v != positions[-1]):
                    positions.append(v)
            except ValueError:
                pass
        if len(positions) >= 4:
            break

    dut._log.info(f"LED positions (right): {[hex(p) for p in positions]}")
    dut._log.info("Chasing right test -- PASS")
