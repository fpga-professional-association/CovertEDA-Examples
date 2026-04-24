// Video Test Pattern Generator - Color bars and checkerboard
// Target: LFE5U-25F (ECP5)
// Generates 640x480 pixel patterns

module pattern_generator (
    input        clk,
    input        reset_n,
    input  [1:0] pattern_sel,   // 0=bars, 1=checker, 2=gradient, 3=solid
    input  [9:0] pixel_x,
    input  [9:0] pixel_y,
    input        pixel_valid,
    output reg [7:0] r_out,
    output reg [7:0] g_out,
    output reg [7:0] b_out,
    output reg       data_valid
);

    localparam WIDTH  = 640;
    localparam HEIGHT = 480;

    wire [2:0] bar_index;
    assign bar_index = pixel_x[9:7];  // divide x by 80 (8 bars)
    wire chk_pattern;
    assign chk_pattern = pixel_x[5] ^ pixel_y[5]; // 32-pixel checkerboard

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            r_out      <= 8'd0;
            g_out      <= 8'd0;
            b_out      <= 8'd0;
            data_valid <= 1'b0;
        end else begin
            data_valid <= pixel_valid;
            if (pixel_valid) begin
                case (pattern_sel)
                    2'b00: begin // Color bars (8 vertical bars)
                        r_out <= bar_index[0] ? 8'd255 : 8'd0;
                        g_out <= bar_index[1] ? 8'd255 : 8'd0;
                        b_out <= bar_index[2] ? 8'd255 : 8'd0;
                    end
                    2'b01: begin // Checkerboard
                        r_out <= chk_pattern ? 8'd255 : 8'd0;
                        g_out <= chk_pattern ? 8'd255 : 8'd0;
                        b_out <= chk_pattern ? 8'd255 : 8'd0;
                    end
                    2'b10: begin // Horizontal gradient
                        r_out <= pixel_x[9:2];
                        g_out <= pixel_x[9:2];
                        b_out <= pixel_x[9:2];
                    end
                    2'b11: begin // Solid white
                        r_out <= 8'd255;
                        g_out <= 8'd255;
                        b_out <= 8'd255;
                    end
                endcase
            end
        end
    end

endmodule
