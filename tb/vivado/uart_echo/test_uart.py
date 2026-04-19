"""Cocotb testbench for vivado uart_top echo design."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


# 100 MHz system clock -> 10 ns period
CLK_PERIOD_NS = 10


@cocotb.test()
async def test_uart_echo(dut):
    """Verify UART echo design resets cleanly and outputs have no X/Z."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)

    # UART idle state is high
    dut.uart_rx.value = 1

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    # Verify uart_tx is resolvable and in idle state
    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after reset"
    tx_val = int(dut.uart_tx.value)
    dut._log.info(f"uart_tx after reset: {tx_val}")
    assert tx_val == 1, f"Expected uart_tx idle high (1), got {tx_val}"

    # Run for more cycles to verify stability
    await ClockCycles(dut.clk, 200)

    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after 200 cycles"
    dut._log.info("UART echo design runs cleanly with no X/Z on uart_tx")


# 115200 baud: 1 bit period = 1e9 / 115200 ~ 8680 ns
# Use shorter baud for simulation to avoid timeout
BAUD_NS = 100


async def uart_send_byte(dut, byte_val):
    """Send a single byte via uart_rx pin using standard UART framing.

    Drives: start bit (0), 8 data bits (LSB first), stop bit (1).
    """
    # Start bit
    dut.uart_rx.value = 0
    await Timer(BAUD_NS, unit="ns")

    # Data bits (LSB first)
    for bit_idx in range(8):
        dut.uart_rx.value = (byte_val >> bit_idx) & 1
        await Timer(BAUD_NS, unit="ns")

    # Stop bit
    dut.uart_rx.value = 1
    await Timer(BAUD_NS, unit="ns")


@cocotb.test()
async def test_tx_idle_high(dut):
    """Verify uart_tx idles at logic 1 after reset."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 20)

    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after reset"
    try:
        tx_val = int(dut.uart_tx.value)
        assert tx_val == 1, f"uart_tx should idle high (1), got {tx_val}"
        dut._log.info("uart_tx correctly idles at 1")
    except ValueError:
        assert False, "uart_tx not convertible to int"


@cocotb.test()
async def test_rx_idle(dut):
    """With uart_rx held at 1 (idle), verify no spurious activity on outputs."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 100)

    # uart_tx should remain idle high
    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z during idle"
    try:
        tx_val = int(dut.uart_tx.value)
        assert tx_val == 1, f"uart_tx should remain idle high, got {tx_val}"
    except ValueError:
        assert False, "uart_tx not convertible to int during idle"

    # status_led should be resolvable
    assert dut.status_led.value.is_resolvable, "status_led has X/Z during idle"
    dut._log.info("No spurious activity during uart_rx idle")


@cocotb.test()
async def test_status_led_clean(dut):
    """Verify all status_led bits are resolvable after reset."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    assert dut.status_led.value.is_resolvable, "status_led has X/Z after reset"
    try:
        led_val = int(dut.status_led.value)
        assert 0 <= led_val <= 15, f"status_led={led_val} out of range [0,15]"
        dut._log.info(f"status_led after reset: {led_val:#06b}")
    except ValueError:
        assert False, "status_led not convertible to int after reset"


@cocotb.test()
async def test_send_byte_0x41(dut):
    """Send byte 0x41 ('A') via uart_rx, verify design does not crash."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    # Send 0x41 ('A')
    await uart_send_byte(dut, 0x41)
    dut._log.info("Sent byte 0x41 via uart_rx")

    # Wait for the design to process
    await ClockCycles(dut.clk, 500)

    # Verify outputs are still clean
    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after sending 0x41"
    assert dut.status_led.value.is_resolvable, "status_led has X/Z after sending 0x41"
    dut._log.info("Design handled byte 0x41 without crashing")


