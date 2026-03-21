// CRC-32 Generator/Checker for Ethernet

module crc32 (
    input  clk,
    input  rst,
    input  [7:0] data_in,
    input  data_valid,
    output [31:0] crc_out,
    output crc_error
);

    reg [31:0] crc_reg;
    wire [31:0] crc_next;
    integer i;

    // CRC polynomial: x^32 + x^26 + x^23 + x^22 + x^16 + x^12 + x^11 + x^10 + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1
    // CRC-32/MPEG-2

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            crc_reg <= 32'hFFFFFFFF;
        end else if (data_valid) begin
            crc_reg <= crc_next;
        end
    end

    // Combinatorial CRC computation
    assign crc_next = compute_crc(crc_reg, data_in);

    function [31:0] compute_crc (input [31:0] crc_in, input [7:0] data);
        reg [31:0] temp;
        integer j;
        begin
            temp = crc_in ^ {24'b0, data};
            for (j = 0; j < 8; j = j + 1) begin
                if (temp[0]) begin
                    temp = (temp >> 1) ^ 32'hEDB88320;
                end else begin
                    temp = temp >> 1;
                end
            end
            compute_crc = temp;
        end
    endfunction

    assign crc_out = crc_reg;
    assign crc_error = (crc_reg != 32'hC704DD7B); // Magic number for valid CRC

endmodule
