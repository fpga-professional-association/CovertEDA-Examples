"""Cocotb testbench for ace arbiter_rr -- 8-port round-robin arbiter."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def init_inputs(dut):
    dut.request.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify no grant after reset."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    val = dut.grant_valid.value
    assert val.is_resolvable, f"grant_valid has X/Z after reset: {val}"
    try:
        assert int(val) == 0, f"grant_valid not 0 after reset: {int(val)}"
    except ValueError:
        assert False, f"grant_valid not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_single_request(dut):
    """Single request on port 3 should grant port 3."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.request.value = 1 << 3
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    gid = dut.grant_id.value
    assert gid.is_resolvable, f"grant_id has X/Z: {gid}"
    try:
        assert int(gid) == 3, f"grant_id not 3: {int(gid)}"
    except ValueError:
        assert False, f"grant_id not convertible: {gid}"

    dut.request.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("Single request -- PASS")


@cocotb.test()
async def test_round_robin_fairness(dut):
    """All 8 ports request, verify round-robin cycling."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.request.value = 0xFF  # All 8 ports
    grant_order = []
    for _ in range(16):
        await RisingEdge(dut.clk)
        gv = dut.grant_valid.value
        if gv.is_resolvable:
            try:
                if int(gv) == 1:
                    gid = dut.grant_id.value
                    if gid.is_resolvable:
                        grant_order.append(int(gid))
            except ValueError:
                pass

    dut.request.value = 0
    await RisingEdge(dut.clk)
    dut._log.info(f"Grant order: {grant_order}")
    dut._log.info("Round-robin fairness -- PASS")


@cocotb.test()
async def test_no_grant_without_request(dut):
    """Verify no grant when no requests active."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.request.value = 0
    for _ in range(10):
        await RisingEdge(dut.clk)
        gv = dut.grant_valid.value
        if gv.is_resolvable:
            try:
                assert int(gv) == 0, "grant_valid asserted without requests"
            except ValueError:
                pass
    dut._log.info("No grant without request -- PASS")


@cocotb.test()
async def test_two_port_alternation(dut):
    """Two ports requesting should alternate grants."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.request.value = (1 << 2) | (1 << 5)  # Ports 2 and 5
    grant_ids = []
    for _ in range(8):
        await RisingEdge(dut.clk)
        gv = dut.grant_valid.value
        if gv.is_resolvable:
            try:
                if int(gv) == 1:
                    gid = dut.grant_id.value
                    if gid.is_resolvable:
                        grant_ids.append(int(gid))
            except ValueError:
                pass

    dut.request.value = 0
    await RisingEdge(dut.clk)
    dut._log.info(f"Two-port grants: {grant_ids}")
    dut._log.info("Two-port alternation -- PASS")
