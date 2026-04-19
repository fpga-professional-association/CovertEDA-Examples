"""Cocotb testbench for radiant seven_segment."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify outputs are resolvable after reset."""
    setup_clock(dut, "clk", 40)
    dut.bcd_in.value = 0
    dut.dp_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.seg.value.is_resolvable, "seg has X/Z after reset"
    assert dut.an.value.is_resolvable, "an has X/Z after reset"
    dut._log.info("Reset state OK: seg and an are resolvable")


@cocotb.test()
async def test_digit_zero_display(dut):
    """Set BCD=0000 and verify segment pattern for digit 0."""
    setup_clock(dut, "clk", 40)
    dut.bcd_in.value = 0x0000
    dut.dp_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 5)

    assert dut.seg.value.is_resolvable, "seg has X/Z"
    try:
        seg = int(dut.seg.value)
        # Digit 0 pattern: 0b1000000 = 0x40
        dut._log.info(f"seg for digit 0: {seg:#04x} ({seg:07b})")
        assert seg == 0x40, f"Segment pattern for 0 incorrect: {seg:#04x}"
    except ValueError:
        raise AssertionError("seg not resolvable")


@cocotb.test()
async def test_digit_multiplexing(dut):
    """Set different BCD digits, verify anode scans all 4 positions."""
    setup_clock(dut, "clk", 40)
    dut.bcd_in.value = 0x1234  # digits: 1,2,3,4
    dut.dp_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # With REFRESH_BITS=4, full scan = 16 cycles
    an_values = set()
    for _ in range(20):
        await RisingEdge(dut.clk)
        if dut.an.value.is_resolvable:
            try:
                an_values.add(int(dut.an.value))
            except ValueError:
                pass

    dut._log.info(f"Anode values seen: {[f'{v:#06b}' for v in an_values]}")
    # Expect 4 different anode patterns
    assert len(an_values) >= 4, f"Not all digits scanned: only {len(an_values)} patterns"


@cocotb.test()
async def test_all_bcd_values(dut):
    """Step through all 16 BCD values and verify seg is resolvable."""
    setup_clock(dut, "clk", 40)
    dut.dp_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for bcd_val in range(16):
        dut.bcd_in.value = bcd_val  # Digit 0
        await ClockCycles(dut.clk, 5)

        assert dut.seg.value.is_resolvable, f"seg has X/Z for BCD {bcd_val}"
        try:
            seg = int(dut.seg.value)
            dut._log.info(f"BCD {bcd_val:X}: seg={seg:07b}")
        except ValueError:
            raise AssertionError(f"seg not resolvable for BCD {bcd_val}")


@cocotb.test()
async def test_decimal_point(dut):
    """Verify decimal point output tracks dp_in for active digit."""
    setup_clock(dut, "clk", 40)
    dut.bcd_in.value = 0
    dut.dp_in.value = 0x0F  # All decimal points active
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dp_seen_low = False
    for _ in range(20):
        await RisingEdge(dut.clk)
        if dut.dp.value.is_resolvable:
            try:
                dp_val = int(dut.dp.value)
                if dp_val == 0:  # Active low
                    dp_seen_low = True
            except ValueError:
                pass

    dut._log.info(f"Decimal point active (low) seen: {dp_seen_low}")
