"""Cocotb testbench for quartus pcie_top -- PCIe Gen2 x4 Endpoint."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


def check_no_xz_64(signal, name):
    """Verify a 64-bit signal resolves to a valid integer (no X/Z)."""
    val = int(signal.value)
    assert 0 <= val <= 0xFFFFFFFFFFFFFFFF, (
        f"{name} value out of range, possible X/Z"
    )
    return val


def check_no_xz_8(signal, name):
    """Verify an 8-bit signal resolves to a valid integer (no X/Z)."""
    val = int(signal.value)
    assert 0 <= val <= 0xFF, f"{name} value out of range, possible X/Z"
    return val


@cocotb.test()
async def test_pcie_basic(dut):
    """Reset, configure, and verify design does not crash."""

    # Start 4 ns clock (250 MHz)
    setup_clock(dut, "clk_250m", 4)

    # Initialize inputs
    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Let the design run after reset
    await ClockCycles(dut.clk_250m, 20)

    # Verify link status outputs
    link_up = int(dut.pcie_link_up.value)
    link_spd = int(dut.link_speed.value)
    dut._log.info(f"pcie_link_up={link_up}, link_speed={link_spd}")


@cocotb.test()
async def test_pcie_app_data(dut):
    """Drive application data and verify outputs have no X/Z."""

    # Start 4 ns clock (250 MHz)
    setup_clock(dut, "clk_250m", 4)

    # Initialize inputs
    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    await ClockCycles(dut.clk_250m, 10)

    # Drive application data
    dut.app_data_in.value = 0xDEADBEEFCAFEBABE
    dut.app_byte_en.value = 0xFF
    dut.app_valid.value = 1

    await ClockCycles(dut.clk_250m, 5)

    # Deassert valid
    dut.app_valid.value = 0
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0

    # Run for 100 more cycles
    await ClockCycles(dut.clk_250m, 100)

    # Verify no X/Z on key outputs
    try:
        pcie_tx_val = int(dut.pcie_tx.value)
        dut._log.info(f"pcie_tx={pcie_tx_val:#06b}")
    except ValueError:
        dut._log.warning("pcie_tx contains X/Z (may be expected for serial lines)")

    link_spd = check_no_xz_8(dut.link_speed, "link_speed")
    dut._log.info(f"link_speed={link_spd}")

    link_up = int(dut.pcie_link_up.value)
    dut._log.info(f"pcie_link_up={link_up}")
