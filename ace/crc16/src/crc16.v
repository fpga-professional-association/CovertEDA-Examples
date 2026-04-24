// CRC-16/CCITT Generator
// Device: Achronix Speedster7t AC7t1500
// Polynomial: x^16 + x^12 + x^5 + 1 (0x1021)

module crc16 (
    input         clk,
    input         rst_n,
    input  [7:0]  data_in,
    input         data_valid,
    input         crc_init,
    output [15:0] crc_out,
    output        crc_valid
);

    reg [15:0] crc_reg;
    reg        valid_r;

    assign crc_out   = crc_reg;
    assign crc_valid = valid_r;

    // Byte-wise CRC computation
    function [15:0] crc_byte;
        input [15:0] crc;
        input [7:0]  data;
        reg [15:0] c;
        integer i;
        begin
            c = crc;
            for (i = 7; i >= 0; i = i - 1) begin
                if (c[15] ^ data[i])
                    c = {c[14:0], 1'b0} ^ 16'h1021;
                else
                    c = {c[14:0], 1'b0};
            end
            crc_byte = c;
        end
    endfunction

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            crc_reg <= 16'hFFFF;
            valid_r <= 1'b0;
        end else begin
            valid_r <= 1'b0;
            if (crc_init) begin
                crc_reg <= 16'hFFFF;
            end else if (data_valid) begin
                crc_reg <= crc_byte(crc_reg, data_in);
                valid_r <= 1'b1;
            end
        end
    end

endmodule
