// ROM Lookup Table - 256x8 ROM with synchronous read
// Target: LFE5U-25F (ECP5)

module rom_lookup (
    input        clk,
    input        reset_n,
    input  [7:0] addr,
    input        rd_en,
    output reg [7:0] data_out,
    output reg       data_valid
);

    reg [7:0] rom [0:255];
    integer i;

    // Initialize ROM with sine-wave approximation lookup
    initial begin
        for (i = 0; i < 256; i = i + 1) begin
            // Simple triangular wave pattern for testability
            if (i < 64)
                rom[i] = i * 4;           // 0 to 252, rising
            else if (i < 128)
                rom[i] = (127 - i) * 4;   // 252 to 0, falling
            else if (i < 192)
                rom[i] = (i - 128) * 4;   // 0 to 252, rising
            else
                rom[i] = (255 - i) * 4;   // 252 to 0, falling
        end
    end

    // Synchronous read with valid flag
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            data_out   <= 8'd0;
            data_valid <= 1'b0;
        end else begin
            if (rd_en) begin
                data_out   <= rom[addr];
                data_valid <= 1'b1;
            end else begin
                data_valid <= 1'b0;
            end
        end
    end

endmodule
