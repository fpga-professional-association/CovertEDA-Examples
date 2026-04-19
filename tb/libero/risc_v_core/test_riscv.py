"""Cocotb testbench for libero rv32i_top.

Models instruction memory in cocotb by monitoring imem_addr and driving
imem_data with a small test program.  Verifies the PC advances and that
register x1 holds the expected value after executing ADDI x1, x0, 5.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut

# Simple test program: instruction memory contents
IMEM = {
    0x00: 0x00500093,  # ADDI x1, x0, 5
    0x04: 0x00300113,  # ADDI x2, x0, 3
    0x08: 0x002081B3,  # ADD  x3, x1, x2
    0x0C: 0x00000013,  # NOP (ADDI x0, x0, 0)
}
DEFAULT_NOP = 0x00000013


async def imem_responder(dut):
    """Background coroutine that models instruction memory.

    On each rising clock edge, read imem_addr and drive imem_data with
    the corresponding instruction from IMEM, defaulting to NOP.
    """
    while True:
        await RisingEdge(dut.clk)
        addr = int(dut.imem_addr.value)
        instr = IMEM.get(addr, DEFAULT_NOP)
        dut.imem_data.value = instr


@cocotb.test()
async def test_addi_program(dut):
    """Load a simple program and verify PC advances and x1 == 5."""

    # Start a 20 ns clock (50 MHz)
    setup_clock(dut, "clk", 20)

    # Drive dmem_data_in to 0 (no data memory response needed)
    dut.dmem_data_in.value = 0

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Launch the instruction memory responder
    cocotb.start_soon(imem_responder(dut))

    # Run for 20 clock cycles to let the CPU execute the program
    await ClockCycles(dut.clk, 20)

    # Verify PC has advanced past address 0x00
    pc_val = int(dut.pc_debug.value)
    dut._log.info(f"PC after 20 cycles: {pc_val:#010x}")
    assert pc_val > 0x00, f"PC should have advanced past 0x00, got {pc_val:#010x}"

    # Verify register x1 holds 5 (from ADDI x1, x0, 5)
    x1_val = int(dut.reg_x1_debug.value)
    dut._log.info(f"x1 after 20 cycles: {x1_val}")
    assert x1_val == 5, f"Expected x1 == 5, got {x1_val}"
