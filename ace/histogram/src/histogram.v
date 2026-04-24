// 256-Bin Histogram Calculator
// Device: Achronix Speedster7t AC7t1500
// Counts occurrences of each 8-bit value

module histogram (
    input         clk,
    input         rst_n,
    input  [7:0]  data_in,
    input         data_valid,
    input         clear,
    input  [7:0]  read_addr,
    input         read_en,
    output [15:0] read_count,
    output        read_valid
);

    // 256 x 16-bit bin memory (packed flat array for iverilog compatibility)
    reg [4095:0] bins_flat;  // 256 * 16 = 4096 bits
    reg [15:0] read_data_r;
    reg        read_valid_r;

    assign read_count = read_data_r;
    assign read_valid = read_valid_r;

    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            bins_flat    <= {4096{1'b0}};
            read_data_r  <= 16'd0;
            read_valid_r <= 1'b0;
        end else if (clear) begin
            bins_flat    <= {4096{1'b0}};
            read_valid_r <= 1'b0;
        end else begin
            read_valid_r <= 1'b0;

            // Increment bin on valid data
            if (data_valid) begin
                if (bins_flat[data_in*16 +: 16] < 16'hFFFF)
                    bins_flat[data_in*16 +: 16] <= bins_flat[data_in*16 +: 16] + 1'b1;
            end

            // Read bin value
            if (read_en) begin
                read_data_r  <= bins_flat[read_addr*16 +: 16];
                read_valid_r <= 1'b1;
            end
        end
    end

endmodule
