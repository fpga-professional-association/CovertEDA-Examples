"""Cocotb testbench for vivado pwm_top with AXI-Lite register access."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut
from axi_lite_driver import axi_write, axi_read


@cocotb.test()
async def test_pwm_red_channel(dut):
    """Write a duty cycle via AXI-Lite and verify pwm_red toggles."""

    # Start a 10 ns clock (100 MHz)
    setup_clock(dut, "clk", 10)

    # Initialize all AXI signals to 0
    dut.axi_awaddr.value = 0
    dut.axi_awvalid.value = 0
    dut.axi_wdata.value = 0
    dut.axi_wstrb.value = 0
    dut.axi_wvalid.value = 0
    dut.axi_bready.value = 0
    dut.axi_araddr.value = 0
    dut.axi_arvalid.value = 0
    dut.axi_rready.value = 0

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write duty cycle value 128 to address 0x00 (red channel)
    await axi_write(dut, 0x00, 128, prefix="axi")
    dut._log.info("Wrote duty cycle 128 to red channel register (0x00)")

    # Wait ~300 clock cycles for PWM to run
    # Count rising and falling edges on pwm_red to verify toggling
    edge_count = 0
    prev_val = int(dut.pwm_red.value)
    for _ in range(300):
        await RisingEdge(dut.clk)
        cur_val = int(dut.pwm_red.value)
        if cur_val != prev_val:
            edge_count += 1
            prev_val = cur_val

    dut._log.info(f"pwm_red toggled {edge_count} times in 300 cycles")
    assert edge_count > 0, "pwm_red did not toggle after writing duty cycle"

    # Verify register readback via AXI read
    readback = await axi_read(dut, 0x00, prefix="axi")
    dut._log.info(f"Read back duty cycle register: {readback}")
    assert readback == 128, f"Expected readback of 128, got {readback}"
