"""Cocotb testbench for blinky_top.

Uses iverilog. The real RTL toggles the LED every 12_000_000 clocks at 12 MHz
(1 s half-period). Simulating that takes too long, so we deposit the counter
near the threshold with cocotb handle assignment and verify the toggle.
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


CLK_PERIOD_NS = 83  # ~12 MHz
THRESHOLD = 12_000_000


async def reset(dut):
    dut.rst_n.value = 0
    await Timer(200, unit="ns")
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_led_starts_low_after_reset(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    assert dut.led.value == 0, f"LED should be 0 after reset, got {dut.led.value}"


@cocotb.test()
async def test_counter_increments(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    start = int(dut.counter.value)
    for _ in range(10):
        await RisingEdge(dut.clk)
    after = int(dut.counter.value)
    assert after == start + 10, f"counter should advance by 10, got {after - start}"


@cocotb.test()
async def test_led_toggles_at_threshold(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)

    # Deposit near threshold to avoid 12M-cycle sim.
    dut.counter.value = THRESHOLD - 3
    await RisingEdge(dut.clk)

    led_before = int(dut.led.value)
    # Wait for counter to cross THRESHOLD and toggle.
    for _ in range(8):
        await RisingEdge(dut.clk)
        if int(dut.led.value) != led_before:
            # Counter should have rolled back near 0.
            assert int(dut.counter.value) < 10
            return
    raise AssertionError("LED did not toggle after crossing threshold")


@cocotb.test()
async def test_reset_clears_counter(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    for _ in range(50):
        await RisingEdge(dut.clk)
    assert int(dut.counter.value) == 50

    dut.rst_n.value = 0
    await Timer(100, unit="ns")
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert int(dut.counter.value) == 0, "reset should clear counter"
    assert int(dut.led.value) == 0, "reset should clear led"
