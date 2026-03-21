// =============================================================================
// DDR3 Memory Test Pattern Generator
// Device: Xilinx Artix-7 XC7A200T-2FBG676C
// Clock: 200 MHz system clock
// =============================================================================

module mem_top (
    input  wire         clk_sys,       // 200 MHz system clock
    input  wire         clk_200_in,    // 200 MHz input (for DDR3)
    input  wire         rst_n,         // Active-low reset

    // DDR3 Interface (simplified for example)
    output wire [12:0]  ddr3_addr,
    output wire [2:0]   ddr3_ba,
    output wire         ddr3_ras_n,
    output wire         ddr3_cas_n,
    output wire         ddr3_we_n,
    inout  wire [63:0]  ddr3_dq,
    inout  wire [7:0]   ddr3_dqs_n,
    inout  wire [7:0]   ddr3_dqs_p,
    output wire         ddr3_ck_p,
    output wire         ddr3_ck_n,
    output wire         ddr3_cke,
    output wire         ddr3_cs_n,
    output wire         ddr3_odt,

    // Test Control Interface
    input  wire         test_en,       // Enable test pattern
    input  wire [7:0]   test_mode,     // Test mode selection
    output wire         test_busy,
    output wire         test_passed,
    output wire         test_failed,

    // Status/Debug
    output wire [31:0]  error_count,
    output wire [15:0]  status
);

    // ---- Internal Signals ----
    wire        traffic_valid;
    wire [63:0] traffic_data;
    wire [27:0] traffic_addr;
    wire        traffic_we;

    wire        checker_error;
    wire [31:0] checker_count;

    // ---- Traffic Generator ----
    traffic_gen #(
        .ADDR_WIDTH(28),
        .DATA_WIDTH(64)
    ) traffic_gen_inst (
        .clk(clk_sys),
        .rst_n(rst_n),
        .test_en(test_en),
        .test_mode(test_mode),
        .addr(traffic_addr),
        .data(traffic_data),
        .we(traffic_we),
        .valid(traffic_valid),
        .busy(test_busy)
    );

    // ---- DDR3 PHY (simplified) ----
    // In a real design, this would instantiate Xilinx DDR3 controller
    // For this example, we use a simple write/read arbiter
    assign ddr3_addr = traffic_addr[12:0];
    assign ddr3_ba = traffic_addr[15:13];
    assign ddr3_we_n = ~traffic_we;
    assign ddr3_ras_n = ~traffic_valid;
    assign ddr3_cas_n = ~traffic_valid;
    assign ddr3_cke = 1'b1;
    assign ddr3_cs_n = 1'b0;
    assign ddr3_odt = 1'b1;
    assign ddr3_ck_p = clk_200_in;
    assign ddr3_ck_n = ~clk_200_in;
    assign ddr3_dq = traffic_we ? traffic_data[63:0] : 64'hzzzzzzzzzzzzzzzz;
    assign ddr3_dqs_p = 8'h00;
    assign ddr3_dqs_n = 8'hff;

    // ---- Pattern Checker ----
    pattern_checker #(
        .ADDR_WIDTH(28),
        .DATA_WIDTH(64)
    ) pattern_checker_inst (
        .clk(clk_sys),
        .rst_n(rst_n),
        .data_in(ddr3_dq),
        .addr_in(traffic_addr),
        .test_mode(test_mode),
        .error(checker_error),
        .error_count(checker_count)
    );

    // ---- Status Logic ----
    assign error_count = checker_count;
    assign test_passed = ~test_busy & ~checker_error;
    assign test_failed = ~test_busy & checker_error;
    assign status = {8'b0, test_mode, test_passed, test_failed, test_busy};

endmodule

// =============================================================================
// Traffic Generator
// =============================================================================

module traffic_gen #(
    parameter ADDR_WIDTH = 28,
    parameter DATA_WIDTH = 64
) (
    input  wire                    clk,
    input  wire                    rst_n,
    input  wire                    test_en,
    input  wire [7:0]              test_mode,
    output reg  [ADDR_WIDTH-1:0]   addr,
    output wire [DATA_WIDTH-1:0]   data,
    output wire                    we,
    output wire                    valid,
    output reg                     busy
);

    reg [ADDR_WIDTH-1:0] addr_counter;
    reg [31:0] pattern_data;
    reg state;

    localparam IDLE = 1'b0, RUNNING = 1'b1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            addr_counter <= {ADDR_WIDTH{1'b0}};
            busy <= 1'b0;
            addr <= {ADDR_WIDTH{1'b0}};
        end else begin
            case (state)
                IDLE: begin
                    busy <= 1'b0;
                    if (test_en) begin
                        state <= RUNNING;
                        busy <= 1'b1;
                        addr_counter <= {ADDR_WIDTH{1'b0}};
                    end
                end

                RUNNING: begin
                    if (addr_counter < (1 << (ADDR_WIDTH - 4))) begin
                        addr <= addr_counter;
                        addr_counter <= addr_counter + 1'b1;
                    end else begin
                        state <= IDLE;
                        busy <= 1'b0;
                    end
                end
            endcase
        end
    end

    // Test data patterns
    always @(*) begin
        case (test_mode)
            8'h00: pattern_data = 32'h00000000;  // All zeros
            8'h01: pattern_data = 32'hFFFFFFFF;  // All ones
            8'h02: pattern_data = 32'hAAAAAAAA;  // Alternating 0101
            8'h03: pattern_data = 32'h55555555;  // Alternating 1010
            8'h04: pattern_data = {addr_counter[15:0], addr_counter[15:0]};  // Address
            8'h05: pattern_data = ~{addr_counter[15:0], addr_counter[15:0]}; // Inv address
            default: pattern_data = 32'h12345678;
        endcase
    end

    assign data = {pattern_data, pattern_data};
    assign we = (state == RUNNING);
    assign valid = (state == RUNNING);

endmodule
