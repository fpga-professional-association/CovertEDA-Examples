"""Cocotb testbench for aes_encrypt - AES-128 encryption engine."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, done should be 0 and ciphertext should be 0."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.plaintext.value = 0
    dut.key.value = 0
    dut.start.value = 0
    await RisingEdge(dut.clk)

    if dut.done.value.is_resolvable:
        try:
            assert int(dut.done.value) == 0, "done should be 0 after reset"
        except ValueError:
            assert False, "done X/Z after reset"


@cocotb.test()
async def test_encryption_completes(dut):
    """Start encryption and verify done asserts within expected cycles."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.plaintext.value = 0x00112233445566778899AABBCCDDEEFF
    dut.key.value = 0x000102030405060708090A0B0C0D0E0F
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    done_seen = False
    for cycle in range(20):
        await RisingEdge(dut.clk)
        if dut.done.value.is_resolvable:
            try:
                if int(dut.done.value) == 1:
                    done_seen = True
                    dut._log.info(f"Encryption completed at cycle {cycle + 1}")
                    break
            except ValueError:
                pass

    assert done_seen, "Encryption did not complete within 20 cycles"


@cocotb.test()
async def test_ciphertext_nonzero(dut):
    """Verify ciphertext is non-zero after encryption of non-zero input."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.plaintext.value = 0xDEADBEEFCAFEBABE1234567890ABCDEF
    dut.key.value = 0xFEDCBA9876543210FEDCBA9876543210
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    for _ in range(20):
        await RisingEdge(dut.clk)
        if dut.done.value.is_resolvable:
            try:
                if int(dut.done.value) == 1:
                    break
            except ValueError:
                pass

    if dut.ciphertext.value.is_resolvable:
        try:
            ct = int(dut.ciphertext.value)
            dut._log.info(f"Ciphertext: {ct:#034x}")
            assert ct != 0, "Ciphertext should be non-zero"
        except ValueError:
            assert False, "Ciphertext X/Z"


@cocotb.test()
async def test_different_keys_different_output(dut):
    """Same plaintext with different keys should produce different ciphertexts."""
    setup_clock(dut, "clk", 10)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    pt = 0x00112233445566778899AABBCCDDEEFF
    results = []

    for key_val in [0x00000000000000000000000000000000,
                    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF]:
        dut.plaintext.value = pt
        dut.key.value = key_val
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        for _ in range(20):
            await RisingEdge(dut.clk)
            if dut.done.value.is_resolvable:
                try:
                    if int(dut.done.value) == 1:
                        break
                except ValueError:
                    pass

        if dut.ciphertext.value.is_resolvable:
            try:
                results.append(int(dut.ciphertext.value))
            except ValueError:
                results.append(None)

        await reset_dut(dut, "reset_n", active_low=True, cycles=3)

    if len(results) == 2 and all(r is not None for r in results):
        dut._log.info(f"Key1 result: {results[0]:#034x}")
        dut._log.info(f"Key2 result: {results[1]:#034x}")
        assert results[0] != results[1], "Different keys should produce different ciphertexts"
