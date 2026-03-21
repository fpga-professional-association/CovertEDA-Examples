// Synchronous FIFO with configurable depth and width
// Suitable for single-clock domain buffering

module fifo_sync #(
    parameter WIDTH = 8,
    parameter DEPTH = 256,
    parameter ADDR_WIDTH = $clog2(DEPTH)
) (
    input clk,
    input reset_n,

    // Write side
    input wr_en,
    input [WIDTH-1:0] wr_data,

    // Read side
    input rd_en,
    output reg [WIDTH-1:0] rd_data,

    // Status
    output empty,
    output full,
    output [ADDR_WIDTH:0] count
);

    reg [WIDTH-1:0] fifo_mem [0:DEPTH-1];
    reg [ADDR_WIDTH-1:0] wr_ptr;
    reg [ADDR_WIDTH-1:0] rd_ptr;
    reg [ADDR_WIDTH:0] count_reg;

    // FIFO write logic
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            wr_ptr <= {ADDR_WIDTH{1'b0}};
            fifo_mem[0] <= {WIDTH{1'b0}};
        end else begin
            if (wr_en && !full) begin
                fifo_mem[wr_ptr] <= wr_data;
                if (wr_ptr == DEPTH - 1) begin
                    wr_ptr <= {ADDR_WIDTH{1'b0}};
                end else begin
                    wr_ptr <= wr_ptr + 1'b1;
                end
            end
        end
    end

    // FIFO read logic
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            rd_ptr <= {ADDR_WIDTH{1'b0}};
            rd_data <= {WIDTH{1'b0}};
        end else begin
            if (rd_en && !empty) begin
                rd_data <= fifo_mem[rd_ptr];
                if (rd_ptr == DEPTH - 1) begin
                    rd_ptr <= {ADDR_WIDTH{1'b0}};
                end else begin
                    rd_ptr <= rd_ptr + 1'b1;
                end
            end
        end
    end

    // Counter and status generation
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            count_reg <= {ADDR_WIDTH+1{1'b0}};
        end else begin
            case({wr_en && !full, rd_en && !empty})
                2'b00: count_reg <= count_reg;
                2'b01: count_reg <= count_reg - 1'b1;
                2'b10: count_reg <= count_reg + 1'b1;
                2'b11: count_reg <= count_reg;
            endcase
        end
    end

    assign empty = (count_reg == 0);
    assign full = (count_reg == DEPTH);
    assign count = count_reg;

endmodule
