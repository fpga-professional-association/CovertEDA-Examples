"""Cocotb testbench for diamond serdes_top – software loopback test.

Since we cannot model a real SERDES transceiver in Icarus, we use a cocotb
coroutine to continuously copy serdes_tx_p -> serdes_rx_p and
serdes_tx_n -> serdes_rx_n each clock cycle, creating a software loopback.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def loopback_driver(dut, num_cycles):
    """Copy TX differential signals to RX each clock cycle."""
    for _ in range(num_cycles):
        await RisingEdge(dut.ref_clk)
        try:
            dut.serdes_rx_p.value = int(dut.serdes_tx_p.value)
            dut.serdes_rx_n.value = int(dut.serdes_tx_n.value)
        except ValueError:
            # TX may contain X/Z early in simulation; drive 0 as default
            dut.serdes_rx_p.value = 0
            dut.serdes_rx_n.value = 1


@cocotb.test()
async def test_loopback(dut):
    """Configure loopback mode, connect tx->rx, check prbs_status_led."""

    # Start ~3.2 ns clock (312.5 MHz)
    setup_clock(dut, "ref_clk", 3.2)

    # Initialize inputs
    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0  # loopback mode

    # Reset (active-low reset_n)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 10)

    # Launch the loopback coroutine for 200 cycles
    cocotb.start_soon(loopback_driver(dut, 200))

    # Run 200 cycles to let the PRBS checker lock
    await ClockCycles(dut.ref_clk, 200)

    # Check prbs_status_led for any lock indication (non-zero)
    status = dut.prbs_status_led.value
    dut._log.info(f"PRBS status LED: {int(status):#010b}")

    try:
        status_int = int(status)
    except ValueError:
        assert False, f"prbs_status_led contains X/Z: {status}"

    assert status_int != 0, (
        f"Expected prbs_status_led to show lock (non-zero), got {status_int:#010b}"
    )
    dut._log.info("SERDES loopback test passed -- PRBS lock detected")
