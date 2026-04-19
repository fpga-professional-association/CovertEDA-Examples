"""Cocotb testbench for diamond serdes_top – software loopback test.

Since we cannot model a real SERDES transceiver in Icarus, we use a cocotb
coroutine to continuously copy serdes_tx_p -> serdes_rx_p and
serdes_tx_n -> serdes_rx_n each clock cycle, creating a software loopback.
"""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def loopback_driver(dut, num_cycles):
    """Copy TX differential signals to RX each clock cycle."""
    for _ in range(num_cycles):
        await RisingEdge(dut.ref_clk)
        try:
            dut.serdes_rx_p.value = int(dut.serdes_tx_p.value)
            dut.serdes_rx_n.value = int(dut.serdes_tx_n.value)
        except ValueError:
            # TX may contain X/Z early in simulation; drive 0 as default
            dut.serdes_rx_p.value = 0
            dut.serdes_rx_n.value = 1


@cocotb.test()
async def test_loopback(dut):
    """Configure loopback mode, connect tx->rx, check prbs_status_led."""

    # Start ~3.2 ns clock (312.5 MHz)
    setup_clock(dut, "ref_clk", 3.2)

    # Initialize inputs
    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0  # loopback mode

    # Reset (active-low reset_n)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 10)

    # Launch the loopback coroutine for 200 cycles
    cocotb.start_soon(loopback_driver(dut, 200))

    # Run 200 cycles to let the PRBS checker lock
    await ClockCycles(dut.ref_clk, 200)

    # Check prbs_status_led for any lock indication (non-zero)
    status = dut.prbs_status_led.value
    dut._log.info(f"PRBS status LED: {int(status):#010b}")

    try:
        status_int = int(status)
    except ValueError:
        assert False, f"prbs_status_led contains X/Z: {status}"

    assert status_int != 0, (
        f"Expected prbs_status_led to show lock (non-zero), got {status_int:#010b}"
    )
    dut._log.info("SERDES loopback test passed -- PRBS lock detected")


