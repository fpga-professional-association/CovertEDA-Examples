// Internet Checksum Calculator (RFC 1071)
// Device: Achronix Speedster7t AC7t1500
// One's complement sum of 16-bit words

module checksum (
    input         clk,
    input         rst_n,
    input  [15:0] data_in,
    input         data_valid,
    input         checksum_init,
    input         checksum_finish,
    output [15:0] checksum_out,
    output        checksum_valid
);

    reg [16:0] accum;  // 17-bit to capture carry
    reg [15:0] result;
    reg        valid_r;

    assign checksum_out   = result;
    assign checksum_valid = valid_r;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            accum   <= 17'd0;
            result  <= 16'd0;
            valid_r <= 1'b0;
        end else begin
            valid_r <= 1'b0;

            if (checksum_init) begin
                accum <= 17'd0;
            end else if (data_valid) begin
                // Add with carry wraparound (one's complement)
                accum <= {1'b0, accum[15:0]} + {1'b0, data_in} + {16'd0, accum[16]};
            end

            if (checksum_finish) begin
                // Fold final carry and complement
                result  <= ~(accum[15:0] + {15'd0, accum[16]});
                valid_r <= 1'b1;
            end
        end
    end

endmodule
