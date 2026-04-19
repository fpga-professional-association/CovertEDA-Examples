"""Cocotb testbench for ace gddr6_top.

Provides a simple Python-dict-based memory model that responds to the DUT's
write and read enable signals, then verifies test_result has no X/Z.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def memory_model(dut):
    """Background coroutine: simple memory model using a Python dict.

    On wr_en: store wr_data at wr_addr.
    On rd_en: drive rd_data from stored value (or 0 if address not found).
    """
    mem = {}

    while True:
        await RisingEdge(dut.clk)

        # Handle writes -- guard against X/Z on addr/data during early cycles
        try:
            if dut.wr_en.value.is_resolvable and int(dut.wr_en.value) == 1:
                addr = int(dut.wr_addr.value)
                data = int(dut.wr_data.value)
                mem[addr] = data
                dut._log.info(f"MEM WRITE: addr={addr:#010x} data={data:#066x}")
        except ValueError:
            pass

        # Handle reads -- guard against X/Z on addr during early cycles
        try:
            if dut.rd_en.value.is_resolvable and int(dut.rd_en.value) == 1:
                addr = int(dut.rd_addr.value)
                data = mem.get(addr, 0)
                dut.rd_data.value = data
                dut._log.info(f"MEM READ:  addr={addr:#010x} data={data:#066x}")
        except ValueError:
            pass


@cocotb.test()
async def test_gddr6_memory(dut):
    """Run the GDDR6 traffic generator with a memory model and check results."""

    # Start a 10 ns clock (100 MHz)
    setup_clock(dut, "clk", 10)

    # Initialise rd_data to 0
    dut.rd_data.value = 0

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Start background memory model
    cocotb.start_soon(memory_model(dut))

    # Run for 200 clock cycles
    await ClockCycles(dut.clk, 200)

    # Verify test_result has no X/Z
    result = dut.test_result.value
    assert result.is_resolvable, (
        f"test_result contains X/Z after 200 cycles: {result}"
    )
    dut._log.info(f"test_result = {int(result):#010x}")
