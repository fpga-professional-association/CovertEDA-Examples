"""Cocotb testbench for ws2812_tx.

Per the RTL:
- Each color bit takes 12 clk cycles (0..11).
- out_bit = color_shift[23] for cycles 0..3 (high portion), then 0 for 4..11.
- So a '1' bit encodes as 4 high / 8 low; a '0' bit encodes as 0 high / 12 low
  (because color_shift[23] is the actual bit being transmitted).
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


CLK_PERIOD_NS = 83  # ~12 MHz
CYCLES_PER_BIT = 12


async def reset(dut):
    dut.rst_n.value = 0
    dut.color.value = 0
    dut.color_valid.value = 0
    await Timer(200, unit="ns")
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def capture_bit_pattern(dut, num_bits):
    """Return a list of `num_bits` entries; each entry is the number of high
    clocks within that bit's 12-cycle window."""
    highs_per_bit = []
    for _ in range(num_bits):
        highs = 0
        for _ in range(CYCLES_PER_BIT):
            await RisingEdge(dut.clk)
            highs += int(dut.ws2812_out.value) & 1
        highs_per_bit.append(highs)
    return highs_per_bit


@cocotb.test()
async def test_idle_output_low(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    for _ in range(20):
        await RisingEdge(dut.clk)
        assert int(dut.ws2812_out.value) == 0, "idle should be low"


@cocotb.test()
async def test_all_ones_color(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)

    dut.color.value = 0xFFFFFF
    dut.color_valid.value = 1
    await RisingEdge(dut.clk)
    dut.color_valid.value = 0
    # After this edge transmitting=1, cycle_count=0. Start sampling now.
    highs = await capture_bit_pattern(dut, 24)
    # Every bit is '1' → 4 highs per bit.
    for i, h in enumerate(highs):
        assert h == 4, f"bit {i}: expected 4 highs, got {h}"


@cocotb.test()
async def test_all_zeros_color(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)

    dut.color.value = 0x000000
    dut.color_valid.value = 1
    await RisingEdge(dut.clk)
    dut.color_valid.value = 0

    highs = await capture_bit_pattern(dut, 24)
    for i, h in enumerate(highs):
        assert h == 0, f"bit {i}: expected 0 highs (zero bit), got {h}"


@cocotb.test()
async def test_msb_first_pattern(dut):
    """color = 0x800000 → MSB is 1, rest 0. Expect first bit to have 4 highs,
    remaining 23 bits to have 0."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)

    dut.color.value = 0x800000
    dut.color_valid.value = 1
    await RisingEdge(dut.clk)
    dut.color_valid.value = 0

    highs = await capture_bit_pattern(dut, 24)
    assert highs[0] == 4, f"first bit expected 4 highs, got {highs[0]}"
    for i in range(1, 24):
        assert highs[i] == 0, f"bit {i} expected 0 highs, got {highs[i]}"
