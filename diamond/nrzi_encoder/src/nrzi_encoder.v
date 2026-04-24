// NRZI Encoder/Decoder
// Target: LFE5U-25F (ECP5)
// Encoder: data=1 causes transition, data=0 no transition
// Decoder: transition=1, no transition=0

module nrzi_encoder (
    input        clk,
    input        reset_n,
    input        data_in,
    input        data_valid,
    input        mode,         // 0=encode, 1=decode
    output reg   data_out,
    output reg   out_valid
);

    reg prev_level;
    reg prev_input;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            data_out   <= 1'b0;
            out_valid  <= 1'b0;
            prev_level <= 1'b0;
            prev_input <= 1'b0;
        end else begin
            out_valid <= data_valid;
            if (data_valid) begin
                if (mode == 0) begin
                    // Encode: toggle on 1, hold on 0
                    if (data_in)
                        prev_level <= ~prev_level;
                    data_out <= data_in ? ~prev_level : prev_level;
                end else begin
                    // Decode: detect transitions
                    data_out   <= data_in ^ prev_input;
                    prev_input <= data_in;
                end
            end
        end
    end

endmodule
