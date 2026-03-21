// Baud Rate Generator

module baud_gen (
    input  clk,
    input  rst_n,
    output reg baud_clk
);

    // 12 MHz / 104 = 115200 baud
    reg [6:0] div_count;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            div_count <= 7'h0;
            baud_clk <= 1'b0;
        end else begin
            if (div_count == 7'd51) begin
                div_count <= 7'h0;
                baud_clk <= ~baud_clk;
            end else begin
                div_count <= div_count + 1'b1;
            end
        end
    end

endmodule
