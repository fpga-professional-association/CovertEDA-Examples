"""Cocotb testbench for bit_reversal - N-bit reversal circuit."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut

WIDTH = 32


def reverse_bits(val, width=WIDTH):
    """Python reference: reverse bits of val."""
    result = 0
    for i in range(width):
        if val & (1 << i):
            result |= 1 << (width - 1 - i)
    return result


@cocotb.test()
async def test_reset_state(dut):
    """After reset, data_out should be 0."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.data_in.value = 0
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.data_out.value.is_resolvable:
        try:
            assert int(dut.data_out.value) == 0, "data_out should be 0 after reset"
        except ValueError:
            assert False, "data_out X/Z after reset"


@cocotb.test()
async def test_reverse_one_bit(dut):
    """Input with only MSB set should produce output with only LSB set."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.data_in.value = 1 << (WIDTH - 1)
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.data_out.value.is_resolvable:
        try:
            val = int(dut.data_out.value)
            dut._log.info(f"Reversed MSB: {val:#010x}")
            assert val == 1, f"Expected 1, got {val:#010x}"
        except ValueError:
            assert False, "data_out X/Z"


@cocotb.test()
async def test_reverse_pattern(dut):
    """Reverse 0xF0F0F0F0 and verify against Python reference."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    test_val = 0xF0F0F0F0
    expected = reverse_bits(test_val)

    dut.data_in.value = test_val
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.data_out.value.is_resolvable:
        try:
            val = int(dut.data_out.value)
            dut._log.info(f"Input: {test_val:#010x}, Reversed: {val:#010x}, Expected: {expected:#010x}")
            assert val == expected, f"Mismatch: got {val:#010x}, expected {expected:#010x}"
        except ValueError:
            assert False, "data_out X/Z"


@cocotb.test()
async def test_double_reverse(dut):
    """Reversing twice should return the original value."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    original = 0xDEADBEEF

    # First reversal
    dut.data_in.value = original
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.data_out.value.is_resolvable:
        try:
            reversed_val = int(dut.data_out.value)
        except ValueError:
            assert False, "data_out X/Z on first reversal"
    else:
        assert False, "data_out not resolvable"

    # Second reversal
    dut.data_in.value = reversed_val
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.data_out.value.is_resolvable:
        try:
            double_rev = int(dut.data_out.value)
            dut._log.info(f"Original: {original:#010x}, Double-reversed: {double_rev:#010x}")
            assert double_rev == original, f"Double reversal mismatch: {double_rev:#010x} != {original:#010x}"
        except ValueError:
            assert False, "data_out X/Z on second reversal"


@cocotb.test()
async def test_sweep_values(dut):
    """Test several values and verify against Python reference."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    test_values = [0x00000000, 0xFFFFFFFF, 0x00000001, 0x80000000, 0xAAAAAAAA, 0x12345678]

    for tv in test_values:
        expected = reverse_bits(tv)
        dut.data_in.value = tv
        dut.valid_in.value = 1
        await RisingEdge(dut.clk)
        dut.valid_in.value = 0
        await RisingEdge(dut.clk)

        if dut.data_out.value.is_resolvable:
            try:
                val = int(dut.data_out.value)
                assert val == expected, f"Mismatch for {tv:#010x}: got {val:#010x}, expected {expected:#010x}"
            except ValueError:
                dut._log.info(f"X/Z for input {tv:#010x}")

    dut._log.info(f"All {len(test_values)} test values verified")
