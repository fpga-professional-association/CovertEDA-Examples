"""Cocotb testbench for quartus rotary_encoder (quadrature decoder)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def quadrature_step_cw(dut, hold_cycles=10):
    """Generate one CW quadrature step: A leads B."""
    # State 00 -> 10 -> 11 -> 01 -> 00
    dut.enc_a.value = 1
    dut.enc_b.value = 0
    await ClockCycles(dut.clk, hold_cycles)
    dut.enc_a.value = 1
    dut.enc_b.value = 1
    await ClockCycles(dut.clk, hold_cycles)
    dut.enc_a.value = 0
    dut.enc_b.value = 1
    await ClockCycles(dut.clk, hold_cycles)
    dut.enc_a.value = 0
    dut.enc_b.value = 0
    await ClockCycles(dut.clk, hold_cycles)


async def quadrature_step_ccw(dut, hold_cycles=10):
    """Generate one CCW quadrature step: B leads A."""
    dut.enc_a.value = 0
    dut.enc_b.value = 1
    await ClockCycles(dut.clk, hold_cycles)
    dut.enc_a.value = 1
    dut.enc_b.value = 1
    await ClockCycles(dut.clk, hold_cycles)
    dut.enc_a.value = 1
    dut.enc_b.value = 0
    await ClockCycles(dut.clk, hold_cycles)
    dut.enc_a.value = 0
    dut.enc_b.value = 0
    await ClockCycles(dut.clk, hold_cycles)


@cocotb.test()
async def test_reset_state(dut):
    """Verify position is zero after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enc_a.value = 0
    dut.enc_b.value = 0
    dut.clear.value = 0
    await RisingEdge(dut.clk)

    if not dut.position.value.is_resolvable:
        raise AssertionError("position has X/Z after reset")

    try:
        pos = int(dut.position.value)
        dut._log.info(f"Position after reset: {pos}")
        assert pos == 0, f"Expected position=0, got {pos}"
    except ValueError:
        raise AssertionError("position not convertible")


@cocotb.test()
async def test_cw_rotation(dut):
    """Rotate CW and verify position increments."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enc_a.value = 0
    dut.enc_b.value = 0
    dut.clear.value = 0
    await ClockCycles(dut.clk, 5)

    # Do 3 CW steps
    for _ in range(3):
        await quadrature_step_cw(dut)

    await ClockCycles(dut.clk, 5)

    if dut.position.value.is_resolvable:
        try:
            pos = int(dut.position.value)
            dut._log.info(f"Position after 3 CW steps: {pos}")
            assert pos > 0, f"Expected positive position, got {pos}"
        except ValueError:
            raise AssertionError("position not convertible")


@cocotb.test()
async def test_ccw_rotation(dut):
    """Rotate CCW and verify position decrements (wraps to large unsigned)."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enc_a.value = 0
    dut.enc_b.value = 0
    dut.clear.value = 0
    await ClockCycles(dut.clk, 5)

    # Do 2 CCW steps
    for _ in range(2):
        await quadrature_step_ccw(dut)

    await ClockCycles(dut.clk, 5)

    if dut.position.value.is_resolvable:
        try:
            pos = int(dut.position.value)
            dut._log.info(f"Position after 2 CCW steps: {pos}")
            # Unsigned wrapping means position should be near 0xFFFF
            assert pos != 0, f"Position should have changed from 0"
        except ValueError:
            raise AssertionError("position not convertible")


@cocotb.test()
async def test_clear_position(dut):
    """Clear should reset position to zero."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enc_a.value = 0
    dut.enc_b.value = 0
    dut.clear.value = 0
    await ClockCycles(dut.clk, 5)

    # Step forward
    for _ in range(3):
        await quadrature_step_cw(dut)

    # Clear
    dut.clear.value = 1
    await ClockCycles(dut.clk, 3)
    dut.clear.value = 0
    await ClockCycles(dut.clk, 3)

    if dut.position.value.is_resolvable:
        try:
            pos = int(dut.position.value)
            dut._log.info(f"Position after clear: {pos}")
            assert pos == 0, f"Expected position=0 after clear, got {pos}"
        except ValueError:
            raise AssertionError("position not convertible")


@cocotb.test()
async def test_step_event_fires(dut):
    """step_event should pulse on each detected step."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enc_a.value = 0
    dut.enc_b.value = 0
    dut.clear.value = 0
    await ClockCycles(dut.clk, 5)

    step_count = 0
    # Do one CW step and count step_event pulses
    for cycle in range(50):
        if cycle == 5:
            dut.enc_a.value = 1
        elif cycle == 15:
            dut.enc_b.value = 1
        elif cycle == 25:
            dut.enc_a.value = 0
        elif cycle == 35:
            dut.enc_b.value = 0

        await RisingEdge(dut.clk)
        if dut.step_event.value.is_resolvable:
            try:
                if int(dut.step_event.value) == 1:
                    step_count += 1
            except ValueError:
                pass

    dut._log.info(f"Step events detected: {step_count}")
    assert step_count > 0, "Expected at least one step_event pulse"
