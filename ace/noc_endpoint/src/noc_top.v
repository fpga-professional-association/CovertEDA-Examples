// NoC Endpoint for Speedster7t
// 500 MHz NoC clock

module noc_top (
    input  clk,
    input  rst_n,
    input  [63:0] noc_in_data,
    input  noc_in_valid,
    output noc_in_ready,
    output [63:0] noc_out_data,
    output noc_out_valid,
    input  noc_out_ready
);

    wire [63:0] adapter_in;
    wire adapter_valid_in;
    wire [63:0] adapter_out;
    wire adapter_valid_out;

    noc_adapter adapter_inst (
        .clk(clk),
        .rst_n(rst_n),
        .in_data(noc_in_data),
        .in_valid(noc_in_valid),
        .in_ready(noc_in_ready),
        .out_data(adapter_in),
        .out_valid(adapter_valid_in)
    );

    packet_builder builder_inst (
        .clk(clk),
        .rst_n(rst_n),
        .in_data(adapter_in),
        .in_valid(adapter_valid_in),
        .out_data(adapter_out),
        .out_valid(adapter_valid_out)
    );

    assign noc_out_data = adapter_out;
    assign noc_out_valid = adapter_valid_out;

endmodule
