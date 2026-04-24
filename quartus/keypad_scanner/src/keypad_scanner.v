// Keypad Scanner - 4x4 matrix keypad scanner
// Quartus / Cyclone IV E (EP4CE6)
// Scans rows, reads columns for key press detection

module keypad_scanner (
    input        clk,
    input        rst_n,
    input  [3:0] col_in,      // column inputs (directly from keypad)
    output [3:0] row_out,     // row scan outputs
    output [3:0] key_code,    // detected key code (0-15)
    output       key_valid,   // key detected pulse
    output       key_pressed  // any key currently pressed
);

    // Scan rate divider (short for simulation)
    parameter SCAN_DIV = 8;

    reg [7:0]  scan_cnt;
    reg [1:0]  row_sel;
    reg [3:0]  row_reg;
    reg [3:0]  key_code_reg;
    reg        key_valid_reg;
    reg        key_pressed_reg;

    assign row_out     = row_reg;
    assign key_code    = key_code_reg;
    assign key_valid   = key_valid_reg;
    assign key_pressed = key_pressed_reg;

    // One-hot row decoder
    always @(*) begin
        case (row_sel)
            2'd0: row_reg = 4'b0001;
            2'd1: row_reg = 4'b0010;
            2'd2: row_reg = 4'b0100;
            2'd3: row_reg = 4'b1000;
        endcase
    end

    reg [3:0] col_sync;
    reg       prev_pressed;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            scan_cnt     <= 8'd0;
            row_sel      <= 2'd0;
            key_code_reg <= 4'd0;
            key_valid_reg <= 1'b0;
            key_pressed_reg <= 1'b0;
            col_sync     <= 4'd0;
            prev_pressed <= 1'b0;
        end else begin
            col_sync      <= col_in;
            key_valid_reg <= 1'b0;

            scan_cnt <= scan_cnt + 8'd1;

            if (scan_cnt == SCAN_DIV - 1) begin
                scan_cnt <= 8'd0;

                // Check if any column is active for current row
                if (col_sync != 4'd0) begin
                    key_pressed_reg <= 1'b1;
                    // Encode key: row*4 + column position
                    if (col_sync[0])
                        key_code_reg <= {row_sel, 2'd0};
                    else if (col_sync[1])
                        key_code_reg <= {row_sel, 2'd1};
                    else if (col_sync[2])
                        key_code_reg <= {row_sel, 2'd2};
                    else
                        key_code_reg <= {row_sel, 2'd3};

                    if (!prev_pressed)
                        key_valid_reg <= 1'b1;
                    prev_pressed <= 1'b1;
                end else begin
                    if (row_sel == 2'd3) begin
                        // Completed full scan with no key found
                        key_pressed_reg <= 1'b0;
                        prev_pressed <= 1'b0;
                    end
                end

                // Advance to next row
                row_sel <= row_sel + 2'd1;
            end
        end
    end

endmodule
