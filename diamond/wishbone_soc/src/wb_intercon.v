// Wishbone Bus Interconnect Module
// Provides address decoding and mux logic for multiple slaves

module wb_intercon (
    // Master interface
    input [31:0] m_addr,
    input [31:0] m_data_wr,
    output [31:0] m_data_rd,
    input [3:0] m_sel,
    input m_we,
    input m_cyc,
    input m_stb,
    output m_ack,

    // Slave 0: SRAM
    output s0_stb,
    input s0_ack,
    output [11:0] s0_addr,
    input [31:0] s0_data_rd,

    // Slave 1: GPIO
    output s1_stb,
    input s1_ack,
    output [3:0] s1_addr,
    input [31:0] s1_data_rd,

    // Slave 2: Timer
    output s2_stb,
    input s2_ack,
    output [3:0] s2_addr,
    input [31:0] s2_data_rd,

    // Global signals
    input clk,
    input reset_n
);

    // Address decoding
    wire [3:0] slave_sel;
    assign slave_sel[0] = (m_addr[31:20] == 12'h000);  // SRAM
    assign slave_sel[1] = (m_addr[31:20] == 12'h100);  // GPIO
    assign slave_sel[2] = (m_addr[31:20] == 12'h200);  // Timer
    assign slave_sel[3] = 1'b0;

    // Slave selection and strobes
    assign s0_stb = m_cyc && m_stb && slave_sel[0];
    assign s1_stb = m_cyc && m_stb && slave_sel[1];
    assign s2_stb = m_cyc && m_stb && slave_sel[2];

    // Address assignments
    assign s0_addr = m_addr[11:0];
    assign s1_addr = m_addr[3:0];
    assign s2_addr = m_addr[3:0];

    // Acknowledge multiplexer
    assign m_ack = (slave_sel[0] && s0_ack) ||
                   (slave_sel[1] && s1_ack) ||
                   (slave_sel[2] && s2_ack);

    // Data multiplexer
    assign m_data_rd = ({32{slave_sel[0]}} & s0_data_rd) |
                       ({32{slave_sel[1]}} & s1_data_rd) |
                       ({32{slave_sel[2]}} & s2_data_rd);

endmodule
