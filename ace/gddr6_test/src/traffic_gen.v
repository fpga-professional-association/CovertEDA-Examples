// GDDR6 Traffic Generator

module traffic_gen (
    input  clk,
    input  rst_n,
    output [31:0] addr,
    output [255:0] data,
    output valid
);

    reg [31:0] addr_reg;
    reg [255:0] data_reg;
    reg valid_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            addr_reg <= 32'h0;
            valid_reg <= 1'b1;
        end else begin
            addr_reg <= addr_reg + 1'b1;
            data_reg <= {data_reg[223:0], addr_reg[31:0]};
            valid_reg <= 1'b1;
        end
    end

    assign addr = addr_reg;
    assign data = data_reg;
    assign valid = valid_reg;

endmodule
