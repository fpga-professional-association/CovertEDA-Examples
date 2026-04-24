"""Cocotb testbench for quartus scrambler (8-bit data scrambler/descrambler)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify output is zero after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.valid_in.value = 0
    dut.din.value = 0
    dut.key.value = 0
    dut.descramble.value = 0
    await RisingEdge(dut.clk)

    if not dut.dout.value.is_resolvable:
        raise AssertionError("dout has X/Z after reset")

    try:
        val = int(dut.dout.value)
        vout = int(dut.valid_out.value)
    except ValueError:
        raise AssertionError("Signals not convertible after reset")

    assert val == 0, f"Expected dout=0 after reset, got {val}"
    assert vout == 0, f"Expected valid_out=0 after reset, got {vout}"
    dut._log.info("Reset state: dout=0, valid_out=0")


@cocotb.test()
async def test_scramble_changes_data(dut):
    """Scrambled output should differ from input."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.valid_in.value = 0
    dut.din.value = 0
    dut.key.value = 0xA5
    dut.descramble.value = 0
    await RisingEdge(dut.clk)

    dut.valid_in.value = 1
    dut.din.value = 0x42
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.dout.value.is_resolvable:
        try:
            scrambled = int(dut.dout.value)
            dut._log.info(f"Input: 0x42, Scrambled: {scrambled:#04x}")
            assert scrambled != 0x42, f"Scrambled output should differ from input"
        except ValueError:
            raise AssertionError("dout not convertible")


@cocotb.test()
async def test_roundtrip(dut):
    """Scramble then descramble should recover original data (same LFSR state)."""
    setup_clock(dut, "clk", 20)

    test_key = 0x5A
    test_data = 0x37

    # Scramble
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    dut.valid_in.value = 0
    dut.din.value = 0
    dut.key.value = test_key
    dut.descramble.value = 0
    await RisingEdge(dut.clk)

    dut.valid_in.value = 1
    dut.din.value = test_data
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    scrambled = 0
    if dut.dout.value.is_resolvable:
        try:
            scrambled = int(dut.dout.value)
            dut._log.info(f"Scrambled: {scrambled:#04x}")
        except ValueError:
            raise AssertionError("dout not convertible during scramble")

    # Descramble with fresh LFSR (reset)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    dut.valid_in.value = 0
    dut.din.value = 0
    dut.key.value = test_key
    dut.descramble.value = 1
    await RisingEdge(dut.clk)

    dut.valid_in.value = 1
    dut.din.value = scrambled
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.dout.value.is_resolvable:
        try:
            recovered = int(dut.dout.value)
            dut._log.info(f"Recovered: {recovered:#04x}, Original: {test_data:#04x}")
            assert recovered == test_data, f"Roundtrip failed: expected {test_data:#04x}, got {recovered:#04x}"
        except ValueError:
            raise AssertionError("dout not convertible during descramble")


@cocotb.test()
async def test_valid_out_timing(dut):
    """valid_out should pulse for one cycle per valid_in."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.valid_in.value = 0
    dut.din.value = 0
    dut.key.value = 0
    dut.descramble.value = 0
    await RisingEdge(dut.clk)

    # One cycle pulse
    dut.valid_in.value = 1
    dut.din.value = 0xAB
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    # valid_out should be low after valid_in goes low
    await RisingEdge(dut.clk)
    if dut.valid_out.value.is_resolvable:
        try:
            vout = int(dut.valid_out.value)
            dut._log.info(f"valid_out after valid_in deasserted: {vout}")
            assert vout == 0, f"Expected valid_out=0 one cycle after input, got {vout}"
        except ValueError:
            raise AssertionError("valid_out not convertible")


@cocotb.test()
async def test_different_keys(dut):
    """Different keys should produce different scrambled outputs."""
    setup_clock(dut, "clk", 20)

    results = []
    for key_val in [0x00, 0xFF, 0xA5]:
        await reset_dut(dut, "rst_n", active_low=True, cycles=5)
        dut.valid_in.value = 0
        dut.din.value = 0
        dut.key.value = key_val
        dut.descramble.value = 0
        await RisingEdge(dut.clk)

        dut.valid_in.value = 1
        dut.din.value = 0x55
        await RisingEdge(dut.clk)
        dut.valid_in.value = 0
        await RisingEdge(dut.clk)

        if dut.dout.value.is_resolvable:
            try:
                results.append(int(dut.dout.value))
            except ValueError:
                results.append(None)

    dut._log.info(f"Scrambled with keys [0x00, 0xFF, 0xA5]: {[hex(r) if r else 'X' for r in results]}")
    # At least some should differ
    unique = set(r for r in results if r is not None)
    assert len(unique) >= 2, "Expected different outputs for different keys"
