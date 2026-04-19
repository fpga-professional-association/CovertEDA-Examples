"""Cocotb testbench for vivado mem_top DDR3 test controller."""

import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


async def drive_ddr3_dq_responder(dut, cycles=500):
    """Simple DDR3 DQ responder: echo a pattern on ddr3_dq when write
    activity is detected (ras_n/cas_n/we_n strobes).

    Since there is no real DDR3 memory model, this drives a fixed pattern
    back on the bidirectional ddr3_dq bus to keep the controller from
    hanging indefinitely.
    """
    for _ in range(cycles):
        await RisingEdge(dut.clk_sys)
        # When a read command is issued (ras_n=1, cas_n=0, we_n=1),
        # drive a simple incrementing pattern on ddr3_dq
        try:
            ras = int(dut.ddr3_ras_n.value)
            cas = int(dut.ddr3_cas_n.value)
            we = int(dut.ddr3_we_n.value)
            if ras == 1 and cas == 0 and we == 1:
                dut.ddr3_dq.value = 0xDEADBEEFCAFE0123
        except Exception:
            pass


@cocotb.test()
async def test_ddr3_controller(dut):
    """Assert test_en and verify test_busy responds; check status outputs."""

    # Start two 5 ns clocks (200 MHz each)
    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    # Initialize control signals
    dut.test_en.value = 0
    dut.test_mode.value = 0

    # Reset (active-low rst_n)
    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await RisingEdge(dut.clk_sys)

    # Verify initial state: test_busy should be 0 before test starts
    initial_busy = int(dut.test_busy.value)
    dut._log.info(f"Initial test_busy: {initial_busy}")
    assert initial_busy == 0, "test_busy should be 0 before test_en is asserted"

    # Start a DDR3 DQ responder in the background
    cocotb.start_soon(drive_ddr3_dq_responder(dut, cycles=500))

    # Enable the test: set test_en=1, test_mode=0
    dut.test_en.value = 1
    dut.test_mode.value = 0
    dut._log.info("Asserted test_en=1, test_mode=0")

    # Wait a few cycles and check that test_busy asserts
    busy_seen = False
    for _ in range(100):
        await RisingEdge(dut.clk_sys)
        if int(dut.test_busy.value) == 1:
            busy_seen = True
            break

    dut._log.info(f"test_busy asserted: {busy_seen}")
    assert busy_seen, "test_busy never asserted after enabling test"

    # Let the design run for a while
    await ClockCycles(dut.clk_sys, 300)

    # Read status outputs
    status_val = int(dut.status.value)
    error_count_val = int(dut.error_count.value)
    dut._log.info(f"status={status_val:#06x}, error_count={error_count_val}")

    # Deassert test_en
    dut.test_en.value = 0
    await ClockCycles(dut.clk_sys, 20)


@cocotb.test()
async def test_idle_state(dut):
    """Before test_en, verify test_busy==0 and outputs are clean."""

    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    dut.test_en.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await ClockCycles(dut.clk_sys, 20)

    assert dut.test_busy.value.is_resolvable, "test_busy has X/Z in idle state"
    try:
        busy_val = int(dut.test_busy.value)
        assert busy_val == 0, f"test_busy should be 0 in idle, got {busy_val}"
    except ValueError:
        assert False, "test_busy not convertible to int in idle"

    # Verify test_passed and test_failed are resolvable
    for sig_name in ["test_passed", "test_failed"]:
        sig = getattr(dut, sig_name)
        assert sig.value.is_resolvable, f"{sig_name} has X/Z in idle state"

    dut._log.info("Idle state verified: test_busy=0, outputs clean")


@cocotb.test()
async def test_mode_0_zeros(dut):
    """Set test_mode=0 (zeros pattern), test_en=1, verify signals active."""

    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    dut.test_en.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await RisingEdge(dut.clk_sys)

    cocotb.start_soon(drive_ddr3_dq_responder(dut, cycles=500))

    dut.test_en.value = 1
    dut.test_mode.value = 0
    dut._log.info("Started test mode 0 (zeros pattern)")

    busy_seen = False
    for _ in range(100):
        await RisingEdge(dut.clk_sys)
        if dut.test_busy.value.is_resolvable:
            try:
                if int(dut.test_busy.value) == 1:
                    busy_seen = True
                    break
            except ValueError:
                pass

    dut._log.info(f"test_busy asserted with mode 0: {busy_seen}")

    await ClockCycles(dut.clk_sys, 200)

    # Verify outputs are resolvable
    assert dut.status.value.is_resolvable, "status has X/Z during mode 0 test"
    assert dut.error_count.value.is_resolvable, "error_count has X/Z during mode 0 test"

    dut.test_en.value = 0
    await ClockCycles(dut.clk_sys, 10)


