"""Cocotb testbench for vivado uart_top echo design."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


# 100 MHz system clock -> 10 ns period
CLK_PERIOD_NS = 10


@cocotb.test()
async def test_uart_echo(dut):
    """Verify UART echo design resets cleanly and outputs have no X/Z."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)

    # UART idle state is high
    dut.uart_rx.value = 1

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    # Verify uart_tx is resolvable and in idle state
    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after reset"
    tx_val = int(dut.uart_tx.value)
    dut._log.info(f"uart_tx after reset: {tx_val}")
    assert tx_val == 1, f"Expected uart_tx idle high (1), got {tx_val}"

    # Run for more cycles to verify stability
    await ClockCycles(dut.clk, 200)

    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after 200 cycles"
    dut._log.info("UART echo design runs cleanly with no X/Z on uart_tx")
