"""Cocotb testbench for radiant priority_encoder."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify outputs clear on reset."""
    setup_clock(dut, "clk", 40)
    dut.req.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.valid.value.is_resolvable, "valid has X/Z after reset"
    try:
        assert int(dut.valid.value) == 0, "valid should be 0 after reset"
        dut._log.info("Reset state OK: valid=0")
    except ValueError:
        raise AssertionError("valid not resolvable after reset")


@cocotb.test()
async def test_single_request(dut):
    """Assert each single request bit and verify correct encoding."""
    setup_clock(dut, "clk", 40)
    dut.req.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for bit in range(8):
        dut.req.value = 1 << bit
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        assert dut.enc_out.value.is_resolvable, f"enc_out has X/Z for req bit {bit}"
        assert dut.valid.value.is_resolvable, f"valid has X/Z for req bit {bit}"
        try:
            enc = int(dut.enc_out.value)
            v = int(dut.valid.value)
            assert v == 1, f"valid not asserted for req bit {bit}"
            assert enc == bit, f"enc_out mismatch: expected {bit}, got {enc}"
            dut._log.info(f"req[{bit}]=1 -> enc_out={enc}, valid={v}")
        except ValueError:
            raise AssertionError(f"Outputs not resolvable for req bit {bit}")


@cocotb.test()
async def test_priority_ordering(dut):
    """With multiple bits set, highest priority bit should win."""
    setup_clock(dut, "clk", 40)
    dut.req.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Set bits 2 and 5 -> priority should be 5
    dut.req.value = 0b00100100
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    assert dut.enc_out.value.is_resolvable, "enc_out has X/Z"
    try:
        enc = int(dut.enc_out.value)
        assert enc == 5, f"Priority mismatch: expected 5, got {enc}"
        dut._log.info(f"req=0b00100100 -> enc_out={enc} (correct: bit 5 wins)")
    except ValueError:
        raise AssertionError("enc_out not resolvable")


@cocotb.test()
async def test_no_request(dut):
    """With no requests, valid should be deasserted."""
    setup_clock(dut, "clk", 40)
    dut.req.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.req.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    assert dut.valid.value.is_resolvable, "valid has X/Z"
    try:
        v = int(dut.valid.value)
        assert v == 0, f"valid should be 0 when no requests: got {v}"
        dut._log.info("No request: valid correctly deasserted")
    except ValueError:
        raise AssertionError("valid not resolvable")


@cocotb.test()
async def test_grant_one_hot(dut):
    """Verify grant output is always one-hot when valid."""
    setup_clock(dut, "clk", 40)
    dut.req.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    test_patterns = [0xFF, 0x0F, 0xF0, 0x55, 0xAA, 0x01, 0x80]
    for pat in test_patterns:
        dut.req.value = pat
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        assert dut.grant.value.is_resolvable, f"grant has X/Z for req={pat:#04x}"
        try:
            g = int(dut.grant.value)
            # One-hot check: exactly one bit set
            assert g != 0 and (g & (g - 1)) == 0, f"grant not one-hot: {g:#04x}"
            dut._log.info(f"req={pat:#04x} -> grant={g:#04x} (one-hot OK)")
        except ValueError:
            raise AssertionError(f"grant not resolvable for req={pat:#04x}")
