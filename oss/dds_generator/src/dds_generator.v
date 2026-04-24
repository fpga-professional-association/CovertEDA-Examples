// Direct Digital Synthesis Waveform Generator
// Device: iCE40UP5K
// Generates sawtooth/triangle/square from phase accumulator

module dds_generator (
    input         clk,
    input         rst_n,
    input  [15:0] freq_word,   // phase increment per clock
    input  [1:0]  waveform,    // 0=saw, 1=triangle, 2=square, 3=pulse
    output [7:0]  dac_out,
    output        dac_valid
);

    reg [15:0] phase_acc;
    reg [7:0]  output_r;
    reg        valid_r;

    assign dac_out   = output_r;
    assign dac_valid = valid_r;

    wire [7:0] phase_msb = phase_acc[15:8];

    // Triangle wave: fold at midpoint
    wire [7:0] triangle = phase_acc[15] ?
                          ~phase_acc[14:7] :
                           phase_acc[14:7];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            phase_acc <= 16'd0;
            output_r  <= 8'd0;
            valid_r   <= 1'b0;
        end else begin
            phase_acc <= phase_acc + freq_word;
            valid_r   <= 1'b1;

            case (waveform)
                2'd0: output_r <= phase_msb;                    // Sawtooth
                2'd1: output_r <= triangle;                     // Triangle
                2'd2: output_r <= phase_acc[15] ? 8'hFF : 8'h00; // Square
                2'd3: output_r <= (phase_msb < 8'd32) ? 8'hFF : 8'h00; // Narrow pulse
            endcase
        end
    end

endmodule
