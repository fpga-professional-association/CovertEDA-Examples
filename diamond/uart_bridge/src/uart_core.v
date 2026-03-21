// UART Core Module
// 8N1 configuration with configurable baud rate
// Implements both TX and RX paths

module uart_core (
    input clk,
    input reset_n,
    input [3:0] baud_rate,  // 0=9600, 1=19200, 2=38400, 3=57600, 4=115200, etc.

    // Transmit interface
    input [7:0] tx_data,
    input tx_valid,
    output reg tx_ready,
    output tx,

    // Receive interface
    output reg [7:0] rx_data,
    output reg rx_valid,
    input rx
);

    // Baud rate divisor lookup table
    reg [15:0] baud_divisor;
    always @(*) begin
        case(baud_rate)
            4'h0: baud_divisor = 16'd5208;  // 9600 @ 48MHz
            4'h1: baud_divisor = 16'd2604;  // 19200
            4'h2: baud_divisor = 16'd1302;  // 38400
            4'h3: baud_divisor = 16'd869;   // 57600
            4'h4: baud_divisor = 16'd434;   // 115200
            default: baud_divisor = 16'd434;
        endcase
    end

    // TX path
    reg [15:0] tx_clk_count;
    reg [10:0] tx_shift;
    reg [3:0] tx_bit_count;
    reg tx_busy;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            tx_clk_count <= 16'h0000;
            tx_shift <= 11'h7FF;
            tx_bit_count <= 4'h0;
            tx_busy <= 1'b0;
            tx_ready <= 1'b1;
        end else begin
            tx_clk_count <= tx_clk_count + 1'b1;

            if (tx_clk_count >= baud_divisor) begin
                tx_clk_count <= 16'h0000;

                if (tx_busy) begin
                    tx_shift <= {1'b1, tx_shift[10:1]};
                    tx_bit_count <= tx_bit_count + 1'b1;

                    if (tx_bit_count == 4'hA) begin
                        tx_busy <= 1'b0;
                        tx_ready <= 1'b1;
                    end
                end
            end

            if (tx_valid && tx_ready && !tx_busy) begin
                tx_shift <= {1'b1, tx_data, 1'b0};
                tx_bit_count <= 4'h0;
                tx_busy <= 1'b1;
                tx_ready <= 1'b0;
            end
        end
    end

    assign tx = tx_shift[0];

    // RX path
    reg [15:0] rx_clk_count;
    reg [10:0] rx_shift;
    reg [3:0] rx_bit_count;
    reg rx_busy;
    reg rx_sync1, rx_sync2;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            rx_clk_count <= 16'h0000;
            rx_shift <= 11'h7FF;
            rx_bit_count <= 4'h0;
            rx_busy <= 1'b0;
            rx_data <= 8'h00;
            rx_valid <= 1'b0;
            rx_sync1 <= 1'b1;
            rx_sync2 <= 1'b1;
        end else begin
            // Synchronize RX input
            rx_sync1 <= rx;
            rx_sync2 <= rx_sync1;

            rx_valid <= 1'b0;

            if (!rx_busy && !rx_sync2) begin
                // Start bit detected
                rx_busy <= 1'b1;
                rx_clk_count <= baud_divisor >> 1;
                rx_bit_count <= 4'h0;
            end else if (rx_busy) begin
                rx_clk_count <= rx_clk_count + 1'b1;

                if (rx_clk_count >= baud_divisor) begin
                    rx_clk_count <= 16'h0000;
                    rx_shift <= {rx_sync2, rx_shift[10:1]};
                    rx_bit_count <= rx_bit_count + 1'b1;

                    if (rx_bit_count == 4'h9) begin
                        rx_data <= rx_shift[8:1];
                        rx_valid <= 1'b1;
                        rx_busy <= 1'b0;
                    end
                end
            end
        end
    end

endmodule
