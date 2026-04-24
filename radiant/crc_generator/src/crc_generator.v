// =============================================================================
// Design      : CRC Generator
// Module      : crc_generator
// Description : CRC-32 generator for 8-bit input data
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module crc_generator (
    input   wire        clk,
    input   wire        rst_n,
    input   wire        valid,          // Input data valid strobe
    input   wire [7:0]  data_in,        // 8-bit data input
    input   wire        init,           // Initialize CRC to all 1s
    output  reg  [31:0] crc_out,        // Current CRC value
    output  reg         crc_valid       // CRC output valid (pulses after valid)
);

    // CRC-32 polynomial: 0x04C11DB7
    // Bit-serial implementation for 8 bits at a time

    reg [31:0] crc_next;
    integer i;

    always @(*) begin
        crc_next = crc_out;
        for (i = 0; i < 8; i = i + 1) begin
            if (crc_next[31] ^ data_in[7-i]) begin
                crc_next = {crc_next[30:0], 1'b0} ^ 32'h04C11DB7;
            end else begin
                crc_next = {crc_next[30:0], 1'b0};
            end
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            crc_out   <= 32'hFFFFFFFF;
            crc_valid <= 1'b0;
        end else if (init) begin
            crc_out   <= 32'hFFFFFFFF;
            crc_valid <= 1'b0;
        end else if (valid) begin
            crc_out   <= crc_next;
            crc_valid <= 1'b1;
        end else begin
            crc_valid <= 1'b0;
        end
    end

endmodule