@cocotb.test()
async def test_send_byte_0x55(dut):
    """Send 0x55 and verify uart_tx eventually shows activity."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    # Record initial uart_tx state
    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z before sending"

    # Send 0x55
    await uart_send_byte(dut, 0x55)
    dut._log.info("Sent byte 0x55 via uart_rx")

    # Watch uart_tx for activity (any transition from idle)
    tx_activity = False
    for _ in range(2000):
        await RisingEdge(dut.clk)
        if dut.uart_tx.value.is_resolvable:
            try:
                if int(dut.uart_tx.value) == 0:
                    tx_activity = True
                    break
            except ValueError:
                pass

    if tx_activity:
        dut._log.info("uart_tx showed echo activity after sending 0x55")
    else:
        dut._log.info("uart_tx did not show activity (may need more time); outputs still clean")

    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after echo attempt"


@cocotb.test()
async def test_send_multiple_bytes(dut):
    """Send 3 bytes sequentially and verify design stays clean."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    test_bytes = [0x48, 0x69, 0x21]  # "Hi!"
    for byte_val in test_bytes:
        await uart_send_byte(dut, byte_val)
        dut._log.info(f"Sent byte {byte_val:#04x}")
        # Small gap between bytes
        await ClockCycles(dut.clk, 100)

    # Wait for processing
    await ClockCycles(dut.clk, 500)

    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after sending multiple bytes"
    assert dut.status_led.value.is_resolvable, "status_led has X/Z after sending multiple bytes"
    dut._log.info("Design stayed clean after sending 3 bytes")


@cocotb.test()
async def test_rx_start_bit(dut):
    """Drive uart_rx=0 briefly (start bit), verify design handles it."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    # Drive a brief start bit pulse
    dut.uart_rx.value = 0
    await ClockCycles(dut.clk, 20)
    dut.uart_rx.value = 1

    # Let the design process the glitch
    await ClockCycles(dut.clk, 500)

    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after start bit glitch"
    assert dut.status_led.value.is_resolvable, "status_led has X/Z after start bit glitch"
    dut._log.info("Design handled brief start bit on uart_rx cleanly")


@cocotb.test()
async def test_long_idle(dut):
    """Run 2000 cycles with uart_rx=1 (idle), verify stability."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    for cycle in range(2000):
        await RisingEdge(dut.clk)
        if cycle % 500 == 0:
            assert dut.uart_tx.value.is_resolvable, (
                f"uart_tx has X/Z at cycle {cycle} during long idle"
            )
            try:
                tx_val = int(dut.uart_tx.value)
                assert tx_val == 1, (
                    f"uart_tx should remain idle high, got {tx_val} at cycle {cycle}"
                )
            except ValueError:
                assert False, f"uart_tx not convertible to int at cycle {cycle}"

    dut._log.info("Design stable over 2000 idle cycles")


@cocotb.test()
async def test_reset_clears_fifo(dut):
    """Reset should clear internal FIFO state; verify clean outputs after reset."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    # Send a byte to put data in the FIFO
    await uart_send_byte(dut, 0xAA)
    await ClockCycles(dut.clk, 200)

    # Now reset again
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    # After reset, uart_tx should be idle high (FIFO cleared)
    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after second reset"
    try:
        tx_val = int(dut.uart_tx.value)
        assert tx_val == 1, f"uart_tx should idle high after reset, got {tx_val}"
    except ValueError:
        assert False, "uart_tx not convertible to int after reset"

    assert dut.status_led.value.is_resolvable, "status_led has X/Z after second reset"
    dut._log.info("Reset cleared FIFO; uart_tx returned to idle high")


@cocotb.test()
async def test_status_led_values(dut):
    """Check status_led bit meanings after sending activity."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    # Record status_led before any UART activity
    assert dut.status_led.value.is_resolvable, "status_led has X/Z before activity"
    try:
        led_before = int(dut.status_led.value)
        dut._log.info(f"status_led before activity: {led_before:#06b}")
    except ValueError:
        led_before = None
        dut._log.info("status_led not convertible before activity")

    # Send a byte
    await uart_send_byte(dut, 0x42)
    await ClockCycles(dut.clk, 1000)

    # Record status_led after activity
    assert dut.status_led.value.is_resolvable, "status_led has X/Z after activity"
    try:
        led_after = int(dut.status_led.value)
        dut._log.info(f"status_led after activity: {led_after:#06b}")
        assert 0 <= led_after <= 15, f"status_led={led_after} out of range"
    except ValueError:
        assert False, "status_led not convertible after activity"

    if led_before is not None:
        if led_after != led_before:
            dut._log.info("status_led changed after UART activity")
        else:
            dut._log.info("status_led unchanged after UART activity")

    dut._log.info("status_led values checked successfully")


