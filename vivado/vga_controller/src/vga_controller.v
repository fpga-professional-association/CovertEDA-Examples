// =============================================================================
// 640x480 VGA Timing Generator with Test Pattern
// Device: Xilinx Artix-7 XC7A35T
// Pixel clock: 25.175 MHz (assume provided externally)
// =============================================================================

module vga_controller (
    input  wire       clk,        // 25 MHz pixel clock
    input  wire       rst_n,
    output reg        hsync,
    output reg        vsync,
    output reg  [3:0] r_out,
    output reg  [3:0] g_out,
    output reg  [3:0] b_out,
    output wire       active
);

    // VGA 640x480 @ 60Hz timing parameters
    parameter H_VISIBLE   = 640;
    parameter H_FRONT     = 16;
    parameter H_SYNC      = 96;
    parameter H_BACK      = 48;
    parameter H_TOTAL     = 800;

    parameter V_VISIBLE   = 480;
    parameter V_FRONT     = 10;
    parameter V_SYNC      = 2;
    parameter V_BACK      = 33;
    parameter V_TOTAL     = 525;

    reg [9:0] h_cnt;
    reg [9:0] v_cnt;

    // Active video region
    wire h_active = (h_cnt < H_VISIBLE);
    wire v_active = (v_cnt < V_VISIBLE);
    assign active = h_active && v_active;

    // Horizontal counter
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            h_cnt <= 10'd0;
        end else begin
            if (h_cnt == H_TOTAL - 1)
                h_cnt <= 10'd0;
            else
                h_cnt <= h_cnt + 1'b1;
        end
    end

    // Vertical counter
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            v_cnt <= 10'd0;
        end else begin
            if (h_cnt == H_TOTAL - 1) begin
                if (v_cnt == V_TOTAL - 1)
                    v_cnt <= 10'd0;
                else
                    v_cnt <= v_cnt + 1'b1;
            end
        end
    end

    // Sync signals (active low)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            hsync <= 1'b1;
            vsync <= 1'b1;
        end else begin
            hsync <= ~((h_cnt >= H_VISIBLE + H_FRONT) &&
                       (h_cnt < H_VISIBLE + H_FRONT + H_SYNC));
            vsync <= ~((v_cnt >= V_VISIBLE + V_FRONT) &&
                       (v_cnt < V_VISIBLE + V_FRONT + V_SYNC));
        end
    end

    // Test pattern: color bars
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            r_out <= 4'd0;
            g_out <= 4'd0;
            b_out <= 4'd0;
        end else if (active) begin
            // 8 vertical color bars
            case (h_cnt[9:7])
                3'd0: begin r_out <= 4'hF; g_out <= 4'hF; b_out <= 4'hF; end  // White
                3'd1: begin r_out <= 4'hF; g_out <= 4'hF; b_out <= 4'h0; end  // Yellow
                3'd2: begin r_out <= 4'h0; g_out <= 4'hF; b_out <= 4'hF; end  // Cyan
                3'd3: begin r_out <= 4'h0; g_out <= 4'hF; b_out <= 4'h0; end  // Green
                3'd4: begin r_out <= 4'hF; g_out <= 4'h0; b_out <= 4'hF; end  // Magenta
                3'd5: begin r_out <= 4'hF; g_out <= 4'h0; b_out <= 4'h0; end  // Red
                3'd6: begin r_out <= 4'h0; g_out <= 4'h0; b_out <= 4'hF; end  // Blue
                3'd7: begin r_out <= 4'h0; g_out <= 4'h0; b_out <= 4'h0; end  // Black
            endcase
        end else begin
            r_out <= 4'd0;
            g_out <= 4'd0;
            b_out <= 4'd0;
        end
    end

endmodule
