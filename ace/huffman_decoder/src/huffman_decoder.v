// Static Huffman Decoder
// Device: Achronix Speedster7t AC7t1500
// Decodes variable-length codes using a hardcoded table

module huffman_decoder (
    input        clk,
    input        rst_n,
    input        bit_in,
    input        bit_valid,
    output [7:0] symbol_out,
    output       symbol_valid,
    output       error
);

    reg [3:0] code_reg;
    reg [2:0] bit_cnt;
    reg [7:0] sym_r;
    reg       sym_valid_r;
    reg       error_r;

    assign symbol_out   = sym_r;
    assign symbol_valid = sym_valid_r;
    assign error        = error_r;

    // Hardcoded Huffman table (simplified example):
    // 0        -> 'A' (0x41)
    // 10       -> 'B' (0x42)
    // 110      -> 'C' (0x43)
    // 1110     -> 'D' (0x44)
    // 11110    -> 'E' (0x45)
    // 11111    -> 'F' (0x46)

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            code_reg    <= 4'd0;
            bit_cnt     <= 3'd0;
            sym_r       <= 8'd0;
            sym_valid_r <= 1'b0;
            error_r     <= 1'b0;
        end else begin
            sym_valid_r <= 1'b0;
            error_r     <= 1'b0;

            if (bit_valid) begin
                code_reg <= {code_reg[2:0], bit_in};
                bit_cnt  <= bit_cnt + 1'b1;

                case (bit_cnt)
                    3'd0: begin
                        if (bit_in == 1'b0) begin
                            sym_r       <= 8'h41; // 'A'
                            sym_valid_r <= 1'b1;
                            bit_cnt     <= 3'd0;
                            code_reg    <= 4'd0;
                        end
                    end
                    3'd1: begin
                        if (code_reg[0] == 1'b1 && bit_in == 1'b0) begin
                            sym_r       <= 8'h42; // 'B'
                            sym_valid_r <= 1'b1;
                            bit_cnt     <= 3'd0;
                            code_reg    <= 4'd0;
                        end
                    end
                    3'd2: begin
                        if (code_reg[1:0] == 2'b11 && bit_in == 1'b0) begin
                            sym_r       <= 8'h43; // 'C'
                            sym_valid_r <= 1'b1;
                            bit_cnt     <= 3'd0;
                            code_reg    <= 4'd0;
                        end
                    end
                    3'd3: begin
                        if (code_reg[2:0] == 3'b111 && bit_in == 1'b0) begin
                            sym_r       <= 8'h44; // 'D'
                            sym_valid_r <= 1'b1;
                            bit_cnt     <= 3'd0;
                            code_reg    <= 4'd0;
                        end
                    end
                    3'd4: begin
                        if (code_reg[3:0] == 4'b1111) begin
                            if (bit_in == 1'b0)
                                sym_r <= 8'h45; // 'E'
                            else
                                sym_r <= 8'h46; // 'F'
                            sym_valid_r <= 1'b1;
                            bit_cnt     <= 3'd0;
                            code_reg    <= 4'd0;
                        end else begin
                            error_r  <= 1'b1;
                            bit_cnt  <= 3'd0;
                            code_reg <= 4'd0;
                        end
                    end
                    default: begin
                        error_r  <= 1'b1;
                        bit_cnt  <= 3'd0;
                        code_reg <= 4'd0;
                    end
                endcase
            end
        end
    end

endmodule
