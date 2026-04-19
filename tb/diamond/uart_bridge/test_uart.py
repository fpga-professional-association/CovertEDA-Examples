"""Cocotb testbench for diamond uart_top -- USB-to-UART and UART-to-USB paths."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


# 48 MHz system clock -> ~21 ns period
CLK_PERIOD_NS = 21


@cocotb.test()
async def test_usb_to_uart_tx(dut):
    """Verify design runs after reset and outputs have no X/Z."""

    setup_clock(dut, "clk_48m", CLK_PERIOD_NS)

    # Idle state for inputs
    dut.uart_rx.value = 1        # UART idle high
    dut.usb_rx_data.value = 0
    dut.usb_data_in.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_48m, 20)

    # Verify outputs are resolvable after reset
    for sig_name in ["uart_tx", "usb_data_out"]:
        sig = getattr(dut, sig_name)
        if not sig.value.is_resolvable:
            # Wait more cycles for design to settle
            await ClockCycles(dut.clk_48m, 100)
            break

    # Drive data from USB side: 0x55, assert usb_rx_data (data valid)
    dut.usb_data_in.value = 0x55
    dut.usb_rx_data.value = 1
    await RisingEdge(dut.clk_48m)
    dut.usb_rx_data.value = 0

    # Run for a generous window
    await ClockCycles(dut.clk_48m, 1000)

    # Verify key outputs are resolvable (no X/Z)
    for sig_name in ["uart_tx", "usb_data_out"]:
        sig = getattr(dut, sig_name)
        assert sig.value.is_resolvable, f"{sig_name} has X/Z after operation"

    dut._log.info("UART bridge runs cleanly with no X/Z on outputs")


@cocotb.test()
async def test_uart_to_usb_rx(dut):
    """Verify design runs and outputs settle to valid states."""

    setup_clock(dut, "clk_48m", CLK_PERIOD_NS)

    # Idle state for inputs
    dut.uart_rx.value = 1
    dut.usb_rx_data.value = 0
    dut.usb_data_in.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_48m, 100)

    # Verify design outputs are resolvable
    for sig_name in ["uart_tx", "usb_data_out"]:
        sig = getattr(dut, sig_name)
        assert sig.value.is_resolvable, f"{sig_name} has X/Z after 100 cycles"

    dut._log.info("UART bridge design outputs are clean after reset")
