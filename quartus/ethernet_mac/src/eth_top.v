// 10/100 Ethernet MAC Top Level
// Cyclone V GX - 5CGXFC7C7F23C8

module eth_top (
    input  clk_125m,
    input  rst_n,

    // MII Interface TX
    output [3:0] mii_txd,
    output mii_tx_en,
    output mii_tx_er,
    input  mii_tx_clk,

    // MII Interface RX
    input  [3:0] mii_rxd,
    input  mii_rx_dv,
    input  mii_rx_er,
    input  mii_rx_clk,

    // MAC Control
    input  [47:0] mac_addr,
    input  [15:0] eth_type,

    // Data Interface
    input  [7:0] tx_data,
    input  tx_valid,
    output tx_ready,

    output [7:0] rx_data,
    output rx_valid,
    output rx_last,
    input  rx_ready
);

    wire mac_tx_clk_int;
    wire mac_rx_clk_int;
    wire [7:0] tx_payload;
    wire [7:0] rx_payload;
    wire crc_valid;

    // TX Path - use the external MII TX clock from the PHY
    mac_tx tx_inst (
        .clk(clk_125m),
        .rst(~rst_n),
        .mii_txd(mii_txd),
        .mii_tx_en(mii_tx_en),
        .mii_tx_er(mii_tx_er),
        .mii_tx_clk(mii_tx_clk),
        .mac_addr(mac_addr),
        .eth_type(eth_type),
        .tx_data(tx_data),
        .tx_valid(tx_valid),
        .tx_ready(tx_ready)
    );

    // RX Path - use the external MII RX clock from the PHY
    mac_rx rx_inst (
        .clk(clk_125m),
        .rst(~rst_n),
        .mii_rxd(mii_rxd),
        .mii_rx_dv(mii_rx_dv),
        .mii_rx_er(mii_rx_er),
        .mii_rx_clk(mii_rx_clk),
        .rx_data(rx_data),
        .rx_valid(rx_valid),
        .rx_last(rx_last),
        .rx_ready(rx_ready),
        .crc_valid(crc_valid)
    );

    // MII Interface Manager - internal clock gen (unused when using external PHY clocks)
    mii_intf mii_inst (
        .clk_125m(clk_125m),
        .tx_clk(mac_tx_clk_int),
        .rx_clk(mac_rx_clk_int)
    );

endmodule
