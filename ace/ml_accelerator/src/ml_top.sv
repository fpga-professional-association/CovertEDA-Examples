// ML Inference Accelerator Top Module
// Device: AC7t1500ES0
// Clock: 400 MHz

module ml_top (
    input  clk,
    input  rst_n,
    input  [31:0] input_data,
    input  input_valid,
    output input_ready,
    output [31:0] output_data,
    output output_valid,
    input  output_ready
);

    wire [31:0] mac_result;
    wire mac_valid;

    mac_array mac_inst (
        .clk(clk),
        .rst_n(rst_n),
        .in_data(input_data),
        .in_valid(input_valid),
        .result(mac_result),
        .result_valid(mac_valid)
    );

    activation act_inst (
        .clk(clk),
        .rst_n(rst_n),
        .in_data(mac_result),
        .in_valid(mac_valid),
        .out_data(output_data),
        .out_valid(output_valid)
    );

    assign input_ready = 1'b1;

endmodule
