"""Cocotb testbench for radiant gpio_controller."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def write_reg(dut, addr, data):
    """Helper: write a register."""
    dut.addr.value = addr
    dut.wr_data.value = data
    dut.wr_en.value = 1
    await RisingEdge(dut.clk)
    dut.wr_en.value = 0
    await RisingEdge(dut.clk)


async def read_reg(dut, addr):
    """Helper: read a register and return value."""
    dut.addr.value = addr
    dut.rd_en.value = 1
    await RisingEdge(dut.clk)
    dut.rd_en.value = 0
    await RisingEdge(dut.clk)
    if dut.rd_data.value.is_resolvable:
        return int(dut.rd_data.value)
    return None


@cocotb.test()
async def test_reset_state(dut):
    """Verify all registers zero after reset."""
    setup_clock(dut, "clk", 40)
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.addr.value = 0
    dut.wr_data.value = 0
    dut.gpio_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.gpio_out.value.is_resolvable, "gpio_out has X/Z after reset"
    assert dut.gpio_oe.value.is_resolvable, "gpio_oe has X/Z after reset"
    try:
        assert int(dut.gpio_out.value) == 0, "gpio_out not zero"
        assert int(dut.gpio_oe.value) == 0, "gpio_oe not zero"
        dut._log.info("Reset state OK")
    except ValueError:
        raise AssertionError("Outputs not resolvable after reset")


@cocotb.test()
async def test_write_direction(dut):
    """Write to direction register and verify gpio_oe."""
    setup_clock(dut, "clk", 40)
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.addr.value = 0
    dut.wr_data.value = 0
    dut.gpio_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await write_reg(dut, 0, 0xF0)  # Upper 4 bits as outputs

    assert dut.gpio_oe.value.is_resolvable, "gpio_oe has X/Z"
    try:
        oe = int(dut.gpio_oe.value)
        assert oe == 0xF0, f"gpio_oe mismatch: {oe:#04x}"
        dut._log.info(f"Direction register OK: gpio_oe={oe:#04x}")
    except ValueError:
        raise AssertionError("gpio_oe not resolvable")


@cocotb.test()
async def test_write_output(dut):
    """Write to output register and verify gpio_out."""
    setup_clock(dut, "clk", 40)
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.addr.value = 0
    dut.wr_data.value = 0
    dut.gpio_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await write_reg(dut, 1, 0xA5)

    assert dut.gpio_out.value.is_resolvable, "gpio_out has X/Z"
    try:
        out = int(dut.gpio_out.value)
        assert out == 0xA5, f"gpio_out mismatch: {out:#04x}"
        dut._log.info(f"Output register OK: gpio_out={out:#04x}")
    except ValueError:
        raise AssertionError("gpio_out not resolvable")


@cocotb.test()
async def test_read_input(dut):
    """Apply gpio_in and read via input register."""
    setup_clock(dut, "clk", 40)
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.addr.value = 0
    dut.wr_data.value = 0
    dut.gpio_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.gpio_in.value = 0x5A
    # Wait for synchronizer (2 stages + 1)
    await ClockCycles(dut.clk, 4)

    val = await read_reg(dut, 2)
    assert val is not None, "rd_data not resolvable"
    assert val == 0x5A, f"Input read mismatch: {val:#04x}"
    dut._log.info(f"Input register read OK: {val:#04x}")


@cocotb.test()
async def test_readback_direction(dut):
    """Write direction register, read it back."""
    setup_clock(dut, "clk", 40)
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.addr.value = 0
    dut.wr_data.value = 0
    dut.gpio_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await write_reg(dut, 0, 0x33)
    val = await read_reg(dut, 0)
    assert val is not None, "rd_data not resolvable"
    assert val == 0x33, f"Direction readback mismatch: {val:#04x}"
    dut._log.info(f"Direction readback OK: {val:#04x}")