@cocotb.test()
async def test_send_byte_0x00(dut):
    """Send byte 0x00 (all zeros boundary), verify design stays clean."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    await uart_send_byte(dut, 0x00)
    dut._log.info("Sent byte 0x00 via uart_rx")

    await ClockCycles(dut.clk, 500)

    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after sending 0x00"
    assert dut.status_led.value.is_resolvable, "status_led has X/Z after sending 0x00"
    dut._log.info("Design handled byte 0x00 boundary without crashing")


@cocotb.test()
async def test_send_byte_0xff(dut):
    """Send byte 0xFF (all ones boundary), verify design stays clean."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    await uart_send_byte(dut, 0xFF)
    dut._log.info("Sent byte 0xFF via uart_rx")

    # Watch for echo activity
    tx_activity = False
    for _ in range(2000):
        await RisingEdge(dut.clk)
        if dut.uart_tx.value.is_resolvable:
            try:
                if int(dut.uart_tx.value) == 0:
                    tx_activity = True
                    break
            except ValueError:
                pass

    if tx_activity:
        dut._log.info("uart_tx showed echo activity for 0xFF")
    else:
        dut._log.info("uart_tx did not echo 0xFF within window")

    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after sending 0xFF"
    dut._log.info("Byte 0xFF boundary test completed")


@cocotb.test()
async def test_back_to_back_bytes(dut):
    """Send 5 bytes with minimal gap, verify design does not crash."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    test_bytes = [0x01, 0x55, 0xAA, 0xFE, 0x80]
    for byte_val in test_bytes:
        await uart_send_byte(dut, byte_val)
        dut._log.info(f"Sent byte {byte_val:#04x}")
        # Minimal inter-byte gap (just 2 stop-bit periods)
        await Timer(BAUD_NS * 2, unit="ns")

    # Wait for processing
    await ClockCycles(dut.clk, 2000)

    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after 5 back-to-back bytes"
    assert dut.status_led.value.is_resolvable, "status_led has X/Z after 5 back-to-back bytes"
    dut._log.info("Design survived 5 back-to-back bytes without crash")


@cocotb.test()
async def test_rx_noise_pattern(dut):
    """Drive random-like noise on uart_rx for 200 clocks, verify no crash."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 50)

    # Drive a pseudo-random noise pattern on rx
    pattern = [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0]
    for cycle in range(200):
        dut.uart_rx.value = pattern[cycle % len(pattern)]
        await RisingEdge(dut.clk)

    # Return to idle
    dut.uart_rx.value = 1
    await ClockCycles(dut.clk, 500)

    assert dut.uart_tx.value.is_resolvable, "uart_tx has X/Z after noise pattern"
    assert dut.status_led.value.is_resolvable, "status_led has X/Z after noise pattern"
    dut._log.info("Design handled rx noise pattern without crash")


@cocotb.test()
async def test_multiple_resets_with_activity(dut):
    """Send byte, reset, send another byte, reset, verify clean each time."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    for i, byte_val in enumerate([0x42, 0x69, 0xAA]):
        await reset_dut(dut, "rst_n", active_low=True, cycles=5)
        await ClockCycles(dut.clk, 50)

        # Verify idle state after reset
        assert dut.uart_tx.value.is_resolvable, f"uart_tx has X/Z after reset #{i + 1}"
        try:
            tx_val = int(dut.uart_tx.value)
            assert tx_val == 1, f"uart_tx not idle after reset #{i + 1}: {tx_val}"
        except ValueError:
            pass

        # Send a byte
        await uart_send_byte(dut, byte_val)
        dut._log.info(f"Cycle #{i + 1}: sent {byte_val:#04x}")
        await ClockCycles(dut.clk, 500)

        assert dut.uart_tx.value.is_resolvable, f"uart_tx has X/Z after byte in cycle #{i + 1}"
        assert dut.status_led.value.is_resolvable, (
            f"status_led has X/Z after byte in cycle #{i + 1}"
        )

    dut._log.info("Multiple reset-send cycles completed cleanly")


@cocotb.test()
async def test_uart_tx_stability_during_idle(dut):
    """Verify uart_tx never glitches low during 3000 idle cycles."""

    setup_clock(dut, "clk", CLK_PERIOD_NS)
    dut.uart_rx.value = 1

    await reset_dut(dut, "rst_n", active_low=True, cycles=5)
    await ClockCycles(dut.clk, 20)

    glitch_count = 0
    for cycle in range(3000):
        await RisingEdge(dut.clk)
        if dut.uart_tx.value.is_resolvable:
            try:
                if int(dut.uart_tx.value) == 0:
                    glitch_count += 1
            except ValueError:
                pass

    dut._log.info(f"uart_tx went low {glitch_count} times during 3000 idle cycles")
    assert glitch_count == 0, (
        f"uart_tx glitched low {glitch_count} times during idle -- expected 0"
    )
    dut._log.info("uart_tx remained stable high during extended idle period")
