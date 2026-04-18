"""SPI master/slave driver for cocotb."""

import cocotb
from cocotb.triggers import Timer


async def spi_transfer(cs_n, sclk, mosi, miso, data, clk_ns=100):
    """Perform a full-duplex SPI transfer (mode 0, MSB first).

    Args:
        cs_n: Chip select signal (active low).
        sclk: SPI clock signal.
        mosi: Master-out-slave-in signal.
        miso: Master-in-slave-out signal (read).
        data: List of bytes to send.
        clk_ns: SPI clock half-period in nanoseconds.

    Returns:
        List of bytes received on miso.
    """
    rx_data = []
    cs_n.value = 0
    await Timer(clk_ns, unit="ns")

    for byte_val in data:
        rx_byte = 0
        for bit in range(7, -1, -1):
            # Drive MOSI on falling edge
            mosi.value = (byte_val >> bit) & 1
            sclk.value = 0
            await Timer(clk_ns, unit="ns")
            # Sample MISO on rising edge
            sclk.value = 1
            await Timer(clk_ns, unit="ns")
            if miso is not None and miso.value.is_resolvable:
                rx_byte = (rx_byte << 1) | (int(miso.value) & 1)
        rx_data.append(rx_byte)

    sclk.value = 0
    await Timer(clk_ns, unit="ns")
    cs_n.value = 1
    await Timer(clk_ns, unit="ns")
    return rx_data
