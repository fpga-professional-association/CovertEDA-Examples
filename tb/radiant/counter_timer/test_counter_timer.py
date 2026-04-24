"""Cocotb testbench for radiant counter_timer."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify counter resets to zero and outputs are clear."""
    setup_clock(dut, "clk", 40)
    dut.enable.value = 0
    dut.prescaler.value = 0
    dut.compare_val.value = 0
    dut.clear.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.count.value.is_resolvable, "count has X/Z after reset"
    try:
        cnt = int(dut.count.value)
        assert cnt == 0, f"count not zero after reset: {cnt}"
        dut._log.info(f"count after reset: {cnt}")
    except ValueError:
        raise AssertionError("count not resolvable after reset")

    assert dut.match.value.is_resolvable, "match has X/Z after reset"
    assert dut.overflow.value.is_resolvable, "overflow has X/Z after reset"


@cocotb.test()
async def test_counting_no_prescaler(dut):
    """Enable counting with prescaler=0, verify count increments each cycle."""
    setup_clock(dut, "clk", 40)
    dut.enable.value = 0
    dut.prescaler.value = 0
    dut.compare_val.value = 100
    dut.clear.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 1
    await ClockCycles(dut.clk, 20)

    assert dut.count.value.is_resolvable, "count has X/Z"
    try:
        cnt = int(dut.count.value)
        dut._log.info(f"count after 20 enabled cycles: {cnt}")
        assert cnt > 0, "count did not increment"
    except ValueError:
        raise AssertionError("count not resolvable")


@cocotb.test()
async def test_prescaler_divides(dut):
    """With prescaler=3, count should increment every 4 cycles."""
    setup_clock(dut, "clk", 40)
    dut.enable.value = 0
    dut.prescaler.value = 3
    dut.compare_val.value = 1000
    dut.clear.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 1
    await ClockCycles(dut.clk, 40)

    assert dut.count.value.is_resolvable, "count has X/Z"
    try:
        cnt = int(dut.count.value)
        dut._log.info(f"count after 40 cycles with prescaler=3: {cnt}")
        # With prescaler=3, expect ~10 increments in 40 cycles
        assert cnt >= 8 and cnt <= 12, f"count {cnt} outside expected range"
    except ValueError:
        raise AssertionError("count not resolvable")


@cocotb.test()
async def test_compare_match(dut):
    """Verify match output asserts when count equals compare_val."""
    setup_clock(dut, "clk", 40)
    dut.enable.value = 0
    dut.prescaler.value = 0
    dut.compare_val.value = 10
    dut.clear.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 1
    match_seen = False
    for _ in range(30):
        await RisingEdge(dut.clk)
        if dut.match.value.is_resolvable:
            try:
                if int(dut.match.value) == 1:
                    match_seen = True
                    dut._log.info("Compare match detected")
                    break
            except ValueError:
                pass

    dut._log.info(f"Match seen: {match_seen}")
    assert match_seen, "Compare match never asserted"


@cocotb.test()
async def test_clear_resets_count(dut):
    """Pulse clear while counting and verify count returns to zero."""
    setup_clock(dut, "clk", 40)
    dut.enable.value = 0
    dut.prescaler.value = 0
    dut.compare_val.value = 1000
    dut.clear.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 1
    await ClockCycles(dut.clk, 15)

    # Pulse clear
    dut.clear.value = 1
    await RisingEdge(dut.clk)
    dut.clear.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    assert dut.count.value.is_resolvable, "count has X/Z after clear"
    try:
        cnt = int(dut.count.value)
        dut._log.info(f"count after clear: {cnt}")
        assert cnt <= 2, f"count not cleared properly: {cnt}"
    except ValueError:
        raise AssertionError("count not resolvable after clear")
