// NoC Adapter

module noc_adapter (
    input  clk,
    input  rst_n,
    input  [63:0] in_data,
    input  in_valid,
    output in_ready,
    output [63:0] out_data,
    output out_valid
);

    reg [63:0] fifo [15:0];
    reg [4:0] wr_ptr, rd_ptr;
    reg fifo_valid;

    assign out_data = fifo[rd_ptr[3:0]];
    assign out_valid = fifo_valid;
    assign in_ready = (wr_ptr != {~rd_ptr[4], rd_ptr[3:0]});

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= 5'h0;
            rd_ptr <= 5'h0;
            fifo_valid <= 1'b0;
        end else begin
            if (in_valid && in_ready) begin
                fifo[wr_ptr[3:0]] <= in_data;
                wr_ptr <= wr_ptr + 1'b1;
            end

            if (out_valid) begin
                rd_ptr <= rd_ptr + 1'b1;
            end

            fifo_valid <= (wr_ptr != rd_ptr);
        end
    end

endmodule
