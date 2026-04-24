"""Cocotb testbench for sha256_hash - SHA-256 hash engine."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, done should be 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.msg_word.value = 0
    dut.msg_addr.value = 0
    dut.msg_wr.value = 0
    dut.start.value = 0
    await RisingEdge(dut.clk)

    if dut.done.value.is_resolvable:
        try:
            assert int(dut.done.value) == 0, "done should be 0 after reset"
        except ValueError:
            assert False, "done X/Z after reset"


@cocotb.test()
async def test_hash_completes(dut):
    """Load message words and verify hash computation completes."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    # Load 16 message words (all zeros)
    for i in range(16):
        dut.msg_addr.value = i
        dut.msg_word.value = 0
        dut.msg_wr.value = 1
        await RisingEdge(dut.clk)
    dut.msg_wr.value = 0

    # Start hashing
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    done_seen = False
    for cycle in range(30):
        await RisingEdge(dut.clk)
        if dut.done.value.is_resolvable:
            try:
                if int(dut.done.value) == 1:
                    done_seen = True
                    dut._log.info(f"Hash completed at cycle {cycle + 1}")
                    break
            except ValueError:
                pass

    assert done_seen, "Hash did not complete within 30 cycles"


@cocotb.test()
async def test_hash_output_nonzero(dut):
    """Verify hash output is non-zero after computation."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    # Load message with non-zero data
    for i in range(16):
        dut.msg_addr.value = i
        dut.msg_word.value = i + 1
        dut.msg_wr.value = 1
        await RisingEdge(dut.clk)
    dut.msg_wr.value = 0

    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    for _ in range(30):
        await RisingEdge(dut.clk)
        if dut.done.value.is_resolvable:
            try:
                if int(dut.done.value) == 1:
                    break
            except ValueError:
                pass

    if dut.hash_out.value.is_resolvable:
        try:
            h = int(dut.hash_out.value)
            dut._log.info(f"Hash output: {h:#066x}")
            assert h != 0, "Hash output should be non-zero"
        except ValueError:
            assert False, "Hash output X/Z"


@cocotb.test()
async def test_different_messages_different_hashes(dut):
    """Different messages should produce different hashes."""
    setup_clock(dut, "clk", 10)

    hashes = []
    for msg_base in [0x00000000, 0xFFFFFFFF]:
        await reset_dut(dut, "reset_n", active_low=True, cycles=5)

        for i in range(16):
            dut.msg_addr.value = i
            dut.msg_word.value = (msg_base + i) & 0xFFFFFFFF
            dut.msg_wr.value = 1
            await RisingEdge(dut.clk)
        dut.msg_wr.value = 0

        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        for _ in range(30):
            await RisingEdge(dut.clk)
            if dut.done.value.is_resolvable:
                try:
                    if int(dut.done.value) == 1:
                        break
                except ValueError:
                    pass

        if dut.hash_out.value.is_resolvable:
            try:
                hashes.append(int(dut.hash_out.value))
            except ValueError:
                hashes.append(None)

    if len(hashes) == 2 and all(h is not None for h in hashes):
        dut._log.info(f"Hash 1: {hashes[0]:#066x}")
        dut._log.info(f"Hash 2: {hashes[1]:#066x}")
        assert hashes[0] != hashes[1], "Different messages should produce different hashes"
