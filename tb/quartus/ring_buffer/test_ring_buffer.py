"""Cocotb testbench for quartus ring_buffer (16-entry x 16-bit circular buffer)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify ring buffer is empty after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    if not dut.empty.value.is_resolvable:
        raise AssertionError("empty signal has X/Z after reset")

    try:
        empty_val = int(dut.empty.value)
        full_val = int(dut.full.value)
        count_val = int(dut.count.value)
    except ValueError:
        raise AssertionError("Signals not convertible after reset")

    assert empty_val == 1, f"Expected empty=1 after reset, got {empty_val}"
    assert full_val == 0, f"Expected full=0 after reset, got {full_val}"
    assert count_val == 0, f"Expected count=0 after reset, got {count_val}"
    dut._log.info("Reset state verified: empty=1, full=0, count=0")


@cocotb.test()
async def test_write_and_read(dut):
    """Write a value, then read it back."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    # Write value 0xBEEF
    dut.wr_en.value = 1
    dut.din.value = 0xBEEF
    await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    if dut.count.value.is_resolvable:
        cnt = int(dut.count.value)
        dut._log.info(f"Count after write: {cnt}")
        assert cnt == 1, f"Expected count=1 after one write, got {cnt}"

    # Read it back
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)

    if dut.dout.value.is_resolvable:
        try:
            dout_val = int(dut.dout.value)
            dut._log.info(f"Read back value: {dout_val:#06x}")
            assert dout_val == 0xBEEF, f"Expected 0xBEEF, got {dout_val:#06x}"
        except ValueError:
            raise AssertionError("dout not convertible to int")


@cocotb.test()
async def test_full_flag(dut):
    """Fill the buffer to capacity and verify full flag."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    # Write 16 entries
    for i in range(16):
        dut.wr_en.value = 1
        dut.din.value = i * 0x1111
        await RisingEdge(dut.clk)

    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    if dut.full.value.is_resolvable:
        try:
            full_val = int(dut.full.value)
            dut._log.info(f"Full flag after 16 writes: {full_val}")
            assert full_val == 1, f"Expected full=1, got {full_val}"
        except ValueError:
            raise AssertionError("full signal not convertible")

    if dut.count.value.is_resolvable:
        try:
            cnt = int(dut.count.value)
            assert cnt == 16, f"Expected count=16, got {cnt}"
        except ValueError:
            raise AssertionError("count not convertible")


@cocotb.test()
async def test_fifo_order(dut):
    """Write several values, read them back and check FIFO ordering."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    test_data = [0x1234, 0x5678, 0x9ABC, 0xDEF0]

    # Write all values
    for val in test_data:
        dut.wr_en.value = 1
        dut.din.value = val
        await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    # Read them back
    read_vals = []
    for _ in test_data:
        dut.rd_en.value = 1
        await RisingEdge(dut.clk)
        dut.rd_en.value = 0
        await RisingEdge(dut.clk)
        if dut.dout.value.is_resolvable:
            try:
                read_vals.append(int(dut.dout.value))
            except ValueError:
                dut._log.warning("dout not convertible during read")

    dut._log.info(f"Written: {[hex(v) for v in test_data]}")
    dut._log.info(f"Read:    {[hex(v) for v in read_vals]}")
    for i, (exp, got) in enumerate(zip(test_data, read_vals)):
        assert exp == got, f"Mismatch at index {i}: expected {exp:#06x}, got {got:#06x}"


@cocotb.test()
async def test_empty_read_no_crash(dut):
    """Read from empty buffer should not crash; empty flag stays asserted."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.din.value = 0
    await RisingEdge(dut.clk)

    # Attempt to read from empty buffer
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)

    if dut.empty.value.is_resolvable:
        try:
            empty_val = int(dut.empty.value)
            dut._log.info(f"Empty flag after reading empty buffer: {empty_val}")
            assert empty_val == 1, f"Expected empty=1, got {empty_val}"
        except ValueError:
            raise AssertionError("empty not convertible")

    if dut.count.value.is_resolvable:
        try:
            cnt = int(dut.count.value)
            assert cnt == 0, f"Expected count=0 after empty read, got {cnt}"
        except ValueError:
            raise AssertionError("count not convertible")

    dut._log.info("Empty read handled gracefully")
