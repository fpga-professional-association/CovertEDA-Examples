"""Cocotb testbench for quartus clock_divider (programmable 8-bit divisor)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify clk_out is low after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.divisor.value = 0
    dut.load.value = 0
    await RisingEdge(dut.clk)

    if not dut.clk_out.value.is_resolvable:
        raise AssertionError("clk_out has X/Z after reset")

    try:
        co = int(dut.clk_out.value)
        assert co == 0, f"Expected clk_out=0 after reset, got {co}"
    except ValueError:
        raise AssertionError("clk_out not convertible")

    dut._log.info("Reset state: clk_out=0")


@cocotb.test()
async def test_divide_by_2(dut):
    """Divisor=0 gives divide-by-2 (toggle every cycle)."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.load.value = 0
    dut.divisor.value = 0
    await RisingEdge(dut.clk)

    # Load divisor=0
    dut.load.value = 1
    dut.divisor.value = 0
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)

    # Count transitions
    transitions = 0
    prev = None
    for _ in range(20):
        await RisingEdge(dut.clk)
        if dut.clk_out.value.is_resolvable:
            try:
                cur = int(dut.clk_out.value)
                if prev is not None and cur != prev:
                    transitions += 1
                prev = cur
            except ValueError:
                pass

    dut._log.info(f"Transitions with div=0 over 20 cycles: {transitions}")
    assert transitions >= 8, f"Expected many transitions, got {transitions}"


@cocotb.test()
async def test_divide_by_10(dut):
    """Divisor=4 gives divide-by-10 (toggle every 5 cycles)."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.load.value = 0
    dut.divisor.value = 0
    await RisingEdge(dut.clk)

    dut.load.value = 1
    dut.divisor.value = 4
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)

    transitions = 0
    prev = None
    for _ in range(100):
        await RisingEdge(dut.clk)
        if dut.clk_out.value.is_resolvable:
            try:
                cur = int(dut.clk_out.value)
                if prev is not None and cur != prev:
                    transitions += 1
                prev = cur
            except ValueError:
                pass

    dut._log.info(f"Transitions with div=4 over 100 cycles: {transitions}")
    # div=4 means toggle every 5 cycles, so ~20 transitions in 100 cycles
    assert 15 <= transitions <= 25, f"Expected ~20 transitions, got {transitions}"


@cocotb.test()
async def test_tick_pulses(dut):
    """tick should pulse once for each clk_out transition."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.load.value = 0
    dut.divisor.value = 0
    await RisingEdge(dut.clk)

    dut.load.value = 1
    dut.divisor.value = 2
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)

    tick_count = 0
    for _ in range(60):
        await RisingEdge(dut.clk)
        if dut.tick.value.is_resolvable:
            try:
                if int(dut.tick.value) == 1:
                    tick_count += 1
            except ValueError:
                pass

    dut._log.info(f"Tick pulses in 60 cycles with div=2: {tick_count}")
    assert tick_count > 5, f"Expected multiple tick pulses, got {tick_count}"


@cocotb.test()
async def test_load_new_divisor(dut):
    """Change divisor mid-operation and verify frequency changes."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.load.value = 0
    dut.divisor.value = 0
    await RisingEdge(dut.clk)

    # Load fast divisor
    dut.load.value = 1
    dut.divisor.value = 1
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)

    fast_transitions = 0
    prev = None
    for _ in range(50):
        await RisingEdge(dut.clk)
        if dut.clk_out.value.is_resolvable:
            try:
                cur = int(dut.clk_out.value)
                if prev is not None and cur != prev:
                    fast_transitions += 1
                prev = cur
            except ValueError:
                pass

    # Load slow divisor
    dut.load.value = 1
    dut.divisor.value = 9
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)

    slow_transitions = 0
    prev = None
    for _ in range(50):
        await RisingEdge(dut.clk)
        if dut.clk_out.value.is_resolvable:
            try:
                cur = int(dut.clk_out.value)
                if prev is not None and cur != prev:
                    slow_transitions += 1
                prev = cur
            except ValueError:
                pass

    dut._log.info(f"Fast (div=1): {fast_transitions} transitions, Slow (div=9): {slow_transitions} transitions")
    assert fast_transitions > slow_transitions, "Fast divisor should have more transitions than slow"
