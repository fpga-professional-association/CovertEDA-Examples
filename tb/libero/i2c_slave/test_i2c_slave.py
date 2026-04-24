"""Cocotb testbench for i2c_slave - I2C slave with register map."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, sda_oe should be 0 (not driving)."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.scl_in.value = 1
    dut.sda_in.value = 1
    dut.reg_rdata.value = 0
    await RisingEdge(dut.clk)

    if dut.sda_oe.value.is_resolvable:
        try:
            assert int(dut.sda_oe.value) == 0, "sda_oe should be 0 after reset"
        except ValueError:
            assert False, "sda_oe X/Z after reset"


@cocotb.test()
async def test_idle_no_drive(dut):
    """With both lines high (idle), slave should not drive SDA."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.scl_in.value = 1
    dut.sda_in.value = 1
    dut.reg_rdata.value = 0

    await ClockCycles(dut.clk, 50)

    if dut.sda_oe.value.is_resolvable:
        try:
            assert int(dut.sda_oe.value) == 0, "Should not drive SDA in idle"
        except ValueError:
            assert False, "sda_oe X/Z in idle"

    if dut.reg_wr.value.is_resolvable:
        try:
            assert int(dut.reg_wr.value) == 0, "No writes in idle"
        except ValueError:
            pass

    dut._log.info("Slave correctly idle with no bus activity")


@cocotb.test()
async def test_outputs_stable(dut):
    """Verify all outputs are stable and resolvable after reset."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.scl_in.value = 1
    dut.sda_in.value = 1
    dut.reg_rdata.value = 0
    await ClockCycles(dut.clk, 10)

    for sig_name in ["sda_out", "sda_oe", "reg_addr", "reg_wdata", "reg_wr"]:
        sig = getattr(dut, sig_name)
        if not sig.value.is_resolvable:
            assert False, f"{sig_name} X/Z after reset"
        try:
            int(sig.value)
        except ValueError:
            assert False, f"{sig_name} not convertible"

    dut._log.info("All outputs stable and resolvable")
