// SERDES Loopback Test - High-Speed Serial Interface Loopback
// Target: LFE5UM5G-85F-8BG756C
// SERDES frequency: 2.5 Gbps (312.5 MHz bit clock)

module serdes_top (
    input ref_clk,          // 312.5 MHz reference clock
    input reset_n,

    // TX side (data output)
    output serdes_tx_p,
    output serdes_tx_n,

    // RX side (data input - looped back)
    input serdes_rx_p,
    input serdes_rx_n,

    // PRBS generator/checker
    output [7:0] prbs_status_led,
    input test_mode           // 0=loopback, 1=PRBS test
);

    // Internal signals
    wire [31:0] tx_data;
    wire [31:0] rx_data;
    wire serdes_clk_tx;
    wire serdes_clk_rx;
    wire tx_ready;
    wire rx_valid;
    wire [7:0] prbs_err;
    wire pll_locked;
    wire prbs_locked;

    // Reference clock PLL (2.5Gbps = 312.5MHz * 8x)
    serdes_wrapper pll_inst (
        .ref_clk(ref_clk),
        .reset_n(reset_n),
        .pll_clk(serdes_clk_tx),
        .pll_locked(pll_locked)
    );

    // SERDES TX wrapper
    serdes_wrapper serdes_tx_inst (
        .clk(serdes_clk_tx),
        .reset_n(reset_n && pll_locked),
        .data_in(tx_data),
        .serial_out_p(serdes_tx_p),
        .serial_out_n(serdes_tx_n)
    );

    // SERDES RX wrapper (looped back for testing)
    serdes_wrapper serdes_rx_inst (
        .clk(serdes_clk_tx),
        .reset_n(reset_n && pll_locked),
        .serial_in_p(serdes_rx_p),
        .serial_in_n(serdes_rx_n),
        .data_out(rx_data)
    );

    // PRBS Generator (TX pattern)
    prbs_gen #(.WIDTH(32)) prbs_tx_inst (
        .clk(serdes_clk_tx),
        .reset_n(reset_n && pll_locked),
        .enable(1'b1),
        .prbs_out(tx_data)
    );

    // PRBS Checker (RX pattern verification)
    prbs_check #(.WIDTH(32)) prbs_rx_inst (
        .clk(serdes_clk_tx),
        .reset_n(reset_n && pll_locked),
        .enable(1'b1),
        .prbs_in(rx_data),
        .prbs_err(prbs_err),
        .locked(prbs_locked)
    );

    // Status LED assignment
    assign prbs_status_led[0] = pll_locked;          // PLL locked indicator
    assign prbs_status_led[1] = prbs_locked;         // PRBS pattern locked
    assign prbs_status_led[2] = (prbs_err == 8'h00); // No errors
    assign prbs_status_led[3] = |prbs_err;           // Error detected
    assign prbs_status_led[4] = rx_valid;            // RX valid
    assign prbs_status_led[5] = tx_ready;            // TX ready
    assign prbs_status_led[6] = 1'b1;                // Power on
    assign prbs_status_led[7] = ~reset_n;            // Reset active

endmodule
