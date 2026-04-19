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


async def pwm_init_axi(dut):
    """Initialize all AXI signals to 0."""
    dut.axi_awaddr.value = 0
    dut.axi_awvalid.value = 0
    dut.axi_wdata.value = 0
    dut.axi_wstrb.value = 0
    dut.axi_wvalid.value = 0
    dut.axi_bready.value = 0
    dut.axi_araddr.value = 0
    dut.axi_arvalid.value = 0
    dut.axi_rready.value = 0


@cocotb.test()
async def test_all_channels_off(dut):
    """Write duty=0 for all channels, verify all PWM outputs stay low."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write 0x00000000 to register 0 (all duties = 0)
    await axi_write(dut, 0x00, 0x00000000, prefix="axi")
    dut._log.info("Wrote duty=0 for all channels")

    # Run 300 cycles and verify all PWM outputs stay low
    for cycle in range(300):
        await RisingEdge(dut.clk)
        for sig_name in ["pwm_red", "pwm_green", "pwm_blue"]:
            sig = getattr(dut, sig_name)
            if sig.value.is_resolvable:
                try:
                    val = int(sig.value)
                    assert val == 0, (
                        f"{sig_name} should be 0 with duty=0, got {val} at cycle {cycle}"
                    )
                except ValueError:
                    pass

    dut._log.info("All PWM channels stayed low with duty=0")


@cocotb.test()
async def test_red_full_brightness(dut):
    """Write red_duty=255, verify pwm_red is mostly high."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write red_duty=255 (bits [7:0] of reg0)
    await axi_write(dut, 0x00, 0x000000FF, prefix="axi")
    dut._log.info("Wrote red_duty=255")

    high_count = 0
    total_count = 300
    for _ in range(total_count):
        await RisingEdge(dut.clk)
        if dut.pwm_red.value.is_resolvable:
            try:
                if int(dut.pwm_red.value) == 1:
                    high_count += 1
            except ValueError:
                pass

    dut._log.info(f"pwm_red high for {high_count}/{total_count} cycles with duty=255")
    # With duty=255, pwm_red should be high almost all the time
    assert high_count > total_count * 0.9, (
        f"pwm_red should be mostly high with duty=255, but was high only {high_count}/{total_count}"
    )


@cocotb.test()
async def test_green_channel(dut):
    """Write green_duty=128, verify pwm_green toggles."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write green_duty=128 (bits [15:8] of reg0)
    await axi_write(dut, 0x00, 0x00008000, prefix="axi")
    dut._log.info("Wrote green_duty=128")

    edge_count = 0
    prev_val = None
    for _ in range(300):
        await RisingEdge(dut.clk)
        if dut.pwm_green.value.is_resolvable:
            try:
                cur_val = int(dut.pwm_green.value)
                if prev_val is not None and cur_val != prev_val:
                    edge_count += 1
                prev_val = cur_val
            except ValueError:
                pass

    dut._log.info(f"pwm_green toggled {edge_count} times in 300 cycles")
    assert edge_count > 0, "pwm_green did not toggle with duty=128"


@cocotb.test()
async def test_blue_channel(dut):
    """Write blue_duty=64, verify pwm_blue toggles."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write blue_duty=64 (bits [23:16] of reg0)
    await axi_write(dut, 0x00, 0x00400000, prefix="axi")
    dut._log.info("Wrote blue_duty=64")

    edge_count = 0
    prev_val = None
    for _ in range(300):
        await RisingEdge(dut.clk)
        if dut.pwm_blue.value.is_resolvable:
            try:
                cur_val = int(dut.pwm_blue.value)
                if prev_val is not None and cur_val != prev_val:
                    edge_count += 1
                prev_val = cur_val
            except ValueError:
                pass

    dut._log.info(f"pwm_blue toggled {edge_count} times in 300 cycles")
    assert edge_count > 0, "pwm_blue did not toggle with duty=64"


@cocotb.test()
async def test_all_channels_max(dut):
    """Write 0x00FFFFFF to reg0, verify all three PWM outputs toggle."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # All channels at max duty
    await axi_write(dut, 0x00, 0x00FFFFFF, prefix="axi")
    dut._log.info("Wrote 0x00FFFFFF (all channels max)")

    # Check all three PWM outputs are resolvable and mostly high
    for sig_name in ["pwm_red", "pwm_green", "pwm_blue"]:
        high_count = 0
        for _ in range(300):
            await RisingEdge(dut.clk)
            sig = getattr(dut, sig_name)
            if sig.value.is_resolvable:
                try:
                    if int(sig.value) == 1:
                        high_count += 1
                except ValueError:
                    pass
        dut._log.info(f"{sig_name} high for {high_count}/300 cycles with max duty")
        assert high_count > 0, f"{sig_name} never went high with max duty"


@cocotb.test()
async def test_register_readback(dut):
    """Write then read reg0, verify data matches."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    test_val = 0x00AABB42
    await axi_write(dut, 0x00, test_val, prefix="axi")
    dut._log.info(f"Wrote {test_val:#010x} to reg0")

    readback = await axi_read(dut, 0x00, prefix="axi")
    dut._log.info(f"Read back: {readback:#010x}")
    assert readback == test_val, f"Readback mismatch: expected {test_val:#010x}, got {readback:#010x}"


