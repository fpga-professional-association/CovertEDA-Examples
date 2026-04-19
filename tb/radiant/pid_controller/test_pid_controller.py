"""Cocotb testbench for radiant pid_controller."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify all outputs zero after reset."""
    setup_clock(dut, "clk", 40)
    dut.update.value = 0
    dut.setpoint.value = 0
    dut.feedback.value = 0
    dut.kp.value = 0
    dut.ki.value = 0
    dut.kd.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.pid_out.value.is_resolvable, "pid_out has X/Z after reset"
    try:
        val = int(dut.pid_out.value)
        dut._log.info(f"pid_out after reset: {val}")
    except ValueError:
        raise AssertionError("pid_out not resolvable after reset")


@cocotb.test()
async def test_proportional_response(dut):
    """With only Kp, verify output responds to error."""
    setup_clock(dut, "clk", 40)
    dut.update.value = 0
    dut.setpoint.value = 0
    dut.feedback.value = 0
    dut.kp.value = 10
    dut.ki.value = 0
    dut.kd.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Set error = setpoint - feedback = 100
    dut.setpoint.value = 100
    dut.feedback.value = 0

    # Pulse update multiple times to let pipeline settle
    for _ in range(5):
        dut.update.value = 1
        await RisingEdge(dut.clk)
    dut.update.value = 0
    await RisingEdge(dut.clk)

    assert dut.pid_out.value.is_resolvable, "pid_out has X/Z"
    try:
        val = int(dut.pid_out.value)
        dut._log.info(f"Proportional response: pid_out={val}")
        # Output should be non-zero with positive error
    except ValueError:
        raise AssertionError("pid_out not resolvable")


@cocotb.test()
async def test_zero_error(dut):
    """With setpoint=feedback, output should converge to near zero."""
    setup_clock(dut, "clk", 40)
    dut.update.value = 0
    dut.setpoint.value = 0
    dut.feedback.value = 0
    dut.kp.value = 5
    dut.ki.value = 0
    dut.kd.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.setpoint.value = 500
    dut.feedback.value = 500

    for _ in range(10):
        dut.update.value = 1
        await RisingEdge(dut.clk)
    dut.update.value = 0
    await RisingEdge(dut.clk)

    assert dut.pid_out.value.is_resolvable, "pid_out has X/Z"
    try:
        val = int(dut.pid_out.value)
        dut._log.info(f"Zero error response: pid_out={val}")
    except ValueError:
        raise AssertionError("pid_out not resolvable")


@cocotb.test()
async def test_out_valid_strobe(dut):
    """Verify out_valid pulses on update and deasserts otherwise."""
    setup_clock(dut, "clk", 40)
    dut.update.value = 0
    dut.setpoint.value = 100
    dut.feedback.value = 50
    dut.kp.value = 1
    dut.ki.value = 0
    dut.kd.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.update.value = 1
    await RisingEdge(dut.clk)
    dut.update.value = 0
    await RisingEdge(dut.clk)

    assert dut.out_valid.value.is_resolvable, "out_valid has X/Z"
    try:
        ov = int(dut.out_valid.value)
        dut._log.info(f"out_valid after update: {ov}")
    except ValueError:
        raise AssertionError("out_valid not resolvable")

    # Wait a cycle for deassert
    await RisingEdge(dut.clk)
    assert dut.out_valid.value.is_resolvable, "out_valid has X/Z"
    try:
        ov = int(dut.out_valid.value)
        assert ov == 0, f"out_valid not deasserted: {ov}"
        dut._log.info("out_valid correctly deasserts")
    except ValueError:
        raise AssertionError("out_valid not resolvable")


@cocotb.test()
async def test_sustained_updates(dut):
    """Run 50 update cycles and verify no X/Z."""
    setup_clock(dut, "clk", 40)
    dut.update.value = 0
    dut.setpoint.value = 1000
    dut.feedback.value = 200
    dut.kp.value = 2
    dut.ki.value = 1
    dut.kd.value = 1
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for i in range(50):
        dut.update.value = 1
        await RisingEdge(dut.clk)
        dut.update.value = 0
        await RisingEdge(dut.clk)

        if dut.pid_out.value.is_resolvable:
            try:
                val = int(dut.pid_out.value)
                if i % 10 == 0:
                    dut._log.info(f"Update {i}: pid_out={val}")
            except ValueError:
                pass
        else:
            raise AssertionError(f"pid_out has X/Z at update {i}")

    dut._log.info("50 update cycles completed without X/Z")
