// Simple Wishbone SoC Top Module
// Bus master: CPU simulation, Bus slaves: SRAM, GPIO, Timer
// Target: LFE5U-85F-6BG554I
// Oscillator: 50 MHz

module soc_top (
    input clk_50m,          // 50 MHz system clock
    input reset_n,          // Active low reset

    // GPIO Interface
    input [3:0] gpio_in,    // 4 GPIO inputs
    output [3:0] gpio_out,  // 4 GPIO outputs

    // Status indicators
    output [3:0] status_led,

    // Serial debug interface
    output debug_tx,
    input debug_rx
);

    // Wishbone bus signals
    wire [31:0] wb_addr;
    wire [31:0] wb_data_wr;
    wire [31:0] wb_data_rd;
    wire [3:0] wb_sel;
    wire wb_we;
    wire wb_cyc;
    wire wb_stb;
    wire wb_ack;

    // Slave select signals
    wire sram_sel;
    wire gpio_sel;
    wire timer_sel;

    // Slave ACK signals
    wire sram_ack;
    wire gpio_ack;
    wire timer_ack;

    // Slave data outputs
    wire [31:0] sram_data;
    wire [31:0] gpio_data;
    wire [31:0] timer_data;

    // Interrupt signals
    wire gpio_irq;
    wire timer_irq;

    // Address decoding
    assign sram_sel = wb_cyc && wb_stb && (wb_addr[31:20] == 12'h000);
    assign gpio_sel = wb_cyc && wb_stb && (wb_addr[31:20] == 12'h100);
    assign timer_sel = wb_cyc && wb_stb && (wb_addr[31:20] == 12'h200);

    // Wishbone bus arbiter and multiplexer
    assign wb_ack = sram_ack | gpio_ack | timer_ack;
    assign wb_data_rd = sram_sel ? sram_data :
                        gpio_sel ? gpio_data :
                        timer_sel ? timer_data : 32'h00000000;

    // Simple CPU simulation (state machine generating test patterns)
    reg [31:0] addr_counter;
    reg [3:0] test_state;
    reg [15:0] cycle_counter;

    always @(posedge clk_50m or negedge reset_n) begin
        if (!reset_n) begin
            addr_counter <= 32'h00000000;
            test_state <= 4'h0;
            cycle_counter <= 16'h0000;
        end else begin
            cycle_counter <= cycle_counter + 1'b1;

            if (cycle_counter == 16'hFFFF) begin
                test_state <= test_state + 1'b1;
                addr_counter <= addr_counter + 32'h00000004;
            end
        end
    end

    assign wb_addr = addr_counter;
    assign wb_data_wr = {test_state, 28'h0000000};
    assign wb_sel = 4'hF;
    assign wb_we = (test_state[0] == 1'b1) ? 1'b1 : 1'b0;
    assign wb_cyc = 1'b1;
    assign wb_stb = (cycle_counter == 0) ? 1'b1 : 1'b0;

    // Instantiate SRAM slave
    wb_sram sram_inst (
        .clk(clk_50m),
        .reset_n(reset_n),
        .wb_addr(wb_addr[11:0]),
        .wb_data_wr(wb_data_wr),
        .wb_data_rd(sram_data),
        .wb_sel(wb_sel),
        .wb_we(wb_we),
        .wb_cyc(wb_cyc),
        .wb_stb(wb_stb && sram_sel),
        .wb_ack(sram_ack)
    );

    // Instantiate GPIO slave
    wb_gpio gpio_inst (
        .clk(clk_50m),
        .reset_n(reset_n),
        .wb_addr(wb_addr[3:0]),
        .wb_data_wr(wb_data_wr),
        .wb_data_rd(gpio_data),
        .wb_sel(wb_sel),
        .wb_we(wb_we),
        .wb_cyc(wb_cyc),
        .wb_stb(wb_stb && gpio_sel),
        .wb_ack(gpio_ack),
        .gpio_in(gpio_in),
        .gpio_out(gpio_out),
        .gpio_irq(gpio_irq)
    );

    // Instantiate Timer slave
    wb_timer timer_inst (
        .clk(clk_50m),
        .reset_n(reset_n),
        .wb_addr(wb_addr[3:0]),
        .wb_data_wr(wb_data_wr),
        .wb_data_rd(timer_data),
        .wb_sel(wb_sel),
        .wb_we(wb_we),
        .wb_cyc(wb_cyc),
        .wb_stb(wb_stb && timer_sel),
        .wb_ack(timer_ack),
        .timer_irq(timer_irq)
    );

    // Status LED assignment
    assign status_led[0] = ~reset_n;
    assign status_led[1] = wb_cyc && wb_stb;
    assign status_led[2] = gpio_irq;
    assign status_led[3] = timer_irq;

    // Debug serial output (simple strobe)
    assign debug_tx = cycle_counter[14];

endmodule
