// MII Interface Clock Generator

module mii_intf (
    input  clk_125m,
    output tx_clk,
    output rx_clk
);

    // For 10/100 Mbps Ethernet:
    // 100 Mbps: 25 MHz MII clock
    // 10 Mbps: 2.5 MHz MII clock
    // Using 125 MHz input clock for simplicity

    reg [2:0] clk_div;

    always @(posedge clk_125m) begin
        clk_div <= clk_div + 1;
    end

    // Generate 25 MHz tx_clk (125M / 5)
    assign tx_clk = clk_div[2];

    // Generate 25 MHz rx_clk (125M / 5)
    assign rx_clk = clk_div[2];

endmodule
