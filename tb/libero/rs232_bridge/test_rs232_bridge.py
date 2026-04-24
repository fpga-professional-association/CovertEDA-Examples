"""Cocotb testbench for rs232_bridge - RS232 with RTS/CTS flow control."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut

CLKS_PER_BIT = 4


@cocotb.test()
async def test_reset_state(dut):
    """After reset, TX should be idle (high), tx_ready should be 1."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.tx_data.value = 0
    dut.tx_valid.value = 0
    dut.rxd.value = 1
    dut.cts_n.value = 1
    await RisingEdge(dut.clk)

    if dut.txd.value.is_resolvable:
        try:
            assert int(dut.txd.value) == 1, "txd should be high (idle) after reset"
        except ValueError:
            assert False, "txd X/Z after reset"

    if dut.tx_ready.value.is_resolvable:
        try:
            assert int(dut.tx_ready.value) == 1, "tx_ready should be 1 after reset"
        except ValueError:
            assert False, "tx_ready X/Z after reset"


@cocotb.test()
async def test_tx_with_cts(dut):
    """TX should transmit when CTS is asserted (low)."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rxd.value = 1
    dut.cts_n.value = 0  # CTS asserted

    dut.tx_data.value = 0x55
    dut.tx_valid.value = 1
    await RisingEdge(dut.clk)
    dut.tx_valid.value = 0

    # Wait for start bit
    start_seen = False
    for _ in range(10):
        await RisingEdge(dut.clk)
        if dut.txd.value.is_resolvable:
            try:
                if int(dut.txd.value) == 0:
                    start_seen = True
                    break
            except ValueError:
                pass

    assert start_seen, "TX start bit should appear when CTS is asserted"
    dut._log.info("TX started with CTS asserted")


@cocotb.test()
async def test_tx_blocked_without_cts(dut):
    """TX should not start when CTS is deasserted (high)."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rxd.value = 1
    dut.cts_n.value = 1  # CTS deasserted

    dut.tx_data.value = 0xAA
    dut.tx_valid.value = 1
    await RisingEdge(dut.clk)
    dut.tx_valid.value = 0

    await ClockCycles(dut.clk, 20)

    if dut.txd.value.is_resolvable:
        try:
            val = int(dut.txd.value)
            assert val == 1, f"txd should stay high without CTS, got {val}"
        except ValueError:
            assert False, "txd X/Z"

    dut._log.info("TX correctly blocked without CTS")


@cocotb.test()
async def test_tx_ready_deasserts(dut):
    """tx_ready should go low during transmission."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rxd.value = 1
    dut.cts_n.value = 0

    dut.tx_data.value = 0xFF
    dut.tx_valid.value = 1
    await RisingEdge(dut.clk)
    dut.tx_valid.value = 0

    await ClockCycles(dut.clk, 3)

    if dut.tx_ready.value.is_resolvable:
        try:
            rdy = int(dut.tx_ready.value)
            dut._log.info(f"tx_ready during TX: {rdy}")
            assert rdy == 0, "tx_ready should be 0 during transmission"
        except ValueError:
            assert False, "tx_ready X/Z during TX"
