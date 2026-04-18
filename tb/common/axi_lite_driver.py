"""AXI-Lite read/write driver for cocotb."""

import cocotb
from cocotb.triggers import RisingEdge


async def axi_write(dut, addr, data, prefix="axi", clk_name="clk"):
    """Perform an AXI-Lite write transaction.

    Args:
        dut: Device under test.
        addr: Write address.
        data: Write data (32-bit).
        prefix: AXI signal prefix (e.g., 'axi', 's_axi').
        clk_name: Clock signal name.
    """
    clk = getattr(dut, clk_name)

    # Write address channel
    getattr(dut, f"{prefix}_awaddr").value = addr
    getattr(dut, f"{prefix}_awvalid").value = 1
    # Write data channel
    getattr(dut, f"{prefix}_wdata").value = data
    getattr(dut, f"{prefix}_wstrb").value = 0xF
    getattr(dut, f"{prefix}_wvalid").value = 1
    # Ready to accept response
    getattr(dut, f"{prefix}_bready").value = 1

    # Wait for both address and data handshakes
    aw_done = False
    w_done = False
    for _ in range(100):
        await RisingEdge(clk)
        if int(getattr(dut, f"{prefix}_awready").value) == 1:
            aw_done = True
        if int(getattr(dut, f"{prefix}_wready").value) == 1:
            w_done = True
        if aw_done and w_done:
            break

    getattr(dut, f"{prefix}_awvalid").value = 0
    getattr(dut, f"{prefix}_wvalid").value = 0

    # Wait for write response
    for _ in range(100):
        await RisingEdge(clk)
        if int(getattr(dut, f"{prefix}_bvalid").value) == 1:
            break
    getattr(dut, f"{prefix}_bready").value = 0


async def axi_read(dut, addr, prefix="axi", clk_name="clk"):
    """Perform an AXI-Lite read transaction. Returns the read data.

    Args:
        dut: Device under test.
        addr: Read address.
        prefix: AXI signal prefix.
        clk_name: Clock signal name.

    Returns:
        32-bit read data value.
    """
    clk = getattr(dut, clk_name)

    getattr(dut, f"{prefix}_araddr").value = addr
    getattr(dut, f"{prefix}_arvalid").value = 1
    getattr(dut, f"{prefix}_rready").value = 1

    for _ in range(100):
        await RisingEdge(clk)
        if int(getattr(dut, f"{prefix}_arready").value) == 1:
            break
    getattr(dut, f"{prefix}_arvalid").value = 0

    for _ in range(100):
        await RisingEdge(clk)
        if int(getattr(dut, f"{prefix}_rvalid").value) == 1:
            break

    result = int(getattr(dut, f"{prefix}_rdata").value)
    getattr(dut, f"{prefix}_rready").value = 0
    return result
