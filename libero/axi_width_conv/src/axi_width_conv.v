// AXI Data Width Converter 32->64 bit
// Target: MPF300T (PolarFire)
// Packs two 32-bit words into one 64-bit word

module axi_width_conv (
    input         clk,
    input         reset_n,
    // 32-bit input port
    input  [31:0] s_data,
    input         s_valid,
    input         s_last,       // last beat of burst
    output reg    s_ready,
    // 64-bit output port
    output reg [63:0] m_data,
    output reg        m_valid,
    output reg        m_last,
    input             m_ready
);

    reg [31:0] low_word;
    reg        has_low;
    reg        low_last;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            low_word <= 32'd0;
            has_low  <= 1'b0;
            low_last <= 1'b0;
            m_data   <= 64'd0;
            m_valid  <= 1'b0;
            m_last   <= 1'b0;
            s_ready  <= 1'b1;
        end else begin
            // Clear valid when downstream accepts
            if (m_valid && m_ready) begin
                m_valid <= 1'b0;
                m_last  <= 1'b0;
            end

            // Accept input when ready
            if (s_valid && s_ready) begin
                if (!has_low) begin
                    // Store first 32-bit word
                    low_word <= s_data;
                    has_low  <= 1'b1;
                    low_last <= s_last;
                    if (s_last) begin
                        // Last beat is odd - pad upper word
                        m_data  <= {32'd0, s_data};
                        m_valid <= 1'b1;
                        m_last  <= 1'b1;
                        has_low <= 1'b0;
                        s_ready <= 1'b0;
                    end
                end else begin
                    // Combine with stored word
                    m_data  <= {s_data, low_word};
                    m_valid <= 1'b1;
                    m_last  <= s_last;
                    has_low <= 1'b0;
                    s_ready <= 1'b0;
                end
            end

            // Re-enable input when output is consumed
            if (!m_valid || m_ready)
                s_ready <= 1'b1;
        end
    end

endmodule
