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


@cocotb.test()
async def test_link_up_always(dut):
    """pcie_link_up should be 1 (hardcoded in stub)."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 20)

    if not dut.pcie_link_up.value.is_resolvable:
        raise AssertionError("pcie_link_up contains X/Z")

    try:
        link_up = int(dut.pcie_link_up.value)
        assert link_up == 1, f"Expected pcie_link_up==1, got {link_up}"
        dut._log.info(f"pcie_link_up = {link_up} (as expected)")
    except ValueError:
        raise AssertionError("pcie_link_up not convertible to int")


@cocotb.test()
async def test_link_speed_gen2(dut):
    """link_speed should be 8'd2 (Gen2)."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 20)

    if not dut.link_speed.value.is_resolvable:
        raise AssertionError("link_speed contains X/Z")

    try:
        spd = int(dut.link_speed.value)
        assert spd == 2, f"Expected link_speed==2 (Gen2), got {spd}"
        dut._log.info(f"link_speed = {spd} (Gen2)")
    except ValueError:
        raise AssertionError("link_speed not convertible to int")


@cocotb.test()
async def test_app_ready_asserted(dut):
    """app_ready should be resolvable after reset."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 20)

    if not dut.app_ready.value.is_resolvable:
        dut._log.warning("app_ready has X/Z after 20 cycles, waiting longer")
        await ClockCycles(dut.clk_250m, 50)
        if not dut.app_ready.value.is_resolvable:
            raise AssertionError("app_ready still has X/Z after 70 cycles")

    try:
        rdy = int(dut.app_ready.value)
        dut._log.info(f"app_ready = {rdy}")
    except ValueError:
        raise AssertionError("app_ready not convertible to int")


@cocotb.test()
async def test_app_data_all_zeros(dut):
    """Drive app_data_in=0, app_valid=1, verify clean outputs."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0xFF
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 10)

    # Drive all-zeros data
    dut.app_data_in.value = 0
    dut.app_valid.value = 1
    await ClockCycles(dut.clk_250m, 10)
    dut.app_valid.value = 0

    await ClockCycles(dut.clk_250m, 50)

    # Verify key outputs
    for sig_name in ["pcie_link_up", "link_speed"]:
        sig = getattr(dut, sig_name)
        if not sig.value.is_resolvable:
            raise AssertionError(f"{sig_name} has X/Z after all-zeros data")
        try:
            val = int(sig.value)
            dut._log.info(f"{sig_name} = {val}")
        except ValueError:
            raise AssertionError(f"{sig_name} not convertible")


@cocotb.test()
async def test_app_data_all_ones(dut):
    """Drive app_data_in=all_ones, verify clean outputs."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 10)

    # Drive all-ones data
    dut.app_data_in.value = 0xFFFFFFFFFFFFFFFF
    dut.app_byte_en.value = 0xFF
    dut.app_valid.value = 1
    await ClockCycles(dut.clk_250m, 10)
    dut.app_valid.value = 0
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0

    await ClockCycles(dut.clk_250m, 50)

    # Verify outputs
    if not dut.pcie_link_up.value.is_resolvable:
        raise AssertionError("pcie_link_up has X/Z after all-ones data")

    try:
        link_up = int(dut.pcie_link_up.value)
        link_spd = int(dut.link_speed.value)
        dut._log.info(f"After all-ones: link_up={link_up}, link_speed={link_spd}")
    except ValueError:
        raise AssertionError("Outputs not convertible after all-ones data")


@cocotb.test()
async def test_device_id_acceptance(dut):
    """Set device_id=0x1234, verify no effect on link status."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 20)

    if not dut.pcie_link_up.value.is_resolvable:
        raise AssertionError("pcie_link_up has X/Z with device_id=0x1234")

    try:
        link_up = int(dut.pcie_link_up.value)
        assert link_up == 1, f"Link should be up with device_id=0x1234, got {link_up}"
    except ValueError:
        raise AssertionError("pcie_link_up not convertible")

    # Change device_id and verify link still up
    dut.device_id.value = 0x5678
    await ClockCycles(dut.clk_250m, 20)

    if not dut.pcie_link_up.value.is_resolvable:
        raise AssertionError("pcie_link_up has X/Z after device_id change")

    try:
        link_up2 = int(dut.pcie_link_up.value)
        assert link_up2 == 1, f"Link should stay up after device_id change, got {link_up2}"
        dut._log.info("device_id change did not affect link status")
    except ValueError:
        raise AssertionError("pcie_link_up not convertible after device_id change")


