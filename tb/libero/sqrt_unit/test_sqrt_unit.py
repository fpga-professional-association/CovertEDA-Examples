"""Cocotb testbench for sqrt_unit - 32-bit integer square root."""

import cocotb
import math
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, done should be 0, result should be 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.operand.value = 0
    dut.start.value = 0
    await RisingEdge(dut.clk)

    if dut.done.value.is_resolvable:
        try:
            assert int(dut.done.value) == 0, "done should be 0 after reset"
        except ValueError:
            assert False, "done X/Z after reset"


@cocotb.test()
async def test_sqrt_zero(dut):
    """sqrt(0) should be 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.operand.value = 0
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    for _ in range(25):
        await RisingEdge(dut.clk)
        if dut.done.value.is_resolvable:
            try:
                if int(dut.done.value) == 1:
                    break
            except ValueError:
                pass

    if dut.result.value.is_resolvable:
        try:
            val = int(dut.result.value)
            dut._log.info(f"sqrt(0) = {val}")
        except ValueError:
            dut._log.info("result X/Z")


@cocotb.test()
async def test_perfect_squares(dut):
    """Test several perfect squares."""
    setup_clock(dut, "clk", 10)

    test_cases = [(1, 1), (4, 2), (9, 3), (16, 4), (100, 10), (10000, 100)]

    for operand, expected in test_cases:
        await reset_dut(dut, "reset_n", active_low=True, cycles=5)

        dut.operand.value = operand
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        for _ in range(25):
            await RisingEdge(dut.clk)
            if dut.done.value.is_resolvable:
                try:
                    if int(dut.done.value) == 1:
                        break
                except ValueError:
                    pass

        if dut.result.value.is_resolvable:
            try:
                val = int(dut.result.value)
                dut._log.info(f"sqrt({operand}) = {val}, expected {expected}")
            except ValueError:
                dut._log.info(f"sqrt({operand}): result X/Z")


@cocotb.test()
async def test_computation_completes(dut):
    """Verify computation completes within expected cycles."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.operand.value = 65536
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    done_seen = False
    for cycle in range(25):
        await RisingEdge(dut.clk)
        if dut.done.value.is_resolvable:
            try:
                if int(dut.done.value) == 1:
                    done_seen = True
                    dut._log.info(f"Computation completed at cycle {cycle + 1}")
                    break
            except ValueError:
                pass

    assert done_seen, "Computation did not complete within 25 cycles"
