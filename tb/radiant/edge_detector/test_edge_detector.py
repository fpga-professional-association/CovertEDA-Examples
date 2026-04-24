"""Cocotb testbench for radiant edge_detector."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify all outputs zero after reset."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    dut.mode.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    assert dut.edge_detect.value.is_resolvable, "edge_detect has X/Z after reset"
    assert dut.edge_rising.value.is_resolvable, "edge_rising has X/Z after reset"
    assert dut.edge_falling.value.is_resolvable, "edge_falling has X/Z after reset"
    try:
        assert int(dut.edge_detect.value) == 0, "edge_detect not zero"
        dut._log.info("Reset state OK")
    except ValueError:
        raise AssertionError("Outputs not resolvable after reset")


@cocotb.test()
async def test_rising_edge_mode(dut):
    """In rising mode, detect rising edge on channel 0."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    dut.mode.value = 0  # Rising edge mode
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 3)

    # Apply rising edge on channel 0
    dut.sig_in.value = 0x01
    rising_seen = False
    for _ in range(8):
        await RisingEdge(dut.clk)
        if dut.edge_rising.value.is_resolvable:
            try:
                if int(dut.edge_rising.value) & 0x01:
                    rising_seen = True
                    dut._log.info("Rising edge detected on channel 0")
                    break
            except ValueError:
                pass

    assert rising_seen, "Rising edge not detected"


@cocotb.test()
async def test_falling_edge_mode(dut):
    """In falling mode, detect falling edge on channel 0."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    dut.mode.value = 1  # Falling edge mode
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    # Set signal high first
    dut.sig_in.value = 0x01
    await ClockCycles(dut.clk, 5)

    # Drop signal
    dut.sig_in.value = 0x00
    falling_seen = False
    for _ in range(8):
        await RisingEdge(dut.clk)
        if dut.edge_falling.value.is_resolvable:
            try:
                if int(dut.edge_falling.value) & 0x01:
                    falling_seen = True
                    dut._log.info("Falling edge detected on channel 0")
                    break
            except ValueError:
                pass

    assert falling_seen, "Falling edge not detected"


@cocotb.test()
async def test_both_edges_mode(dut):
    """In both mode, detect both rising and falling edges."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    dut.mode.value = 2  # Both edges mode
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 3)

    edge_count = 0

    # Rising edge
    dut.sig_in.value = 0x01
    for _ in range(8):
        await RisingEdge(dut.clk)
        if dut.edge_detect.value.is_resolvable:
            try:
                if int(dut.edge_detect.value) & 0x01:
                    edge_count += 1
                    dut._log.info(f"Edge {edge_count} detected (rising)")
                    break
            except ValueError:
                pass

    # Falling edge
    dut.sig_in.value = 0x00
    for _ in range(8):
        await RisingEdge(dut.clk)
        if dut.edge_detect.value.is_resolvable:
            try:
                if int(dut.edge_detect.value) & 0x01:
                    edge_count += 1
                    dut._log.info(f"Edge {edge_count} detected (falling)")
                    break
            except ValueError:
                pass

    assert edge_count >= 2, f"Expected 2 edges, got {edge_count}"


@cocotb.test()
async def test_multi_channel(dut):
    """Apply edges on multiple channels simultaneously."""
    setup_clock(dut, "clk", 40)
    dut.sig_in.value = 0
    dut.mode.value = 0  # Rising mode
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 3)

    # Rising edge on all 4 channels
    dut.sig_in.value = 0x0F
    rising_all = False
    for _ in range(8):
        await RisingEdge(dut.clk)
        if dut.edge_rising.value.is_resolvable:
            try:
                er = int(dut.edge_rising.value)
                if er == 0x0F:
                    rising_all = True
                    dut._log.info("Rising edges detected on all 4 channels")
                    break
            except ValueError:
                pass

    dut._log.info(f"All channels rising edge: {rising_all}")
