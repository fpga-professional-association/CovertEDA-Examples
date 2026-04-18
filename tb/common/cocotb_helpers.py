"""Common cocotb helper utilities: clock, reset, signal wait."""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, with_timeout


def setup_clock(dut, pin_name, period_ns):
    """Start a clock on the given pin with the specified period in ns."""
    clk = getattr(dut, pin_name)
    cocotb.start_soon(Clock(clk, period_ns, unit="ns").start())


async def reset_dut(dut, pin_name, active_low=True, cycles=5):
    """Assert reset for the given number of clock cycles then deassert.

    Args:
        dut: Device under test.
        pin_name: Name of the reset pin.
        active_low: If True, reset is active when driven low.
        cycles: Number of clock cycles to hold reset.
    """
    rst = getattr(dut, pin_name)
    rst.value = 0 if active_low else 1
    for _ in range(cycles):
        await Timer(10, unit="ns")
    rst.value = 1 if active_low else 0
    await Timer(10, unit="ns")


async def wait_for_signal(dut, pin_name, value, timeout_ns=10000):
    """Wait for a signal to reach a specific value, with timeout.

    Returns True if signal reached the value, False on timeout.
    """
    sig = getattr(dut, pin_name)
    deadline = cocotb.utils.get_sim_time(unit="ns") + timeout_ns
    while cocotb.utils.get_sim_time(unit="ns") < deadline:
        if int(sig.value) == value:
            return True
        await Timer(1, unit="ns")
    return False
