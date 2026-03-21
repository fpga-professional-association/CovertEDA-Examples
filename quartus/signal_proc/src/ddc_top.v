// Digital Downconverter (DDC) Top Level
// Arria II GX - EP2AGX125EF29C5

module ddc_top (
    input  clk_200m,
    input  rst_n,

    // Input Signal (from ADC)
    input  [15:0] adc_data,
    input  adc_valid,

    // Frequency Control
    input  [31:0] nco_freq,        // NCO tuning word
    input  [15:0] decim_rate,      // Decimation rate

    // Output Data
    output [31:0] i_data,
    output [31:0] q_data,
    output output_valid
);

    // Internal signals
    wire [15:0] nco_i;
    wire [15:0] nco_q;
    wire nco_valid;

    wire [31:0] mix_i;
    wire [31:0] mix_q;
    wire mix_valid;

    wire [31:0] cic_i;
    wire [31:0] cic_q;
    wire cic_valid;

    wire [31:0] fir_i;
    wire [31:0] fir_q;
    wire fir_valid;

    // NCO (Numerically Controlled Oscillator)
    nco nco_inst (
        .clk(clk_200m),
        .rst(~rst_n),
        .freq_word(nco_freq),
        .i_out(nco_i),
        .q_out(nco_q),
        .valid(nco_valid)
    );

    // Mixer
    // I = adc_data * cos(θ)
    // Q = adc_data * sin(θ)
    always @(posedge clk_200m) begin
        if (~rst_n) begin
            // Reset mixer
        end else if (adc_valid && nco_valid) begin
            // Multiply adc_data with NCO outputs
        end
    end

    // CIC Decimator (Cascade Integrator-Comb)
    cic_filter #(
        .N(5),                    // 5 stages
        .R(16)                   // Decimation factor
    ) cic_inst (
        .clk(clk_200m),
        .rst(~rst_n),
        .i_data_in(mix_i),
        .q_data_in(mix_q),
        .data_valid_in(mix_valid),
        .decim_rate(decim_rate),
        .i_data_out(cic_i),
        .q_data_out(cic_q),
        .data_valid_out(cic_valid)
    );

    // FIR Decimation Filter
    fir_decimate fir_inst (
        .clk(clk_200m),
        .rst(~rst_n),
        .i_data_in(cic_i),
        .q_data_in(cic_q),
        .data_valid_in(cic_valid),
        .i_data_out(fir_i),
        .q_data_out(fir_q),
        .data_valid_out(fir_valid)
    );

    assign i_data = fir_i;
    assign q_data = fir_q;
    assign output_valid = fir_valid;

endmodule
