"""Cocotb testbench for pwm_dac.

pwm_out is high whenever the free-running 8-bit counter is less than the
latched sample value. Over a full 256-clock window, duty cycle ≈ sample/256.

Note: audio_top has an undriven `addr` signal feeding sample_rom, so we test
the DAC in isolation rather than through the top.
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


CLK_PERIOD_NS = 83  # ~12 MHz


async def reset(dut):
    dut.rst_n.value = 0
    dut.sample.value = 0
    dut.sample_valid.value = 0
    await Timer(200, unit="ns")
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def measure_duty_cycle(dut, window=256):
    highs = 0
    for _ in range(window):
        await RisingEdge(dut.clk)
        highs += int(dut.pwm_out.value) & 1
    return highs / window


@cocotb.test()
async def test_pwm_low_when_sample_zero(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    dut.sample.value = 0
    dut.sample_valid.value = 1
    await RisingEdge(dut.clk)
    dut.sample_valid.value = 0

    duty = await measure_duty_cycle(dut)
    assert duty == 0.0, f"sample=0 should give 0% duty, got {duty:.2%}"


@cocotb.test()
async def test_pwm_full_when_sample_255(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    dut.sample.value = 0xFF
    dut.sample_valid.value = 1
    await RisingEdge(dut.clk)
    dut.sample_valid.value = 0

    duty = await measure_duty_cycle(dut)
    # Counter never reaches 255 (< comparison), so ~255/256 high.
    assert duty > 0.99, f"sample=0xFF should give near-100% duty, got {duty:.2%}"


@cocotb.test()
async def test_pwm_midscale(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    dut.sample.value = 128
    dut.sample_valid.value = 1
    await RisingEdge(dut.clk)
    dut.sample_valid.value = 0

    duty = await measure_duty_cycle(dut)
    assert 0.45 < duty < 0.55, f"sample=128 should give ~50% duty, got {duty:.2%}"


@cocotb.test()
async def test_sample_only_latched_when_valid(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)

    dut.sample.value = 64
    dut.sample_valid.value = 1
    await RisingEdge(dut.clk)
    dut.sample_valid.value = 0
    duty_before = await measure_duty_cycle(dut)

    # Change sample but don't pulse valid; latched value should persist.
    dut.sample.value = 200
    duty_after = await measure_duty_cycle(dut)

    assert abs(duty_before - duty_after) < 0.02, (
        f"duty changed without valid pulse: {duty_before:.2%} → {duty_after:.2%}"
    )
