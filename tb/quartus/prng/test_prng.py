"""Cocotb testbench for quartus prng (32-bit xorshift PRNG)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify default seed is loaded after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 0
    dut.seed_wr.value = 0
    dut.seed_val.value = 0
    await RisingEdge(dut.clk)

    if not dut.rng_out.value.is_resolvable:
        raise AssertionError("rng_out has X/Z after reset")

    try:
        val = int(dut.rng_out.value)
        dut._log.info(f"State after reset: {val:#010x}")
        assert val == 0x12345678, f"Expected default seed 0x12345678, got {val:#010x}"
    except ValueError:
        raise AssertionError("rng_out not convertible")


@cocotb.test()
async def test_generates_different_values(dut):
    """Enable PRNG for several cycles, verify output changes."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 0
    dut.seed_wr.value = 0
    dut.seed_val.value = 0
    await RisingEdge(dut.clk)

    values = set()
    dut.enable.value = 1
    for _ in range(20):
        await RisingEdge(dut.clk)
        if dut.rng_out.value.is_resolvable:
            try:
                values.add(int(dut.rng_out.value))
            except ValueError:
                pass
    dut.enable.value = 0
    await RisingEdge(dut.clk)

    dut._log.info(f"Generated {len(values)} unique values in 20 cycles")
    assert len(values) > 5, f"Expected diverse output, only got {len(values)} unique values"


@cocotb.test()
async def test_seed_load(dut):
    """Load a custom seed and verify it takes effect."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 0
    dut.seed_wr.value = 0
    dut.seed_val.value = 0
    await RisingEdge(dut.clk)

    # Load custom seed
    dut.seed_wr.value = 1
    dut.seed_val.value = 0xAAAA5555
    await RisingEdge(dut.clk)
    dut.seed_wr.value = 0
    await RisingEdge(dut.clk)

    if dut.rng_out.value.is_resolvable:
        try:
            val = int(dut.rng_out.value)
            dut._log.info(f"State after seed load: {val:#010x}")
            assert val == 0xAAAA5555, f"Expected seed 0xAAAA5555, got {val:#010x}"
        except ValueError:
            raise AssertionError("rng_out not convertible")


@cocotb.test()
async def test_deterministic_sequence(dut):
    """Same seed should produce same sequence of values."""
    setup_clock(dut, "clk", 20)

    sequences = []
    for run in range(2):
        await reset_dut(dut, "rst_n", active_low=True, cycles=5)
        dut.enable.value = 0
        dut.seed_wr.value = 0
        dut.seed_val.value = 0
        await RisingEdge(dut.clk)

        # Load same seed
        dut.seed_wr.value = 1
        dut.seed_val.value = 0xDEADBEEF
        await RisingEdge(dut.clk)
        dut.seed_wr.value = 0
        await RisingEdge(dut.clk)

        seq = []
        dut.enable.value = 1
        for _ in range(10):
            await RisingEdge(dut.clk)
            if dut.rng_out.value.is_resolvable:
                try:
                    seq.append(int(dut.rng_out.value))
                except ValueError:
                    seq.append(None)
        dut.enable.value = 0
        sequences.append(seq)

    dut._log.info(f"Run 1: {[hex(v) if v else 'X' for v in sequences[0]]}")
    dut._log.info(f"Run 2: {[hex(v) if v else 'X' for v in sequences[1]]}")
    assert sequences[0] == sequences[1], "Sequences from same seed differ!"


@cocotb.test()
async def test_valid_signal(dut):
    """valid should assert only when enable is high."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.enable.value = 0
    dut.seed_wr.value = 0
    dut.seed_val.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    if dut.valid.value.is_resolvable:
        try:
            v = int(dut.valid.value)
            dut._log.info(f"valid when disabled: {v}")
            assert v == 0, f"Expected valid=0 when disabled, got {v}"
        except ValueError:
            raise AssertionError("valid not convertible")

    dut.enable.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    if dut.valid.value.is_resolvable:
        try:
            v = int(dut.valid.value)
            dut._log.info(f"valid when enabled: {v}")
            assert v == 1, f"Expected valid=1 when enabled, got {v}"
        except ValueError:
            raise AssertionError("valid not convertible")
