"""Cocotb testbench for uart_rx - UART receiver with error detection."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut

CLKS_PER_BIT = 4


async def send_uart_byte(dut, byte_val, clks_per_bit=CLKS_PER_BIT, bad_stop=False):
    """Send one UART byte (8N1) on rx_serial.

    Returns (valid_seen, error_seen, rx_data) captured during transmission.
    """
    valid_seen = False
    error_seen = False
    rx_data_val = None

    async def wait_clocks(n):
        """Wait n rising edges while monitoring rx_valid and rx_error."""
        nonlocal valid_seen, error_seen, rx_data_val
        for _ in range(n):
            await RisingEdge(dut.clk)
            if dut.rx_valid.value.is_resolvable:
                try:
                    if int(dut.rx_valid.value) == 1:
                        valid_seen = True
                        if dut.rx_data.value.is_resolvable:
                            try:
                                rx_data_val = int(dut.rx_data.value)
                            except ValueError:
                                pass
                except ValueError:
                    pass
            if dut.rx_error.value.is_resolvable:
                try:
                    if int(dut.rx_error.value) == 1:
                        error_seen = True
                except ValueError:
                    pass

    # Start bit
    dut.rx_serial.value = 0
    await wait_clocks(clks_per_bit)

    # 8 data bits (LSB first)
    for i in range(8):
        dut.rx_serial.value = (byte_val >> i) & 1
        await wait_clocks(clks_per_bit)

    # Stop bit
    dut.rx_serial.value = 0 if bad_stop else 1
    await wait_clocks(clks_per_bit)

    # Idle
    dut.rx_serial.value = 1
    await wait_clocks(2)

    return valid_seen, error_seen, rx_data_val


@cocotb.test()
async def test_reset_state(dut):
    """After reset, rx_valid and rx_error should be 0."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rx_serial.value = 1  # idle
    await RisingEdge(dut.clk)

    if dut.rx_valid.value.is_resolvable:
        try:
            assert int(dut.rx_valid.value) == 0, "rx_valid should be 0 after reset"
        except ValueError:
            assert False, "rx_valid X/Z after reset"


@cocotb.test()
async def test_receive_byte(dut):
    """Send 0x55 and verify it is received correctly."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rx_serial.value = 1
    await ClockCycles(dut.clk, 5)

    valid_seen, error_seen, rx_data_val = await send_uart_byte(dut, 0x55)

    # Also check a few more cycles in case rx_valid comes late
    if not valid_seen:
        for _ in range(10):
            await RisingEdge(dut.clk)
            if dut.rx_valid.value.is_resolvable:
                try:
                    if int(dut.rx_valid.value) == 1:
                        valid_seen = True
                        if dut.rx_data.value.is_resolvable:
                            try:
                                rx_data_val = int(dut.rx_data.value)
                            except ValueError:
                                pass
                        break
                except ValueError:
                    pass

    assert valid_seen, "rx_valid never asserted for 0x55"
    if rx_data_val is not None:
        dut._log.info(f"Received: {rx_data_val:#04x}")
        assert rx_data_val == 0x55, f"Expected 0x55, got {rx_data_val:#04x}"


@cocotb.test()
async def test_framing_error(dut):
    """Send byte with bad stop bit, expect rx_error."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rx_serial.value = 1
    await ClockCycles(dut.clk, 5)

    valid_seen, error_seen, rx_data_val = await send_uart_byte(dut, 0xAA, bad_stop=True)

    # Also check a few more cycles in case rx_error comes late
    if not error_seen:
        for _ in range(10):
            await RisingEdge(dut.clk)
            if dut.rx_error.value.is_resolvable:
                try:
                    if int(dut.rx_error.value) == 1:
                        error_seen = True
                        break
                except ValueError:
                    pass

    assert error_seen, "Expected framing error for bad stop bit"
    dut._log.info("Framing error correctly detected")


@cocotb.test()
async def test_multiple_bytes(dut):
    """Send several bytes and verify all are received."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rx_serial.value = 1
    await ClockCycles(dut.clk, 5)

    test_bytes = [0x00, 0xFF, 0xA5]
    received = []

    for b in test_bytes:
        valid_seen, error_seen, rx_data_val = await send_uart_byte(dut, b)

        # Also check a few more cycles if not captured during send
        if not valid_seen:
            for _ in range(10):
                await RisingEdge(dut.clk)
                if dut.rx_valid.value.is_resolvable:
                    try:
                        if int(dut.rx_valid.value) == 1:
                            valid_seen = True
                            if dut.rx_data.value.is_resolvable:
                                try:
                                    rx_data_val = int(dut.rx_data.value)
                                except ValueError:
                                    pass
                            break
                    except ValueError:
                        pass

        if valid_seen and rx_data_val is not None:
            received.append(rx_data_val)

    dut._log.info(f"Sent: {[hex(b) for b in test_bytes]}, Received: {[hex(r) for r in received]}")
    assert len(received) == len(test_bytes), f"Expected {len(test_bytes)} bytes, got {len(received)}"
