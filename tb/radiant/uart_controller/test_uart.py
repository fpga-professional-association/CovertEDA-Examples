"""Cocotb testbench for radiant uart_top -- TX and RX paths."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


# 50 MHz system clock  -> 20 ns period
CLK_PERIOD_NS = 20


@cocotb.test()
async def test_uart_tx(dut):
    """Verify UART TX resets cleanly and outputs have no X/Z."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.rx.value = 1  # idle high
    dut.tx_valid.value = 0
    dut.tx_data.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    # Verify key outputs are resolvable
    for sig_name in ["tx", "tx_ready"]:
        sig = getattr(dut, sig_name)
        assert sig.value.is_resolvable, f"{sig_name} has X/Z after reset"

    tx_val = int(dut.tx.value)
    dut._log.info(f"TX idle state: {tx_val}")
    assert tx_val == 1, f"Expected TX idle high (1), got {tx_val}"

    tx_ready_val = int(dut.tx_ready.value)
    dut._log.info(f"tx_ready: {tx_ready_val}")

    dut._log.info("UART TX reset state is clean")


@cocotb.test()
async def test_uart_rx(dut):
    """Verify UART RX outputs are clean after reset."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.rx.value = 1  # idle high
    dut.tx_valid.value = 0
    dut.tx_data.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    # Verify key outputs are resolvable
    for sig_name in ["tx", "rx_valid", "rx_data"]:
        sig = getattr(dut, sig_name)
        assert sig.value.is_resolvable, f"{sig_name} has X/Z after reset"
        dut._log.info(f"{sig_name} = {int(sig.value):#x}")

    dut._log.info("UART RX reset state is clean (no X/Z on outputs)")
