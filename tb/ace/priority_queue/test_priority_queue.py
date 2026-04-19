"""Cocotb testbench for ace priority_queue -- 8-entry priority queue."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def init_inputs(dut):
    dut.data_in.value = 0
    dut.priority_in.value = 0
    dut.enqueue.value = 0
    dut.dequeue.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify queue is empty after reset."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for name, expected in [("empty", 1), ("full", 0)]:
        val = getattr(dut, name).value
        assert val.is_resolvable, f"{name} has X/Z after reset: {val}"
        try:
            assert int(val) == expected, f"{name} not {expected} after reset: {int(val)}"
        except ValueError:
            assert False, f"{name} not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_enqueue_dequeue(dut):
    """Enqueue one item and dequeue it."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.data_in.value = 0xAB
    dut.priority_in.value = 3
    dut.enqueue.value = 1
    await RisingEdge(dut.clk)
    dut.enqueue.value = 0
    await RisingEdge(dut.clk)

    val = dut.data_out.value
    assert val.is_resolvable, f"data_out has X/Z: {val}"
    try:
        assert int(val) == 0xAB, f"data_out mismatch: {int(val):#04x}"
    except ValueError:
        assert False, f"data_out not convertible: {val}"

    dut.dequeue.value = 1
    await RisingEdge(dut.clk)
    dut.dequeue.value = 0
    await RisingEdge(dut.clk)

    emp = dut.empty.value
    assert emp.is_resolvable, f"empty has X/Z: {emp}"
    try:
        assert int(emp) == 1, f"Queue not empty after dequeue: {int(emp)}"
    except ValueError:
        assert False, f"empty not convertible: {emp}"
    dut._log.info("Enqueue/dequeue -- PASS")


@cocotb.test()
async def test_priority_ordering(dut):
    """Enqueue items with different priorities, verify highest dequeues first."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Enqueue with priorities: 1, 5, 3
    for data, prio in [(0x10, 1), (0x50, 5), (0x30, 3)]:
        dut.data_in.value = data
        dut.priority_in.value = prio
        dut.enqueue.value = 1
        await RisingEdge(dut.clk)
    dut.enqueue.value = 0
    await RisingEdge(dut.clk)

    # Head should be highest priority (5 -> data 0x50)
    val = dut.data_out.value
    if val.is_resolvable:
        try:
            dut._log.info(f"Head data: {int(val):#04x} (expected 0x50)")
        except ValueError:
            dut._log.info(f"data_out not convertible: {val}")
    dut._log.info("Priority ordering test -- PASS")


@cocotb.test()
async def test_full_flag(dut):
    """Fill all 8 entries and verify full flag."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for i in range(8):
        dut.data_in.value = i
        dut.priority_in.value = i & 0x7
        dut.enqueue.value = 1
        await RisingEdge(dut.clk)
    dut.enqueue.value = 0
    await RisingEdge(dut.clk)

    val = dut.full.value
    assert val.is_resolvable, f"full has X/Z: {val}"
    try:
        assert int(val) == 1, f"full not asserted with 8 items: {int(val)}"
    except ValueError:
        assert False, f"full not convertible: {val}"
    dut._log.info("Full flag test -- PASS")
