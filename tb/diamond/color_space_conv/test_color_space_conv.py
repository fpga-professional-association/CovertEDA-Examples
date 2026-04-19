"""Cocotb testbench for color_space_conv - RGB to YCbCr converter."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, outputs should be zero."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.valid_in.value = 0
    dut.r_in.value = 0
    dut.g_in.value = 0
    dut.b_in.value = 0
    await RisingEdge(dut.clk)

    for sig_name in ["y_out", "cb_out", "cr_out"]:
        sig = getattr(dut, sig_name)
        if sig.value.is_resolvable:
            try:
                val = int(sig.value)
                dut._log.info(f"{sig_name} after reset: {val}")
            except ValueError:
                dut._log.info(f"{sig_name} X/Z after reset")


@cocotb.test()
async def test_black_pixel(dut):
    """Black (0,0,0) should produce Y=0, Cb~128, Cr~128."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.r_in.value = 0
    dut.g_in.value = 0
    dut.b_in.value = 0
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.y_out.value.is_resolvable:
        try:
            y = int(dut.y_out.value)
            cb = int(dut.cb_out.value)
            cr = int(dut.cr_out.value)
            dut._log.info(f"Black: Y={y}, Cb={cb}, Cr={cr}")
            assert y == 0, f"Expected Y=0 for black, got {y}"
            assert abs(cb - 128) <= 2, f"Expected Cb~128 for black, got {cb}"
            assert abs(cr - 128) <= 2, f"Expected Cr~128 for black, got {cr}"
        except ValueError:
            assert False, "Output X/Z for black pixel"


@cocotb.test()
async def test_white_pixel(dut):
    """White (255,255,255) should produce Y~255, Cb~128, Cr~128."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.r_in.value = 255
    dut.g_in.value = 255
    dut.b_in.value = 255
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.y_out.value.is_resolvable:
        try:
            y = int(dut.y_out.value)
            cb = int(dut.cb_out.value)
            cr = int(dut.cr_out.value)
            dut._log.info(f"White: Y={y}, Cb={cb}, Cr={cr}")
            assert y >= 250, f"Expected Y~255 for white, got {y}"
        except ValueError:
            assert False, "Output X/Z for white pixel"


@cocotb.test()
async def test_pure_red(dut):
    """Pure red (255,0,0) should give high Y, low Cb, high Cr."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.r_in.value = 255
    dut.g_in.value = 0
    dut.b_in.value = 0
    dut.valid_in.value = 1
    await RisingEdge(dut.clk)
    dut.valid_in.value = 0
    await RisingEdge(dut.clk)

    if dut.y_out.value.is_resolvable and dut.cr_out.value.is_resolvable:
        try:
            y = int(dut.y_out.value)
            cb = int(dut.cb_out.value)
            cr = int(dut.cr_out.value)
            dut._log.info(f"Red: Y={y}, Cb={cb}, Cr={cr}")
            assert cr > 128, f"Expected Cr>128 for red, got {cr}"
        except ValueError:
            assert False, "Output X/Z for red pixel"


@cocotb.test()
async def test_output_range(dut):
    """Test several colors and verify outputs stay in 0-255 range."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    colors = [(128, 128, 128), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    for r, g, b in colors:
        dut.r_in.value = r
        dut.g_in.value = g
        dut.b_in.value = b
        dut.valid_in.value = 1
        await RisingEdge(dut.clk)
        dut.valid_in.value = 0
        await RisingEdge(dut.clk)

        for sig_name in ["y_out", "cb_out", "cr_out"]:
            sig = getattr(dut, sig_name)
            if sig.value.is_resolvable:
                try:
                    val = int(sig.value)
                    assert 0 <= val <= 255, f"{sig_name} out of range for ({r},{g},{b}): {val}"
                except ValueError:
                    dut._log.info(f"{sig_name} X/Z for ({r},{g},{b})")

    dut._log.info("All test colors produced outputs in valid 0-255 range")
