"""Cocotb testbench for uart_top (baud_gen + uart_tx).

12 MHz clk → baud_gen divides by 104 → ~115,384 Hz baud clock.
uart_tx frames: start(0), data[0..7] LSB first, stop(1).
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, First


CLK_PERIOD_NS = 83  # ~12 MHz
BAUD_PERIOD_NS = CLK_PERIOD_NS * 104  # 2 * 52 = 104 clk per baud bit

async def reset(dut):
    dut.rst_n.value = 0
    dut.valid.value = 0
    dut.data_in.value = 0
    await Timer(500, unit="ns")
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_ready_high_after_reset(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    # Let a baud tick land.
    for _ in range(300):
        await RisingEdge(dut.clk)
    assert int(dut.ready.value) == 1, "ready should be high when idle"
    assert int(dut.uart_tx.value) == 1, "uart_tx line should be high when idle"


async def send_and_sample(dut, byte):
    dut.data_in.value = byte
    dut.valid.value = 1
    # Detect start-of-frame (uart_tx falling edge) immediately while valid is high,
    # so we don't miss the start bit to prior shifts.
    for _ in range(20_000):
        await RisingEdge(dut.clk)
        if int(dut.uart_tx.value) == 0:
            break
    else:
        raise AssertionError("never saw start bit")
    # Keep valid asserted through one more cycle, then drop so no retrigger.
    await RisingEdge(dut.clk)
    dut.valid.value = 0

    # Now we're ~1 clk into the start-bit period. Align to mid-bit.
    await Timer(BAUD_PERIOD_NS // 2 - CLK_PERIOD_NS, unit="ns")
    assert int(dut.uart_tx.value) == 0, "start bit should be 0"

    received = 0
    for i in range(8):
        await Timer(BAUD_PERIOD_NS, unit="ns")
        bit = int(dut.uart_tx.value)
        received |= (bit & 1) << i

    await Timer(BAUD_PERIOD_NS, unit="ns")
    assert int(dut.uart_tx.value) == 1, "stop bit should be 1"
    assert received == byte, f"got 0x{received:02x}, expected 0x{byte:02x}"


@cocotb.test()
async def test_send_byte_0xa5(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    await send_and_sample(dut, 0xA5)


@cocotb.test()
async def test_send_byte_0x00(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    await send_and_sample(dut, 0x00)


@cocotb.test()
async def test_send_byte_0xff(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await reset(dut)
    await send_and_sample(dut, 0xFF)
