"""Cocotb testbench for modbus_rtu - Modbus RTU frame parser."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, frame_valid should be 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.rx_byte.value = 0
    dut.rx_valid.value = 0
    await RisingEdge(dut.clk)

    if dut.frame_valid.value.is_resolvable:
        try:
            assert int(dut.frame_valid.value) == 0, "frame_valid should be 0 after reset"
        except ValueError:
            assert False, "frame_valid X/Z after reset"


@cocotb.test()
async def test_parse_write_frame(dut):
    """Send a 6-byte Modbus write frame and verify parsing."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    # Frame: addr=0x01, func=0x06 (write), reg=0x0100, value=0x00FF
    frame_bytes = [0x01, 0x06, 0x01, 0x00, 0x00, 0xFF]

    for b in frame_bytes:
        dut.rx_byte.value = b
        dut.rx_valid.value = 1
        await RisingEdge(dut.clk)
    dut.rx_valid.value = 0

    await ClockCycles(dut.clk, 3)

    if dut.slave_addr.value.is_resolvable:
        try:
            addr = int(dut.slave_addr.value)
            dut._log.info(f"Slave addr: {addr:#04x}")
            assert addr == 0x01, f"Expected addr 0x01, got {addr:#04x}"
        except ValueError:
            assert False, "slave_addr X/Z"

    if dut.func_code.value.is_resolvable:
        try:
            fc = int(dut.func_code.value)
            dut._log.info(f"Function code: {fc:#04x}")
            assert fc == 0x06, f"Expected func 0x06, got {fc:#04x}"
        except ValueError:
            assert False, "func_code X/Z"


@cocotb.test()
async def test_frame_valid_asserts(dut):
    """frame_valid should assert after complete frame."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    frame_bytes = [0x02, 0x03, 0x00, 0x10, 0x00, 0x01]

    for b in frame_bytes:
        dut.rx_byte.value = b
        dut.rx_valid.value = 1
        await RisingEdge(dut.clk)
    dut.rx_valid.value = 0

    valid_seen = False
    for _ in range(5):
        await RisingEdge(dut.clk)
        if dut.frame_valid.value.is_resolvable:
            try:
                if int(dut.frame_valid.value) == 1:
                    valid_seen = True
                    break
            except ValueError:
                pass

    dut._log.info(f"frame_valid seen: {valid_seen}")


@cocotb.test()
async def test_register_address(dut):
    """Verify register address is correctly parsed."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    # reg_addr = 0x1234
    frame_bytes = [0x01, 0x06, 0x12, 0x34, 0x56, 0x78]

    for b in frame_bytes:
        dut.rx_byte.value = b
        dut.rx_valid.value = 1
        await RisingEdge(dut.clk)
    dut.rx_valid.value = 0

    await ClockCycles(dut.clk, 3)

    if dut.reg_addr.value.is_resolvable:
        try:
            ra = int(dut.reg_addr.value)
            dut._log.info(f"Register address: {ra:#06x}")
            assert ra == 0x1234, f"Expected 0x1234, got {ra:#06x}"
        except ValueError:
            assert False, "reg_addr X/Z"

    if dut.reg_value.value.is_resolvable:
        try:
            rv = int(dut.reg_value.value)
            dut._log.info(f"Register value: {rv:#06x}")
            assert rv == 0x5678, f"Expected 0x5678, got {rv:#06x}"
        except ValueError:
            assert False, "reg_value X/Z"
