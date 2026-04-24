"""Cocotb testbench for radiant lfsr."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_to_seed(dut):
    """Verify LFSR resets to default seed value."""
    setup_clock(dut, "clk", 40)
    dut.enable.value = 0
    dut.load.value = 0
    dut.seed_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.lfsr_out.value.is_resolvable, "lfsr_out has X/Z after reset"
    try:
        val = int(dut.lfsr_out.value)
        assert val == 0xACE1, f"lfsr_out not seed value: {val:#06x}"
        dut._log.info(f"Reset to seed OK: {val:#06x}")
    except ValueError:
        raise AssertionError("lfsr_out not resolvable after reset")


@cocotb.test()
async def test_no_lockup(dut):
    """Run LFSR for many cycles, verify it does not lock up at zero."""
    setup_clock(dut, "clk", 40)
    dut.enable.value = 0
    dut.load.value = 0
    dut.seed_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.enable.value = 1
    zero_count = 0
    for i in range(500):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if dut.lfsr_out.value.is_resolvable:
            try:
                val = int(dut.lfsr_out.value)
                if val == 0:
                    zero_count += 1
                    dut._log.info(f"LFSR output zero at cycle {i}")
            except ValueError:
                pass

    dut._log.info(f"LFSR ran 500 cycles, zero occurrences: {zero_count}")
    # A maximal-length LFSR with non-zero seed should never reach zero
    assert zero_count == 0, f"LFSR reached zero state {zero_count} times in 500 cycles"


@cocotb.test()
async def test_sequence_varies(dut):
    """Verify LFSR produces different values over time."""
    setup_clock(dut, "clk", 40)
    dut.enable.value = 0
    dut.load.value = 0
    dut.seed_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.enable.value = 1
    values = set()
    for _ in range(100):
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        if dut.lfsr_out.value.is_resolvable:
            try:
                values.add(int(dut.lfsr_out.value))
            except ValueError:
                pass

    dut._log.info(f"Unique values in 100 cycles: {len(values)}")
    assert len(values) > 50, f"LFSR not random enough: only {len(values)} unique values"


@cocotb.test()
async def test_enable_hold(dut):
    """Disable LFSR and verify it holds its value."""
    setup_clock(dut, "clk", 40)
    dut.enable.value = 0
    dut.load.value = 0
    dut.seed_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.enable.value = 1
    await ClockCycles(dut.clk, 10)
    await Timer(1, unit="ns")

    assert dut.lfsr_out.value.is_resolvable, "lfsr_out has X/Z"
    try:
        val_before = int(dut.lfsr_out.value)
    except ValueError:
        raise AssertionError("lfsr_out not resolvable")

    dut.enable.value = 0
    await ClockCycles(dut.clk, 10)
    await Timer(1, unit="ns")

    assert dut.lfsr_out.value.is_resolvable, "lfsr_out has X/Z after disable"
    try:
        val_after = int(dut.lfsr_out.value)
        assert val_before == val_after, f"LFSR changed while disabled: {val_before:#06x} -> {val_after:#06x}"
        dut._log.info(f"Enable hold OK: lfsr stays at {val_after:#06x}")
    except ValueError:
        raise AssertionError("lfsr_out not resolvable after disable")


@cocotb.test()
async def test_load_seed(dut):
    """Load a custom seed and verify output."""
    setup_clock(dut, "clk", 40)
    dut.enable.value = 0
    dut.load.value = 0
    dut.seed_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.seed_in.value = 0x1234
    dut.load.value = 1
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.lfsr_out.value.is_resolvable, "lfsr_out has X/Z after load"
    try:
        val = int(dut.lfsr_out.value)
        assert val == 0x1234, f"lfsr_out mismatch after load: {val:#06x}"
        dut._log.info(f"Seed loaded OK: {val:#06x}")
    except ValueError:
        raise AssertionError("lfsr_out not resolvable after load")
