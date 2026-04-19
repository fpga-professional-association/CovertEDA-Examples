"""Wishbone bus driver for cocotb."""

import cocotb
from cocotb.triggers import RisingEdge


async def wb_write(dut, addr, data, clk_name="clk"):
    """Perform a Wishbone single write cycle.

    Expects dut to have: wb_addr, wb_data_o (or wb_dat_o), wb_we, wb_cyc,
    wb_stb, wb_ack, wb_sel.
    """
    clk = getattr(dut, clk_name)
    await RisingEdge(clk)
    dut.wb_addr.value = addr
    if hasattr(dut, "wb_data_o"):
        dut.wb_data_o.value = data
    else:
        dut.wb_dat_o.value = data
    dut.wb_we.value = 1
    dut.wb_sel.value = 0xF
    dut.wb_cyc.value = 1
    dut.wb_stb.value = 1
    # Wait for ack
    for _ in range(100):
        await RisingEdge(clk)
        if int(dut.wb_ack.value) == 1:
            break
    dut.wb_cyc.value = 0
    dut.wb_stb.value = 0
    dut.wb_we.value = 0


async def wb_read(dut, addr, clk_name="clk"):
    """Perform a Wishbone single read cycle. Returns the read data."""
    clk = getattr(dut, clk_name)
    await RisingEdge(clk)
    dut.wb_addr.value = addr
    dut.wb_we.value = 0
    dut.wb_sel.value = 0xF
    dut.wb_cyc.value = 1
    dut.wb_stb.value = 1
    for _ in range(100):
        await RisingEdge(clk)
        if int(dut.wb_ack.value) == 1:
            break
    if hasattr(dut, "wb_data_i"):
        result = int(dut.wb_data_i.value)
    else:
        result = int(dut.wb_dat_i.value)
    dut.wb_cyc.value = 0
    dut.wb_stb.value = 0
    return result
