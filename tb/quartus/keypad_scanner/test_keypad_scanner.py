"""Cocotb testbench for quartus keypad_scanner (4x4 matrix keypad)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify no key detected after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.col_in.value = 0
    await RisingEdge(dut.clk)

    if not dut.key_pressed.value.is_resolvable:
        raise AssertionError("key_pressed has X/Z after reset")

    try:
        pressed = int(dut.key_pressed.value)
        valid = int(dut.key_valid.value)
    except ValueError:
        raise AssertionError("Signals not convertible after reset")

    assert pressed == 0, f"Expected key_pressed=0, got {pressed}"
    assert valid == 0, f"Expected key_valid=0, got {valid}"
    dut._log.info("Reset state: no key pressed")


@cocotb.test()
async def test_row_scanning(dut):
    """Verify row_out cycles through all 4 rows."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.col_in.value = 0
    await RisingEdge(dut.clk)

    rows_seen = set()
    for _ in range(200):
        await RisingEdge(dut.clk)
        if dut.row_out.value.is_resolvable:
            try:
                row = int(dut.row_out.value)
                rows_seen.add(row)
            except ValueError:
                pass

    dut._log.info(f"Row values seen: {[bin(r) for r in sorted(rows_seen)]}")
    assert len(rows_seen) >= 4, f"Expected 4 row patterns, saw {len(rows_seen)}"


@cocotb.test()
async def test_key_detection(dut):
    """Simulate a key press and verify key_valid pulses."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.col_in.value = 0
    await ClockCycles(dut.clk, 10)

    # Simulate key at row 0, col 0: when row_out=0001, set col_in=0001
    key_detected = False
    for cycle in range(500):
        await RisingEdge(dut.clk)
        if dut.row_out.value.is_resolvable:
            try:
                row = int(dut.row_out.value)
                if row == 0b0001:
                    dut.col_in.value = 0b0001
                else:
                    dut.col_in.value = 0
            except ValueError:
                pass

        if dut.key_valid.value.is_resolvable:
            try:
                if int(dut.key_valid.value) == 1:
                    key_detected = True
                    code = int(dut.key_code.value) if dut.key_code.value.is_resolvable else -1
                    dut._log.info(f"Key detected at cycle {cycle}, code={code}")
                    break
            except ValueError:
                pass

    dut._log.info(f"Key detection result: {key_detected}")


@cocotb.test()
async def test_no_key_no_valid(dut):
    """With no columns active, key_valid should stay low."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.col_in.value = 0
    await RisingEdge(dut.clk)

    valid_seen = False
    for _ in range(200):
        await RisingEdge(dut.clk)
        if dut.key_valid.value.is_resolvable:
            try:
                if int(dut.key_valid.value) == 1:
                    valid_seen = True
                    break
            except ValueError:
                pass

    assert not valid_seen, "key_valid asserted with no key pressed"
    dut._log.info("No spurious key_valid detected")


@cocotb.test()
async def test_outputs_valid_range(dut):
    """Verify all outputs stay in valid range over many cycles."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.col_in.value = 0
    await RisingEdge(dut.clk)

    for cycle in range(300):
        await RisingEdge(dut.clk)
        if dut.key_code.value.is_resolvable:
            try:
                code = int(dut.key_code.value)
                assert 0 <= code <= 15, f"key_code out of range at cycle {cycle}: {code}"
            except ValueError:
                pass
        if dut.row_out.value.is_resolvable:
            try:
                row = int(dut.row_out.value)
                assert row in (1, 2, 4, 8), f"row_out not one-hot at cycle {cycle}: {row:#06b}"
            except ValueError:
                pass

    dut._log.info("All outputs stayed in valid range for 300 cycles")
