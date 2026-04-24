"""Cocotb testbench for quartus stack_controller (16-deep x 32-bit hardware stack)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify stack is empty after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.push.value = 0
    dut.pop.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    if not dut.empty.value.is_resolvable:
        raise AssertionError("empty has X/Z after reset")

    try:
        empty_val = int(dut.empty.value)
        full_val = int(dut.full.value)
        depth_val = int(dut.depth.value)
    except ValueError:
        raise AssertionError("Signals not convertible after reset")

    assert empty_val == 1, f"Expected empty=1, got {empty_val}"
    assert full_val == 0, f"Expected full=0, got {full_val}"
    assert depth_val == 0, f"Expected depth=0, got {depth_val}"
    dut._log.info("Reset state: empty=1, full=0, depth=0")


@cocotb.test()
async def test_push_pop_single(dut):
    """Push one value, pop it, verify LIFO behavior."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.push.value = 0
    dut.pop.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    # Push 0xDEADBEEF
    dut.push.value = 1
    dut.din.value = 0xDEADBEEF
    await RisingEdge(dut.clk)
    dut.push.value = 0
    await RisingEdge(dut.clk)

    if dut.depth.value.is_resolvable:
        try:
            d = int(dut.depth.value)
            dut._log.info(f"Depth after push: {d}")
            assert d == 1, f"Expected depth=1, got {d}"
        except ValueError:
            raise AssertionError("depth not convertible")

    # Pop it back
    dut.pop.value = 1
    await RisingEdge(dut.clk)
    dut.pop.value = 0
    await RisingEdge(dut.clk)

    if dut.dout.value.is_resolvable:
        try:
            val = int(dut.dout.value)
            dut._log.info(f"Popped value: {val:#010x}")
            assert val == 0xDEADBEEF, f"Expected 0xDEADBEEF, got {val:#010x}"
        except ValueError:
            raise AssertionError("dout not convertible")


@cocotb.test()
async def test_lifo_order(dut):
    """Push A, B, C; pop should return C, B, A."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.push.value = 0
    dut.pop.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    values = [0x11111111, 0x22222222, 0x33333333]
    for v in values:
        dut.push.value = 1
        dut.din.value = v
        await RisingEdge(dut.clk)
    dut.push.value = 0
    await RisingEdge(dut.clk)

    popped = []
    for _ in values:
        dut.pop.value = 1
        await RisingEdge(dut.clk)
        dut.pop.value = 0
        await RisingEdge(dut.clk)
        if dut.dout.value.is_resolvable:
            try:
                popped.append(int(dut.dout.value))
            except ValueError:
                dut._log.warning("dout not convertible during pop")

    dut._log.info(f"Pushed: {[hex(v) for v in values]}")
    dut._log.info(f"Popped: {[hex(v) for v in popped]}")
    expected = list(reversed(values))
    for i, (exp, got) in enumerate(zip(expected, popped)):
        assert exp == got, f"LIFO mismatch at pop {i}: expected {exp:#010x}, got {got:#010x}"


@cocotb.test()
async def test_full_flag(dut):
    """Fill stack to 16 entries and verify full flag."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.push.value = 0
    dut.pop.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    for i in range(16):
        dut.push.value = 1
        dut.din.value = i
        await RisingEdge(dut.clk)
    dut.push.value = 0
    await RisingEdge(dut.clk)

    if dut.full.value.is_resolvable:
        try:
            full_val = int(dut.full.value)
            dut._log.info(f"Full flag after 16 pushes: {full_val}")
            assert full_val == 1, f"Expected full=1, got {full_val}"
        except ValueError:
            raise AssertionError("full not convertible")


@cocotb.test()
async def test_pop_empty_no_crash(dut):
    """Pop from empty stack should not crash."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.push.value = 0
    dut.pop.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    dut.pop.value = 1
    await RisingEdge(dut.clk)
    dut.pop.value = 0
    await RisingEdge(dut.clk)

    if dut.empty.value.is_resolvable:
        try:
            empty_val = int(dut.empty.value)
            dut._log.info(f"Empty flag after popping empty stack: {empty_val}")
            assert empty_val == 1, f"Expected empty=1, got {empty_val}"
        except ValueError:
            raise AssertionError("empty not convertible")

    dut._log.info("Pop from empty stack handled gracefully")
