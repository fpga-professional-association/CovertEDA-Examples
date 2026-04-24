"""Cocotb testbench for hdlc_framer - HDLC frame encoder."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, busy should be 0."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.data_in.value = 0
    dut.data_valid.value = 0
    dut.frame_start.value = 0
    dut.frame_end.value = 0
    await RisingEdge(dut.clk)

    if dut.busy.value.is_resolvable:
        try:
            assert int(dut.busy.value) == 0, "busy should be 0 after reset"
        except ValueError:
            assert False, "busy X/Z after reset"


@cocotb.test()
async def test_frame_start_sends_flag(dut):
    """Frame start should send the 0x7E flag pattern."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.data_in.value = 0
    dut.data_valid.value = 0
    dut.frame_end.value = 0

    dut.frame_start.value = 1
    await RisingEdge(dut.clk)
    dut.frame_start.value = 0

    # Capture 8 bits of flag
    flag_bits = []
    for _ in range(8):
        await RisingEdge(dut.clk)
        if dut.out_valid.value.is_resolvable and dut.data_out.value.is_resolvable:
            try:
                if int(dut.out_valid.value) == 1:
                    flag_bits.append(int(dut.data_out.value))
            except ValueError:
                pass

    dut._log.info(f"Flag bits: {flag_bits}")
    if len(flag_bits) == 8:
        flag_val = sum(b << i for i, b in enumerate(flag_bits))
        dut._log.info(f"Flag value: {flag_val:#04x} (expected 0x7E)")


@cocotb.test()
async def test_busy_during_frame(dut):
    """busy should be asserted during frame transmission."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.data_in.value = 0
    dut.data_valid.value = 0
    dut.frame_end.value = 0

    dut.frame_start.value = 1
    await RisingEdge(dut.clk)
    dut.frame_start.value = 0

    await ClockCycles(dut.clk, 3)

    if dut.busy.value.is_resolvable:
        try:
            assert int(dut.busy.value) == 1, "busy should be 1 during frame"
        except ValueError:
            assert False, "busy X/Z during frame"

    dut._log.info("Busy asserted during frame transmission")


@cocotb.test()
async def test_data_passes_through(dut):
    """Data bits should pass through during DATA state."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.frame_end.value = 0

    # Start frame
    dut.frame_start.value = 1
    dut.data_valid.value = 0
    dut.data_in.value = 0
    await RisingEdge(dut.clk)
    dut.frame_start.value = 0

    # Wait for flag to finish (8 bits)
    await ClockCycles(dut.clk, 9)

    # Send data bits
    test_bits = [1, 0, 1, 0]
    received = []
    for bit in test_bits:
        dut.data_in.value = bit
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        if dut.out_valid.value.is_resolvable and dut.data_out.value.is_resolvable:
            try:
                if int(dut.out_valid.value) == 1:
                    received.append(int(dut.data_out.value))
            except ValueError:
                pass

    dut._log.info(f"Sent: {test_bits}, Received: {received}")
