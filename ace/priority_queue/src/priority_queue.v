// 8-Entry Priority Queue
// Device: Achronix Speedster7t AC7t1500
// Maintains sorted order, highest priority dequeues first

module priority_queue (
    input         clk,
    input         rst_n,
    input  [7:0]  data_in,
    input  [2:0]  priority_in,
    input         enqueue,
    input         dequeue,
    output [7:0]  data_out,
    output [2:0]  priority_out,
    output        valid,
    output        full,
    output        empty
);

    reg [7:0] data_mem  [0:7];
    reg [2:0] prio_mem  [0:7];
    reg [3:0] count;

    assign empty        = (count == 4'd0);
    assign full         = (count == 4'd8);
    assign valid        = !empty;
    assign data_out     = empty ? 8'd0 : data_mem[0];
    assign priority_out = empty ? 3'd0 : prio_mem[0];

    integer i, j;
    reg [3:0] insert_pos;
    reg found;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 4'd0;
            for (i = 0; i < 8; i = i + 1) begin
                data_mem[i] <= 8'd0;
                prio_mem[i] <= 3'd0;
            end
        end else begin
            if (enqueue && !full) begin
                // Find insertion point (sorted by priority, highest first)
                insert_pos = count;
                found = 1'b0;
                for (i = 0; i < 8; i = i + 1) begin
                    if (i < count && !found) begin
                        if (priority_in > prio_mem[i]) begin
                            insert_pos = i[3:0];
                            found = 1'b1;
                        end
                    end
                end

                // Shift elements down
                for (i = 7; i > 0; i = i - 1) begin
                    if (i[3:0] > insert_pos && i < 8) begin
                        data_mem[i] <= data_mem[i-1];
                        prio_mem[i] <= prio_mem[i-1];
                    end
                end

                // Insert new element
                data_mem[insert_pos] <= data_in;
                prio_mem[insert_pos] <= priority_in;
                count <= count + 1'b1;
            end

            if (dequeue && !empty) begin
                // Shift all elements up (remove head)
                for (i = 0; i < 7; i = i + 1) begin
                    data_mem[i] <= data_mem[i+1];
                    prio_mem[i] <= prio_mem[i+1];
                end
                data_mem[7] <= 8'd0;
                prio_mem[7] <= 3'd0;
                count <= count - 1'b1;
            end
        end
    end

endmodule
