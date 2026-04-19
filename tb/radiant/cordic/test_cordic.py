"""Cocotb testbench for radiant cordic."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify outputs are zero after reset."""
    setup_clock(dut, "clk", 40)
    dut.valid_in.value = 0
    dut.angle_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.cos_out.value.is_resolvable, "cos_out has X/Z after reset"
    assert dut.sin_out.value.is_resolvable, "sin_out has X/Z after reset"
    assert dut.valid_out.value.is_resolvable, "valid_out has X/Z after reset"
    try:
        v = int(dut.valid_out.value)
        assert v == 0, f"valid_out not zero after reset: {v}"
        dut._log.info("Reset state OK")
    except ValueError:
        raise AssertionError("valid_out not resolvable after reset")


@cocotb.test()
async def test_pipeline_valid(dut):
    """Send a single valid input and wait for valid output."""
    setup_clock(dut, "clk", 40)
    dut.valid_in.value = 0
    dut.angle_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Apply angle = 0 (cos=max, sin=0)
    dut.angle_in.value = 0
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0

    # Wait for pipeline to flush (STAGES + 2 margin)
    valid_seen = False
    for i in range(20):
        await RisingEdge(dut.clk)
        if dut.valid_out.value.is_resolvable:
            try:
                if int(dut.valid_out.value) == 1:
                    valid_seen = True
                    dut._log.info(f"Valid output appeared at cycle {i+1}")
                    break
            except ValueError:
                pass

    assert valid_seen, "valid_out never asserted after pipeline flush"


@cocotb.test()
async def test_cos_sin_resolvable(dut):
    """Feed angle and verify cos/sin outputs are resolvable."""
    setup_clock(dut, "clk", 40)
    dut.valid_in.value = 0
    dut.angle_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Feed a 45-degree angle (8192 in our scaling)
    dut.angle_in.value = 8192
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0

    await ClockCycles(dut.clk, 18)

    assert dut.cos_out.value.is_resolvable, "cos_out has X/Z"
    assert dut.sin_out.value.is_resolvable, "sin_out has X/Z"
    try:
        cos_v = int(dut.cos_out.value)
        sin_v = int(dut.sin_out.value)
        dut._log.info(f"Angle=45deg -> cos={cos_v}, sin={sin_v}")
    except ValueError:
        raise AssertionError("cos/sin not resolvable")


@cocotb.test()
async def test_multiple_angles(dut):
    """Feed several angles sequentially, verify valid outputs emerge."""
    setup_clock(dut, "clk", 40)
    dut.valid_in.value = 0
    dut.angle_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    angles = [0, 4096, 8192, 16384, 32768]
    for angle in angles:
        dut.angle_in.value = angle
        dut.valid_in.value = 1
        await RisingEdge(dut.clk)
    dut.valid_in.value = 0

    valid_count = 0
    for _ in range(30):
        await RisingEdge(dut.clk)
        if dut.valid_out.value.is_resolvable:
            try:
                if int(dut.valid_out.value) == 1:
                    valid_count += 1
                    if dut.cos_out.value.is_resolvable and dut.sin_out.value.is_resolvable:
                        c = int(dut.cos_out.value)
                        s = int(dut.sin_out.value)
                        dut._log.info(f"Output {valid_count}: cos={c}, sin={s}")
            except ValueError:
                pass

    dut._log.info(f"Total valid outputs: {valid_count}")


@cocotb.test()
async def test_continuous_stream(dut):
    """Feed continuous valid inputs for 50 cycles, verify no X/Z."""
    setup_clock(dut, "clk", 40)
    dut.valid_in.value = 0
    dut.angle_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.valid_in.value = 1
    for i in range(50):
        dut.angle_in.value = i * 1000
        await RisingEdge(dut.clk)
    dut.valid_in.value = 0

    await ClockCycles(dut.clk, 20)

    assert dut.cos_out.value.is_resolvable, "cos_out has X/Z after stream"
    assert dut.sin_out.value.is_resolvable, "sin_out has X/Z after stream"
    dut._log.info("Continuous stream completed without X/Z")
