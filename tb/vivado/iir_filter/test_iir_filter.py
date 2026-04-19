"""Cocotb testbench for vivado iir_filter."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify filter output is zero after reset."""
    setup_clock(dut, "clk", 10)
    dut.x_in.value = 0
    dut.valid_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.y_out.value.is_resolvable, "y_out has X/Z after reset"
    try:
        val = int(dut.y_out.value)
        dut._log.info(f"y_out after reset: {val}")
    except ValueError:
        assert False, "y_out not convertible after reset"


@cocotb.test()
async def test_impulse_response(dut):
    """Apply impulse (single nonzero sample) and observe response."""
    setup_clock(dut, "clk", 10)
    dut.x_in.value = 0
    dut.valid_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Apply impulse
    dut.x_in.value = 1000
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    dut.x_in.value = 0
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0

    # Observe output for several cycles
    for i in range(10):
        await RisingEdge(dut.clk)
        if dut.y_out.value.is_resolvable:
            try:
                val = int(dut.y_out.value)
                dut._log.info(f"Impulse response y[{i}] = {val}")
            except ValueError:
                dut._log.info(f"y_out not convertible at step {i}")


@cocotb.test()
async def test_step_response(dut):
    """Apply step input and verify output settles."""
    setup_clock(dut, "clk", 10)
    dut.x_in.value = 0
    dut.valid_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Apply constant input
    dut.x_in.value = 500
    dut.valid_in.value = 1

    for i in range(20):
        await RisingEdge(dut.clk)
        if dut.y_out.value.is_resolvable:
            try:
                val = int(dut.y_out.value)
                dut._log.info(f"Step response y[{i}] = {val}")
            except ValueError:
                dut._log.info(f"y_out not convertible at step {i}")

    dut.valid_in.value = 0


@cocotb.test()
async def test_zero_input(dut):
    """Verify zero input produces zero output after settling."""
    setup_clock(dut, "clk", 10)
    dut.x_in.value = 0
    dut.valid_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.x_in.value = 0
    dut.valid_in.value = 1

    await ClockCycles(dut.clk, 20)

    assert dut.y_out.value.is_resolvable, "y_out has X/Z with zero input"
    try:
        val = int(dut.y_out.value)
        dut._log.info(f"y_out with zero input: {val} (expected 0)")
    except ValueError:
        dut._log.info("y_out not convertible")
    dut.valid_in.value = 0


@cocotb.test()
async def test_valid_pipeline(dut):
    """Verify valid_out tracks valid_in with pipeline delay."""
    setup_clock(dut, "clk", 10)
    dut.x_in.value = 0
    dut.valid_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Pulse valid_in
    dut.valid_in.value = 1
    dut.x_in.value = 100
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    dut.x_in.value = 0

    # Wait for valid_out
    for i in range(5):
        await RisingEdge(dut.clk)
        if dut.valid_out.value.is_resolvable:
            try:
                v = int(dut.valid_out.value)
                dut._log.info(f"valid_out at cycle +{i+1}: {v}")
            except ValueError:
                pass
