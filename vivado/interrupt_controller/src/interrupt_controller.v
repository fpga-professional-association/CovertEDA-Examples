// =============================================================================
// 8-Source Interrupt Controller with Priority Encoding
// Device: Xilinx Artix-7 XC7A35T
// =============================================================================

module interrupt_controller (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] irq_in,       // 8 interrupt request lines
    input  wire [7:0] irq_mask,     // Interrupt mask (1=enabled)
    input  wire       irq_ack,      // Acknowledge current interrupt
    output reg  [2:0] irq_id,       // ID of highest-priority active IRQ
    output reg        irq_valid,    // An unmasked IRQ is pending
    output reg  [7:0] irq_pending   // Pending interrupt status register
);

    // Edge detection for IRQ inputs
    reg [7:0] irq_prev;
    wire [7:0] irq_edge;
    assign irq_edge = irq_in & ~irq_prev;

    // Masked pending interrupts
    wire [7:0] irq_active;
    assign irq_active = irq_pending & irq_mask;

    // Priority encoder: lowest bit = highest priority
    reg [2:0] highest_pri;
    reg       has_irq;

    always @(*) begin
        highest_pri = 3'd0;
        has_irq = 1'b0;
        if (irq_active[0])      begin highest_pri = 3'd0; has_irq = 1'b1; end
        else if (irq_active[1]) begin highest_pri = 3'd1; has_irq = 1'b1; end
        else if (irq_active[2]) begin highest_pri = 3'd2; has_irq = 1'b1; end
        else if (irq_active[3]) begin highest_pri = 3'd3; has_irq = 1'b1; end
        else if (irq_active[4]) begin highest_pri = 3'd4; has_irq = 1'b1; end
        else if (irq_active[5]) begin highest_pri = 3'd5; has_irq = 1'b1; end
        else if (irq_active[6]) begin highest_pri = 3'd6; has_irq = 1'b1; end
        else if (irq_active[7]) begin highest_pri = 3'd7; has_irq = 1'b1; end
    end

    // Edge detection register
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            irq_prev <= 8'd0;
        end else begin
            irq_prev <= irq_in;
        end
    end

    // Pending register: set on rising edge of irq_in, cleared on ack
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            irq_pending <= 8'd0;
        end else begin
            // Set pending on rising edge
            irq_pending <= (irq_pending | irq_edge);

            // Clear on acknowledge
            if (irq_ack && irq_valid) begin
                irq_pending[irq_id] <= 1'b0;
            end
        end
    end

    // Output registers
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            irq_id    <= 3'd0;
            irq_valid <= 1'b0;
        end else begin
            irq_id    <= highest_pri;
            irq_valid <= has_irq;
        end
    end

endmodule
