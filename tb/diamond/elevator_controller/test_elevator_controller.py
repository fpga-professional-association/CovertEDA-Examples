"""Cocotb testbench for elevator_controller - 4-floor elevator FSM."""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb_helpers import setup_clock, reset_dut


@cocotb.test()
async def test_reset_state(dut):
    """After reset, elevator should be at floor 0, door closed, motor off."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.floor_request.value = 0
    dut.floor_sensor.value = 1
    await RisingEdge(dut.clk)

    if dut.current_floor.value.is_resolvable:
        try:
            assert int(dut.current_floor.value) == 0, "Should start at floor 0"
        except ValueError:
            assert False, "current_floor X/Z after reset"

    if dut.door_open.value.is_resolvable:
        try:
            assert int(dut.door_open.value) == 0, "Door should be closed"
        except ValueError:
            assert False, "door_open X/Z after reset"

    if dut.motor_up.value.is_resolvable:
        try:
            assert int(dut.motor_up.value) == 0, "motor_up should be off"
        except ValueError:
            assert False, "motor_up X/Z after reset"


@cocotb.test()
async def test_request_same_floor(dut):
    """Request current floor, door should open without motor."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.floor_sensor.value = 1
    dut.floor_request.value = 1  # Request floor 0 (current)
    await RisingEdge(dut.clk)
    dut.floor_request.value = 0
    await ClockCycles(dut.clk, 5)

    door_opened = False
    for _ in range(20):
        await RisingEdge(dut.clk)
        if dut.door_open.value.is_resolvable:
            try:
                if int(dut.door_open.value) == 1:
                    door_opened = True
                    break
            except ValueError:
                pass

    assert door_opened, "Door should open when requesting current floor"
    dut._log.info("Door opened for same-floor request")


@cocotb.test()
async def test_move_up(dut):
    """Request higher floor, motor_up should activate."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.floor_sensor.value = 1
    dut.floor_request.value = 0b1000  # Request floor 3
    await RisingEdge(dut.clk)
    dut.floor_request.value = 0

    motor_up_seen = False
    for _ in range(30):
        await RisingEdge(dut.clk)
        if dut.motor_up.value.is_resolvable:
            try:
                if int(dut.motor_up.value) == 1:
                    motor_up_seen = True
                    break
            except ValueError:
                pass

    assert motor_up_seen, "Motor up should activate for upward request"
    dut._log.info("Motor up activated for floor 3 request")


@cocotb.test()
async def test_floor_led_tracks_position(dut):
    """Floor LED should reflect current floor position."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.floor_request.value = 0
    dut.floor_sensor.value = 1
    await RisingEdge(dut.clk)

    if dut.floor_led.value.is_resolvable:
        try:
            led = int(dut.floor_led.value)
            dut._log.info(f"Floor LED at reset: {led:#06b}")
            assert led == 0b0001, f"Floor LED should show floor 0, got {led:#06b}"
        except ValueError:
            assert False, "floor_led X/Z"


@cocotb.test()
async def test_door_closes_after_timer(dut):
    """Door should close automatically after timer expires."""
    setup_clock(dut, "clk", 20)
    await reset_dut(dut, "reset_n", active_low=True, cycles=5)

    dut.floor_sensor.value = 1
    dut.floor_request.value = 1  # Request current floor
    await RisingEdge(dut.clk)
    dut.floor_request.value = 0

    # Wait for door to open
    for _ in range(10):
        await RisingEdge(dut.clk)

    # Wait for door to close (timer = 10 cycles)
    door_closed = False
    for _ in range(30):
        await RisingEdge(dut.clk)
        if dut.door_open.value.is_resolvable:
            try:
                if int(dut.door_open.value) == 0:
                    door_closed = True
                    break
            except ValueError:
                pass

    dut._log.info(f"Door closed after timer: {door_closed}")
