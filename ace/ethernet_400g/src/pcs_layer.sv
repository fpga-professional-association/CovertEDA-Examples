// PCS Layer for 400G Ethernet

module pcs_layer (
    input  clk_ref,
    input  rst_n,
    input  [255:0] in_data,
    output [255:0] out_data,
    output out_valid
);

    reg [255:0] pcs_data;
    reg pcs_valid;

    always @(posedge clk_ref or negedge rst_n) begin
        if (!rst_n) begin
            pcs_data <= 256'h0;
            pcs_valid <= 1'b0;
        end else begin
            pcs_data <= in_data;
            pcs_valid <= 1'b1;
        end
    end

    assign out_data = pcs_data;
    assign out_valid = pcs_valid;

endmodule
