// Pixel Counter - Generates pixel coordinates and sync signals
// For 1920x1080@60Hz video format

module pixel_counter (
    input clk,
    input reset_n,
    input hsync,
    input vsync,

    output reg [10:0] h_count,
    output reg [10:0] v_count,
    output reg line_end,
    output reg frame_end
);

    // Horizontal timing parameters (1920x1080 @ 60Hz)
    localparam H_ACTIVE = 11'd1920;
    localparam H_TOTAL = 11'd2200;
    localparam V_ACTIVE = 11'd1080;
    localparam V_TOTAL = 11'd1125;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            h_count <= 11'h000;
            v_count <= 11'h000;
            line_end <= 1'b0;
            frame_end <= 1'b0;
        end else begin
            line_end <= 1'b0;
            frame_end <= 1'b0;

            // Horizontal counter
            if (h_count == H_TOTAL - 1) begin
                h_count <= 11'h000;
                line_end <= 1'b1;

                // Vertical counter
                if (v_count == V_TOTAL - 1) begin
                    v_count <= 11'h000;
                    frame_end <= 1'b1;
                end else begin
                    v_count <= v_count + 1'b1;
                end
            end else begin
                h_count <= h_count + 1'b1;
            end
        end
    end

endmodule
