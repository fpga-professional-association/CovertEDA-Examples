// Temperature Sensor SPI Reader with Threshold
// Device: iCE40UP5K
// Reads 16-bit temperature via SPI and compares against threshold

module temp_sensor_spi (
    input         clk,
    input         rst_n,
    input         start,
    input  [15:0] threshold,

    // SPI interface
    output        spi_clk,
    output        spi_cs_n,
    input         spi_miso,

    // Output
    output [15:0] temp_data,
    output        temp_valid,
    output        over_threshold
);

    reg [4:0] bit_cnt;
    reg [15:0] shift_reg;
    reg [7:0] clk_div;
    reg       spi_clk_r;
    reg       spi_cs_r;
    reg [15:0] temp_r;
    reg       temp_valid_r;
    reg       over_r;
    reg [1:0] state;

    localparam S_IDLE = 2'd0;
    localparam S_READ = 2'd1;
    localparam S_DONE = 2'd2;

    parameter CLK_DIV = 8'd6;  // SPI clock divider

    assign spi_clk        = spi_clk_r;
    assign spi_cs_n       = spi_cs_r;
    assign temp_data      = temp_r;
    assign temp_valid     = temp_valid_r;
    assign over_threshold = over_r;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state       <= S_IDLE;
            bit_cnt     <= 5'd0;
            shift_reg   <= 16'd0;
            clk_div     <= 8'd0;
            spi_clk_r   <= 1'b0;
            spi_cs_r    <= 1'b1;
            temp_r      <= 16'd0;
            temp_valid_r <= 1'b0;
            over_r      <= 1'b0;
        end else begin
            temp_valid_r <= 1'b0;
            case (state)
                S_IDLE: begin
                    spi_cs_r  <= 1'b1;
                    spi_clk_r <= 1'b0;
                    if (start) begin
                        spi_cs_r  <= 1'b0;
                        bit_cnt   <= 5'd0;
                        shift_reg <= 16'd0;
                        clk_div   <= 8'd0;
                        state     <= S_READ;
                    end
                end
                S_READ: begin
                    clk_div <= clk_div + 1'b1;
                    if (clk_div == CLK_DIV) begin
                        clk_div   <= 8'd0;
                        spi_clk_r <= ~spi_clk_r;
                        if (spi_clk_r == 1'b0) begin
                            // Rising edge: sample MISO
                            shift_reg <= {shift_reg[14:0], spi_miso};
                            bit_cnt   <= bit_cnt + 1'b1;
                            if (bit_cnt == 5'd15)
                                state <= S_DONE;
                        end
                    end
                end
                S_DONE: begin
                    spi_cs_r     <= 1'b1;
                    spi_clk_r    <= 1'b0;
                    temp_r       <= shift_reg;
                    temp_valid_r <= 1'b1;
                    over_r       <= (shift_reg > threshold);
                    state        <= S_IDLE;
                end
            endcase
        end
    end

endmodule
