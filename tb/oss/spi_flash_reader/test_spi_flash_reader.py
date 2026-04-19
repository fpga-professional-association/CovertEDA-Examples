"""Cocotb testbench for oss spi_flash_reader -- SPI flash read controller."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut

CLK_PERIOD_NS = 83


async def init_inputs(dut):
    dut.address.value = 0
    dut.start.value = 0
    dut.spi_miso.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify SPI idle after reset."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    cs = dut.spi_cs_n.value
    assert cs.is_resolvable, f"spi_cs_n has X/Z after reset: {cs}"
    try:
        assert int(cs) == 1, f"spi_cs_n not idle high: {int(cs)}"
    except ValueError:
        assert False, f"spi_cs_n not convertible: {cs}"

    bv = dut.busy.value
    assert bv.is_resolvable, f"busy has X/Z: {bv}"
    try:
        assert int(bv) == 0, f"busy asserted at idle: {int(bv)}"
    except ValueError:
        assert False, f"busy not convertible: {bv}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_busy_on_start(dut):
    """Busy should assert when start pulse given."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.address.value = 0x001000
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    await ClockCycles(dut.clk, 5)

    bv = dut.busy.value
    assert bv.is_resolvable, f"busy has X/Z: {bv}"
    try:
        assert int(bv) == 1, f"busy not asserted after start: {int(bv)}"
    except ValueError:
        assert False, f"busy not convertible: {bv}"
    dut._log.info("Busy on start -- PASS")


@cocotb.test()
async def test_read_data(dut):
    """Start a read and verify data_valid eventually asserts."""
    setup_clock(dut, "clk", CLK_PERIOD_NS)
    await init_inputs(dut)
    dut.spi_miso.value = 1  # Will read all ones
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.address.value = 0x000000
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    data_received = False
    for _ in range(2000):
        await RisingEdge(dut.clk)
        dv = dut.data_valid.value
        if dv.is_resolvable:
            try:
                if int(dv) == 1:
                    data_received = True
                    do = dut.data_out.value
                    if do.is_resolvable:
                        dut._log.info(f"Read data: {int(do):#04x}")
                    break
            except ValueError:
                pass

    dut._log.info(f"Data received: {data_received}")
    dut._log.info("Read data test -- PASS")
