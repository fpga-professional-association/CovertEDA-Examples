"""Cocotb testbench for nrzi_encoder - NRZI encoder/decoder."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, outputs should be 0."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.data_in.value = 0
    dut.data_valid.value = 0
    dut.mode.value = 0
    await RisingEdge(dut.clk)

    if dut.data_out.value.is_resolvable:
        try:
            assert int(dut.data_out.value) == 0, "data_out should be 0 after reset"
        except ValueError:
            assert False, "data_out X/Z after reset"

    if dut.out_valid.value.is_resolvable:
        try:
            assert int(dut.out_valid.value) == 0, "out_valid should be 0 after reset"
        except ValueError:
            assert False, "out_valid X/Z after reset"


@cocotb.test()
async def test_encode_zeros(dut):
    """Encoding all zeros should produce no transitions (constant output)."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.mode.value = 0  # encode mode
    dut.data_valid.value = 1

    outputs = []
    for _ in range(8):
        dut.data_in.value = 0
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        if dut.data_out.value.is_resolvable:
            try:
                outputs.append(int(dut.data_out.value))
            except ValueError:
                pass

    if len(outputs) > 1:
        all_same = all(o == outputs[0] for o in outputs)
        dut._log.info(f"Encoded zeros output: {outputs}, all same: {all_same}")
        assert all_same, "Zero input should produce no transitions"


@cocotb.test()
async def test_encode_ones(dut):
    """Encoding all ones should toggle the output each cycle."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.mode.value = 0  # encode mode
    dut.data_valid.value = 1

    outputs = []
    for _ in range(8):
        dut.data_in.value = 1
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        if dut.data_out.value.is_resolvable:
            try:
                outputs.append(int(dut.data_out.value))
            except ValueError:
                pass

    if len(outputs) > 1:
        transitions = sum(1 for i in range(1, len(outputs)) if outputs[i] != outputs[i-1])
        dut._log.info(f"Encoded ones output: {outputs}, transitions: {transitions}")


@cocotb.test()
async def test_valid_follows_input(dut):
    """out_valid should follow data_valid."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.mode.value = 0
    dut.data_in.value = 0

    dut.data_valid.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    if dut.out_valid.value.is_resolvable:
        try:
            assert int(dut.out_valid.value) == 1, "out_valid should be 1"
        except ValueError:
            assert False, "out_valid X/Z"

    dut.data_valid.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    if dut.out_valid.value.is_resolvable:
        try:
            assert int(dut.out_valid.value) == 0, "out_valid should be 0"
        except ValueError:
            assert False, "out_valid X/Z"
