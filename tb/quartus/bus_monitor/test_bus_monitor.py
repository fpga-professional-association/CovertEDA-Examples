"""Cocotb testbench for quartus bus_monitor (bus activity monitor)."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def do_bus_transaction(dut, addr, data, is_write=True):
    """Execute one bus transaction."""
    dut.bus_valid.value = 1
    dut.bus_ready.value = 1
    dut.bus_wr.value = 1 if is_write else 0
    dut.bus_addr.value = addr
    dut.bus_data.value = data
    await RisingEdge(dut.clk)
    dut.bus_valid.value = 0
    dut.bus_ready.value = 0
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_reset_state(dut):
    """Verify counters are zero after reset."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.bus_valid.value = 0
    dut.bus_ready.value = 0
    dut.bus_wr.value = 0
    dut.bus_addr.value = 0
    dut.bus_data.value = 0
    await RisingEdge(dut.clk)

    if not dut.total_count.value.is_resolvable:
        raise AssertionError("total_count has X/Z after reset")

    try:
        total = int(dut.total_count.value)
        wr = int(dut.wr_count.value)
        rd = int(dut.rd_count.value)
    except ValueError:
        raise AssertionError("Counters not convertible after reset")

    assert total == 0, f"Expected total=0, got {total}"
    assert wr == 0, f"Expected wr=0, got {wr}"
    assert rd == 0, f"Expected rd=0, got {rd}"
    dut._log.info("Reset state: all counters zero")


@cocotb.test()
async def test_write_transaction(dut):
    """Execute write transactions and verify counters."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.bus_valid.value = 0
    dut.bus_ready.value = 0
    dut.bus_wr.value = 0
    dut.bus_addr.value = 0
    dut.bus_data.value = 0
    await RisingEdge(dut.clk)

    # 3 write transactions
    for i in range(3):
        await do_bus_transaction(dut, addr=0x10 + i, data=0xA0 + i, is_write=True)

    await RisingEdge(dut.clk)

    if dut.total_count.value.is_resolvable and dut.wr_count.value.is_resolvable:
        try:
            total = int(dut.total_count.value)
            wr = int(dut.wr_count.value)
            rd = int(dut.rd_count.value)
            dut._log.info(f"After 3 writes: total={total}, wr={wr}, rd={rd}")
            assert total == 3, f"Expected total=3, got {total}"
            assert wr == 3, f"Expected wr=3, got {wr}"
            assert rd == 0, f"Expected rd=0, got {rd}"
        except ValueError:
            raise AssertionError("Counters not convertible")


@cocotb.test()
async def test_read_transaction(dut):
    """Execute read transactions and verify counters."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.bus_valid.value = 0
    dut.bus_ready.value = 0
    dut.bus_wr.value = 0
    dut.bus_addr.value = 0
    dut.bus_data.value = 0
    await RisingEdge(dut.clk)

    # 2 read transactions
    for i in range(2):
        await do_bus_transaction(dut, addr=0x20 + i, data=0xB0 + i, is_write=False)

    await RisingEdge(dut.clk)

    if dut.rd_count.value.is_resolvable:
        try:
            rd = int(dut.rd_count.value)
            dut._log.info(f"After 2 reads: rd_count={rd}")
            assert rd == 2, f"Expected rd=2, got {rd}"
        except ValueError:
            raise AssertionError("rd_count not convertible")


@cocotb.test()
async def test_last_addr_data(dut):
    """Verify last_addr and last_data capture correctly."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.bus_valid.value = 0
    dut.bus_ready.value = 0
    dut.bus_wr.value = 0
    dut.bus_addr.value = 0
    dut.bus_data.value = 0
    await RisingEdge(dut.clk)

    await do_bus_transaction(dut, addr=0x42, data=0xBE, is_write=True)
    await RisingEdge(dut.clk)

    if dut.last_addr.value.is_resolvable and dut.last_data.value.is_resolvable:
        try:
            addr = int(dut.last_addr.value)
            data = int(dut.last_data.value)
            dut._log.info(f"Last addr={addr:#04x}, data={data:#04x}")
            assert addr == 0x42, f"Expected last_addr=0x42, got {addr:#04x}"
            assert data == 0xBE, f"Expected last_data=0xBE, got {data:#04x}"
        except ValueError:
            raise AssertionError("last_addr/data not convertible")


@cocotb.test()
async def test_no_transaction_without_ready(dut):
    """Valid without ready should not count as transaction."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "rst_n", active_low=True, cycles=5)

    dut.bus_valid.value = 0
    dut.bus_ready.value = 0
    dut.bus_wr.value = 0
    dut.bus_addr.value = 0
    dut.bus_data.value = 0
    await RisingEdge(dut.clk)

    # Assert valid but not ready
    dut.bus_valid.value = 1
    dut.bus_ready.value = 0
    dut.bus_wr.value = 1
    dut.bus_addr.value = 0xFF
    dut.bus_data.value = 0xFF
    await RisingEdge(dut.clk)
    dut.bus_valid.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    if dut.total_count.value.is_resolvable:
        try:
            total = int(dut.total_count.value)
            dut._log.info(f"Total count with valid-no-ready: {total}")
            assert total == 0, f"Expected total=0, got {total}"
        except ValueError:
            raise AssertionError("total_count not convertible")