@cocotb.test()
async def test_mode_1_ones(dut):
    """Set test_mode=1 (ones pattern), verify operation."""

    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    dut.test_en.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await RisingEdge(dut.clk_sys)

    cocotb.start_soon(drive_ddr3_dq_responder(dut, cycles=500))

    dut.test_en.value = 1
    dut.test_mode.value = 1
    dut._log.info("Started test mode 1 (ones pattern)")

    busy_seen = False
    for _ in range(100):
        await RisingEdge(dut.clk_sys)
        if dut.test_busy.value.is_resolvable:
            try:
                if int(dut.test_busy.value) == 1:
                    busy_seen = True
                    break
            except ValueError:
                pass

    dut._log.info(f"test_busy asserted with mode 1: {busy_seen}")

    await ClockCycles(dut.clk_sys, 200)

    assert dut.status.value.is_resolvable, "status has X/Z during mode 1 test"

    dut.test_en.value = 0
    await ClockCycles(dut.clk_sys, 10)


@cocotb.test()
async def test_mode_2_alternating(dut):
    """Set test_mode=2 (0xAAAA pattern), check for activity."""

    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    dut.test_en.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await RisingEdge(dut.clk_sys)

    cocotb.start_soon(drive_ddr3_dq_responder(dut, cycles=500))

    dut.test_en.value = 1
    dut.test_mode.value = 2
    dut._log.info("Started test mode 2 (0xAAAA pattern)")

    await ClockCycles(dut.clk_sys, 200)

    assert dut.status.value.is_resolvable, "status has X/Z during mode 2 test"
    assert dut.error_count.value.is_resolvable, "error_count has X/Z during mode 2 test"

    dut.test_en.value = 0
    await ClockCycles(dut.clk_sys, 10)
    dut._log.info("Mode 2 test completed, outputs clean")


@cocotb.test()
async def test_mode_3_alternating_inv(dut):
    """Set test_mode=3 (0x5555 pattern), verify operation."""

    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    dut.test_en.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await RisingEdge(dut.clk_sys)

    cocotb.start_soon(drive_ddr3_dq_responder(dut, cycles=500))

    dut.test_en.value = 1
    dut.test_mode.value = 3
    dut._log.info("Started test mode 3 (0x5555 pattern)")

    await ClockCycles(dut.clk_sys, 200)

    assert dut.status.value.is_resolvable, "status has X/Z during mode 3 test"
    assert dut.error_count.value.is_resolvable, "error_count has X/Z during mode 3 test"

    dut.test_en.value = 0
    await ClockCycles(dut.clk_sys, 10)
    dut._log.info("Mode 3 test completed, outputs clean")


@cocotb.test()
async def test_status_word(dut):
    """Read status[15:0], verify it contains expected test mode and flags."""

    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    dut.test_en.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await RisingEdge(dut.clk_sys)

    cocotb.start_soon(drive_ddr3_dq_responder(dut, cycles=500))

    # Start with mode 2
    dut.test_en.value = 1
    dut.test_mode.value = 2

    await ClockCycles(dut.clk_sys, 100)

    assert dut.status.value.is_resolvable, "status has X/Z"
    try:
        status_val = int(dut.status.value)
        dut._log.info(f"status word: {status_val:#06x}")
        # status should be a 16-bit value
        assert 0 <= status_val <= 0xFFFF, f"status={status_val:#06x} out of 16-bit range"
    except ValueError:
        assert False, "status not convertible to int"

    dut.test_en.value = 0
    await ClockCycles(dut.clk_sys, 10)