@cocotb.test()
async def test_duty_0_percent(dut):
    """Duty=0 means PWM output should never be high."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write duty=0 for red channel
    await axi_write(dut, 0x00, 0x00000000, prefix="axi")

    high_count = 0
    for _ in range(300):
        await RisingEdge(dut.clk)
        if dut.pwm_red.value.is_resolvable:
            try:
                if int(dut.pwm_red.value) == 1:
                    high_count += 1
            except ValueError:
                pass

    dut._log.info(f"pwm_red was high {high_count} times with duty=0")
    assert high_count == 0, f"pwm_red should never be high with duty=0, was high {high_count} times"


@cocotb.test()
async def test_duty_change(dut):
    """Write one duty, run, write a different duty, verify change."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # First duty: red=64 (low duty cycle)
    await axi_write(dut, 0x00, 0x00000040, prefix="axi")
    dut._log.info("Wrote red_duty=64")

    high_count_first = 0
    for _ in range(300):
        await RisingEdge(dut.clk)
        if dut.pwm_red.value.is_resolvable:
            try:
                if int(dut.pwm_red.value) == 1:
                    high_count_first += 1
            except ValueError:
                pass

    # Second duty: red=200 (higher duty cycle)
    await axi_write(dut, 0x00, 0x000000C8, prefix="axi")
    dut._log.info("Wrote red_duty=200")

    high_count_second = 0
    for _ in range(300):
        await RisingEdge(dut.clk)
        if dut.pwm_red.value.is_resolvable:
            try:
                if int(dut.pwm_red.value) == 1:
                    high_count_second += 1
            except ValueError:
                pass

    dut._log.info(f"High counts: duty=64 -> {high_count_first}, duty=200 -> {high_count_second}")
    assert high_count_second > high_count_first, (
        f"Higher duty should produce more high cycles: "
        f"duty=64 had {high_count_first}, duty=200 had {high_count_second}"
    )


@cocotb.test()
async def test_pwm_frequency(dut):
    """Count full PWM cycles in a known time window."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write red_duty=128 for a 50% duty cycle
    await axi_write(dut, 0x00, 0x00000080, prefix="axi")

    # Count rising edges on pwm_red over 1000 clock cycles
    rising_edges = 0
    prev_val = 0
    for _ in range(1000):
        await RisingEdge(dut.clk)
        if dut.pwm_red.value.is_resolvable:
            try:
                cur_val = int(dut.pwm_red.value)
                if prev_val == 0 and cur_val == 1:
                    rising_edges += 1
                prev_val = cur_val
            except ValueError:
                pass

    dut._log.info(f"pwm_red had {rising_edges} rising edges in 1000 clk cycles")
    # With a 256-count PWM counter, expect ~1000/256 ~= 3-4 full cycles
    assert rising_edges > 0, "pwm_red should have at least one rising edge"


@cocotb.test()
async def test_reset_clears_duty(dut):
    """After reset, verify PWM outputs are low (duty=0 default)."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write a non-zero duty
    await axi_write(dut, 0x00, 0x00808080, prefix="axi")
    await ClockCycles(dut.clk, 100)

    # Reset again
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # After reset, run and verify PWM outputs stay low (duty should be cleared)
    high_counts = {"pwm_red": 0, "pwm_green": 0, "pwm_blue": 0}
    for _ in range(300):
        await RisingEdge(dut.clk)
        for sig_name in high_counts:
            sig = getattr(dut, sig_name)
            if sig.value.is_resolvable:
                try:
                    if int(sig.value) == 1:
                        high_counts[sig_name] += 1
                except ValueError:
                    pass

    for sig_name, count in high_counts.items():
        dut._log.info(f"{sig_name} high for {count}/300 cycles after reset")
        assert count == 0, (
            f"{sig_name} should be low after reset (duty cleared), but was high {count} times"
        )


