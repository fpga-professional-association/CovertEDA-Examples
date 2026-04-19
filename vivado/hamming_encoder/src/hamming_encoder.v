// =============================================================================
// (8,4) Hamming Encoder/Decoder with Single-Error Correction
// Device: Xilinx Artix-7 XC7A35T
// Encodes 4 data bits into 8 bits (4 data + 3 parity + 1 overall parity)
// =============================================================================

module hamming_encoder (
    input  wire       clk,
    input  wire       rst_n,

    // Encoder
    input  wire [3:0] enc_data_in,
    input  wire       enc_valid,
    output reg  [7:0] enc_data_out,
    output reg        enc_done,

    // Decoder
    input  wire [7:0] dec_data_in,
    input  wire       dec_valid,
    output reg  [3:0] dec_data_out,
    output reg        dec_done,
    output reg        dec_error,      // Single-bit error detected & corrected
    output reg        dec_uncorrectable  // Double-bit error detected
);

    // === ENCODER ===
    // Data bits: d3, d2, d1, d0
    // Codeword: [p0, p1, d0, p2, d1, d2, d3, p_overall]
    // p1 covers positions with bit 0 set: 1,3,5,7
    // p2 covers positions with bit 1 set: 2,3,6,7
    // p4 covers positions with bit 2 set: 4,5,6,7
    // p0 (overall parity) covers all

    wire p1_enc, p2_enc, p4_enc, p0_enc;
    assign p1_enc = enc_data_in[0] ^ enc_data_in[1] ^ enc_data_in[3];
    assign p2_enc = enc_data_in[0] ^ enc_data_in[2] ^ enc_data_in[3];
    assign p4_enc = enc_data_in[1] ^ enc_data_in[2] ^ enc_data_in[3];
    assign p0_enc = p1_enc ^ p2_enc ^ enc_data_in[0] ^ p4_enc ^
                    enc_data_in[1] ^ enc_data_in[2] ^ enc_data_in[3];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            enc_data_out <= 8'd0;
            enc_done     <= 1'b0;
        end else begin
            enc_done <= 1'b0;
            if (enc_valid) begin
                enc_data_out <= {p0_enc, enc_data_in[3], enc_data_in[2],
                                 enc_data_in[1], p4_enc, enc_data_in[0],
                                 p2_enc, p1_enc};
                enc_done <= 1'b1;
            end
        end
    end

    // === DECODER ===
    // Recalculate syndrome
    wire [2:0] syndrome;
    wire s1, s2, s4;

    // Positions: 0:p1, 1:p2, 2:d0, 3:p4, 4:d1, 5:d2, 6:d3, 7:p0
    assign s1 = dec_data_in[0] ^ dec_data_in[2] ^ dec_data_in[4] ^ dec_data_in[6];
    assign s2 = dec_data_in[1] ^ dec_data_in[2] ^ dec_data_in[5] ^ dec_data_in[6];
    assign s4 = dec_data_in[3] ^ dec_data_in[4] ^ dec_data_in[5] ^ dec_data_in[6];
    assign syndrome = {s4, s2, s1};

    wire overall_parity;
    assign overall_parity = ^dec_data_in;  // XOR of all 8 bits

    // Corrected codeword
    reg [7:0] corrected;

    always @(*) begin
        corrected = dec_data_in;
        if (syndrome != 3'd0 && overall_parity) begin
            // Single-bit error: flip the error position
            corrected[syndrome - 1] = ~dec_data_in[syndrome - 1];
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            dec_data_out      <= 4'd0;
            dec_done          <= 1'b0;
            dec_error         <= 1'b0;
            dec_uncorrectable <= 1'b0;
        end else begin
            dec_done          <= 1'b0;
            dec_error         <= 1'b0;
            dec_uncorrectable <= 1'b0;

            if (dec_valid) begin
                // Extract data bits from corrected codeword
                dec_data_out <= {corrected[6], corrected[5], corrected[4], corrected[2]};
                dec_done     <= 1'b1;

                if (syndrome != 3'd0) begin
                    if (overall_parity) begin
                        dec_error <= 1'b1;  // Single-bit error, corrected
                    end else begin
                        dec_uncorrectable <= 1'b1;  // Double-bit error
                    end
                end
            end
        end
    end

endmodule
