// =============================================================================
// Design      : Priority Encoder
// Module      : priority_encoder
// Description : 8-input priority encoder with valid output
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module priority_encoder (
    input   wire        clk,
    input   wire        rst_n,
    input   wire [7:0]  req,        // Request inputs (active high)
    output  reg  [2:0]  enc_out,    // Encoded output (highest priority index)
    output  reg         valid,      // At least one request active
    output  reg  [7:0]  grant       // One-hot grant for highest priority
);

    reg [2:0] enc_comb;
    reg       valid_comb;
    reg [7:0] grant_comb;

    // Combinational priority logic (bit 7 = highest priority)
    always @(*) begin
        enc_comb   = 3'd0;
        valid_comb = 1'b0;
        grant_comb = 8'd0;

        casez (req)
            8'b1???????: begin enc_comb = 3'd7; valid_comb = 1'b1; grant_comb = 8'b10000000; end
            8'b01??????: begin enc_comb = 3'd6; valid_comb = 1'b1; grant_comb = 8'b01000000; end
            8'b001?????: begin enc_comb = 3'd5; valid_comb = 1'b1; grant_comb = 8'b00100000; end
            8'b0001????: begin enc_comb = 3'd4; valid_comb = 1'b1; grant_comb = 8'b00010000; end
            8'b00001???: begin enc_comb = 3'd3; valid_comb = 1'b1; grant_comb = 8'b00001000; end
            8'b000001??: begin enc_comb = 3'd2; valid_comb = 1'b1; grant_comb = 8'b00000100; end
            8'b0000001?: begin enc_comb = 3'd1; valid_comb = 1'b1; grant_comb = 8'b00000010; end
            8'b00000001: begin enc_comb = 3'd0; valid_comb = 1'b1; grant_comb = 8'b00000001; end
            default:     begin enc_comb = 3'd0; valid_comb = 1'b0; grant_comb = 8'b00000000; end
        endcase
    end

    // Registered outputs
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            enc_out <= 3'd0;
            valid   <= 1'b0;
            grant   <= 8'd0;
        end else begin
            enc_out <= enc_comb;
            valid   <= valid_comb;
            grant   <= grant_comb;
        end
    end

endmodule
