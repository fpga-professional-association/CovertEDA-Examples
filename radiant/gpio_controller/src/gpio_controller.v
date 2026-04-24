// =============================================================================
// Design      : GPIO Controller
// Module      : gpio_controller
// Description : 8-bit GPIO with direction register and output enable
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module gpio_controller (
    input   wire        clk,
    input   wire        rst_n,
    input   wire        wr_en,          // Write enable
    input   wire        rd_en,          // Read enable
    input   wire [1:0]  addr,           // Register address
    input   wire [7:0]  wr_data,        // Write data
    output  reg  [7:0]  rd_data,        // Read data
    input   wire [7:0]  gpio_in,        // GPIO input pins
    output  wire [7:0]  gpio_out,       // GPIO output pins
    output  wire [7:0]  gpio_oe         // GPIO output enable (1=output)
);

    // Register map:
    // addr=0: GPIO_DIR  - direction register (1=output, 0=input)
    // addr=1: GPIO_OUT  - output data register
    // addr=2: GPIO_IN   - input data register (read-only)
    // addr=3: GPIO_IE   - interrupt enable (placeholder)

    reg [7:0] dir_reg;
    reg [7:0] out_reg;
    reg [7:0] ie_reg;
    reg [7:0] gpio_in_sync0, gpio_in_sync1;

    assign gpio_out = out_reg;
    assign gpio_oe  = dir_reg;

    // Input synchronizer (2-stage)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            gpio_in_sync0 <= 8'd0;
            gpio_in_sync1 <= 8'd0;
        end else begin
            gpio_in_sync0 <= gpio_in;
            gpio_in_sync1 <= gpio_in_sync0;
        end
    end

    // Register write
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            dir_reg <= 8'd0;    // All inputs by default
            out_reg <= 8'd0;
            ie_reg  <= 8'd0;
        end else if (wr_en) begin
            case (addr)
                2'd0: dir_reg <= wr_data;
                2'd1: out_reg <= wr_data;
                2'd3: ie_reg  <= wr_data;
                default: ;
            endcase
        end
    end

    // Register read
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_data <= 8'd0;
        end else if (rd_en) begin
            case (addr)
                2'd0: rd_data <= dir_reg;
                2'd1: rd_data <= out_reg;
                2'd2: rd_data <= gpio_in_sync1;
                2'd3: rd_data <= ie_reg;
                default: rd_data <= 8'd0;
            endcase
        end
    end

endmodule
