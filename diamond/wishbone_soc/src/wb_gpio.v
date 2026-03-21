// Wishbone GPIO Slave
// 4-bit input, 4-bit output, interrupt on input change

module wb_gpio (
    input clk,
    input reset_n,
    input [3:0] wb_addr,
    input [31:0] wb_data_wr,
    output reg [31:0] wb_data_rd,
    input [3:0] wb_sel,
    input wb_we,
    input wb_cyc,
    input wb_stb,
    output reg wb_ack,
    input [3:0] gpio_in,
    output reg [3:0] gpio_out,
    output reg gpio_irq
);

    // GPIO registers
    reg [3:0] gpio_out_r;
    reg [3:0] gpio_in_r;
    reg [3:0] gpio_in_sync;
    reg [3:0] gpio_in_prev;
    reg [3:0] gpio_irq_mask;
    reg [3:0] gpio_irq_status;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            gpio_out <= 4'h0;
            gpio_out_r <= 4'h0;
            gpio_in_r <= 4'h0;
            gpio_in_sync <= 4'h0;
            gpio_in_prev <= 4'h0;
            gpio_irq_mask <= 4'h0;
            gpio_irq_status <= 4'h0;
            gpio_irq <= 1'b0;
            wb_ack <= 1'b0;
        end else begin
            // Synchronize GPIO inputs
            gpio_in_sync <= gpio_in;
            gpio_in_r <= gpio_in_sync;

            // Detect input changes
            gpio_in_prev <= gpio_in_r;
            if (gpio_in_r != gpio_in_prev) begin
                gpio_irq_status <= 4'hF;
            end else begin
                if (gpio_irq_status != 0) begin
                    gpio_irq_status <= gpio_irq_status - 1'b1;
                end
            end

            // IRQ generation
            gpio_irq <= |(gpio_irq_status & gpio_irq_mask);

            // Wishbone write
            if (wb_stb && wb_cyc && wb_we) begin
                case(wb_addr[3:2])
                    2'h0: gpio_out_r <= wb_data_wr[3:0];
                    2'h1: gpio_irq_mask <= wb_data_wr[3:0];
                    default: ;
                endcase
                wb_ack <= 1'b1;
            end else if (wb_stb && wb_cyc) begin
                // Wishbone read
                case(wb_addr[3:2])
                    2'h0: wb_data_rd <= {28'h0000000, gpio_out_r};
                    2'h1: wb_data_rd <= {28'h0000000, gpio_in_r};
                    2'h2: wb_data_rd <= {28'h0000000, gpio_irq_mask};
                    2'h3: wb_data_rd <= {28'h0000000, gpio_irq_status};
                    default: wb_data_rd <= 32'h00000000;
                endcase
                wb_ack <= 1'b1;
            end else begin
                wb_ack <= 1'b0;
            end

            // Output assignment
            gpio_out <= gpio_out_r;
        end
    end

endmodule
