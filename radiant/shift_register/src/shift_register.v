// =============================================================================
// Design      : Shift Register
// Module      : shift_register
// Description : 32-bit shift register with serial in/out, parallel load
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module shift_register (
    input   wire        clk,
    input   wire        rst_n,
    input   wire        serial_in,
    input   wire        shift_en,       // Shift enable
    input   wire        load,           // Parallel load strobe
    input   wire [1:0]  dir,            // 00=left, 01=right, 10=rotate left, 11=rotate right
    input   wire [31:0] parallel_in,    // Parallel load data
    output  wire        serial_out,
    output  reg  [31:0] data_out
);

    assign serial_out = (dir[0]) ? data_out[0] : data_out[31];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            data_out <= 32'd0;
        end else if (load) begin
            data_out <= parallel_in;
        end else if (shift_en) begin
            case (dir)
                2'b00: data_out <= {data_out[30:0], serial_in};          // Shift left
                2'b01: data_out <= {serial_in, data_out[31:1]};          // Shift right
                2'b10: data_out <= {data_out[30:0], data_out[31]};       // Rotate left
                2'b11: data_out <= {data_out[0], data_out[31:1]};        // Rotate right
                default: data_out <= data_out;
            endcase
        end
    end

endmodule
