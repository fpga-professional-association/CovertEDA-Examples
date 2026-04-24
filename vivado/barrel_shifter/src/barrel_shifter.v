// =============================================================================
// 32-bit Barrel Shifter with Left/Right/Arithmetic Modes
// Device: Xilinx Artix-7 XC7A35T
// =============================================================================

module barrel_shifter (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] data_in,
    input  wire [4:0]  shift_amt,
    input  wire [1:0]  mode,       // 00=left, 01=right logical, 10=right arithmetic, 11=rotate left
    input  wire        valid_in,
    output reg  [31:0] data_out,
    output reg         valid_out
);

    reg [31:0] shifted;

    always @(*) begin
        case (mode)
            2'b00: shifted = data_in << shift_amt;                          // Left shift
            2'b01: shifted = data_in >> shift_amt;                          // Right logical
            2'b10: shifted = $signed(data_in) >>> shift_amt;                // Right arithmetic
            2'b11: shifted = (data_in << shift_amt) |                      // Rotate left
                             (data_in >> (32 - shift_amt));
            default: shifted = data_in;
        endcase
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            data_out  <= 32'd0;
            valid_out <= 1'b0;
        end else begin
            data_out  <= shifted;
            valid_out <= valid_in;
        end
    end

endmodule