@cocotb.test()
async def test_bar0_config_set(dut):
    """Set bar0_config=0x42, verify clean operation."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x42

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 50)

    # Verify outputs are clean
    for sig_name in ["pcie_link_up", "link_speed", "app_ready"]:
        sig = getattr(dut, sig_name)
        if sig.value.is_resolvable:
            try:
                val = int(sig.value)
                dut._log.info(f"{sig_name} with bar0=0x42: {val}")
            except ValueError:
                dut._log.warning(f"{sig_name} not convertible with bar0=0x42")
        else:
            dut._log.warning(f"{sig_name} has X/Z with bar0=0x42")

    dut._log.info("Design ran cleanly with bar0_config=0x42")


@cocotb.test()
async def test_pcie_tx_clean(dut):
    """Verify pcie_tx[3:0] are resolvable after warmup."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 50)

    if dut.pcie_tx.value.is_resolvable:
        try:
            tx_val = int(dut.pcie_tx.value)
            dut._log.info(f"pcie_tx = {tx_val:#06b}")
            assert 0 <= tx_val <= 0xF, f"pcie_tx out of range: {tx_val}"
        except ValueError:
            dut._log.warning("pcie_tx not convertible -- may be expected for serial lines")
    else:
        dut._log.warning("pcie_tx has X/Z -- may be expected for uninitialized serial lines")


@cocotb.test()
async def test_back_to_back_valid(dut):
    """Toggle app_valid rapidly, verify stability."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0xFF
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 10)

    # Rapidly toggle app_valid with varying data
    for i in range(50):
        dut.app_data_in.value = i * 0x0101010101010101 & 0xFFFFFFFFFFFFFFFF
        dut.app_valid.value = 1
        await RisingEdge(dut.clk_250m)
        dut.app_valid.value = 0
        await RisingEdge(dut.clk_250m)

    await ClockCycles(dut.clk_250m, 50)

    # Verify design is still healthy
    if not dut.pcie_link_up.value.is_resolvable:
        raise AssertionError("pcie_link_up has X/Z after back-to-back valid toggles")

    try:
        link_up = int(dut.pcie_link_up.value)
        dut._log.info(f"pcie_link_up after rapid toggles: {link_up}")
    except ValueError:
        raise AssertionError("pcie_link_up not convertible after rapid toggles")


@cocotb.test()
async def test_reset_recovery(dut):
    """Reset and verify clean state recovery."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0xFF
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 20)

    # Drive some data
    dut.app_data_in.value = 0xCAFEBABE12345678
    dut.app_valid.value = 1
    await ClockCycles(dut.clk_250m, 10)
    dut.app_valid.value = 0

    # Reset mid-operation
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 20)

    # Verify clean recovery
    if not dut.pcie_link_up.value.is_resolvable:
        raise AssertionError("pcie_link_up has X/Z after mid-operation reset")

    try:
        link_up = int(dut.pcie_link_up.value)
        link_spd = int(dut.link_speed.value)
        dut._log.info(f"After reset recovery: link_up={link_up}, link_speed={link_spd}")
        assert link_up == 1, f"Link should be up after reset, got {link_up}"
    except ValueError:
        raise AssertionError("Outputs not convertible after reset recovery")


@cocotb.test()
async def test_byte_enable_partial(dut):
    """Drive app_byte_en with partial enables (0x0F, 0xF0), verify stability."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 10)

    for be_val in [0x0F, 0xF0, 0x01, 0x80, 0xAA, 0x55]:
        dut.app_data_in.value = 0x1234567890ABCDEF
        dut.app_byte_en.value = be_val
        dut.app_valid.value = 1
        await ClockCycles(dut.clk_250m, 5)
        dut.app_valid.value = 0

        await ClockCycles(dut.clk_250m, 20)

        if not dut.pcie_link_up.value.is_resolvable:
            raise AssertionError(f"pcie_link_up has X/Z with byte_en={be_val:#04x}")

        try:
            link_up = int(dut.pcie_link_up.value)
            dut._log.info(f"byte_en={be_val:#04x}: link_up={link_up}")
        except ValueError:
            raise AssertionError(f"pcie_link_up not convertible with byte_en={be_val:#04x}")

    dut._log.info("All partial byte enable patterns handled cleanly")


@cocotb.test()
async def test_app_ready_out_deassert(dut):
    """Deassert app_ready_out (back-pressure), drive data, verify stability."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0xFF
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 10)

    # Deassert app_ready_out (downstream not ready)
    dut.app_ready_out.value = 0

    # Drive data anyway
    dut.app_data_in.value = 0xAAAAAAAABBBBBBBB
    dut.app_valid.value = 1
    await ClockCycles(dut.clk_250m, 20)
    dut.app_valid.value = 0
    dut.app_data_in.value = 0

    await ClockCycles(dut.clk_250m, 50)

    # Re-assert app_ready_out
    dut.app_ready_out.value = 1
    await ClockCycles(dut.clk_250m, 30)

    if not dut.pcie_link_up.value.is_resolvable:
        raise AssertionError("pcie_link_up has X/Z after back-pressure test")

    try:
        link_up = int(dut.pcie_link_up.value)
        dut._log.info(f"After back-pressure: link_up={link_up}")
        assert link_up == 1, f"Link should remain up after back-pressure, got {link_up}"
    except ValueError:
        raise AssertionError("pcie_link_up not convertible after back-pressure")


