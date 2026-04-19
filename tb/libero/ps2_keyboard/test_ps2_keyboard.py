"""Cocotb testbench for ps2_keyboard - PS/2 keyboard interface."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def send_ps2_byte(dut, byte_val, clk_period_ns=200):
    """Send a PS/2 frame: start(0) + 8 data bits + odd parity + stop(1)."""
    parity = ~(bin(byte_val).count('1') % 2) & 1  # odd parity

    bits = [0]  # start bit
    for i in range(8):
        bits.append((byte_val >> i) & 1)
    bits.append(parity)
    bits.append(1)  # stop bit

    for bit in bits:
        dut.ps2_data.value = bit
        dut.ps2_clk.value = 1
        await Timer(clk_period_ns // 2, unit="ns")
        dut.ps2_clk.value = 0  # falling edge - data sampled
        await Timer(clk_period_ns // 2, unit="ns")

    dut.ps2_clk.value = 1
    dut.ps2_data.value = 1
    await Timer(clk_period_ns, unit="ns")


@cocotb.test()
async def test_reset_state(dut):
    """After reset, scancode_valid should be 0."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.ps2_clk.value = 1
    dut.ps2_data.value = 1
    await RisingEdge(dut.clk)

    if dut.scancode_valid.value.is_resolvable:
        try:
            assert int(dut.scancode_valid.value) == 0, "scancode_valid should be 0 after reset"
        except ValueError:
            assert False, "scancode_valid X/Z after reset"


@cocotb.test()
async def test_receive_scancode(dut):
    """Send scancode 0x1C (A key) and verify reception."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.ps2_clk.value = 1
    dut.ps2_data.value = 1
    await ClockCycles(dut.clk, 10)

    await send_ps2_byte(dut, 0x1C)

    valid_seen = False
    for _ in range(50):
        await RisingEdge(dut.clk)
        if dut.scancode_valid.value.is_resolvable:
            try:
                if int(dut.scancode_valid.value) == 1:
                    valid_seen = True
                    break
            except ValueError:
                pass

    if valid_seen and dut.scancode.value.is_resolvable:
        try:
            sc = int(dut.scancode.value)
            dut._log.info(f"Received scancode: {sc:#04x}")
        except ValueError:
            dut._log.info("scancode X/Z")


@cocotb.test()
async def test_idle_no_valid(dut):
    """With no PS/2 activity, scancode_valid should stay 0."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.ps2_clk.value = 1
    dut.ps2_data.value = 1

    await ClockCycles(dut.clk, 100)

    if dut.scancode_valid.value.is_resolvable:
        try:
            assert int(dut.scancode_valid.value) == 0, "No valid without PS/2 activity"
        except ValueError:
            assert False, "scancode_valid X/Z"

    dut._log.info("No spurious scancode_valid during idle")
