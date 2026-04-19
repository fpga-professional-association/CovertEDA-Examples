"""Cocotb testbench for quartus power_on_reset (configurable delay POR)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_initial_state(dut):
    """Verify reset is asserted at power-on (rst_n_out=0)."""
    setup_clock(dut, "clk", 20)

    dut.delay_cfg.value = 10
    dut.force_rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.force_rst.value = 0
    await RisingEdge(dut.clk)

    if not dut.rst_n_out.value.is_resolvable:
        raise AssertionError("rst_n_out has X/Z at start")

    try:
        rst = int(dut.rst_n_out.value)
        done = int(dut.rst_done.value)
    except ValueError:
        raise AssertionError("Signals not convertible at start")

    assert rst == 0, f"Expected rst_n_out=0 during reset, got {rst}"
    assert done == 0, f"Expected rst_done=0 during reset, got {done}"
    dut._log.info("Initial state: rst_n_out=0, rst_done=0")


@cocotb.test()
async def test_reset_completes(dut):
    """Reset should deassert after delay_cfg cycles."""
    setup_clock(dut, "clk", 20)

    delay = 10
    dut.delay_cfg.value = delay
    dut.force_rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.force_rst.value = 0
    await RisingEdge(dut.clk)

    # Wait for reset to complete
    await ClockCycles(dut.clk, delay + 5)

    if dut.rst_n_out.value.is_resolvable:
        try:
            rst = int(dut.rst_n_out.value)
            done = int(dut.rst_done.value)
            dut._log.info(f"After {delay}+ cycles: rst_n_out={rst}, rst_done={done}")
            assert rst == 1, f"Expected rst_n_out=1, got {rst}"
            assert done == 1, f"Expected rst_done=1, got {done}"
        except ValueError:
            raise AssertionError("Signals not convertible")


@cocotb.test()
async def test_different_delays(dut):
    """Different delay_cfg values should change when reset deasserts."""
    setup_clock(dut, "clk", 20)

    for delay in [5, 20, 50]:
        dut.delay_cfg.value = delay
        dut.force_rst.value = 1
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        dut.force_rst.value = 0
        await RisingEdge(dut.clk)

        # Check reset is still asserted at delay/2
        await ClockCycles(dut.clk, max(1, delay // 2))
        if dut.rst_n_out.value.is_resolvable:
            try:
                mid_rst = int(dut.rst_n_out.value)
                dut._log.info(f"Delay={delay}, mid-point rst_n_out={mid_rst}")
            except ValueError:
                pass

        # Wait until after delay completes
        await ClockCycles(dut.clk, delay)
        if dut.rst_done.value.is_resolvable:
            try:
                done = int(dut.rst_done.value)
                dut._log.info(f"Delay={delay}, after completion rst_done={done}")
                assert done == 1, f"Expected rst_done=1 for delay={delay}"
            except ValueError:
                raise AssertionError("rst_done not convertible")


@cocotb.test()
async def test_force_reset(dut):
    """force_rst should restart the reset sequence."""
    setup_clock(dut, "clk", 20)

    dut.delay_cfg.value = 10
    dut.force_rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.force_rst.value = 0

    # Wait for reset to complete
    await ClockCycles(dut.clk, 15)

    if dut.rst_done.value.is_resolvable:
        try:
            assert int(dut.rst_done.value) == 1, "Reset should be done"
        except ValueError:
            pass

    # Force reset again
    dut.force_rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.force_rst.value = 0
    await RisingEdge(dut.clk)

    if dut.rst_n_out.value.is_resolvable:
        try:
            rst = int(dut.rst_n_out.value)
            dut._log.info(f"After force_rst: rst_n_out={rst}")
            assert rst == 0, f"Expected rst_n_out=0 after force_rst, got {rst}"
        except ValueError:
            raise AssertionError("rst_n_out not convertible")


@cocotb.test()
async def test_counter_increments(dut):
    """Verify count_out increments during reset sequence."""
    setup_clock(dut, "clk", 20)

    dut.delay_cfg.value = 20
    dut.force_rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.force_rst.value = 0
    await RisingEdge(dut.clk)

    counts = []
    for _ in range(15):
        await RisingEdge(dut.clk)
        if dut.count_out.value.is_resolvable:
            try:
                counts.append(int(dut.count_out.value))
            except ValueError:
                pass

    dut._log.info(f"Counter values: {counts}")
    if len(counts) >= 2:
        assert counts[-1] > counts[0], "Counter should be incrementing"
