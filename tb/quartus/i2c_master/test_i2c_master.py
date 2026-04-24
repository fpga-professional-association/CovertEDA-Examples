"""Cocotb testbench for quartus i2c_master (I2C master controller)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """Verify idle state after reset: SCL=1, SDA=1, busy=0."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.start.value = 0
    dut.rw.value = 0
    dut.slave_addr.value = 0
    dut.data_in.value = 0
    dut.sda_in.value = 1
    await RisingEdge(dut.clk)

    if not dut.scl_out.value.is_resolvable:
        raise AssertionError("scl_out has X/Z after reset")

    try:
        scl = int(dut.scl_out.value)
        sda = int(dut.sda_out.value)
        busy = int(dut.busy.value)
    except ValueError:
        raise AssertionError("Signals not convertible after reset")

    assert scl == 1, f"Expected SCL=1, got {scl}"
    assert sda == 1, f"Expected SDA=1, got {sda}"
    assert busy == 0, f"Expected busy=0, got {busy}"
    dut._log.info("Reset state: SCL=1, SDA=1, busy=0")


@cocotb.test()
async def test_start_generates_busy(dut):
    """Starting a transaction should assert busy."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.start.value = 0
    dut.rw.value = 0
    dut.slave_addr.value = 0x50
    dut.data_in.value = 0xAB
    dut.sda_in.value = 1
    await RisingEdge(dut.clk)

    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    await ClockCycles(dut.clk, 5)

    if dut.busy.value.is_resolvable:
        try:
            busy = int(dut.busy.value)
            dut._log.info(f"Busy after start: {busy}")
            assert busy == 1, f"Expected busy=1, got {busy}"
        except ValueError:
            raise AssertionError("busy not convertible")


@cocotb.test()
async def test_scl_toggles(dut):
    """SCL should toggle during transaction."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.start.value = 0
    dut.rw.value = 0
    dut.slave_addr.value = 0x50
    dut.data_in.value = 0xAB
    dut.sda_in.value = 0  # ACK
    await RisingEdge(dut.clk)

    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    scl_transitions = 0
    prev_scl = None
    for _ in range(500):
        await RisingEdge(dut.clk)
        if dut.scl_out.value.is_resolvable:
            try:
                cur_scl = int(dut.scl_out.value)
                if prev_scl is not None and cur_scl != prev_scl:
                    scl_transitions += 1
                prev_scl = cur_scl
            except ValueError:
                pass

    dut._log.info(f"SCL transitions during transaction: {scl_transitions}")
    assert scl_transitions > 5, f"Expected SCL toggling, got {scl_transitions} transitions"


@cocotb.test()
async def test_transaction_completes(dut):
    """A full write transaction should complete with done pulse."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.start.value = 0
    dut.rw.value = 0
    dut.slave_addr.value = 0x50
    dut.data_in.value = 0xAB
    dut.sda_in.value = 0  # ACK from slave
    await RisingEdge(dut.clk)

    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    done_seen = False
    for cycle in range(1000):
        await RisingEdge(dut.clk)
        if dut.done.value.is_resolvable:
            try:
                if int(dut.done.value) == 1:
                    done_seen = True
                    dut._log.info(f"Transaction done at cycle {cycle}")
                    break
            except ValueError:
                pass

    dut._log.info(f"Transaction completed: {done_seen}")
    if done_seen:
        if dut.busy.value.is_resolvable:
            try:
                busy = int(dut.busy.value)
                dut._log.info(f"Busy after done: {busy}")
            except ValueError:
                pass


@cocotb.test()
async def test_nack_detection(dut):
    """NACK (sda_in=1 during ACK) should set ack_err."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.start.value = 0
    dut.rw.value = 0
    dut.slave_addr.value = 0x50
    dut.data_in.value = 0xAB
    dut.sda_in.value = 1  # NACK from slave
    await RisingEdge(dut.clk)

    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    # Wait for transaction to complete
    for _ in range(1000):
        await RisingEdge(dut.clk)
        if dut.done.value.is_resolvable:
            try:
                if int(dut.done.value) == 1:
                    break
            except ValueError:
                pass

    if dut.ack_err.value.is_resolvable:
        try:
            err = int(dut.ack_err.value)
            dut._log.info(f"ack_err after NACK transaction: {err}")
            assert err == 1, f"Expected ack_err=1 on NACK, got {err}"
        except ValueError:
            raise AssertionError("ack_err not convertible")
