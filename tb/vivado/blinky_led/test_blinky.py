"""Cocotb testbench for vivado blinky_top."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_led_changes(dut):
    """Verify LED output is clean after reset and design runs without X/Z."""

    # Start a 10 ns clock (100 MHz)
    setup_clock(dut, "clk_in", 10)

    # Drive btn_in to 0 (no buttons pressed)
    dut.btn_in.value = 0

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Capture the initial LED value after reset
    await RisingEdge(dut.clk_in)
    assert dut.led_out.value.is_resolvable, "led_out has X/Z right after reset"
    initial_led = int(dut.led_out.value)
    dut._log.info(f"Initial LED value after reset: {initial_led:#06b}")

    # Run for some cycles
    await ClockCycles(dut.clk_in, 100)

    # Verify LED is still resolvable (no X/Z)
    assert dut.led_out.value.is_resolvable, "led_out has X/Z after 100 cycles"
    final_led = int(dut.led_out.value)
    dut._log.info(f"Final LED value after 100 cycles: {final_led:#06b}")

    dut._log.info("Blinky design runs cleanly with no X/Z on LED output")


@cocotb.test()
async def test_reset_state(dut):
    """Verify led_out is in a known state immediately after reset."""

    setup_clock(dut, "clk_in", 10)
    dut.btn_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk_in)

    assert dut.led_out.value.is_resolvable, "led_out has X/Z right after reset"
    try:
        led_val = int(dut.led_out.value)
        dut._log.info(f"led_out after reset: {led_val:#06b}")
    except ValueError:
        dut._log.info("led_out not convertible to int after reset (X/Z)")
        assert False, "led_out should be resolvable after reset"


@cocotb.test()
async def test_btn_input_0(dut):
    """Set btn_in=0, run 100 cycles, verify outputs are clean."""

    setup_clock(dut, "clk_in", 10)
    dut.btn_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(100):
        await RisingEdge(dut.clk_in)
        assert dut.led_out.value.is_resolvable, f"led_out has X/Z at cycle {cycle}"

    try:
        led_val = int(dut.led_out.value)
        dut._log.info(f"led_out after 100 cycles with btn_in=0: {led_val:#06b}")
    except ValueError:
        assert False, "led_out not resolvable after 100 cycles with btn_in=0"


@cocotb.test()
async def test_btn_input_1(dut):
    """Set btn_in=1, run 100 cycles, check behavior."""

    setup_clock(dut, "clk_in", 10)
    dut.btn_in.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(100):
        await RisingEdge(dut.clk_in)
        assert dut.led_out.value.is_resolvable, f"led_out has X/Z at cycle {cycle} with btn_in=1"

    try:
        led_val = int(dut.led_out.value)
        dut._log.info(f"led_out after 100 cycles with btn_in=1: {led_val:#06b}")
    except ValueError:
        assert False, "led_out not resolvable after 100 cycles with btn_in=1"


@cocotb.test()
async def test_btn_input_2(dut):
    """Set btn_in=2, run 100 cycles, verify outputs."""

    setup_clock(dut, "clk_in", 10)
    dut.btn_in.value = 2

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(100):
        await RisingEdge(dut.clk_in)
        assert dut.led_out.value.is_resolvable, f"led_out has X/Z at cycle {cycle} with btn_in=2"

    try:
        led_val = int(dut.led_out.value)
        dut._log.info(f"led_out after 100 cycles with btn_in=2: {led_val:#06b}")
    except ValueError:
        assert False, "led_out not resolvable after 100 cycles with btn_in=2"


@cocotb.test()
async def test_btn_input_3(dut):
    """Set btn_in=3, run 100 cycles, verify outputs."""

    setup_clock(dut, "clk_in", 10)
    dut.btn_in.value = 3

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(100):
        await RisingEdge(dut.clk_in)
        assert dut.led_out.value.is_resolvable, f"led_out has X/Z at cycle {cycle} with btn_in=3"

    try:
        led_val = int(dut.led_out.value)
        dut._log.info(f"led_out after 100 cycles with btn_in=3: {led_val:#06b}")
    except ValueError:
        assert False, "led_out not resolvable after 100 cycles with btn_in=3"


@cocotb.test()
async def test_led_range(dut):
    """Verify led_out stays within 0-15 for 300 cycles."""

    setup_clock(dut, "clk_in", 10)
    dut.btn_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(300):
        await RisingEdge(dut.clk_in)
        if not dut.led_out.value.is_resolvable:
            assert False, f"led_out has X/Z at cycle {cycle}"
        try:
            led_val = int(dut.led_out.value)
            assert 0 <= led_val <= 15, (
                f"led_out={led_val} out of range [0,15] at cycle {cycle}"
            )
        except ValueError:
            assert False, f"led_out not convertible to int at cycle {cycle}"

    dut._log.info("led_out stayed within 0-15 for all 300 cycles")


@cocotb.test()
async def test_reset_during_run(dut):
    """Reset mid-operation, verify the design recovers cleanly."""

    setup_clock(dut, "clk_in", 10)
    dut.btn_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Run for 50 cycles
    await ClockCycles(dut.clk_in, 50)
    assert dut.led_out.value.is_resolvable, "led_out has X/Z before mid-run reset"
    try:
        pre_reset_val = int(dut.led_out.value)
        dut._log.info(f"led_out before mid-run reset: {pre_reset_val:#06b}")
    except ValueError:
        pass

    # Assert reset again mid-run
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Verify recovery
    await RisingEdge(dut.clk_in)
    assert dut.led_out.value.is_resolvable, "led_out has X/Z after mid-run reset"
    try:
        post_reset_val = int(dut.led_out.value)
        dut._log.info(f"led_out after mid-run reset: {post_reset_val:#06b}")
    except ValueError:
        assert False, "led_out not resolvable after mid-run reset"

    # Run 50 more cycles to confirm stability
    await ClockCycles(dut.clk_in, 50)
    assert dut.led_out.value.is_resolvable, "led_out has X/Z after recovery"
    dut._log.info("Design recovered cleanly from mid-run reset")


@cocotb.test()
async def test_long_run(dut):
    """Run 1000 cycles and verify no X/Z appears on led_out."""

    setup_clock(dut, "clk_in", 10)
    dut.btn_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(1000):
        await RisingEdge(dut.clk_in)
        if not dut.led_out.value.is_resolvable:
            assert False, f"led_out has X/Z at cycle {cycle} during long run"

    try:
        final_val = int(dut.led_out.value)
        dut._log.info(f"led_out after 1000 cycles: {final_val:#06b}")
    except ValueError:
        assert False, "led_out not resolvable after 1000 cycles"

    dut._log.info("Long run of 1000 cycles completed with no X/Z")


@cocotb.test()
async def test_multiple_resets(dut):
    """Apply 3 reset cycles and verify design stays clean each time."""

    setup_clock(dut, "clk_in", 10)
    dut.btn_in.value = 0

    for reset_num in range(3):
        await reset_dut(dut, "rst_n", active_low=True, cycles=5)
        await RisingEdge(dut.clk_in)

        assert dut.led_out.value.is_resolvable, (
            f"led_out has X/Z after reset #{reset_num + 1}"
        )
        try:
            led_val = int(dut.led_out.value)
            dut._log.info(f"led_out after reset #{reset_num + 1}: {led_val:#06b}")
        except ValueError:
            assert False, f"led_out not resolvable after reset #{reset_num + 1}"

        # Run some cycles between resets
        await ClockCycles(dut.clk_in, 30)
        assert dut.led_out.value.is_resolvable, (
            f"led_out has X/Z after running 30 cycles post-reset #{reset_num + 1}"
        )

    dut._log.info("Design survived 3 consecutive resets cleanly")


@cocotb.test()
async def test_btn_change_during_run(dut):
    """Change btn_in mid-operation and verify design handles it cleanly."""

    setup_clock(dut, "clk_in", 10)
    dut.btn_in.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Run with btn_in=0
    await ClockCycles(dut.clk_in, 50)
    assert dut.led_out.value.is_resolvable, "led_out has X/Z with btn_in=0"
    try:
        val_btn0 = int(dut.led_out.value)
        dut._log.info(f"led_out with btn_in=0 after 50 cycles: {val_btn0:#06b}")
    except ValueError:
        pass

    # Switch to btn_in=1
    dut.btn_in.value = 1
    await ClockCycles(dut.clk_in, 50)
    assert dut.led_out.value.is_resolvable, "led_out has X/Z after btn_in changed to 1"
    try:
        val_btn1 = int(dut.led_out.value)
        dut._log.info(f"led_out with btn_in=1 after 50 cycles: {val_btn1:#06b}")
    except ValueError:
        pass

    # Switch to btn_in=3
    dut.btn_in.value = 3
    await ClockCycles(dut.clk_in, 50)
    assert dut.led_out.value.is_resolvable, "led_out has X/Z after btn_in changed to 3"
    try:
        val_btn3 = int(dut.led_out.value)
        dut._log.info(f"led_out with btn_in=3 after 50 cycles: {val_btn3:#06b}")
    except ValueError:
        pass

    # Switch back to btn_in=0
    dut.btn_in.value = 0
    await ClockCycles(dut.clk_in, 50)
    assert dut.led_out.value.is_resolvable, "led_out has X/Z after btn_in returned to 0"

    dut._log.info("Design handled btn_in changes during operation cleanly")