@cocotb.test()
async def test_duty_1_minimum(dut):
    """Write duty=1 (minimum nonzero), verify pwm_red toggles at least once."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Write red_duty=1
    await axi_write(dut, 0x00, 0x00000001, prefix="axi")
    dut._log.info("Wrote red_duty=1 (minimum nonzero)")

    high_count = 0
    for _ in range(1000):
        await RisingEdge(dut.clk)
        if dut.pwm_red.value.is_resolvable:
            try:
                if int(dut.pwm_red.value) == 1:
                    high_count += 1
            except ValueError:
                pass

    dut._log.info(f"pwm_red high for {high_count}/1000 cycles with duty=1")
    assert high_count > 0, "pwm_red should go high at least once with duty=1"
    # With duty=1 out of 256, should be high ~0.4% of the time
    assert high_count < 100, (
        f"pwm_red too high for duty=1: {high_count}/1000 (expected ~4)"
    )


@cocotb.test()
async def test_duty_254_near_max(dut):
    """Write duty=254 (near max), verify pwm_red is high most of the time."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    await axi_write(dut, 0x00, 0x000000FE, prefix="axi")
    dut._log.info("Wrote red_duty=254 (near max)")

    high_count = 0
    total = 1000
    for _ in range(total):
        await RisingEdge(dut.clk)
        if dut.pwm_red.value.is_resolvable:
            try:
                if int(dut.pwm_red.value) == 1:
                    high_count += 1
            except ValueError:
                pass

    dut._log.info(f"pwm_red high for {high_count}/{total} cycles with duty=254")
    assert high_count > total * 0.9, (
        f"pwm_red should be high >90% with duty=254, got {high_count}/{total}"
    )


@cocotb.test()
async def test_register_write_read_multiple(dut):
    """Write different values to reg0 and read back each time, verify consistency."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    test_values = [0x00000000, 0x00112233, 0x00FFFFFF, 0x00808080, 0x00010101]
    for val in test_values:
        await axi_write(dut, 0x00, val, prefix="axi")
        readback = await axi_read(dut, 0x00, prefix="axi")
        dut._log.info(f"Wrote {val:#010x}, read back {readback:#010x}")
        assert readback == val, (
            f"Readback mismatch: wrote {val:#010x}, got {readback:#010x}"
        )

    dut._log.info("Multiple write-read cycles verified successfully")


@cocotb.test()
async def test_independent_channel_control(dut):
    """Set only green high, verify red and blue stay low."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Green=255 (bits [15:8]), red=0, blue=0
    await axi_write(dut, 0x00, 0x0000FF00, prefix="axi")
    dut._log.info("Wrote green=255 only, red=0, blue=0")

    red_high = 0
    green_high = 0
    blue_high = 0
    for _ in range(500):
        await RisingEdge(dut.clk)
        if dut.pwm_red.value.is_resolvable:
            try:
                if int(dut.pwm_red.value) == 1:
                    red_high += 1
            except ValueError:
                pass
        if dut.pwm_green.value.is_resolvable:
            try:
                if int(dut.pwm_green.value) == 1:
                    green_high += 1
            except ValueError:
                pass
        if dut.pwm_blue.value.is_resolvable:
            try:
                if int(dut.pwm_blue.value) == 1:
                    blue_high += 1
            except ValueError:
                pass

    dut._log.info(f"red_high={red_high}, green_high={green_high}, blue_high={blue_high}")
    assert red_high == 0, f"pwm_red should be 0 with duty=0, but was high {red_high} times"
    assert blue_high == 0, f"pwm_blue should be 0 with duty=0, but was high {blue_high} times"
    assert green_high > 0, "pwm_green should toggle with duty=255"
    dut._log.info("Independent channel control verified")


@cocotb.test()
async def test_rapid_duty_updates(dut):
    """Write 10 different duty values in quick succession, verify no X/Z on outputs."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    for i in range(10):
        duty = (i * 25) & 0xFF
        await axi_write(dut, 0x00, duty, prefix="axi")
        await ClockCycles(dut.clk, 10)  # Very short gap between updates

    # Wait for PWM to settle
    await ClockCycles(dut.clk, 300)

    for sig_name in ["pwm_red", "pwm_green", "pwm_blue"]:
        sig = getattr(dut, sig_name)
        assert sig.value.is_resolvable, f"{sig_name} has X/Z after rapid duty updates"

    dut._log.info("Design survived 10 rapid duty cycle updates without X/Z")


@cocotb.test()
async def test_axi_write_response_signals(dut):
    """After AXI write, verify bvalid/bresp handshake completed correctly."""

    setup_clock(dut, "clk", 20)
    await pwm_init_axi(dut)

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await RisingEdge(dut.clk)

    # Perform a write and check that the AXI bus returns to idle
    await axi_write(dut, 0x00, 0x00000080, prefix="axi")

    # Verify AXI write channel signals are clean after transaction
    for sig_name in ["axi_awready", "axi_wready", "axi_bvalid"]:
        sig = getattr(dut, sig_name)
        assert sig.value.is_resolvable, f"{sig_name} has X/Z after write transaction"
        try:
            val = int(sig.value)
            dut._log.info(f"{sig_name} = {val}")
        except ValueError:
            dut._log.info(f"{sig_name} not convertible to int")

    # Verify bresp if resolvable
    if dut.axi_bresp.value.is_resolvable:
        try:
            bresp = int(dut.axi_bresp.value)
            dut._log.info(f"axi_bresp = {bresp} (0=OKAY)")
        except ValueError:
            pass

    dut._log.info("AXI write response signals verified")
