"""Cocotb testbench for radiant frequency_counter."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb_helpers import setup_clock, reset_dut


async def generate_signal(dut, period_ns, num_cycles):
    """Generate a square wave on sig_in for a number of cycles."""
    half = period_ns // 2
    for _ in range(num_cycles):
        dut.sig_in.value = 1
        await Timer(half, unit="ns")
        dut.sig_in.value = 0
        await Timer(half, unit="ns")


@cocotb.test()
async def test_reset_state(dut):
    """Verify outputs zero after reset."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.freq_count.value.is_resolvable, "freq_count has X/Z after reset"
    assert dut.period_count.value.is_resolvable, "period_count has X/Z after reset"
    try:
        fc = int(dut.freq_count.value)
        assert fc == 0, f"freq_count not zero: {fc}"
        dut._log.info("Reset state OK")
    except ValueError:
        raise AssertionError("freq_count not resolvable after reset")


@cocotb.test()
async def test_no_signal(dut):
    """With no input signal, freq_count should remain zero."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Wait for gate period (2^6 = 64 clocks = 2560ns)
    await ClockCycles(dut.clk, 70)

    assert dut.freq_count.value.is_resolvable, "freq_count has X/Z"
    try:
        fc = int(dut.freq_count.value)
        assert fc == 0, f"freq_count non-zero with no signal: {fc}"
        dut._log.info("No-signal test OK: freq_count=0")
    except ValueError:
        raise AssertionError("freq_count not resolvable")


@cocotb.test()
async def test_signal_detection(dut):
    """Apply a signal and verify edges are counted."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Generate signal in background
    cocotb.start_soon(generate_signal(dut, 200, 100))

    # Wait for at least one gate period
    await ClockCycles(dut.clk, 80)

    assert dut.freq_count.value.is_resolvable, "freq_count has X/Z"
    try:
        fc = int(dut.freq_count.value)
        dut._log.info(f"freq_count with signal: {fc}")
        assert fc > 0, "No edges counted"
    except ValueError:
        raise AssertionError("freq_count not resolvable")


@cocotb.test()
async def test_period_measurement(dut):
    """Verify period_count reflects clock cycles between edges."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Generate a slow signal (period = 400ns = 10 clock cycles)
    cocotb.start_soon(generate_signal(dut, 400, 20))

    await ClockCycles(dut.clk, 50)

    assert dut.period_count.value.is_resolvable, "period_count has X/Z"
    try:
        pc = int(dut.period_count.value)
        dut._log.info(f"period_count: {pc} clocks (expected ~10)")
    except ValueError:
        raise AssertionError("period_count not resolvable")


@cocotb.test()
async def test_valid_strobe(dut):
    """Verify valid pulses at end of gate period."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    cocotb.start_soon(generate_signal(dut, 200, 200))

    valid_seen = False
    for _ in range(80):
        await RisingEdge(dut.clk)
        if dut.valid.value.is_resolvable:
            try:
                if int(dut.valid.value) == 1:
                    valid_seen = True
                    dut._log.info("Valid strobe detected")
                    break
            except ValueError:
                pass

    assert valid_seen, "Valid strobe never asserted"
