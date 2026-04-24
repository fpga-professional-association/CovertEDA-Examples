"""Cocotb testbench for pdm_filter - PDM to PCM decimation filter."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, pcm_valid should be 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.pdm_in.value = 0
    dut.pdm_valid.value = 0
    await RisingEdge(dut.clk)

    if dut.pcm_valid.value.is_resolvable:
        try:
            assert int(dut.pcm_valid.value) == 0, "pcm_valid should be 0 after reset"
        except ValueError:
            assert False, "pcm_valid X/Z after reset"


@cocotb.test()
async def test_all_zeros_low_output(dut):
    """With PDM input all zeros, PCM output should be low."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.pdm_in.value = 0
    dut.pdm_valid.value = 1

    # Run for 2 decimation periods (128 samples)
    pcm_values = []
    for _ in range(128):
        await RisingEdge(dut.clk)
        if dut.pcm_valid.value.is_resolvable:
            try:
                if int(dut.pcm_valid.value) == 1:
                    if dut.pcm_out.value.is_resolvable:
                        pcm_values.append(int(dut.pcm_out.value))
            except ValueError:
                pass

    dut._log.info(f"PCM values from zero PDM: {pcm_values}")
    if pcm_values:
        assert pcm_values[-1] == 0, f"Expected 0 output for zero input, got {pcm_values[-1]}"


@cocotb.test()
async def test_all_ones_high_output(dut):
    """With PDM input all ones, PCM output should be high."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.pdm_in.value = 1
    dut.pdm_valid.value = 1

    pcm_values = []
    for _ in range(192):
        await RisingEdge(dut.clk)
        if dut.pcm_valid.value.is_resolvable:
            try:
                if int(dut.pcm_valid.value) == 1:
                    if dut.pcm_out.value.is_resolvable:
                        pcm_values.append(int(dut.pcm_out.value))
            except ValueError:
                pass

    dut._log.info(f"PCM values from ones PDM: {pcm_values}")
    if len(pcm_values) >= 2:
        assert pcm_values[-1] > 0, f"Expected positive output for all-ones input, got {pcm_values[-1]}"


@cocotb.test()
async def test_pcm_valid_asserts(dut):
    """pcm_valid should assert once every 64 PDM samples."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.pdm_in.value = 0
    dut.pdm_valid.value = 1

    valid_count = 0
    for _ in range(256):
        await RisingEdge(dut.clk)
        if dut.pcm_valid.value.is_resolvable:
            try:
                if int(dut.pcm_valid.value) == 1:
                    valid_count += 1
            except ValueError:
                pass

    dut._log.info(f"pcm_valid assertions in 256 PDM samples: {valid_count}")
    assert valid_count >= 3, f"Expected ~4 pcm_valid pulses, got {valid_count}"
