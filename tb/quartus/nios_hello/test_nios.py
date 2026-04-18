"""Cocotb testbench for quartus nios_top with altpll stub."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


def check_no_xz(signal, name):
    """Verify a signal resolves to a valid integer (no X/Z)."""
    val = int(signal.value)
    assert 0 <= val <= 0xFF, f"{name} value {val} out of range, possible X/Z"
    return val


@cocotb.test()
async def test_nios_basic(dut):
    """Reset, drive sw_input, verify led_output and seg_output have no X/Z."""

    # Start a 10 ns clock (100 MHz)
    setup_clock(dut, "clk_100m", 10)

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Drive switch inputs
    dut.sw_input.value = 0xA5

    # Run for 50 clock cycles to let design settle
    await ClockCycles(dut.clk_100m, 50)

    # Verify no X/Z on LED and segment outputs
    led_val = check_no_xz(dut.led_output, "led_output")
    seg_val = check_no_xz(dut.seg_output, "seg_output")
    dut._log.info(f"led_output={led_val:#04x}, seg_output={seg_val:#04x}")


@cocotb.test()
async def test_nios_switch_change(dut):
    """Drive different sw_input values and verify outputs respond."""

    # Start a 10 ns clock (100 MHz)
    setup_clock(dut, "clk_100m", 10)

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    test_values = [0x00, 0xFF, 0x55, 0xAA, 0x0F, 0xF0]

    for sw_val in test_values:
        dut.sw_input.value = sw_val
        await ClockCycles(dut.clk_100m, 20)

        led_val = check_no_xz(dut.led_output, "led_output")
        seg_val = check_no_xz(dut.seg_output, "seg_output")
        dut._log.info(
            f"sw_input={sw_val:#04x} -> led_output={led_val:#04x}, "
            f"seg_output={seg_val:#04x}"
        )
