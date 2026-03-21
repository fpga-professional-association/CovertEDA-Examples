// Video Line Scaler - 720p to 1080p vertical scaling
// Target: LFE5U-85F-8BG756C
// Pixel clock: 148.5 MHz (1080p@60Hz compatible)

module scaler_top (
    input pixel_clk,        // 148.5 MHz pixel clock
    input reset_n,

    // Video input (720p: 1280x720@60Hz)
    input vsync_in,         // Vertical sync
    input hsync_in,         // Horizontal sync
    input [23:0] pixel_in,  // 24-bit RGB (8-8-8)
    input valid_in,         // Pixel valid

    // Video output (1080p: 1920x1080@60Hz)
    output vsync_out,
    output hsync_out,
    output [23:0] pixel_out,// 24-bit RGB output
    output valid_out,

    // Status/debug
    output [7:0] debug_status
);

    // Internal signals
    wire [10:0] h_count;
    wire [10:0] v_count;
    wire [23:0] pixel_buffered;
    wire pixel_valid_buffered;
    wire [23:0] pixel_interpolated;
    wire line_complete;
    wire frame_complete;

    // Pixel counter for input timing
    pixel_counter px_cnt_in (
        .clk(pixel_clk),
        .reset_n(reset_n),
        .hsync(hsync_in),
        .vsync(vsync_in),
        .h_count(h_count),
        .v_count(v_count),
        .line_end(line_complete),
        .frame_end(frame_complete)
    );

    // Line buffer (stores 1280 pixels of input line)
    line_buffer line_buf (
        .clk(pixel_clk),
        .reset_n(reset_n),
        .wr_en(valid_in),
        .wr_data(pixel_in),
        .wr_addr(h_count[9:0]),
        .rd_en(valid_out),
        .rd_data(pixel_buffered),
        .rd_addr(h_count[9:0])
    );

    // Vertical interpolator (scaling 720p 480 lines to 1080p 720 lines)
    interpolator interp (
        .clk(pixel_clk),
        .reset_n(reset_n),
        .pixel_in(pixel_buffered),
        .v_count_in(v_count),
        .pixel_out(pixel_interpolated),
        .valid_in(pixel_valid_buffered),
        .valid_out(valid_out)
    );

    // Output assignment
    assign pixel_out = pixel_interpolated;
    assign hsync_out = hsync_in;
    assign vsync_out = vsync_in;

    // Status/Debug output
    assign debug_status[0] = valid_in;
    assign debug_status[1] = valid_out;
    assign debug_status[2] = line_complete;
    assign debug_status[3] = frame_complete;
    assign debug_status[4] = vsync_in;
    assign debug_status[5] = hsync_in;
    assign debug_status[7:6] = v_count[9:8];

endmodule
