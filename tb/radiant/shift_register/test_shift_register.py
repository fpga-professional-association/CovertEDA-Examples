"""Cocotb testbench for radiant shift_register."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify register clears to zero on reset."""
    setup_clock(dut, "clk", 40)
    dut.serial_in.value = 0
    dut.shift_en.value = 0
    dut.load.value = 0
    dut.dir.value = 0
    dut.parallel_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.data_out.value.is_resolvable, "data_out has X/Z after reset"
    try:
        val = int(dut.data_out.value)
        assert val == 0, f"data_out not zero after reset: {val}"
        dut._log.info(f"data_out after reset: {val:#010x}")
    except ValueError:
        raise AssertionError("data_out not resolvable after reset")


@cocotb.test()
async def test_parallel_load(dut):
    """Load a parallel value and verify output."""
    setup_clock(dut, "clk", 40)
    dut.serial_in.value = 0
    dut.shift_en.value = 0
    dut.load.value = 0
    dut.dir.value = 0
    dut.parallel_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    dut.parallel_in.value = 0xDEADBEEF
    dut.load.value = 1
    await RisingEdge(dut.clk)
    dut.load.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.data_out.value.is_resolvable, "data_out has X/Z after load"
    try:
        val = int(dut.data_out.value)
        assert val == 0xDEADBEEF, f"data_out mismatch: {val:#010x}"
        dut._log.info(f"Parallel load OK: {val:#010x}")
    except ValueError:
        raise AssertionError("data_out not resolvable after load")


@cocotb.test()
async def test_shift_left(dut):
    """Shift left with serial_in=0, verify value shifts left."""
    setup_clock(dut, "clk", 40)
    dut.serial_in.value = 0
    dut.shift_en.value = 0
    dut.load.value = 0
    dut.dir.value = 0
    dut.parallel_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Load a known value
    dut.parallel_in.value = 0x00000001
    dut.load.value = 1
    await RisingEdge(dut.clk)
    # Deassert load and wait a full cycle to ensure load is cleared
    dut.load.value = 0
    dut.shift_en.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # Confirm loaded value
    if dut.data_out.value.is_resolvable:
        try:
            loaded = int(dut.data_out.value)
            dut._log.info(f"Loaded value: {loaded:#010x}")
        except ValueError:
            pass

    # Shift left 4 times with serial_in=0
    # RTL: data_out <= {data_out[30:0], serial_in}
    dut.shift_en.value = 1
    dut.dir.value = 0  # left
    dut.serial_in.value = 0
    for _ in range(4):
        await RisingEdge(dut.clk)
    dut.shift_en.value = 0
    await Timer(1, unit="ns")

    # After 4 left shifts of 0x00000001 with serial_in=0:
    # cycle 1: {0x00000001[30:0], 0} = 0x00000002
    # cycle 2: {0x00000002[30:0], 0} = 0x00000004
    # cycle 3: {0x00000004[30:0], 0} = 0x00000008
    # cycle 4: {0x00000008[30:0], 0} = 0x00000010
    assert dut.data_out.value.is_resolvable, "data_out has X/Z after shift"
    try:
        val = int(dut.data_out.value)
        expected = 0x00000010
        assert val == expected, f"Shift left mismatch: got {val:#010x}, expected {expected:#010x}"
        dut._log.info(f"Shift left 4x: {val:#010x}")
    except ValueError:
        raise AssertionError("data_out not resolvable after shift")


@cocotb.test()
async def test_shift_right(dut):
    """Shift right with serial_in=0, verify value shifts right."""
    setup_clock(dut, "clk", 40)
    dut.serial_in.value = 0
    dut.shift_en.value = 0
    dut.load.value = 0
    dut.dir.value = 0
    dut.parallel_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Load a known value
    dut.parallel_in.value = 0x80000000
    dut.load.value = 1
    await RisingEdge(dut.clk)
    # Deassert load and wait a full cycle
    dut.load.value = 0
    dut.shift_en.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # Confirm loaded value
    if dut.data_out.value.is_resolvable:
        try:
            loaded = int(dut.data_out.value)
            dut._log.info(f"Loaded value: {loaded:#010x}")
        except ValueError:
            pass

    # Shift right 4 times with serial_in=0
    # RTL: data_out <= {serial_in, data_out[31:1]}
    dut.shift_en.value = 1
    dut.dir.value = 1  # right
    dut.serial_in.value = 0
    for _ in range(4):
        await RisingEdge(dut.clk)
    dut.shift_en.value = 0
    await Timer(1, unit="ns")

    # After 4 right shifts of 0x80000000 with serial_in=0:
    # cycle 1: {0, 0x80000000[31:1]} = 0x40000000
    # cycle 2: 0x20000000
    # cycle 3: 0x10000000
    # cycle 4: 0x08000000
    assert dut.data_out.value.is_resolvable, "data_out has X/Z after shift"
    try:
        val = int(dut.data_out.value)
        expected = 0x08000000
        assert val == expected, f"Shift right mismatch: got {val:#010x}, expected {expected:#010x}"
        dut._log.info(f"Shift right 4x: {val:#010x}")
    except ValueError:
        raise AssertionError("data_out not resolvable after shift")


@cocotb.test()
async def test_rotate_left(dut):
    """Rotate left and verify bit wraps from MSB to LSB."""
    setup_clock(dut, "clk", 40)
    dut.serial_in.value = 0
    dut.shift_en.value = 0
    dut.load.value = 0
    dut.dir.value = 0
    dut.parallel_in.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Load value with MSB set
    dut.parallel_in.value = 0x80000001
    dut.load.value = 1
    await RisingEdge(dut.clk)
    # Deassert load and wait a full cycle to ensure load is cleared
    dut.load.value = 0
    dut.shift_en.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # Confirm loaded value
    if dut.data_out.value.is_resolvable:
        try:
            loaded = int(dut.data_out.value)
            dut._log.info(f"Loaded value before rotate: {loaded:#010x}")
        except ValueError:
            pass

    # Rotate left 1 time
    # RTL: data_out <= {data_out[30:0], data_out[31]}
    # 0x80000001 = 1000...0001 -> {000...0001, 1} = 0x00000003
    dut.shift_en.value = 1
    dut.dir.value = 2  # rotate left
    await RisingEdge(dut.clk)
    dut.shift_en.value = 0
    await Timer(1, unit="ns")

    assert dut.data_out.value.is_resolvable, "data_out has X/Z after rotate"
    try:
        val = int(dut.data_out.value)
        expected = 0x00000003
        assert val == expected, f"Rotate left mismatch: got {val:#010x}, expected {expected:#010x}"
        dut._log.info(f"Rotate left 1x: {val:#010x}")
    except ValueError:
        raise AssertionError("data_out not resolvable after rotate")
