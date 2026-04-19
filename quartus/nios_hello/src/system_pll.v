// System PLL - Generates 100MHz from input clock
// Stub replacement for synthesis on Cyclone 10 GX
// (altpll megafunction is not available for this device family)

module system_pll (
    input  areset,
    input  inclk0,
    output c0,
    output locked
);

    // Simple pass-through for synthesis validation
    // In a real design, use an IOPLL or fPLL IP for Cyclone 10 GX
    assign c0 = inclk0;
    assign locked = ~areset;

endmodule
