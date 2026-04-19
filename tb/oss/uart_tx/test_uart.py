"""Cocotb testbench for oss uart_top -- UART transmitter.

Verifies that the design resets cleanly, the ready signal asserts,
and the uart_tx output has no X/Z.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles, FallingEdge
from cocotb_helpers import setup_clock, reset_dut


# ~12 MHz iCE40 clock -> 83 ns period
CLK_PERIOD_NS = 83


@cocotb.test()
async def test_uart_tx_byte(dut):
    """Verify transmitter ready signal and uart_tx is not X/Z."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)

    # Initialize inputs
    dut.data_in.value = 0
    dut.valid.value = 0

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 10)

    # Wait until ready is asserted
    ready_seen = False
    for _ in range(100):
        await RisingEdge(dut.clk)
        try:
            if dut.ready.value.is_resolvable and int(dut.ready.value) == 1:
                ready_seen = True
                break
        except ValueError:
            pass

    assert ready_seen, "Transmitter not ready after reset"
    dut._log.info("Transmitter ready signal asserted")

    # Verify uart_tx is in idle state (high) and resolvable
    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after reset"
    uart_tx_val = int(dut.uart_tx.value)
    dut._log.info(f"uart_tx idle state: {uart_tx_val}")
    assert uart_tx_val == 1, f"Expected uart_tx idle high (1), got {uart_tx_val}"

    # Drive data_in and assert valid for one clock cycle
    test_byte = 0x41  # 'A'
    dut.data_in.value = test_byte
    dut.valid.value = 1
    await RisingEdge(dut.clk)
    dut.valid.value = 0

    # Wait for some cycles and verify uart_tx is still resolvable
    await ClockCycles(dut.clk, 200)

    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z during transmission"
    dut._log.info("UART TX test completed: ready asserts, uart_tx is clean")
