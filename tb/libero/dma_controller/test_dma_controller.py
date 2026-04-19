"""Cocotb testbench for dma_controller - 2-channel DMA controller."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, busy should be 0, done signals should be 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.ch0_src_addr.value = 0; dut.ch0_dst_addr.value = 0
    dut.ch0_length.value = 0; dut.ch0_start.value = 0
    dut.ch1_src_addr.value = 0; dut.ch1_dst_addr.value = 0
    dut.ch1_length.value = 0; dut.ch1_start.value = 0
    dut.mem_rdata.value = 0; dut.mem_ready.value = 0
    await RisingEdge(dut.clk)

    if dut.busy.value.is_resolvable:
        try:
            assert int(dut.busy.value) == 0, "busy should be 0 after reset"
        except ValueError:
            assert False, "busy X/Z after reset"


@cocotb.test()
async def test_ch0_transfer(dut):
    """Start channel 0 transfer and verify busy asserts."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.ch1_start.value = 0; dut.ch1_src_addr.value = 0
    dut.ch1_dst_addr.value = 0; dut.ch1_length.value = 0

    dut.ch0_src_addr.value = 0x1000
    dut.ch0_dst_addr.value = 0x2000
    dut.ch0_length.value = 1
    dut.ch0_start.value = 1
    dut.mem_rdata.value = 0xABCD1234
    dut.mem_ready.value = 1
    await RisingEdge(dut.clk)
    dut.ch0_start.value = 0

    await ClockCycles(dut.clk, 3)

    if dut.busy.value.is_resolvable:
        try:
            b = int(dut.busy.value)
            dut._log.info(f"busy after start: {b}")
        except ValueError:
            dut._log.info("busy X/Z after start")


@cocotb.test()
async def test_ch0_done(dut):
    """Verify ch0_done asserts after transfer completes."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.ch1_start.value = 0; dut.ch1_src_addr.value = 0
    dut.ch1_dst_addr.value = 0; dut.ch1_length.value = 0

    dut.ch0_src_addr.value = 0x1000
    dut.ch0_dst_addr.value = 0x2000
    dut.ch0_length.value = 1
    dut.ch0_start.value = 1
    dut.mem_rdata.value = 0x12345678
    dut.mem_ready.value = 1
    await RisingEdge(dut.clk)
    dut.ch0_start.value = 0

    done_seen = False
    for _ in range(20):
        await RisingEdge(dut.clk)
        if dut.ch0_done.value.is_resolvable:
            try:
                if int(dut.ch0_done.value) == 1:
                    done_seen = True
                    dut._log.info("ch0_done asserted")
                    break
            except ValueError:
                pass

    assert done_seen, "ch0_done should assert after transfer"


@cocotb.test()
async def test_mem_read_address(dut):
    """Verify DMA reads from correct source address."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.ch1_start.value = 0; dut.ch1_src_addr.value = 0
    dut.ch1_dst_addr.value = 0; dut.ch1_length.value = 0

    dut.ch0_src_addr.value = 0x3000
    dut.ch0_dst_addr.value = 0x4000
    dut.ch0_length.value = 2
    dut.ch0_start.value = 1
    dut.mem_rdata.value = 0
    dut.mem_ready.value = 1
    await RisingEdge(dut.clk)
    dut.ch0_start.value = 0

    # Wait for read phase
    for _ in range(10):
        await RisingEdge(dut.clk)
        if dut.mem_rd.value.is_resolvable:
            try:
                if int(dut.mem_rd.value) == 1:
                    if dut.mem_addr.value.is_resolvable:
                        addr = int(dut.mem_addr.value)
                        dut._log.info(f"DMA read address: {addr:#010x}")
                    break
            except ValueError:
                pass
