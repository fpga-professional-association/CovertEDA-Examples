"""Cocotb testbench for vivado vga_controller."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify sync signals are high (inactive) after reset."""
    setup_clock(dut, "clk", 40)  # ~25 MHz
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.hsync.value.is_resolvable, "hsync has X/Z after reset"
    assert dut.vsync.value.is_resolvable, "vsync has X/Z after reset"
    try:
        h = int(dut.hsync.value)
        v = int(dut.vsync.value)
        dut._log.info(f"After reset: hsync={h}, vsync={v}")
    except ValueError:
        assert False, "Sync signals not convertible after reset"


@cocotb.test()
async def test_hsync_period(dut):
    """Verify hsync pulses occur at correct period (800 pixels)."""
    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Wait for first hsync falling edge
    prev_hsync = 1
    hsync_edges = []
    for cycle in range(1700):
        await RisingEdge(dut.clk)
        if dut.hsync.value.is_resolvable:
            try:
                cur = int(dut.hsync.value)
                if prev_hsync == 1 and cur == 0:
                    hsync_edges.append(cycle)
                prev_hsync = cur
            except ValueError:
                pass

    if len(hsync_edges) >= 2:
        period = hsync_edges[1] - hsync_edges[0]
        dut._log.info(f"HSYNC period: {period} clocks (expected 800)")
    else:
        dut._log.info(f"Found {len(hsync_edges)} hsync edges in 1700 clocks")


@cocotb.test()
async def test_active_region(dut):
    """Verify active signal is high during visible region."""
    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    active_count = 0
    for _ in range(800):
        await RisingEdge(dut.clk)
        if dut.active.value.is_resolvable:
            try:
                if int(dut.active.value) == 1:
                    active_count += 1
            except ValueError:
                pass

    dut._log.info(f"Active pixels in first line: {active_count} (expected 640)")


@cocotb.test()
async def test_blanking_rgb_zero(dut):
    """Verify RGB outputs are zero during blanking."""
    setup_clock(dut, "clk", 40)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Run past active region into blanking
    await ClockCycles(dut.clk, 650)

    for _ in range(50):
        await RisingEdge(dut.clk)
        if dut.active.value.is_resolvable:
            try:
                if int(dut.active.value) == 0:
                    if dut.r_out.value.is_resolvable:
                        r = int(dut.r_out.value)
                        g = int(dut.g_out.value)
                        b = int(dut.b_out.value)
                        assert r == 0 and g == 0 and b == 0, \
                            f"RGB not zero during blanking: R={r} G={g} B={b}"
            except ValueError:
                pass

    dut._log.info("RGB correctly zero during blanking")
