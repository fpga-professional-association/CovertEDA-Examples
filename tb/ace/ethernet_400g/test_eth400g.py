"""Cocotb testbench for ace eth400g_top (SystemVerilog).

Drives a 256-bit TX data pattern, waits for the ready handshake, and verifies
output signals have no X/Z.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_eth400g_tx_rx(dut):
    """Drive a TX packet and verify outputs have no X/Z."""

    # Start a 10 ns clock (100 MHz) on clk_ref
    setup_clock(dut, "clk_ref", 10)

    # Initialise inputs
    dut.tx_data.value = 0
    dut.tx_valid.value = 0
    dut.rx_ready.value = 1  # Always ready to receive

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Drive a 256-bit TX data pattern: 0xDEAD...BEEF
    # Build a 256-bit value with DEAD at the top and BEEF at the bottom
    tx_pattern = (0xDEAD << 240) | (0xBEEF)
    # Fill the middle with a recognisable pattern
    tx_pattern |= (0xCAFEBABE_12345678_9ABCDEF0_DEADBEEF << 64)
    tx_pattern |= (0xFEEDFACE_00C0FFEE << 0)

    dut.tx_data.value = tx_pattern
    dut.tx_valid.value = 1
    dut._log.info(f"Driving tx_data = {tx_pattern:#066x}")

    # Wait for tx_ready handshake
    for _ in range(1000):
        await RisingEdge(dut.clk_ref)
        if dut.tx_ready.value.is_resolvable and int(dut.tx_ready.value) == 1:
            break
    else:
        dut._log.warning("tx_ready did not assert within 1000 cycles")

    # Deassert tx_valid after handshake
    await RisingEdge(dut.clk_ref)
    dut.tx_valid.value = 0

    # Run 100 more cycles for pipeline to process
    await ClockCycles(dut.clk_ref, 100)

    # Verify outputs have no X/Z
    rx_data = dut.rx_data.value
    rx_valid = dut.rx_valid.value
    tx_ready_val = dut.tx_ready.value

    assert rx_data.is_resolvable, f"rx_data contains X/Z: {rx_data}"
    assert rx_valid.is_resolvable, f"rx_valid contains X/Z: {rx_valid}"
    assert tx_ready_val.is_resolvable, f"tx_ready contains X/Z: {tx_ready_val}"

    dut._log.info(
        f"Final state: rx_valid={int(rx_valid)}, "
        f"rx_data={int(rx_data):#066x}, tx_ready={int(tx_ready_val)}"
    )
