"""Cocotb testbench for vivado mem_top DDR3 test controller."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def drive_ddr3_dq_responder(dut, cycles=500):
    """Simple DDR3 DQ responder: echo a pattern on ddr3_dq when write
    activity is detected (ras_n/cas_n/we_n strobes).

    Since there is no real DDR3 memory model, this drives a fixed pattern
    back on the bidirectional ddr3_dq bus to keep the controller from
    hanging indefinitely.
    """
    for _ in range(cycles):
        await RisingEdge(dut.clk_sys)
        # When a read command is issued (ras_n=1, cas_n=0, we_n=1),
        # drive a simple incrementing pattern on ddr3_dq
        try:
            ras = int(dut.ddr3_ras_n.value)
            cas = int(dut.ddr3_cas_n.value)
            we = int(dut.ddr3_we_n.value)
            if ras == 1 and cas == 0 and we == 1:
                dut.ddr3_dq.value = 0xDEADBEEFCAFE0123
        except Exception:
            pass


@cocotb.test()
async def test_ddr3_controller(dut):
    """Assert test_en and verify test_busy responds; check status outputs."""

    # Start two 5 ns clocks (200 MHz each)
    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    # Initialize control signals
    dut.test_en.value = 0
    dut.test_mode.value = 0

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await RisingEdge(dut.clk_sys)

    # Verify initial state: test_busy should be 0 before test starts
    initial_busy = int(dut.test_busy.value)
    dut._log.info(f"Initial test_busy: {initial_busy}")
    assert initial_busy == 0, "test_busy should be 0 before test_en is asserted"

    # Start a DDR3 DQ responder in the background
    cocotb.start_soon(drive_ddr3_dq_responder(dut, cycles=500))

    # Enable the test: set test_en=1, test_mode=0
    dut.test_en.value = 1
    dut.test_mode.value = 0
    dut._log.info("Asserted test_en=1, test_mode=0")

    # Wait a few cycles and check that test_busy asserts
    busy_seen = False
    for _ in range(100):
        await RisingEdge(dut.clk_sys)
        if int(dut.test_busy.value) == 1:
            busy_seen = True
            break

    dut._log.info(f"test_busy asserted: {busy_seen}")
    assert busy_seen, "test_busy never asserted after enabling test"

    # Let the design run for a while
    await ClockCycles(dut.clk_sys, 300)

    # Read status outputs
    status_val = int(dut.status.value)
    error_count_val = int(dut.error_count.value)
    dut._log.info(f"status={status_val:#06x}, error_count={error_count_val}")

    # Deassert test_en
    dut.test_en.value = 0
    await ClockCycles(dut.clk_sys, 20)
