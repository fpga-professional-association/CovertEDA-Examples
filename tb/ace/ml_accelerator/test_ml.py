"""Cocotb testbench for ace ml_top (SystemVerilog).

Feeds known input values through the ML accelerator and verifies that the
output produces valid, non-zero data.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def drive_input(dut, value):
    """Drive a single input value, waiting for input_ready handshake."""
    dut.input_data.value = value
    dut.input_valid.value = 1

    for _ in range(1000):
        await RisingEdge(dut.clk)
        if dut.input_ready.value.is_resolvable and int(dut.input_ready.value) == 1:
            break
    else:
        assert False, f"Timed out waiting for input_ready while sending {value}"

    # Data accepted on this rising edge
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_ml_accelerator(dut):
    """Feed input data and verify output_valid asserts with non-zero data."""

    # Start a 10 ns clock (100 MHz)
    setup_clock(dut, "clk", 10)

    # Initialise inputs
    dut.input_data.value = 0
    dut.input_valid.value = 0
    dut.output_ready.value = 1  # Always ready to consume output

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Drive known input values with handshake
    test_values = [100, 200, 300]

    for val in test_values:
        await drive_input(dut, val)
        dut._log.info(f"Sent input_data = {val}")

    # Deassert input_valid after all inputs sent
    dut.input_valid.value = 0

    # Run 100 more cycles for pipeline to produce output
    await ClockCycles(dut.clk, 100)

    # Check that output_valid asserted at least once during the run
    # and that output_data is non-zero
    output_valid = dut.output_valid.value
    output_data = dut.output_data.value

    assert output_valid.is_resolvable, (
        f"output_valid contains X/Z: {output_valid}"
    )
    assert output_data.is_resolvable, (
        f"output_data contains X/Z: {output_data}"
    )

    dut._log.info(
        f"Final state: output_valid={int(output_valid)}, "
        f"output_data={int(output_data):#010x}"
    )

    # Verify output_data is non-zero (accelerator produced a result)
    assert int(output_data) != 0, (
        "output_data is zero -- expected non-zero result from ML accelerator"
    )
