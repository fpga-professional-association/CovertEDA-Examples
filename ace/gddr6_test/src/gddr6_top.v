// GDDR6 Memory Test Module

module gddr6_top (
    input  clk,
    input  rst_n,
    output [31:0] wr_addr,
    output [255:0] wr_data,
    output wr_en,
    input  [255:0] rd_data,
    output [31:0] rd_addr,
    output rd_en,
    output [31:0] test_result
);

    wire [31:0] gen_addr;
    wire [255:0] gen_data;
    wire gen_valid;

    traffic_gen tgen (
        .clk(clk),
        .rst_n(rst_n),
        .addr(gen_addr),
        .data(gen_data),
        .valid(gen_valid)
    );

    data_checker u_checker (
        .clk(clk),
        .rst_n(rst_n),
        .expected(gen_data),
        .actual(rd_data),
        .valid(gen_valid),
        .result(test_result)
    );

    assign wr_addr = gen_addr;
    assign wr_data = gen_data;
    assign wr_en = gen_valid;
    assign rd_addr = gen_addr + 1'b1;
    assign rd_en = gen_valid;

endmodule
