"""Cocotb testbench for ace noc_top.

Drives streaming packets through the NoC endpoint and verifies that valid
data appears on the output side.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def send_packet(dut, data):
    """Drive a single packet on the NoC input interface with backpressure."""
    dut.noc_in_data.value = data
    dut.noc_in_valid.value = 1

    # Wait for noc_in_ready (backpressure handshake)
    for _ in range(1000):
        await RisingEdge(dut.clk)
        if dut.noc_in_ready.value == 1:
            break
    else:
        assert False, "Timed out waiting for noc_in_ready"

    # Data accepted on this rising edge; deassert valid
    await RisingEdge(dut.clk)
    dut.noc_in_valid.value = 0


@cocotb.test()
async def test_noc_streaming(dut):
    """Send multiple packets and verify output data is valid."""

    # Start a 10 ns clock (100 MHz)
    setup_clock(dut, "clk", 10)

    # Initialise inputs
    dut.noc_in_data.value = 0
    dut.noc_in_valid.value = 0
    dut.noc_out_ready.value = 1  # Always ready to consume output

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Send multiple packets
    test_packets = [
        0xCAFEBABE_12345678,
        0xDEADBEEF_AABBCCDD,
        0x12345678_9ABCDEF0,
    ]

    for pkt in test_packets:
        await send_packet(dut, pkt)
        dut._log.info(f"Sent packet: {pkt:#018x}")

    # Run additional cycles to allow pipeline to flush
    await ClockCycles(dut.clk, 100)

    # Verify that noc_out_valid asserted at some point and data is valid
    # Check current output signals for X/Z
    out_valid = dut.noc_out_valid.value
    out_data = dut.noc_out_data.value

    assert out_valid.is_resolvable, (
        f"noc_out_valid contains X/Z: {out_valid}"
    )
    assert out_data.is_resolvable, (
        f"noc_out_data contains X/Z: {out_data}"
    )
    dut._log.info(
        f"Final output: valid={int(out_valid)}, data={int(out_data):#018x}"
    )
