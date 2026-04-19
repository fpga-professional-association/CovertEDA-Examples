// PS/2 Keyboard Interface - Scancode receiver
// Target: MPF100T (PolarFire)
// Receives 11-bit PS/2 frames: start(0), 8 data, parity, stop(1)

module ps2_keyboard (
    input        clk,
    input        reset_n,
    input        ps2_clk,
    input        ps2_data,
    output reg [7:0] scancode,
    output reg       scancode_valid,
    output reg       parity_error
);

    reg [3:0]  bit_cnt;
    reg [10:0] shift_reg;
    reg        ps2_clk_d1, ps2_clk_d2;
    wire       ps2_clk_fall;

    // Synchronize and detect falling edge of PS/2 clock
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            ps2_clk_d1 <= 1'b1;
            ps2_clk_d2 <= 1'b1;
        end else begin
            ps2_clk_d1 <= ps2_clk;
            ps2_clk_d2 <= ps2_clk_d1;
        end
    end

    assign ps2_clk_fall = ps2_clk_d2 & ~ps2_clk_d1;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            bit_cnt        <= 4'd0;
            shift_reg      <= 11'd0;
            scancode       <= 8'd0;
            scancode_valid <= 1'b0;
            parity_error   <= 1'b0;
        end else begin
            scancode_valid <= 1'b0;
            parity_error   <= 1'b0;

            if (ps2_clk_fall) begin
                shift_reg <= {ps2_data, shift_reg[10:1]};
                bit_cnt   <= bit_cnt + 1;

                if (bit_cnt == 4'd10) begin
                    bit_cnt <= 0;
                    // Frame: [0]=start, [8:1]=data, [9]=parity, [10]=stop
                    if (shift_reg[0] == 1'b0 && ps2_data == 1'b1) begin
                        // Valid frame markers
                        scancode <= shift_reg[8:1];
                        // Check odd parity
                        if (^shift_reg[9:1] == 1'b1)
                            scancode_valid <= 1'b1;
                        else
                            parity_error <= 1'b1;
                    end
                end
            end
        end
    end

endmodule
