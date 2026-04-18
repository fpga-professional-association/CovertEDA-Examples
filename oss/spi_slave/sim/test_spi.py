"""Cocotb testbench for spi_top (SPI slave + reg bank).

SPI mode 0, MSB-first, 32-bit frames. The slave samples MOSI on posedge
spi_clk and shifts rx_data out on falling edges after 32 bits.

The RTL has a few quirks worth noting:
- spi_miso is declared as `output` (not `output reg`) but assigned in an
  always block. iverilog accepts this; Verilator would reject.
- shift_out is never loaded, so MISO always reads 0.
- rx_valid latches on bit 31 and stays high afterward (no clear).
- reg_bank's write_en is driven by an undriven wire in spi_top → no writes
  ever happen. We only validate the SPI shift-in path.
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer


CLK_PERIOD_NS = 83       # ~12 MHz system clock
SPI_HALF_NS   = 500      # 1 MHz SPI clock


async def reset(dut):
    dut.rst_n.value = 0
    dut.spi_clk.value = 0
    dut.spi_cs_n.value = 1
    dut.spi_mosi.value = 0
    await Timer(500, unit="ns")
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def spi_send_word(dut, word):
    """Clock a 32-bit word into the slave, MSB first, mode 0."""
    dut.spi_cs_n.value = 0
    await Timer(SPI_HALF_NS, unit="ns")
    for i in range(32):
        bit = (word >> (31 - i)) & 1
        dut.spi_mosi.value = bit
        await Timer(SPI_HALF_NS, unit="ns")
        dut.spi_clk.value = 1
        await Timer(SPI_HALF_NS, unit="ns")
        dut.spi_clk.value = 0
    await Timer(SPI_HALF_NS, unit="ns")
    dut.spi_cs_n.value = 1
    await Timer(SPI_HALF_NS * 2, unit="ns")


@cocotb.test()
async def test_rx_valid_low_before_transfer(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    for _ in range(100):
        await RisingEdge(dut.clk)
    assert int(dut.rx_valid.value) == 0, "rx_valid should be low before any transfer"


@cocotb.test()
async def test_single_word_captured(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)

    await spi_send_word(dut, 0xDEADBEEF)
    # give rx_valid time to propagate to the sync domain
    for _ in range(50):
        await RisingEdge(dut.clk)

    assert int(dut.rx_data.value) == 0xDEADBEEF, \
        f"rx_data = 0x{int(dut.rx_data.value):08x}, expected 0xDEADBEEF"
    assert int(dut.rx_valid.value) == 1, "rx_valid should be high after 32 bits"


@cocotb.test()
async def test_second_word_overwrites(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)

    await spi_send_word(dut, 0x12345678)
    for _ in range(50):
        await RisingEdge(dut.clk)
    assert int(dut.rx_data.value) == 0x12345678

    await spi_send_word(dut, 0xA5A5A5A5)
    for _ in range(50):
        await RisingEdge(dut.clk)
    assert int(dut.rx_data.value) == 0xA5A5A5A5


@cocotb.test()
async def test_all_zeros_word(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)

    await spi_send_word(dut, 0x00000000)
    for _ in range(50):
        await RisingEdge(dut.clk)
    assert int(dut.rx_data.value) == 0x00000000
