// =============================================================================
// Manchester Encoder/Decoder
// Device: Xilinx Artix-7 XC7A35T
// IEEE 802.3 convention: 0 = low-to-high, 1 = high-to-low
// =============================================================================

module manchester_encoder (
    input  wire       clk,
    input  wire       rst_n,

    // Encoder
    input  wire       tx_data,      // Data bit to encode
    input  wire       tx_valid,     // Data valid
    output reg        tx_out,       // Manchester encoded output
    output reg        tx_ready,     // Ready for next bit

    // Decoder
    input  wire       rx_in,        // Manchester encoded input
    output reg        rx_data,      // Decoded data bit
    output reg        rx_valid      // Decoded data valid
);

    // === ENCODER ===
    // Two phases per bit: first half and second half
    reg enc_phase;      // 0 = first half, 1 = second half
    reg enc_bit;        // Current bit being encoded
    reg enc_active;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx_out     <= 1'b0;
            tx_ready   <= 1'b1;
            enc_phase  <= 1'b0;
            enc_bit    <= 1'b0;
            enc_active <= 1'b0;
        end else begin
            if (enc_active) begin
                if (enc_phase == 1'b0) begin
                    // First half of bit period
                    tx_out    <= enc_bit;  // For '1': high first, for '0': low first
                    enc_phase <= 1'b1;
                    tx_ready  <= 1'b0;
                end else begin
                    // Second half: invert
                    tx_out     <= ~enc_bit;
                    enc_phase  <= 1'b0;
                    enc_active <= 1'b0;
                    tx_ready   <= 1'b1;
                end
            end else if (tx_valid) begin
                enc_bit    <= tx_data;
                enc_active <= 1'b1;
                enc_phase  <= 1'b0;
                tx_ready   <= 1'b0;
            end
        end
    end

    // === DECODER ===
    // Sample at mid-bit and detect transitions
    reg rx_prev;
    reg [1:0] rx_cnt;
    reg rx_synced;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_data   <= 1'b0;
            rx_valid  <= 1'b0;
            rx_prev   <= 1'b0;
            rx_cnt    <= 2'd0;
            rx_synced <= 1'b0;
        end else begin
            rx_prev  <= rx_in;
            rx_valid <= 1'b0;

            // Detect transition (mid-bit for Manchester)
            if (rx_in != rx_prev) begin
                if (rx_cnt == 2'd1) begin
                    // Mid-bit transition: decode
                    // High-to-low = 1, Low-to-high = 0
                    rx_data  <= rx_prev;  // Previous value was the first half
                    rx_valid <= 1'b1;
                    rx_cnt   <= 2'd0;
                    rx_synced <= 1'b1;
                end else begin
                    // Bit boundary transition
                    rx_cnt <= 2'd0;
                end
            end else if (rx_synced) begin
                rx_cnt <= rx_cnt + 1'b1;
            end
        end
    end

endmodule
