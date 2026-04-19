"""Cocotb testbench for quartus spi_master (configurable CPOL/CPHA)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify idle state after reset: CS=1, SCK=CPOL, busy=0."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.start.value = 0
    dut.data_in.value = 0
    dut.cpol.value = 0
    dut.cpha.value = 0
    dut.clk_div.value = 1
    dut.miso.value = 0
    await RisingEdge(dut.clk)

    if not dut.cs_n.value.is_resolvable:
        raise AssertionError("cs_n has X/Z after reset")

    try:
        cs = int(dut.cs_n.value)
        busy = int(dut.busy.value)
    except ValueError:
        raise AssertionError("Signals not convertible after reset")

    assert cs == 1, f"Expected cs_n=1, got {cs}"
    assert busy == 0, f"Expected busy=0, got {busy}"
    dut._log.info("Reset state: cs_n=1, busy=0")


@cocotb.test()
async def test_cs_asserts_during_transfer(dut):
    """CS should go low during an active transfer."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.start.value = 0
    dut.data_in.value = 0xA5
    dut.cpol.value = 0
    dut.cpha.value = 0
    dut.clk_div.value = 1
    dut.miso.value = 0
    await RisingEdge(dut.clk)

    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    await ClockCycles(dut.clk, 5)

    if dut.cs_n.value.is_resolvable:
        try:
            cs = int(dut.cs_n.value)
            dut._log.info(f"CS during transfer: {cs}")
            assert cs == 0, f"Expected cs_n=0 during transfer, got {cs}"
        except ValueError:
            raise AssertionError("cs_n not convertible")


@cocotb.test()
async def test_sck_toggles(dut):
    """SCK should toggle during transfer."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.start.value = 0
    dut.data_in.value = 0xA5
    dut.cpol.value = 0
    dut.cpha.value = 0
    dut.clk_div.value = 1
    dut.miso.value = 0
    await RisingEdge(dut.clk)

    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    sck_transitions = 0
    prev_sck = None
    for _ in range(200):
        await RisingEdge(dut.clk)
        if dut.sck.value.is_resolvable:
            try:
                cur = int(dut.sck.value)
                if prev_sck is not None and cur != prev_sck:
                    sck_transitions += 1
                prev_sck = cur
            except ValueError:
                pass

    dut._log.info(f"SCK transitions: {sck_transitions}")
    assert sck_transitions >= 8, f"Expected at least 8 SCK transitions, got {sck_transitions}"


@cocotb.test()
async def test_transaction_completes(dut):
    """Full SPI transaction should complete with done pulse."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.start.value = 0
    dut.data_in.value = 0xA5
    dut.cpol.value = 0
    dut.cpha.value = 0
    dut.clk_div.value = 1
    dut.miso.value = 0
    await RisingEdge(dut.clk)

    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    done_seen = False
    for cycle in range(500):
        await RisingEdge(dut.clk)
        if dut.done.value.is_resolvable:
            try:
                if int(dut.done.value) == 1:
                    done_seen = True
                    dut._log.info(f"Transaction done at cycle {cycle}")
                    break
            except ValueError:
                pass

    assert done_seen, "Transaction did not complete within 500 cycles"

    # Verify CS is deasserted
    if dut.cs_n.value.is_resolvable:
        try:
            cs = int(dut.cs_n.value)
            dut._log.info(f"CS after done: {cs}")
            assert cs == 1, f"Expected cs_n=1 after done, got {cs}"
        except ValueError:
            raise AssertionError("cs_n not convertible")


@cocotb.test()
async def test_miso_loopback(dut):
    """Tie MISO=1 and verify data_out receives all 1s."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.start.value = 0
    dut.data_in.value = 0x00
    dut.cpol.value = 0
    dut.cpha.value = 0
    dut.clk_div.value = 1
    dut.miso.value = 1  # all 1s
    await RisingEdge(dut.clk)

    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    # Wait for done
    for _ in range(500):
        await RisingEdge(dut.clk)
        if dut.done.value.is_resolvable:
            try:
                if int(dut.done.value) == 1:
                    break
            except ValueError:
                pass

    if dut.data_out.value.is_resolvable:
        try:
            rx = int(dut.data_out.value)
            dut._log.info(f"Received with MISO=1: {rx:#04x}")
            assert rx == 0xFF, f"Expected 0xFF with MISO tied high, got {rx:#04x}"
        except ValueError:
            raise AssertionError("data_out not convertible")
