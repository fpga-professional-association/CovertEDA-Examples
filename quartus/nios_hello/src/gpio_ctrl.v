// GPIO Controller - Bidirectional GPIO Interface

module gpio_ctrl (
    input  clk,
    input  rst,
    input  [7:0] oe,           // Output enable per pin
    input  [7:0] data_out,     // Data to output
    output [7:0] data_in,      // Data from input
    inout  [7:0] bidir         // Bidirectional pins
);

    // Input register for synchronization
    reg [7:0] data_in_sync;
    wire [7:0] bidir_in;

    // Tri-state logic
    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : gpio_pins
            assign bidir[i] = oe[i] ? data_out[i] : 1'bz;
            assign bidir_in[i] = bidir[i];
        end
    endgenerate

    // Input synchronization
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            data_in_sync <= 8'b0;
        end else begin
            data_in_sync <= bidir_in;
        end
    end

    assign data_in = data_in_sync;

endmodule
