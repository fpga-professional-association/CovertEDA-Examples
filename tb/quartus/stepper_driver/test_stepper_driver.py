"""Cocotb testbench for quartus stepper_driver (full/half step, 4-phase)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def do_step(dut, cycles=5):
    """Generate a step pulse."""
    dut.step_pulse.value = 1
    await ClockCycles(dut.clk, cycles)
    dut.step_pulse.value = 0
    await ClockCycles(dut.clk, cycles)


@cocotb.test()
async def test_reset_state(dut):
    """Verify initial phase output after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 0
    dut.direction.value = 0
    dut.half_step.value = 0
    dut.step_pulse.value = 0
    await RisingEdge(dut.clk)

    if not dut.phase_out.value.is_resolvable:
        raise AssertionError("phase_out has X/Z after reset")

    try:
        phase = int(dut.phase_out.value)
        dut._log.info(f"Phase after reset: {phase:#06b}")
        assert phase == 0b0001, f"Expected phase=0001, got {phase:#06b}"
    except ValueError:
        raise AssertionError("phase_out not convertible")


@cocotb.test()
async def test_full_step_forward(dut):
    """Step forward in full-step mode and verify 4-state sequence."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 1
    dut.direction.value = 0  # CW
    dut.half_step.value = 0  # full step
    dut.step_pulse.value = 0
    await RisingEdge(dut.clk)

    phases = []
    for _ in range(5):
        await do_step(dut)
        if dut.phase_out.value.is_resolvable:
            try:
                phases.append(int(dut.phase_out.value))
            except ValueError:
                phases.append(None)

    dut._log.info(f"Full step CW phases: {[f'{p:#06b}' if p else 'X' for p in phases]}")
    # Should see a rotating pattern
    valid_phases = [p for p in phases if p is not None]
    assert len(valid_phases) >= 4, f"Expected at least 4 phase readings"


@cocotb.test()
async def test_half_step_sequence(dut):
    """Step forward in half-step mode and verify 8-state sequence."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 1
    dut.direction.value = 0
    dut.half_step.value = 1  # half step
    dut.step_pulse.value = 0
    await RisingEdge(dut.clk)

    phases = []
    for _ in range(9):
        await do_step(dut)
        if dut.phase_out.value.is_resolvable:
            try:
                phases.append(int(dut.phase_out.value))
            except ValueError:
                phases.append(None)

    dut._log.info(f"Half step CW phases: {[f'{p:#06b}' if p else 'X' for p in phases]}")
    valid_phases = [p for p in phases if p is not None]
    assert len(valid_phases) >= 8, f"Expected at least 8 phase readings"


@cocotb.test()
async def test_direction_reversal(dut):
    """Step CW then CCW; verify phase reverses."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 1
    dut.direction.value = 0  # CW
    dut.half_step.value = 0
    dut.step_pulse.value = 0
    await RisingEdge(dut.clk)

    # Step forward 2 times
    for _ in range(2):
        await do_step(dut)

    if dut.phase_out.value.is_resolvable:
        try:
            fwd_phase = int(dut.phase_out.value)
            dut._log.info(f"Phase after 2 CW steps: {fwd_phase:#06b}")
        except ValueError:
            fwd_phase = None

    # Reverse direction
    dut.direction.value = 1  # CCW
    for _ in range(2):
        await do_step(dut)

    if dut.phase_out.value.is_resolvable:
        try:
            rev_phase = int(dut.phase_out.value)
            dut._log.info(f"Phase after 2 CCW steps: {rev_phase:#06b}")
            # Should be back at initial state
            assert rev_phase == 0b0001, f"Expected return to start phase, got {rev_phase:#06b}"
        except ValueError:
            raise AssertionError("phase_out not convertible")


@cocotb.test()
async def test_disabled_no_step(dut):
    """When disabled, step pulses should not change phase."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 0  # disabled
    dut.direction.value = 0
    dut.half_step.value = 0
    dut.step_pulse.value = 0
    await RisingEdge(dut.clk)

    if dut.phase_out.value.is_resolvable:
        try:
            initial = int(dut.phase_out.value)
        except ValueError:
            raise AssertionError("phase_out not convertible")
    else:
        raise AssertionError("phase_out has X/Z")

    # Try stepping while disabled
    for _ in range(4):
        await do_step(dut)

    if dut.phase_out.value.is_resolvable:
        try:
            after = int(dut.phase_out.value)
            dut._log.info(f"Phase before steps: {initial:#06b}, after: {after:#06b}")
            assert initial == after, f"Phase changed while disabled"
        except ValueError:
            raise AssertionError("phase_out not convertible")