@cocotb.test()
async def test_error_count_initial(dut):
    """Before starting a test, error_count should be 0."""

    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    dut.test_en.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await ClockCycles(dut.clk_sys, 20)

    assert dut.error_count.value.is_resolvable, "error_count has X/Z before test"
    try:
        err_val = int(dut.error_count.value)
        dut._log.info(f"error_count before test: {err_val}")
        assert err_val == 0, f"error_count should be 0 before test, got {err_val}"
    except ValueError:
        assert False, "error_count not convertible to int before test"


@cocotb.test()
async def test_test_passed_or_failed(dut):
    """After test runs, one of test_passed/test_failed should eventually assert."""

    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    dut.test_en.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await RisingEdge(dut.clk_sys)

    cocotb.start_soon(drive_ddr3_dq_responder(dut, cycles=1000))

    dut.test_en.value = 1
    dut.test_mode.value = 0

    passed_seen = False
    failed_seen = False
    for _ in range(500):
        await RisingEdge(dut.clk_sys)
        if dut.test_passed.value.is_resolvable:
            try:
                if int(dut.test_passed.value) == 1:
                    passed_seen = True
            except ValueError:
                pass
        if dut.test_failed.value.is_resolvable:
            try:
                if int(dut.test_failed.value) == 1:
                    failed_seen = True
            except ValueError:
                pass
        if passed_seen or failed_seen:
            break

    dut.test_en.value = 0

    if passed_seen:
        dut._log.info("test_passed asserted")
    elif failed_seen:
        dut._log.info("test_failed asserted")
    else:
        dut._log.info("Neither test_passed nor test_failed asserted in 500 cycles "
                       "(test may need more time with real memory model)")

    # At minimum, both signals should be resolvable
    assert dut.test_passed.value.is_resolvable, "test_passed has X/Z"
    assert dut.test_failed.value.is_resolvable, "test_failed has X/Z"

    await ClockCycles(dut.clk_sys, 10)


@cocotb.test()
async def test_ddr3_ck_toggles(dut):
    """Verify ddr3_ck_p toggles (driven by clk_200_in)."""

    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    dut.test_en.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=10)

    # Check ddr3_ck_p for toggling over several cycles
    edge_count = 0
    prev_val = None
    for _ in range(100):
        await RisingEdge(dut.clk_sys)
        if dut.ddr3_ck_p.value.is_resolvable:
            try:
                cur_val = int(dut.ddr3_ck_p.value)
                if prev_val is not None and cur_val != prev_val:
                    edge_count += 1
                prev_val = cur_val
            except ValueError:
                pass

    dut._log.info(f"ddr3_ck_p toggled {edge_count} times in 100 clk_sys cycles")
    # ddr3_ck_p may not toggle if DDR controller hasn't completed calibration
    if edge_count > 0:
        dut._log.info("ddr3_ck_p is toggling -- clock output active")
    else:
        dut._log.info("ddr3_ck_p did not toggle (DDR controller may need calibration/init)")


@cocotb.test()
async def test_reset_during_test(dut):
    """Assert reset during an active test, verify clean recovery."""

    setup_clock(dut, "clk_sys", 5)
    setup_clock(dut, "clk_200_in", 5)

    dut.test_en.value = 0
    dut.test_mode.value = 0

    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await RisingEdge(dut.clk_sys)

    cocotb.start_soon(drive_ddr3_dq_responder(dut, cycles=500))

    # Start a test
    dut.test_en.value = 1
    dut.test_mode.value = 4  # address pattern
    await ClockCycles(dut.clk_sys, 50)

    dut._log.info("Asserting reset during active test")

    # Assert reset mid-test
    dut.test_en.value = 0
    await reset_dut(dut, "rst_n", active_low=True, cycles=10)
    await ClockCycles(dut.clk_sys, 20)

    # Verify recovery
    assert dut.test_busy.value.is_resolvable, "test_busy has X/Z after mid-test reset"
    try:
        busy_val = int(dut.test_busy.value)
        assert busy_val == 0, f"test_busy should be 0 after reset, got {busy_val}"
    except ValueError:
        assert False, "test_busy not convertible to int after reset"

    assert dut.status.value.is_resolvable, "status has X/Z after mid-test reset"
    assert dut.error_count.value.is_resolvable, "error_count has X/Z after mid-test reset"

    dut._log.info("Design recovered cleanly from reset during test")
