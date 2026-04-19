// =============================================================================
// Design      : CORDIC Calculator
// Module      : cordic
// Description : 16-bit CORDIC sin/cos calculator (pipelined)
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module cordic #(
    parameter WIDTH  = 16,
    parameter STAGES = 12
)(
    input   wire                clk,
    input   wire                rst_n,
    input   wire                valid_in,
    input   wire [WIDTH-1:0]    angle_in,       // Input angle (0..65535 maps to 0..360 degrees)
    output  reg                 valid_out,
    output  reg  [WIDTH-1:0]    cos_out,
    output  reg  [WIDTH-1:0]    sin_out
);

    // CORDIC angle lookup table (atan(2^-i) scaled to 16-bit range)
    reg [WIDTH-1:0] atan_table [0:STAGES-1];

    initial begin
        atan_table[0]  = 16'd8192;    // atan(2^0)  = 45.0 deg
        atan_table[1]  = 16'd4836;    // atan(2^-1) = 26.57 deg
        atan_table[2]  = 16'd2555;    // atan(2^-2) = 14.04 deg
        atan_table[3]  = 16'd1297;    // atan(2^-3) = 7.13 deg
        atan_table[4]  = 16'd651;     // atan(2^-4) = 3.58 deg
        atan_table[5]  = 16'd326;     // atan(2^-5) = 1.79 deg
        atan_table[6]  = 16'd163;     // atan(2^-6) = 0.90 deg
        atan_table[7]  = 16'd81;      // atan(2^-7) = 0.45 deg
        atan_table[8]  = 16'd41;
        atan_table[9]  = 16'd20;
        atan_table[10] = 16'd10;
        atan_table[11] = 16'd5;
    end

    // Pipeline registers
    reg signed [WIDTH:0] x [0:STAGES];
    reg signed [WIDTH:0] y [0:STAGES];
    reg signed [WIDTH:0] z [0:STAGES];
    reg                  v [0:STAGES];

    // CORDIC gain constant K ~ 0.6073 * 2^15 = 19898
    localparam signed [WIDTH:0] K_INIT = 17'sd19898;

    integer i;

    // Stage 0: Initialize
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x[0] <= 0;
            y[0] <= 0;
            z[0] <= 0;
            v[0] <= 0;
        end else begin
            x[0] <= K_INIT;
            y[0] <= 0;
            z[0] <= $signed({1'b0, angle_in});
            v[0] <= valid_in;
        end
    end

    // Pipeline stages
    genvar s;
    generate
        for (s = 0; s < STAGES; s = s + 1) begin : cordic_stage
            always @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    x[s+1] <= 0;
                    y[s+1] <= 0;
                    z[s+1] <= 0;
                    v[s+1] <= 0;
                end else begin
                    if (z[s] >= 0) begin
                        x[s+1] <= x[s] - (y[s] >>> s);
                        y[s+1] <= y[s] + (x[s] >>> s);
                        z[s+1] <= z[s] - $signed({1'b0, atan_table[s]});
                    end else begin
                        x[s+1] <= x[s] + (y[s] >>> s);
                        y[s+1] <= y[s] - (x[s] >>> s);
                        z[s+1] <= z[s] + $signed({1'b0, atan_table[s]});
                    end
                    v[s+1] <= v[s];
                end
            end
        end
    endgenerate

    // Output
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cos_out   <= 0;
            sin_out   <= 0;
            valid_out <= 0;
        end else begin
            cos_out   <= x[STAGES][WIDTH-1:0];
            sin_out   <= y[STAGES][WIDTH-1:0];
            valid_out <= v[STAGES];
        end
    end

endmodule
