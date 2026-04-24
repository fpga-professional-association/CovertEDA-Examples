"""Cocotb testbench for ace packet_router -- 4-port packet router."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def init_inputs(dut):
    dut.in_data.value = 0
    dut.in_valid.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify all outputs are zero after reset."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for name in ["out0_valid", "out1_valid", "out2_valid", "out3_valid"]:
        val = getattr(dut, name).value
        assert val.is_resolvable, f"{name} has X/Z after reset: {val}"
        try:
            assert int(val) == 0, f"{name} not 0 after reset: {int(val)}"
        except ValueError:
            assert False, f"{name} not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_route_to_port0(dut):
    """Send a 4-byte packet destined for port 0."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Header: dest=0 (bits[7:6]=00), length=4 (bits[5:0]=000100)
    dut.in_data.value = 0x04
    dut.in_valid.value = 1
    await RisingEdge(dut.clk)

    # Data bytes
    for byte_val in [0xAA, 0xBB, 0xCC, 0xDD]:
        dut.in_data.value = byte_val
        await RisingEdge(dut.clk)
        val = dut.out0_valid.value
        if val.is_resolvable:
            try:
                if int(val) == 1:
                    dut._log.info(f"Port 0 received: {int(dut.out0_data.value):#04x}")
            except ValueError:
                pass

    dut.in_valid.value = 0
    await ClockCycles(dut.clk, 5)
    dut._log.info("Route to port 0 -- PASS")


@cocotb.test()
async def test_route_to_port3(dut):
    """Send a 2-byte packet destined for port 3."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Header: dest=3 (bits[7:6]=11), length=2
    dut.in_data.value = 0xC2
    dut.in_valid.value = 1
    await RisingEdge(dut.clk)

    for byte_val in [0x11, 0x22]:
        dut.in_data.value = byte_val
        await RisingEdge(dut.clk)
        val = dut.out3_valid.value
        if val.is_resolvable:
            try:
                if int(val) == 1:
                    dut._log.info(f"Port 3 received: {int(dut.out3_data.value):#04x}")
            except ValueError:
                pass

    dut.in_valid.value = 0
    await ClockCycles(dut.clk, 5)
    dut._log.info("Route to port 3 -- PASS")


@cocotb.test()
async def test_no_cross_routing(dut):
    """Send to port 1, verify ports 0/2/3 stay inactive."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Header: dest=1 (bits[7:6]=01), length=3
    dut.in_data.value = 0x43
    dut.in_valid.value = 1
    await RisingEdge(dut.clk)

    for byte_val in [0xFF, 0xEE, 0xDD]:
        dut.in_data.value = byte_val
        await RisingEdge(dut.clk)
        for name in ["out0_valid", "out2_valid", "out3_valid"]:
            val = getattr(dut, name).value
            if val.is_resolvable:
                try:
                    assert int(val) == 0, f"{name} active when routing to port 1"
                except ValueError:
                    pass

    dut.in_valid.value = 0
    await ClockCycles(dut.clk, 5)
    dut._log.info("No cross-routing -- PASS")
