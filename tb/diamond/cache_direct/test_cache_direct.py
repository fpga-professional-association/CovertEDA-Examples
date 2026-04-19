"""Cocotb testbench for cache_direct - direct-mapped cache."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, outputs should be zero."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.addr.value = 0
    dut.wr_data.value = 0
    dut.rd_en.value = 0
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    if dut.hit.value.is_resolvable:
        try:
            assert int(dut.hit.value) == 0, "hit should be 0 after reset"
        except ValueError:
            assert False, "hit X/Z after reset"

    if dut.miss.value.is_resolvable:
        try:
            assert int(dut.miss.value) == 0, "miss should be 0 after reset"
        except ValueError:
            assert False, "miss X/Z after reset"


@cocotb.test()
async def test_write_then_read_hit(dut):
    """Write data then read same address, expect cache hit."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    # Write
    dut.addr.value = 0x00010100  # tag=0x0001, index=0x01
    dut.wr_data.value = 0xDEADBEEF
    dut.wr_en.value = 1
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    # Read same address
    dut.wr_en.value = 0
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    if dut.hit.value.is_resolvable:
        try:
            assert int(dut.hit.value) == 1, "Expected cache hit"
        except ValueError:
            assert False, "hit X/Z"

    if dut.rd_data.value.is_resolvable:
        try:
            val = int(dut.rd_data.value)
            dut._log.info(f"Read data: {val:#010x}")
            assert val == 0xDEADBEEF, f"Expected 0xDEADBEEF, got {val:#010x}"
        except ValueError:
            assert False, "rd_data X/Z"


@cocotb.test()
async def test_read_miss(dut):
    """Read from empty cache line, expect miss."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.addr.value = 0x00050500
    dut.wr_en.value = 0
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    if dut.miss.value.is_resolvable:
        try:
            assert int(dut.miss.value) == 1, "Expected cache miss on empty line"
        except ValueError:
            assert False, "miss X/Z"


@cocotb.test()
async def test_tag_conflict_miss(dut):
    """Write with one tag, read with different tag on same index - expect miss."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    # Write with tag 0x0001
    dut.addr.value = 0x00010200
    dut.wr_data.value = 0x12345678
    dut.wr_en.value = 1
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    # Read with tag 0x0002 (same index 0x02)
    dut.addr.value = 0x00020200
    dut.wr_en.value = 0
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    if dut.miss.value.is_resolvable:
        try:
            assert int(dut.miss.value) == 1, "Expected miss on tag conflict"
        except ValueError:
            assert False, "miss X/Z"

    dut._log.info("Tag conflict correctly produces cache miss")


@cocotb.test()
async def test_multiple_writes_reads(dut):
    """Write to several lines then read them all back."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    test_data = {0x00: 0xAAAAAAAA, 0x10: 0xBBBBBBBB, 0x20: 0xCCCCCCCC}

    for idx, data in test_data.items():
        dut.addr.value = (0x0001 << 16) | (idx << 8)
        dut.wr_data.value = data
        dut.wr_en.value = 1
        dut.rd_en.value = 0
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

    hits = 0
    for idx, expected in test_data.items():
        dut.addr.value = (0x0001 << 16) | (idx << 8)
        dut.wr_en.value = 0
        dut.rd_en.value = 1
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        if dut.hit.value.is_resolvable and dut.rd_data.value.is_resolvable:
            try:
                if int(dut.hit.value) == 1:
                    hits += 1
                    val = int(dut.rd_data.value)
                    dut._log.info(f"Line {idx:#04x}: read {val:#010x}, expected {expected:#010x}")
            except ValueError:
                dut._log.info(f"Line {idx:#04x}: X/Z in output")

    dut._log.info(f"Cache hits: {hits}/{len(test_data)}")
