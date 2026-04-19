"""Bit-bang UART TX/RX driver for cocotb."""

import cocotb
from cocotb.triggers import Timer


async def send_byte(pin, byte_val, baud_ns):
    """Send a single byte over UART (8N1) by bit-banging the pin.

    Args:
        pin: cocotb signal handle for the TX/RX line to drive.
        byte_val: Integer byte value (0-255) to transmit.
        baud_ns: Bit period in nanoseconds (e.g., 8680 for 115200 baud).
    """
    # Start bit (low)
    pin.value = 0
    await Timer(baud_ns, unit="ns")
    # Data bits (LSB first)
    for i in range(8):
        pin.value = (byte_val >> i) & 1
        await Timer(baud_ns, unit="ns")
    # Stop bit (high)
    pin.value = 1
    await Timer(baud_ns, unit="ns")


async def receive_byte(pin, baud_ns):
    """Receive a single byte from UART (8N1) by sampling the pin.

    Args:
        pin: cocotb signal handle for the line to sample.
        baud_ns: Bit period in nanoseconds.

    Returns:
        Integer byte value (0-255).
    """
    # Wait for start bit (falling edge)
    while int(pin.value) != 0:
        await Timer(1, unit="ns")
    # Sample at midpoint of each bit
    await Timer(baud_ns // 2, unit="ns")  # center of start bit
    await Timer(baud_ns, unit="ns")       # center of bit 0
    byte_val = 0
    for i in range(8):
        if int(pin.value):
            byte_val |= (1 << i)
        if i < 7:
            await Timer(baud_ns, unit="ns")
    # Wait for stop bit
    await Timer(baud_ns, unit="ns")
    return byte_val
