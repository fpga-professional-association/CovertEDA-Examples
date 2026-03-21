// UART Transmitter

module uart_tx (
    input  clk,
    input  rst_n,
    input  baud_clk,
    input  [7:0] data,
    input  valid,
    output ready,
    output uart_tx
);

    reg [9:0] shift_reg;
    reg [3:0] bit_count;
    reg transmitting;

    assign ready = !transmitting;
    assign uart_tx = (transmitting) ? shift_reg[0] : 1'b1;

    always @(posedge baud_clk or negedge rst_n) begin
        if (!rst_n) begin
            transmitting <= 1'b0;
            bit_count <= 4'h0;
            shift_reg <= 10'b1111111111;
        end else if (valid && !transmitting) begin
            shift_reg <= {1'b1, data, 1'b0};
            bit_count <= 4'h0;
            transmitting <= 1'b1;
        end else if (transmitting) begin
            shift_reg <= {1'b1, shift_reg[9:1]};
            bit_count <= bit_count + 1'b1;
            if (bit_count == 4'h9) begin
                transmitting <= 1'b0;
            end
        end
    end

endmodule
