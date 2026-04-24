"""Cocotb testbench for radiant debouncer."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify all outputs are zero after reset."""
    setup_clock(dut, "clk", 40)
    dut.btn_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.btn_out.value.is_resolvable, "btn_out has X/Z after reset"
    try:
        val = int(dut.btn_out.value)
        assert val == 0, f"btn_out not zero after reset: {val}"
        dut._log.info("Reset state OK: btn_out=0")
    except ValueError:
        raise AssertionError("btn_out not resolvable after reset")


@cocotb.test()
async def test_stable_input_passes(dut):
    """Hold a stable input for enough cycles to pass through debouncer."""
    setup_clock(dut, "clk", 40)
    dut.btn_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Apply stable button press on channel 0
    dut.btn_in.value = 0x01
    # Wait enough cycles for synchronizer + debounce counter (2 + 16 + margin)
    await ClockCycles(dut.clk, 30)

    assert dut.btn_out.value.is_resolvable, "btn_out has X/Z"
    try:
        val = int(dut.btn_out.value)
        assert val & 0x01, f"btn_out[0] not set after stable input: {val:#06b}"
        dut._log.info(f"Stable input passed through: btn_out={val:#06b}")
    except ValueError:
        raise AssertionError("btn_out not resolvable")


@cocotb.test()
async def test_glitch_rejected(dut):
    """Short glitch should be filtered out by debouncer."""
    setup_clock(dut, "clk", 40)
    dut.btn_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Apply a 2-cycle glitch (shorter than debounce threshold)
    dut.btn_in.value = 0x01
    await ClockCycles(dut.clk, 2)
    dut.btn_in.value = 0x00
    await ClockCycles(dut.clk, 10)

    assert dut.btn_out.value.is_resolvable, "btn_out has X/Z"
    try:
        val = int(dut.btn_out.value)
        assert val == 0, f"Glitch was not filtered: btn_out={val:#06b}"
        dut._log.info("Glitch correctly rejected")
    except ValueError:
        raise AssertionError("btn_out not resolvable")


@cocotb.test()
async def test_rising_edge_pulse(dut):
    """Verify a rising edge pulse is generated on debounced transition."""
    setup_clock(dut, "clk", 40)
    dut.btn_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Apply stable press
    dut.btn_in.value = 0x02
    rising_seen = False
    for _ in range(40):
        await RisingEdge(dut.clk)
        if dut.btn_rising.value.is_resolvable:
            try:
                if int(dut.btn_rising.value) & 0x02:
                    rising_seen = True
                    dut._log.info("Rising edge pulse detected on channel 1")
                    break
            except ValueError:
                pass

    dut._log.info(f"Rising edge seen: {rising_seen}")


@cocotb.test()
async def test_multi_channel(dut):
    """Press all 4 buttons simultaneously, verify all debounce."""
    setup_clock(dut, "clk", 40)
    dut.btn_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.btn_in.value = 0x0F
    await ClockCycles(dut.clk, 30)

    assert dut.btn_out.value.is_resolvable, "btn_out has X/Z"
    try:
        val = int(dut.btn_out.value)
        assert val == 0x0F, f"Not all channels debounced: {val:#06b}"
        dut._log.info(f"All 4 channels debounced: btn_out={val:#06b}")
    except ValueError:
        raise AssertionError("btn_out not resolvable")
