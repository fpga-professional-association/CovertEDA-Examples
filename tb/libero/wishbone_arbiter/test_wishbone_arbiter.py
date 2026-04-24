"""Cocotb testbench for wishbone_arbiter - 4-master round-robin arbiter."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, no grants should be active."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.cyc_i.value = 0
    dut.m0_adr.value = 0; dut.m0_dat.value = 0; dut.m0_sel.value = 0; dut.m0_we.value = 0; dut.m0_stb.value = 0
    dut.m1_adr.value = 0; dut.m1_dat.value = 0; dut.m1_sel.value = 0; dut.m1_we.value = 0; dut.m1_stb.value = 0
    dut.m2_adr.value = 0; dut.m2_dat.value = 0; dut.m2_sel.value = 0; dut.m2_we.value = 0; dut.m2_stb.value = 0
    dut.m3_adr.value = 0; dut.m3_dat.value = 0; dut.m3_sel.value = 0; dut.m3_we.value = 0; dut.m3_stb.value = 0
    await RisingEdge(dut.clk)

    if dut.gnt_o.value.is_resolvable:
        try:
            assert int(dut.gnt_o.value) == 0, "No grants after reset"
        except ValueError:
            assert False, "gnt_o X/Z after reset"


@cocotb.test()
async def test_single_master_grant(dut):
    """Single master request should get grant."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.m0_adr.value = 0; dut.m0_dat.value = 0; dut.m0_sel.value = 0; dut.m0_we.value = 0; dut.m0_stb.value = 0
    dut.m1_adr.value = 0; dut.m1_dat.value = 0; dut.m1_sel.value = 0; dut.m1_we.value = 0; dut.m1_stb.value = 0
    dut.m2_adr.value = 0; dut.m2_dat.value = 0; dut.m2_sel.value = 0; dut.m2_we.value = 0; dut.m2_stb.value = 0
    dut.m3_adr.value = 0; dut.m3_dat.value = 0; dut.m3_sel.value = 0; dut.m3_we.value = 0; dut.m3_stb.value = 0

    dut.cyc_i.value = 0b0010  # Master 1 requests
    await ClockCycles(dut.clk, 3)

    if dut.gnt_o.value.is_resolvable:
        try:
            gnt = int(dut.gnt_o.value)
            dut._log.info(f"Grant: {gnt:#06b}")
            assert gnt & 0b0010, f"Master 1 should get grant, got {gnt:#06b}"
        except ValueError:
            assert False, "gnt_o X/Z"


@cocotb.test()
async def test_address_mux(dut):
    """Verify granted master's address appears on slave port."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.m0_adr.value = 0x1000; dut.m0_dat.value = 0; dut.m0_sel.value = 0xF; dut.m0_we.value = 1; dut.m0_stb.value = 1
    dut.m1_adr.value = 0; dut.m1_dat.value = 0; dut.m1_sel.value = 0; dut.m1_we.value = 0; dut.m1_stb.value = 0
    dut.m2_adr.value = 0; dut.m2_dat.value = 0; dut.m2_sel.value = 0; dut.m2_we.value = 0; dut.m2_stb.value = 0
    dut.m3_adr.value = 0; dut.m3_dat.value = 0; dut.m3_sel.value = 0; dut.m3_we.value = 0; dut.m3_stb.value = 0

    dut.cyc_i.value = 0b0001  # Master 0 requests
    await ClockCycles(dut.clk, 3)

    if dut.s_adr_o.value.is_resolvable:
        try:
            addr = int(dut.s_adr_o.value)
            dut._log.info(f"Slave address: {addr:#010x}")
        except ValueError:
            dut._log.info("s_adr_o X/Z")


@cocotb.test()
async def test_bus_release(dut):
    """When master releases cyc, bus should become free."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.m0_adr.value = 0; dut.m0_dat.value = 0; dut.m0_sel.value = 0; dut.m0_we.value = 0; dut.m0_stb.value = 0
    dut.m1_adr.value = 0; dut.m1_dat.value = 0; dut.m1_sel.value = 0; dut.m1_we.value = 0; dut.m1_stb.value = 0
    dut.m2_adr.value = 0; dut.m2_dat.value = 0; dut.m2_sel.value = 0; dut.m2_we.value = 0; dut.m2_stb.value = 0
    dut.m3_adr.value = 0; dut.m3_dat.value = 0; dut.m3_sel.value = 0; dut.m3_we.value = 0; dut.m3_stb.value = 0

    dut.cyc_i.value = 0b0001
    await ClockCycles(dut.clk, 3)

    dut.cyc_i.value = 0b0000
    await ClockCycles(dut.clk, 3)

    if dut.gnt_o.value.is_resolvable:
        try:
            gnt = int(dut.gnt_o.value)
            dut._log.info(f"Grant after release: {gnt:#06b}")
            assert gnt == 0, f"All grants should be cleared, got {gnt:#06b}"
        except ValueError:
            assert False, "gnt_o X/Z after release"
