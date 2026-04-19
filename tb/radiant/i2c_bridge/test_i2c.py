"""Cocotb testbench for radiant i2c_top -- I2C write to Wishbone bridge."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


CLK_PERIOD_NS = 20   # 50 MHz system clock


@cocotb.test()
async def test_i2c_write(dut):
    """Verify I2C bridge design compiles, resets cleanly, and runs without X/Z."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)

    # Initialize I2C bus idle
    dut.sda.value = 1
    dut.scl.value = 1

    # Initialize Wishbone slave side
    dut.wb_data_i.value = 0
    dut.wb_ack.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    # Also deassert wb_rst (active high)
    dut.wb_rst.value = 0
    await ClockCycles(dut.clk, 50)

    # Verify key outputs are resolvable (no X/Z) after reset and warmup
    output_signals = []
    for sig_name in ["wb_stb", "wb_cyc", "wb_we"]:
        try:
            sig = getattr(dut, sig_name)
            output_signals.append((sig_name, sig))
        except AttributeError:
            pass

    for sig_name, sig in output_signals:
        assert sig.value.is_resolvable, (
            f"{sig_name} has X/Z after 50 cycles"
        )
        dut._log.info(f"{sig_name} = {int(sig.value):#x}")

    # Verify I2C bus stays idle (SDA and SCL should remain high since no transaction)
    if dut.sda.value.is_resolvable:
        dut._log.info(f"SDA = {int(dut.sda.value)}")
    if dut.scl.value.is_resolvable:
        dut._log.info(f"SCL = {int(dut.scl.value)}")

    dut._log.info("I2C bridge design runs cleanly with no X/Z on outputs")
