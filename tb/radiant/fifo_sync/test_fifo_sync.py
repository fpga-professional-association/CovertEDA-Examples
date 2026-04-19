"""Cocotb testbench for radiant fifo_sync."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_empty(dut):
    """Verify FIFO is empty after reset."""
    setup_clock(dut, "clk", 40)
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.empty.value.is_resolvable, "empty has X/Z after reset"
    assert dut.full.value.is_resolvable, "full has X/Z after reset"
    try:
        e = int(dut.empty.value)
        f = int(dut.full.value)
        assert e == 1, f"FIFO not empty after reset: empty={e}"
        assert f == 0, f"FIFO full after reset: full={f}"
        dut._log.info("Reset state OK: empty=1, full=0")
    except ValueError:
        raise AssertionError("Flags not resolvable after reset")


@cocotb.test()
async def test_write_read_single(dut):
    """Write one item, read it back, verify data integrity."""
    setup_clock(dut, "clk", 40)
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write 0xAB
    dut.wr_data.value = 0xAB
    dut.wr_en.value = 1
    await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # Verify not empty
    assert dut.empty.value.is_resolvable, "empty has X/Z after write"
    try:
        assert int(dut.empty.value) == 0, "FIFO still empty after write"
    except ValueError:
        raise AssertionError("empty not resolvable")

    # Read - assert rd_en for one cycle, data appears on rd_data after the edge
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    dut.rd_en.value = 0
    await Timer(1, unit="ns")

    assert dut.rd_data.value.is_resolvable, "rd_data has X/Z"
    try:
        rd = int(dut.rd_data.value)
        assert rd == 0xAB, f"Read data mismatch: {rd:#04x} != 0xAB"
        dut._log.info(f"Write/read single OK: {rd:#04x}")
    except ValueError:
        raise AssertionError("rd_data not resolvable")


@cocotb.test()
async def test_fill_to_full(dut):
    """Write 8 items and verify full flag asserts."""
    setup_clock(dut, "clk", 40)
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write 8 items one per clock cycle
    for i in range(8):
        dut.wr_data.value = i + 1
        dut.wr_en.value = 1
        await RisingEdge(dut.clk)

    dut.wr_en.value = 0
    await Timer(1, unit="ns")

    assert dut.full.value.is_resolvable, "full has X/Z"
    try:
        f = int(dut.full.value)
        cnt = int(dut.count.value) if dut.count.value.is_resolvable else -1
        dut._log.info(f"After 8 writes: full={f}, count={cnt}")
        assert f == 1, f"FIFO not full after 8 writes: full={f}, count={cnt}"
        dut._log.info("FIFO full after 8 writes OK")
    except ValueError:
        raise AssertionError("full not resolvable")


@cocotb.test()
async def test_fifo_ordering(dut):
    """Write sequential values, read them back in order."""
    setup_clock(dut, "clk", 40)
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write 5 values
    for i in range(5):
        dut.wr_data.value = (i + 1) * 10
        dut.wr_en.value = 1
        await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    # Read 5 values - registered output means data appears after the edge
    read_vals = []
    for i in range(5):
        dut.rd_en.value = 1
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if dut.rd_data.value.is_resolvable:
            try:
                read_vals.append(int(dut.rd_data.value))
            except ValueError:
                pass
    dut.rd_en.value = 0

    expected = [10, 20, 30, 40, 50]
    dut._log.info(f"Read values: {read_vals}")
    assert read_vals == expected, f"FIFO order mismatch: {read_vals} != {expected}"


@cocotb.test()
async def test_overflow_protection(dut):
    """Write more than 8 items and verify FIFO does not corrupt."""
    setup_clock(dut, "clk", 40)
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.wr_data.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write 10 items (2 overflow)
    for i in range(10):
        dut.wr_data.value = i
        dut.wr_en.value = 1
        await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # Read all available and verify count
    assert dut.count.value.is_resolvable, "count has X/Z"
    try:
        cnt = int(dut.count.value)
        dut._log.info(f"FIFO count after 10 writes: {cnt}")
        assert cnt <= 8, f"FIFO count exceeds depth: {cnt}"
    except ValueError:
        raise AssertionError("count not resolvable")
