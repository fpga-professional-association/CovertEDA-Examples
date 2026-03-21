// Sample Buffer for ADC Data

module sample_buffer (
    input  clk,
    input  rst_n,
    input  [7:0] spi_data,
    input  spi_valid,
    output [11:0] adc_data,
    output adc_valid
);

    reg [11:0] data_latch;
    reg valid_reg;
    reg [7:0] upper_byte;
    reg got_upper;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            data_latch <= 12'h0;
            valid_reg <= 1'b0;
            upper_byte <= 8'h0;
            got_upper <= 1'b0;
        end else if (spi_valid) begin
            if (!got_upper) begin
                upper_byte <= spi_data;
                got_upper <= 1'b1;
                valid_reg <= 1'b0;
            end else begin
                data_latch <= {upper_byte[3:0], spi_data[7:4]};
                valid_reg <= 1'b1;
                got_upper <= 1'b0;
            end
        end else begin
            valid_reg <= 1'b0;
        end
    end

    assign adc_data = data_latch;
    assign adc_valid = valid_reg;

endmodule
