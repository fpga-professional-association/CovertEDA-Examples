// =============================================================================
// Design      : Seven Segment Display Driver
// Module      : seven_segment
// Description : 4-digit 7-segment display driver with BCD input
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module seven_segment #(
    parameter REFRESH_BITS = 8  // 2^8 clocks per digit refresh
)(
    input   wire        clk,
    input   wire        rst_n,
    input   wire [15:0] bcd_in,     // 4 BCD digits (4 bits each)
    input   wire [3:0]  dp_in,      // Decimal point per digit
    output  reg  [6:0]  seg,        // 7-segment outputs (a-g, active low)
    output  reg  [3:0]  an,         // Digit anode select (active low)
    output  reg         dp          // Decimal point output
);

    reg [REFRESH_BITS-1:0] refresh_cnt;
    wire [1:0] digit_sel;
    reg [3:0]  current_bcd;

    assign digit_sel = refresh_cnt[REFRESH_BITS-1:REFRESH_BITS-2];

    // Refresh counter
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            refresh_cnt <= {REFRESH_BITS{1'b0}};
        else
            refresh_cnt <= refresh_cnt + 1'b1;
    end

    // Digit multiplexer
    always @(*) begin
        case (digit_sel)
            2'd0: begin current_bcd = bcd_in[3:0];   an = 4'b1110; dp = ~dp_in[0]; end
            2'd1: begin current_bcd = bcd_in[7:4];   an = 4'b1101; dp = ~dp_in[1]; end
            2'd2: begin current_bcd = bcd_in[11:8];  an = 4'b1011; dp = ~dp_in[2]; end
            2'd3: begin current_bcd = bcd_in[15:12]; an = 4'b0111; dp = ~dp_in[3]; end
            default: begin current_bcd = 4'd0; an = 4'b1111; dp = 1'b1; end
        endcase
    end

    // BCD to 7-segment decoder (active low: 0=on)
    always @(*) begin
        case (current_bcd)
            //                    gfedcba
            4'h0: seg = 7'b1000000;
            4'h1: seg = 7'b1111001;
            4'h2: seg = 7'b0100100;
            4'h3: seg = 7'b0110000;
            4'h4: seg = 7'b0011001;
            4'h5: seg = 7'b0010010;
            4'h6: seg = 7'b0000010;
            4'h7: seg = 7'b1111000;
            4'h8: seg = 7'b0000000;
            4'h9: seg = 7'b0010000;
            4'hA: seg = 7'b0001000;
            4'hB: seg = 7'b0000011;
            4'hC: seg = 7'b1000110;
            4'hD: seg = 7'b0100001;
            4'hE: seg = 7'b0000110;
            4'hF: seg = 7'b0001110;
            default: seg = 7'b1111111;
        endcase
    end

endmodule