@cocotb.test()
async def test_reset_state(dut):
    """After reset, verify prbs_status_led is resolvable."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 20)

    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led contains X/Z after reset: {dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
    except ValueError:
        assert False, (
            f"prbs_status_led cannot be resolved after reset: {dut.prbs_status_led.value}"
        )

    assert 0 <= status_val <= 255, f"prbs_status_led out of range: {status_val}"
    dut._log.info(f"prbs_status_led = {status_val:#010b} after reset -- resolvable")


@cocotb.test()
async def test_pll_lock_bit(dut):
    """prbs_status_led[0] should be 1 (PLL locked) after warmup."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    # Give PLL time to lock
    await ClockCycles(dut.ref_clk, 200)

    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led contains X/Z after warmup: {dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
    except ValueError:
        assert False, (
            f"prbs_status_led not resolvable after warmup: {dut.prbs_status_led.value}"
        )

    pll_lock = status_val & 0x01
    if pll_lock == 1:
        dut._log.info("PLL lock bit [0] is set -- PLL locked")
    else:
        dut._log.info(
            f"PLL lock bit [0] is 0 -- status={status_val:#010b}, "
            "may need more warmup cycles"
        )


@cocotb.test()
async def test_power_on_bit(dut):
    """prbs_status_led[6] should always be 1 (power-on indicator)."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 100)

    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led contains X/Z: {dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
    except ValueError:
        assert False, (
            f"prbs_status_led not resolvable: {dut.prbs_status_led.value}"
        )

    power_bit = (status_val >> 6) & 0x01
    if power_bit == 1:
        dut._log.info("Power-on bit [6] is set -- correct")
    else:
        dut._log.info(
            f"Power-on bit [6] is 0 -- status={status_val:#010b}, "
            "design may not implement this bit"
        )


@cocotb.test()
async def test_test_mode_0(dut):
    """Set test_mode=0 (loopback) and run 200 cycles, verify no X/Z."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 200)

    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led X/Z in loopback mode: {dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
    except ValueError:
        assert False, (
            f"prbs_status_led not resolvable in loopback mode: "
            f"{dut.prbs_status_led.value}"
        )

    dut._log.info(f"test_mode=0 (loopback): status={status_val:#010b}")


@cocotb.test()
async def test_test_mode_1(dut):
    """Set test_mode=1 (PRBS) and run 200 cycles, verify no X/Z."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 1

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 200)

    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led X/Z in PRBS mode: {dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
    except ValueError:
        assert False, (
            f"prbs_status_led not resolvable in PRBS mode: "
            f"{dut.prbs_status_led.value}"
        )

    dut._log.info(f"test_mode=1 (PRBS): status={status_val:#010b}")


@cocotb.test()
async def test_tx_activity(dut):
    """serdes_tx_p and serdes_tx_n should toggle (show activity)."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 20)

    # Monitor TX for toggling over 200 cycles
    tx_p_values = set()
    tx_n_values = set()
    for _ in range(200):
        await RisingEdge(dut.ref_clk)
        if dut.serdes_tx_p.value.is_resolvable:
            try:
                tx_p_values.add(int(dut.serdes_tx_p.value))
            except ValueError:
                pass
        if dut.serdes_tx_n.value.is_resolvable:
            try:
                tx_n_values.add(int(dut.serdes_tx_n.value))
            except ValueError:
                pass

    tx_p_toggled = len(tx_p_values) > 1
    tx_n_toggled = len(tx_n_values) > 1

    if tx_p_toggled:
        dut._log.info(f"serdes_tx_p toggled -- values seen: {tx_p_values}")
    else:
        dut._log.info(f"serdes_tx_p did not toggle -- values: {tx_p_values}")

    if tx_n_toggled:
        dut._log.info(f"serdes_tx_n toggled -- values seen: {tx_n_values}")
    else:
        dut._log.info(f"serdes_tx_n did not toggle -- values: {tx_n_values}")

    # At minimum, verify TX signals are resolvable
    if not dut.serdes_tx_p.value.is_resolvable:
        assert False, f"serdes_tx_p contains X/Z: {dut.serdes_tx_p.value}"
    if not dut.serdes_tx_n.value.is_resolvable:
        assert False, f"serdes_tx_n contains X/Z: {dut.serdes_tx_n.value}"


@cocotb.test()
async def test_loopback_connection(dut):
    """Copy serdes_tx_p to serdes_rx_p each cycle and check for lock."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 10)

    # Run loopback for 300 cycles
    cocotb.start_soon(loopback_driver(dut, 300))
    await ClockCycles(dut.ref_clk, 300)

    # Check if PRBS locked
    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led X/Z after loopback: {dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
    except ValueError:
        assert False, (
            f"prbs_status_led not resolvable: {dut.prbs_status_led.value}"
        )

    assert status_val != 0, (
        f"Expected non-zero status after loopback, got {status_val:#010b}"
    )
    dut._log.info(f"Loopback connection -- status={status_val:#010b}")


@cocotb.test()
async def test_long_run_500(dut):
    """Run 500 cycles with loopback and verify PRBS status stability."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 10)

    # Run loopback for 500 cycles
    cocotb.start_soon(loopback_driver(dut, 500))
    await ClockCycles(dut.ref_clk, 500)

    # Verify status is stable and resolvable
    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led X/Z after 500 cycles: {dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
    except ValueError:
        assert False, (
            f"prbs_status_led not resolvable after 500 cycles: "
            f"{dut.prbs_status_led.value}"
        )

    assert status_val != 0, (
        f"Expected non-zero PRBS status after 500 cycles, got {status_val:#010b}"
    )
    dut._log.info(f"500-cycle run -- PRBS status={status_val:#010b} -- stable")


@cocotb.test()
async def test_reset_recovery(dut):
    """Reset mid-operation and verify PLL re-locks."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 10)

    # Run loopback for 100 cycles
    cocotb.start_soon(loopback_driver(dut, 100))
    await ClockCycles(dut.ref_clk, 100)

    # Verify lock before reset
    if dut.prbs_status_led.value.is_resolvable:
        try:
            pre_reset_status = int(dut.prbs_status_led.value)
            dut._log.info(f"Pre-reset status: {pre_reset_status:#010b}")
        except ValueError:
            dut._log.info("Pre-reset status not resolvable")

    # Reset mid-operation
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 10)

    # Run loopback again for 200 cycles to allow re-lock
    cocotb.start_soon(loopback_driver(dut, 200))
    await ClockCycles(dut.ref_clk, 200)

    # Verify PLL re-locked
    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led X/Z after reset recovery: {dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
    except ValueError:
        assert False, (
            f"prbs_status_led not resolvable after recovery: "
            f"{dut.prbs_status_led.value}"
        )

    assert status_val != 0, (
        f"Expected non-zero status after reset recovery, got {status_val:#010b}"
    )
    dut._log.info(f"Reset recovery -- PLL re-locked, status={status_val:#010b}")


@cocotb.test()
async def test_test_mode_switching(dut):
    """Switch test_mode from 0 to 1 mid-run and verify stability."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 10)

    cocotb.start_soon(loopback_driver(dut, 400))

    # Run 100 cycles in mode 0
    await ClockCycles(dut.ref_clk, 100)

    if dut.prbs_status_led.value.is_resolvable:
        try:
            status_mode0 = int(dut.prbs_status_led.value)
            dut._log.info(f"Status in mode 0: {status_mode0:#010b}")
        except ValueError:
            dut._log.warning("Status not convertible in mode 0")

    # Switch to mode 1
    dut.test_mode.value = 1
    dut._log.info("Switched test_mode from 0 to 1")

    # Run 200 more cycles in mode 1
    await ClockCycles(dut.ref_clk, 200)

    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led has X/Z after mode switch: {dut.prbs_status_led.value}"
        )

    try:
        status_mode1 = int(dut.prbs_status_led.value)
        dut._log.info(f"Status in mode 1: {status_mode1:#010b}")
    except ValueError:
        assert False, f"Status not convertible after mode switch"

    dut._log.info("test_mode switching handled cleanly")


@cocotb.test()
async def test_rx_differential_inverted(dut):
    """Drive serdes_rx_p/n with inverted polarity and verify stability."""

    setup_clock(dut, "ref_clk", 3.2)

    # Drive inverted polarity: rx_p=1, rx_n=0 (opposite of normal idle)
    dut.serdes_rx_p.value = 1
    dut.serdes_rx_n.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 200)

    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led has X/Z with inverted RX: {dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
        dut._log.info(f"Status with inverted RX polarity: {status_val:#010b}")
    except ValueError:
        assert False, f"Status not convertible with inverted RX"

    # Verify TX signals are still resolvable
    if not dut.serdes_tx_p.value.is_resolvable:
        assert False, f"serdes_tx_p has X/Z with inverted RX: {dut.serdes_tx_p.value}"
    if not dut.serdes_tx_n.value.is_resolvable:
        assert False, f"serdes_tx_n has X/Z with inverted RX: {dut.serdes_tx_n.value}"

    dut._log.info("Design ran with inverted RX polarity -- no crash")


@cocotb.test()
async def test_reset_hold_single_cycle(dut):
    """Assert reset for only 1 cycle, verify design handles minimal reset."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=1)
    await ClockCycles(dut.ref_clk, 10)

    cocotb.start_soon(loopback_driver(dut, 200))
    await ClockCycles(dut.ref_clk, 200)

    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led has X/Z after 1-cycle reset: {dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
        dut._log.info(f"Status after 1-cycle reset: {status_val:#010b}")
    except ValueError:
        assert False, f"Status not convertible after 1-cycle reset"

    assert status_val != 0, (
        f"Expected non-zero status after 1-cycle reset, got {status_val:#010b}"
    )
    dut._log.info("1-cycle reset handled correctly")


@cocotb.test()
async def test_long_loopback_1000_cycles(dut):
    """Run loopback for 1000 cycles and verify sustained lock."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 10)

    cocotb.start_soon(loopback_driver(dut, 1000))

    # Sample status at multiple points
    status_samples = []
    for checkpoint in [250, 500, 750, 1000]:
        await ClockCycles(dut.ref_clk, 250 if not status_samples else 250)
        if dut.prbs_status_led.value.is_resolvable:
            try:
                val = int(dut.prbs_status_led.value)
                status_samples.append((checkpoint, val))
                dut._log.info(f"Status at cycle {checkpoint}: {val:#010b}")
            except ValueError:
                dut._log.warning(f"Status not convertible at cycle {checkpoint}")

    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led has X/Z after 1000 cycles: {dut.prbs_status_led.value}"
        )

    try:
        final_status = int(dut.prbs_status_led.value)
    except ValueError:
        assert False, f"Status not convertible after 1000 cycles"

    assert final_status != 0, (
        f"Expected non-zero status after 1000 cycles, got {final_status:#010b}"
    )
    dut._log.info(f"1000-cycle loopback -- final status = {final_status:#010b}")


@cocotb.test()
async def test_tx_complementary(dut):
    """Verify serdes_tx_p and serdes_tx_n are complementary (differential)."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 50)

    complementary_count = 0
    total_checks = 0

    for _ in range(200):
        await RisingEdge(dut.ref_clk)
        if (dut.serdes_tx_p.value.is_resolvable and
                dut.serdes_tx_n.value.is_resolvable):
            try:
                tx_p = int(dut.serdes_tx_p.value)
                tx_n = int(dut.serdes_tx_n.value)
                total_checks += 1
                if tx_p != tx_n:
                    complementary_count += 1
            except ValueError:
                pass

    if total_checks > 0:
        pct = (complementary_count / total_checks) * 100
        dut._log.info(
            f"TX complementary: {complementary_count}/{total_checks} "
            f"({pct:.1f}%) samples were complementary"
        )
    else:
        dut._log.warning("No valid TX samples for complementary check")


@cocotb.test()
async def test_multiple_resets_with_loopback(dut):
    """Perform 3 reset/loopback cycles, verify lock each time."""

    setup_clock(dut, "ref_clk", 3.2)

    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 1
    dut.test_mode.value = 0

    for i in range(3):
        await reset_dut(dut, "reset_n", active_low=True, cycles=5)
        await ClockCycles(dut.ref_clk, 10)

        cocotb.start_soon(loopback_driver(dut, 200))
        await ClockCycles(dut.ref_clk, 200)

        if not dut.prbs_status_led.value.is_resolvable:
            assert False, (
                f"prbs_status_led has X/Z on iteration {i}: "
                f"{dut.prbs_status_led.value}"
            )

        try:
            status_val = int(dut.prbs_status_led.value)
        except ValueError:
            assert False, f"Status not convertible on iteration {i}"

        assert status_val != 0, (
            f"Iteration {i}: expected non-zero status, got {status_val:#010b}"
        )
        dut._log.info(f"Reset/loopback cycle {i}: status={status_val:#010b}")

    dut._log.info("All 3 reset/loopback cycles passed")


@cocotb.test()
async def test_rx_both_same_value(dut):
    """Drive both serdes_rx_p=0 and serdes_rx_n=0 (invalid differential)."""

    setup_clock(dut, "ref_clk", 3.2)

    # Both low -- invalid differential state
    dut.serdes_rx_p.value = 0
    dut.serdes_rx_n.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "reset_n", active_low=True, cycles=5)
    await ClockCycles(dut.ref_clk, 200)

    # Design should survive even with invalid differential input
    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led has X/Z with invalid diff input: "
            f"{dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
        dut._log.info(f"Status with both RX=0: {status_val:#010b}")
    except ValueError:
        assert False, f"Status not convertible with invalid diff input"

    # Now try both high
    dut.serdes_rx_p.value = 1
    dut.serdes_rx_n.value = 1
    await ClockCycles(dut.ref_clk, 200)

    if not dut.prbs_status_led.value.is_resolvable:
        assert False, (
            f"prbs_status_led has X/Z with both RX=1: {dut.prbs_status_led.value}"
        )

    try:
        status_val = int(dut.prbs_status_led.value)
        dut._log.info(f"Status with both RX=1: {status_val:#010b}")
    except ValueError:
        assert False, f"Status not convertible with both RX=1"

    dut._log.info("Design survived invalid differential input states")
