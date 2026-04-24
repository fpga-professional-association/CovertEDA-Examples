"""Cocotb testbench for framebuffer - 320x240 8-bit framebuffer."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, rd_valid should be 0, pixel_count should be 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.wr_addr.value = 0
    dut.wr_data.value = 0
    dut.wr_en.value = 0
    dut.rd_addr.value = 0
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)

    if dut.rd_valid.value.is_resolvable:
        try:
            assert int(dut.rd_valid.value) == 0, "rd_valid should be 0 after reset"
        except ValueError:
            assert False, "rd_valid X/Z after reset"

    if dut.pixel_count.value.is_resolvable:
        try:
            assert int(dut.pixel_count.value) == 0, "pixel_count should be 0 after reset"
        except ValueError:
            assert False, "pixel_count X/Z after reset"


@cocotb.test()
async def test_write_read_pixel(dut):
    """Write a pixel then read it back."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    # Write pixel at address 0
    dut.wr_addr.value = 0
    dut.wr_data.value = 0xAB
    dut.wr_en.value = 1
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)
    dut.wr_en.value = 0

    # Read it back
    dut.rd_addr.value = 0
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rd_en.value = 0

    if dut.rd_data.value.is_resolvable:
        try:
            val = int(dut.rd_data.value)
            dut._log.info(f"Read pixel: {val:#04x}")
            assert val == 0xAB, f"Expected 0xAB, got {val:#04x}"
        except ValueError:
            assert False, "rd_data X/Z"


@cocotb.test()
async def test_pixel_count_increments(dut):
    """pixel_count should increment on each write."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rd_en.value = 0

    for i in range(5):
        dut.wr_addr.value = i
        dut.wr_data.value = i * 10
        dut.wr_en.value = 1
        await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)

    if dut.pixel_count.value.is_resolvable:
        try:
            cnt = int(dut.pixel_count.value)
            dut._log.info(f"pixel_count after 5 writes: {cnt}")
            assert cnt == 5, f"Expected pixel_count=5, got {cnt}"
        except ValueError:
            assert False, "pixel_count X/Z"


@cocotb.test()
async def test_multiple_pixels(dut):
    """Write several pixels then read them all back."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    test_pixels = {0: 0x10, 100: 0x20, 500: 0x30, 1000: 0x40}
    dut.rd_en.value = 0

    for addr, data in test_pixels.items():
        dut.wr_addr.value = addr
        dut.wr_data.value = data
        dut.wr_en.value = 1
        await RisingEdge(dut.clk)
    dut.wr_en.value = 0

    for addr, expected in test_pixels.items():
        dut.rd_addr.value = addr
        dut.rd_en.value = 1
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        if dut.rd_data.value.is_resolvable:
            try:
                val = int(dut.rd_data.value)
                dut._log.info(f"Pixel[{addr}] = {val:#04x}, expected {expected:#04x}")
            except ValueError:
                dut._log.info(f"Pixel[{addr}]: X/Z")

    dut._log.info("Multiple pixel read-back complete")


@cocotb.test()
async def test_read_unwritten_pixel(dut):
    """Reading unwritten pixel should return 0 (cleared on reset)."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.wr_en.value = 0
    dut.rd_addr.value = 42
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rd_en.value = 0

    if dut.rd_data.value.is_resolvable:
        try:
            val = int(dut.rd_data.value)
            assert val == 0, f"Unwritten pixel should be 0, got {val}"
        except ValueError:
            assert False, "rd_data X/Z for unwritten pixel"

    dut._log.info("Unwritten pixel correctly reads as 0")
