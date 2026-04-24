// =============================================================================
// Design      : Gray Code Counter
// Module      : gray_counter
// Description : 8-bit Gray code counter with binary output
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module gray_counter (
    input   wire        clk,
    input   wire        rst_n,
    input   wire        enable,
    output  reg  [7:0]  gray_out,     // Gray code output
    output  wire [7:0]  binary_out    // Binary conversion of gray output
);

    reg [7:0] binary_cnt;

    // Binary to Gray conversion
    wire [7:0] gray_next;
    assign gray_next = binary_cnt ^ (binary_cnt >> 1);

    // Gray to Binary conversion for output
    assign binary_out[7] = gray_out[7];
    assign binary_out[6] = gray_out[7] ^ gray_out[6];
    assign binary_out[5] = binary_out[6] ^ gray_out[5];
    assign binary_out[4] = binary_out[5] ^ gray_out[4];
    assign binary_out[3] = binary_out[4] ^ gray_out[3];
    assign binary_out[2] = binary_out[3] ^ gray_out[2];
    assign binary_out[1] = binary_out[2] ^ gray_out[1];
    assign binary_out[0] = binary_out[1] ^ gray_out[0];

    // Binary counter
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            binary_cnt <= 8'd0;
        end else if (enable) begin
            binary_cnt <= binary_cnt + 8'd1;
        end
    end

    // Gray code register
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            gray_out <= 8'd0;
        end else if (enable) begin
            gray_out <= gray_next;
        end
    end

endmodule