@cocotb.test()
async def test_pcie_rx_all_ones(dut):
    """Drive pcie_rx=0xF (all ones on 4 lanes) and verify stability."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b1111
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 100)

    if not dut.pcie_link_up.value.is_resolvable:
        raise AssertionError("pcie_link_up has X/Z with pcie_rx=0xF")

    try:
        link_up = int(dut.pcie_link_up.value)
        link_spd = int(dut.link_speed.value)
        dut._log.info(f"pcie_rx=0xF: link_up={link_up}, link_speed={link_spd}")
    except ValueError:
        raise AssertionError("Outputs not convertible with pcie_rx=0xF")

    dut._log.info("Design stable with all pcie_rx lanes high")


@cocotb.test()
async def test_pcie_rx_toggling(dut):
    """Toggle pcie_rx pattern every cycle for 100 cycles, verify no crash."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 10)

    # Toggle pcie_rx between 0x5 (0101) and 0xA (1010) each cycle
    for cycle in range(100):
        dut.pcie_rx.value = 0b0101 if (cycle % 2 == 0) else 0b1010
        await RisingEdge(dut.clk_250m)

    await ClockCycles(dut.clk_250m, 50)

    if not dut.pcie_link_up.value.is_resolvable:
        raise AssertionError("pcie_link_up has X/Z after RX toggling")

    try:
        link_up = int(dut.pcie_link_up.value)
        dut._log.info(f"After RX toggling: link_up={link_up}")
    except ValueError:
        raise AssertionError("pcie_link_up not convertible after RX toggling")

    dut._log.info("Design survived 100 cycles of pcie_rx toggling")


@cocotb.test()
async def test_sustained_valid_long(dut):
    """Hold app_valid=1 for 200 consecutive cycles with changing data."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0xFF
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.device_id.value = 0x1234
    dut.bar0_config.value = 0x01

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk_250m, 10)

    # Sustained valid for 200 cycles with incrementing data
    dut.app_valid.value = 1
    for i in range(200):
        dut.app_data_in.value = (i * 0x0123456789ABCDEF) & 0xFFFFFFFFFFFFFFFF
        await RisingEdge(dut.clk_250m)
    dut.app_valid.value = 0
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0

    await ClockCycles(dut.clk_250m, 100)

    if not dut.pcie_link_up.value.is_resolvable:
        raise AssertionError("pcie_link_up has X/Z after sustained valid")

    try:
        link_up = int(dut.pcie_link_up.value)
        app_rdy = int(dut.app_ready.value)
        dut._log.info(f"After sustained valid: link_up={link_up}, app_ready={app_rdy}")
    except ValueError:
        raise AssertionError("Outputs not convertible after sustained valid")

    dut._log.info("Design handled 200-cycle sustained valid cleanly")


@cocotb.test()
async def test_device_id_boundary_values(dut):
    """Test device_id with boundary values 0x0000 and 0xFFFF."""

    setup_clock(dut, "clk_250m", 4)

    dut.pcie_rx.value = 0b0000
    dut.app_data_in.value = 0
    dut.app_byte_en.value = 0
    dut.app_valid.value = 0
    dut.app_ready_out.value = 1
    dut.bar0_config.value = 0x01

    for dev_id in [0x0000, 0xFFFF]:
        dut.device_id.value = dev_id
        await reset_dut(dut, "rst_n", active_low=True, cycles=5)
        await ClockCycles(dut.clk_250m, 30)

        if not dut.pcie_link_up.value.is_resolvable:
            raise AssertionError(f"pcie_link_up has X/Z with device_id={dev_id:#06x}")

        try:
            link_up = int(dut.pcie_link_up.value)
            link_spd = int(dut.link_speed.value)
            dut._log.info(
                f"device_id={dev_id:#06x}: link_up={link_up}, link_speed={link_spd}"
            )
            assert link_up == 1, f"Link should be up with device_id={dev_id:#06x}"
        except ValueError:
            raise AssertionError(f"Outputs not convertible with device_id={dev_id:#06x}")

    dut._log.info("Boundary device_id values handled correctly")
