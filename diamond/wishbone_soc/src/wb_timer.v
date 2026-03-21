// Wishbone Timer Slave
// 32-bit counter with configurable prescaler and interrupts

module wb_timer (
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
    output reg timer_irq
);

    // Timer registers
    reg [31:0] timer_counter;
    reg [31:0] timer_limit;
    reg [15:0] timer_prescale;
    reg [15:0] prescale_counter;
    reg timer_enable;
    reg timer_irq_en;
    reg timer_irq_r;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            timer_counter <= 32'h00000000;
            timer_limit <= 32'hFFFFFFFF;
            timer_prescale <= 16'h0000;
            prescale_counter <= 16'h0000;
            timer_enable <= 1'b0;
            timer_irq_en <= 1'b0;
            timer_irq <= 1'b0;
            timer_irq_r <= 1'b0;
            wb_ack <= 1'b0;
        end else begin
            // Prescaler
            prescale_counter <= prescale_counter + 1'b1;
            if (prescale_counter >= timer_prescale) begin
                prescale_counter <= 16'h0000;

                // Timer counter increment
                if (timer_enable) begin
                    if (timer_counter == timer_limit) begin
                        timer_counter <= 32'h00000000;
                        timer_irq_r <= 1'b1;
                    end else begin
                        timer_counter <= timer_counter + 1'b1;
                    end
                end
            end

            // IRQ generation
            if (timer_irq_r && timer_irq_en) begin
                timer_irq <= 1'b1;
                timer_irq_r <= 1'b0;
            end else begin
                timer_irq <= 1'b0;
            end

            // Wishbone write
            if (wb_stb && wb_cyc && wb_we) begin
                case(wb_addr[3:2])
                    2'h0: timer_counter <= wb_data_wr;
                    2'h1: timer_limit <= wb_data_wr;
                    2'h2: begin
                        timer_prescale <= wb_data_wr[15:0];
                        timer_enable <= wb_data_wr[16];
                        timer_irq_en <= wb_data_wr[17];
                    end
                    default: ;
                endcase
                wb_ack <= 1'b1;
            end else if (wb_stb && wb_cyc) begin
                // Wishbone read
                case(wb_addr[3:2])
                    2'h0: wb_data_rd <= timer_counter;
                    2'h1: wb_data_rd <= timer_limit;
                    2'h2: wb_data_rd <= {14'h0000, timer_irq_en, timer_enable, timer_prescale};
                    2'h3: wb_data_rd <= {31'h00000000, timer_irq_r};
                    default: wb_data_rd <= 32'h00000000;
                endcase
                wb_ack <= 1'b1;
            end else begin
                wb_ack <= 1'b0;
            end
        end
    end

endmodule
