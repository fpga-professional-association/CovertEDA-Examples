// ASCII to Morse Code Encoder with LED/Audio Output
// Device: iCE40UP5K
// Converts 8-bit ASCII to Morse dot/dash sequences

module morse_encoder (
    input        clk,
    input        rst_n,
    input  [7:0] char_in,
    input        char_valid,
    output       morse_out,
    output       busy
);

    // Timing: dot=1 unit, dash=3 units, inter-element gap=1 unit
    parameter UNIT_CYCLES = 12000; // ~1ms at 12 MHz

    reg [3:0] pattern;    // up to 4 elements (dot=0, dash=1)
    reg [2:0] length;     // number of elements
    reg [2:0] elem_idx;
    reg [15:0] timer;
    reg [1:0] state;
    reg       output_r;

    localparam S_IDLE  = 2'd0;
    localparam S_ON    = 2'd1;
    localparam S_GAP   = 2'd2;

    assign morse_out = output_r;
    assign busy      = (state != S_IDLE);

    // Simplified Morse lookup (A-H only for compact design)
    // A: .- (01) len=2, B: -... (1000) len=4, C: -.-. (1010) len=4
    // D: -.. (100) len=3, E: . (0) len=1, F: ..-. (0010) len=4
    // G: --. (110) len=3, H: .... (0000) len=4
    always @(*) begin
        case (char_in & 8'hDF)  // Upper-case mask
            8'h41: begin pattern = 4'b0100; length = 3'd2; end // A
            8'h42: begin pattern = 4'b1000; length = 3'd4; end // B
            8'h43: begin pattern = 4'b1010; length = 3'd4; end // C
            8'h44: begin pattern = 4'b1000; length = 3'd3; end // D
            8'h45: begin pattern = 4'b0000; length = 3'd1; end // E
            8'h46: begin pattern = 4'b0010; length = 3'd4; end // F
            8'h47: begin pattern = 4'b1100; length = 3'd3; end // G
            8'h48: begin pattern = 4'b0000; length = 3'd4; end // H
            default: begin pattern = 4'b0000; length = 3'd0; end
        endcase
    end

    reg [2:0] cur_len;
    reg [3:0] cur_pat;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state    <= S_IDLE;
            elem_idx <= 3'd0;
            timer    <= 16'd0;
            output_r <= 1'b0;
            cur_len  <= 3'd0;
            cur_pat  <= 4'd0;
        end else begin
            case (state)
                S_IDLE: begin
                    output_r <= 1'b0;
                    if (char_valid && length > 0) begin
                        cur_pat  <= pattern;
                        cur_len  <= length;
                        elem_idx <= 3'd0;
                        timer    <= 16'd0;
                        state    <= S_ON;
                        output_r <= 1'b1;
                    end
                end
                S_ON: begin
                    output_r <= 1'b1;
                    timer    <= timer + 1'b1;
                    // Dot=1 unit, Dash=3 units
                    if (cur_pat[cur_len - 1 - elem_idx] == 1'b1) begin
                        if (timer >= UNIT_CYCLES * 3 - 1) begin
                            timer    <= 16'd0;
                            output_r <= 1'b0;
                            state    <= S_GAP;
                        end
                    end else begin
                        if (timer >= UNIT_CYCLES - 1) begin
                            timer    <= 16'd0;
                            output_r <= 1'b0;
                            state    <= S_GAP;
                        end
                    end
                end
                S_GAP: begin
                    output_r <= 1'b0;
                    timer    <= timer + 1'b1;
                    if (timer >= UNIT_CYCLES - 1) begin
                        timer    <= 16'd0;
                        elem_idx <= elem_idx + 1'b1;
                        if (elem_idx + 1 >= cur_len)
                            state <= S_IDLE;
                        else
                            state <= S_ON;
                    end
                end
            endcase
        end
    end

endmodule
