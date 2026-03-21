// FIR Decimation Filter
// Polyphase FIR for final decimation stage

module fir_decimate (
    input  clk,
    input  rst,
    input  [31:0] i_data_in,
    input  [31:0] q_data_in,
    input  data_valid_in,
    output [31:0] i_data_out,
    output [31:0] q_data_out,
    output data_valid_out
);

    // 32-tap FIR filter coefficients (symmetrical)
    localparam [15:0] h0  = 16'h0001;
    localparam [15:0] h1  = 16'h0003;
    localparam [15:0] h2  = 16'h0007;
    localparam [15:0] h3  = 16'h000F;
    localparam [15:0] h4  = 16'h001F;
    localparam [15:0] h5  = 16'h003F;
    localparam [15:0] h6  = 16'h007E;
    localparam [15:0] h7  = 16'h00FD;
    localparam [15:0] h8  = 16'h01FA;
    localparam [15:0] h9  = 16'h03F4;
    localparam [15:0] h10 = 16'h07E7;
    localparam [15:0] h11 = 16'h0FCE;
    localparam [15:0] h12 = 16'h1F9C;
    localparam [15:0] h13 = 16'h3F38;
    localparam [15:0] h14 = 16'h7E6F;
    localparam [15:0] h15 = 16'h7FFF;  // Middle tap (normalization)

    // Shift registers for input samples
    reg [31:0] i_sr [0:31];
    reg [31:0] q_sr [0:31];

    // Output accumulators
    reg [47:0] i_acc;
    reg [47:0] q_acc;
    reg output_valid_r;

    integer i, j;

    // Shift register and multiply-accumulate
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            for (i = 0; i < 32; i = i + 1) begin
                i_sr[i] <= 32'b0;
                q_sr[i] <= 32'b0;
            end
            i_acc <= 48'b0;
            q_acc <= 48'b0;
            output_valid_r <= 1'b0;
        end else if (data_valid_in) begin
            // Shift inputs
            for (i = 31; i > 0; i = i - 1) begin
                i_sr[i] <= i_sr[i-1];
                q_sr[i] <= q_sr[i-1];
            end
            i_sr[0] <= i_data_in;
            q_sr[0] <= q_data_in;

            // Multiply-accumulate with FIR coefficients
            i_acc <= 48'b0;
            q_acc <= 48'b0;

            // Unroll multiply-accumulate loop
            i_acc <= i_acc + (i_sr[0] * h0) + (i_sr[1] * h1) + (i_sr[2] * h2) + (i_sr[3] * h3);
            q_acc <= q_acc + (q_sr[0] * h0) + (q_sr[1] * h1) + (q_sr[2] * h2) + (q_sr[3] * h3);

            i_acc <= i_acc + (i_sr[4] * h4) + (i_sr[5] * h5) + (i_sr[6] * h6) + (i_sr[7] * h7);
            q_acc <= q_acc + (q_sr[4] * h4) + (q_sr[5] * h5) + (q_sr[6] * h6) + (q_sr[7] * h7);

            i_acc <= i_acc + (i_sr[8] * h8) + (i_sr[9] * h9) + (i_sr[10] * h10) + (i_sr[11] * h11);
            q_acc <= q_acc + (q_sr[8] * h8) + (q_sr[9] * h9) + (q_sr[10] * h10) + (q_sr[11] * h11);

            i_acc <= i_acc + (i_sr[12] * h12) + (i_sr[13] * h13) + (i_sr[14] * h14) + (i_sr[15] * h15);
            q_acc <= q_acc + (q_sr[12] * h12) + (q_sr[13] * h13) + (q_sr[14] * h14) + (q_sr[15] * h15);

            output_valid_r <= 1'b1;
        end else begin
            output_valid_r <= 1'b0;
        end
    end

    assign i_data_out = i_acc[47:16];  // Truncate to 32 bits
    assign q_data_out = q_acc[47:16];
    assign data_valid_out = output_valid_r;

endmodule
