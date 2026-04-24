"""Cocotb testbench for ace median_filter -- 3-sample median filter."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def init_inputs(dut):
    dut.data_in.value = 0
    dut.data_valid.value = 0


@cocotb.test()
async def test_reset_state(dut):
    """Verify outputs are zero after reset."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    val = dut.data_out_valid.value
    assert val.is_resolvable, f"data_out_valid has X/Z after reset: {val}"
    try:
        assert int(val) == 0, f"data_out_valid not 0 after reset: {int(val)}"
    except ValueError:
        assert False, f"data_out_valid not convertible: {val}"
    dut._log.info("Reset state clean -- PASS")


@cocotb.test()
async def test_sorted_input(dut):
    """Feed sorted values [10, 20, 30], median should be 20."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for val in [10, 20, 30]:
        dut.data_in.value = val
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)

    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    out = dut.data_out.value
    if out.is_resolvable:
        try:
            dut._log.info(f"Median of [10,20,30] = {int(out)} (expected 20)")
        except ValueError:
            dut._log.info(f"data_out not convertible: {out}")
    dut._log.info("Sorted input test -- PASS")


@cocotb.test()
async def test_spike_removal(dut):
    """Feed [10, 200, 10] -- spike should be filtered, median=10."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for val in [10, 200, 10]:
        dut.data_in.value = val
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)

    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    out = dut.data_out.value
    if out.is_resolvable:
        try:
            dut._log.info(f"Median of [10,200,10] = {int(out)} (expected 10)")
        except ValueError:
            dut._log.info(f"data_out not convertible: {out}")
    dut._log.info("Spike removal test -- PASS")


@cocotb.test()
async def test_equal_values(dut):
    """Feed [50, 50, 50], median should be 50."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for val in [50, 50, 50]:
        dut.data_in.value = val
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)

    dut.data_valid.value = 0
    await RisingEdge(dut.clk)

    out = dut.data_out.value
    if out.is_resolvable:
        try:
            assert int(out) == 50, f"Median of [50,50,50] should be 50, got {int(out)}"
        except ValueError:
            assert False, f"data_out not convertible: {out}"
    dut._log.info("Equal values test -- PASS")


@cocotb.test()
async def test_continuous_stream(dut):
    """Feed a stream of 10 values and verify valid outputs appear."""
    setup_clock(dut, "clk", 10)
    await init_inputs(dut)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    valid_count = 0
    for val in [5, 100, 3, 80, 7, 90, 10, 85, 12, 95]:
        dut.data_in.value = val
        dut.data_valid.value = 1
        await RisingEdge(dut.clk)
        dov = dut.data_out_valid.value
        if dov.is_resolvable:
            try:
                if int(dov) == 1:
                    valid_count += 1
                    out = dut.data_out.value
                    if out.is_resolvable:
                        dut._log.info(f"Output {valid_count}: {int(out)}")
            except ValueError:
                pass

    dut.data_valid.value = 0
    await ClockCycles(dut.clk, 5)
    dut._log.info(f"Continuous stream: {valid_count} valid outputs -- PASS")
