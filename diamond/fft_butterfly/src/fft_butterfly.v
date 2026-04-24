// Radix-2 FFT Butterfly - 16-bit complex arithmetic
// Target: LFE5U-45F (ECP5)
// Computes: A_out = A_in + W*B_in, B_out = A_in - W*B_in

module fft_butterfly (
    input         clk,
    input         reset_n,
    input         valid_in,
    input  signed [15:0] ar_in,   // A real
    input  signed [15:0] ai_in,   // A imaginary
    input  signed [15:0] br_in,   // B real
    input  signed [15:0] bi_in,   // B imaginary
    input  signed [15:0] wr_in,   // Twiddle real
    input  signed [15:0] wi_in,   // Twiddle imaginary
    output reg signed [15:0] ar_out,
    output reg signed [15:0] ai_out,
    output reg signed [15:0] br_out,
    output reg signed [15:0] bi_out,
    output reg        valid_out
);

    // Pipeline stage 1: multiply
    reg signed [31:0] mult_rr, mult_ri, mult_ir, mult_ii;
    reg signed [15:0] ar_d1, ai_d1;
    reg valid_d1;

    // Pipeline stage 2: add/sub
    reg signed [31:0] wb_real, wb_imag;
    reg signed [15:0] ar_d2, ai_d2;
    reg valid_d2;

    // Stage 1: Complex multiply W * B
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            mult_rr <= 0; mult_ri <= 0;
            mult_ir <= 0; mult_ii <= 0;
            ar_d1 <= 0; ai_d1 <= 0;
            valid_d1 <= 0;
        end else begin
            valid_d1 <= valid_in;
            ar_d1 <= ar_in;
            ai_d1 <= ai_in;
            mult_rr <= wr_in * br_in;
            mult_ii <= wi_in * bi_in;
            mult_ri <= wr_in * bi_in;
            mult_ir <= wi_in * br_in;
        end
    end

    // Stage 2: Combine multiply results
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            wb_real <= 0; wb_imag <= 0;
            ar_d2 <= 0; ai_d2 <= 0;
            valid_d2 <= 0;
        end else begin
            valid_d2 <= valid_d1;
            ar_d2 <= ar_d1;
            ai_d2 <= ai_d1;
            wb_real <= mult_rr - mult_ii;
            wb_imag <= mult_ri + mult_ir;
        end
    end

    // Stage 3: Butterfly add/subtract with truncation
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            ar_out <= 0; ai_out <= 0;
            br_out <= 0; bi_out <= 0;
            valid_out <= 0;
        end else begin
            valid_out <= valid_d2;
            // Truncate from Q15 fixed-point: take bits [30:15]
            ar_out <= ar_d2 + wb_real[30:15];
            ai_out <= ai_d2 + wb_imag[30:15];
            br_out <= ar_d2 - wb_real[30:15];
            bi_out <= ai_d2 - wb_imag[30:15];
        end
    end

endmodule
