"""Cocotb testbench for libero motor_top.

Verifies PWM output toggling when speed_cmd is set, and quadrature
encoder counting when encoder_a/encoder_b are driven in sequence.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


def count_transitions(values):
    """Count the number of 0->1 or 1->0 transitions in a list of values."""
    transitions = 0
    for i in range(1, len(values)):
        if values[i] != values[i - 1]:
            transitions += 1
    return transitions


@cocotb.test()
async def test_pwm_toggling(dut):
    """Set speed_cmd and verify PWM outputs toggle over 200 cycles."""

    # Start a 20 ns clock (50 MHz)
    setup_clock(dut, "clk", 20)

    # Initialize inputs
    dut.speed_cmd.value = 0
    dut.encoder_a.value = 0
    dut.encoder_b.value = 0

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Set a non-zero speed command
    dut.speed_cmd.value = 1000

    # Record PWM output values over 200 clock cycles
    pwm_u_vals = []
    pwm_v_vals = []
    pwm_w_vals = []

    for _ in range(200):
        await RisingEdge(dut.clk)
        pwm_u_vals.append(int(dut.pwm_u.value))
        pwm_v_vals.append(int(dut.pwm_v.value))
        pwm_w_vals.append(int(dut.pwm_w.value))

    # Verify that at least one PWM output has toggled
    u_trans = count_transitions(pwm_u_vals)
    v_trans = count_transitions(pwm_v_vals)
    w_trans = count_transitions(pwm_w_vals)

    dut._log.info(
        f"PWM transitions over 200 cycles: "
        f"pwm_u={u_trans}, pwm_v={v_trans}, pwm_w={w_trans}"
    )

    total_transitions = u_trans + v_trans + w_trans
    assert total_transitions > 0, (
        "Expected at least one PWM output to toggle, but none did"
    )


@cocotb.test()
async def test_encoder_counting(dut):
    """Drive quadrature encoder signals and verify encoder_count increments."""

    # Start a 20 ns clock (50 MHz)
    setup_clock(dut, "clk", 20)

    # Initialize inputs
    dut.speed_cmd.value = 0
    dut.encoder_a.value = 0
    dut.encoder_b.value = 0

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Record the initial encoder count
    await RisingEdge(dut.clk)
    initial_count = int(dut.encoder_count.value)
    dut._log.info(f"Initial encoder_count: {initial_count}")

    # Drive quadrature encoder sequence (forward rotation):
    # State sequence: (A=0,B=0) -> (A=1,B=0) -> (A=1,B=1) -> (A=0,B=1) -> (A=0,B=0)
    # Each full cycle represents one encoder tick
    for step in range(8):  # 8 full quadrature cycles
        # Phase 1: A=1, B=0
        dut.encoder_a.value = 1
        dut.encoder_b.value = 0
        await ClockCycles(dut.clk, 4)

        # Phase 2: A=1, B=1
        dut.encoder_a.value = 1
        dut.encoder_b.value = 1
        await ClockCycles(dut.clk, 4)

        # Phase 3: A=0, B=1
        dut.encoder_a.value = 0
        dut.encoder_b.value = 1
        await ClockCycles(dut.clk, 4)

        # Phase 4: A=0, B=0
        dut.encoder_a.value = 0
        dut.encoder_b.value = 0
        await ClockCycles(dut.clk, 4)

    # Allow a few more cycles for the count to settle
    await ClockCycles(dut.clk, 10)

    final_count = int(dut.encoder_count.value)
    dut._log.info(f"Final encoder_count after 8 quadrature cycles: {final_count}")

    assert final_count > initial_count, (
        f"Expected encoder_count to increment from {initial_count}, "
        f"but got {final_count}"
    )
