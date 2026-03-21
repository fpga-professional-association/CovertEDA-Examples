// MAC Engine for 400G Ethernet

module mac_engine (
    input  clk_ref,
    input  rst_n,
    input  [255:0] tx_data,
    input  tx_valid,
    output reg tx_ready,
    output [255:0] mac_data,
    output mac_valid
);

    reg [255:0] data_buf;
    reg valid_buf;

    always @(posedge clk_ref or negedge rst_n) begin
        if (!rst_n) begin
            tx_ready <= 1'b1;
            valid_buf <= 1'b0;
        end else if (tx_valid && tx_ready) begin
            data_buf <= tx_data;
            valid_buf <= 1'b1;
            tx_ready <= 1'b1;
        end else begin
            valid_buf <= 1'b0;
        end
    end

    assign mac_data = data_buf;
    assign mac_valid = valid_buf;

endmodule
