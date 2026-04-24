"""Cocotb testbench for ace reed_solomon -- RS(255,223) encoder."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def init_inputs(dut):
    dut.data_in.value = 0
    dut.data_valid.value = 0
    dut.sof.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify outputs are zero after reset."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for name in ["parity_valid", "busy"]:
        val = getattr(dut, name).value
        assert val.is_resolvable, f"{name} has X/Z after reset: {val}"
        try:
            assert int(val) == 0, f"{name} not 0 after reset: {int(val)}"
        except ValueError:
            assert False, f"{name} not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_encoder_busy_during_data(dut):
    """Feed a few data bytes and verify busy asserts."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Start of frame + first data byte
    dut.sof.value = 1
    dut.data_in.value = 0x01
    dut.data_valid.value = 1
    await RisingEdge(dut.clk)
    dut.sof.value = 0

    await RisingEdge(dut.clk)
    val = dut.busy.value
    assert val.is_resolvable, f"busy has X/Z: {val}"
    try:
        assert int(val) == 1, f"busy not asserted during data: {int(val)}"
    except ValueError:
        assert False, f"busy not convertible: {val}"

    dut.data_valid.value = 0
    await ClockCycles(dut.clk, 5)
    dut._log.info("Busy during data -- PASS")


@cocotb.test()
async def test_full_frame_parity(dut):
    """Send 223 data bytes and verify 32 parity bytes emerge."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # SOF + first byte
    dut.sof.value = 1
    dut.data_in.value = 0x00
    dut.data_valid.value = 1
    await RisingEdge(dut.clk)
    dut.sof.value = 0

    # Remaining 222 data bytes
    for i in range(1, 223):
        dut.data_in.value = i & 0xFF
        await RisingEdge(dut.clk)

    dut.data_valid.value = 0

    # Collect parity bytes
    parity_count = 0
    for _ in range(50):
        await RisingEdge(dut.clk)
        pv = dut.parity_valid.value
        if pv.is_resolvable:
            try:
                if int(pv) == 1:
                    parity_count += 1
                    po = dut.parity_out.value
                    if po.is_resolvable:
                        dut._log.info(f"Parity byte {parity_count}: {int(po):#04x}")
            except ValueError:
                pass

    dut._log.info(f"Total parity bytes: {parity_count}")
    assert parity_count == 32, f"Expected 32 parity bytes, got {parity_count}"
    dut._log.info("Full frame parity generation -- PASS")


@cocotb.test()
async def test_idle_after_parity(dut):
    """After parity output completes, busy should deassert."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.sof.value = 1
    dut.data_in.value = 0xFF
    dut.data_valid.value = 1
    await RisingEdge(dut.clk)
    dut.sof.value = 0

    for i in range(222):
        dut.data_in.value = (i + 1) & 0xFF
        await RisingEdge(dut.clk)

    dut.data_valid.value = 0
    await ClockCycles(dut.clk, 40)

    val = dut.busy.value
    assert val.is_resolvable, f"busy has X/Z after parity: {val}"
    try:
        assert int(val) == 0, f"busy not deasserted after parity: {int(val)}"
    except ValueError:
        assert False, f"busy not convertible: {val}"
    dut._log.info("Idle after parity -- PASS")
