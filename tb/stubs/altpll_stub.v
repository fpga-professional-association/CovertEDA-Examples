// Stub for Altera altpll IP — passthrough for simulation with Icarus Verilog
// Matches the port interface used by MegaWizard-generated wrappers
module altpll #(
    parameter bandwidth_type = "AUTO",
    parameter clk0_divide_by = 1,
    parameter clk0_duty_cycle = 50,
    parameter clk0_multiply_by = 1,
    parameter clk0_phase_shift = "0",
    parameter compensate_clock = "CLK0",
    parameter inclk0_input_frequency = 10000,
    parameter intended_device_family = "Cyclone IV E",
    parameter lpm_hint = "",
    parameter lpm_type = "altpll",
    parameter operation_mode = "NORMAL",
    parameter port_activeclock = "PORT_UNUSED",
    parameter port_areset = "PORT_USED",
    parameter port_clkbad0 = "PORT_UNUSED",
    parameter port_clkbad1 = "PORT_UNUSED",
    parameter port_clkloss = "PORT_UNUSED",
    parameter port_clkswitch = "PORT_UNUSED",
    parameter port_configupdate = "PORT_UNUSED",
    parameter port_fbin = "PORT_UNUSED",
    parameter port_phasecounterselect = "PORT_UNUSED",
    parameter port_phasedone = "PORT_UNUSED",
    parameter port_phaseinc = "PORT_UNUSED",
    parameter port_phaseshift = "PORT_UNUSED",
    parameter port_scanaclr = "PORT_UNUSED",
    parameter port_scanclk = "PORT_UNUSED",
    parameter port_scanclkena = "PORT_UNUSED",
    parameter port_scandata = "PORT_UNUSED",
    parameter port_scandataout = "PORT_UNUSED",
    parameter port_scandone = "PORT_UNUSED",
    parameter port_scanread = "PORT_UNUSED",
    parameter port_scanwrite = "PORT_UNUSED",
    parameter self_reset_on_loss_of_lock = "OFF",
    parameter width_clock = 5
) (
    input  [1:0]  inclk,
    input         areset,
    input         clkswitch,
    input         configupdate,
    input  [3:0]  phasecounterselect,
    input         phaseinc,
    input         phaseshift,
    input         scanaclr,
    input         scanclk,
    input         scanclkena,
    input         scandata,
    input         scanread,
    input         scanwrite,
    input  [0:0]  clkena,
    input  [0:0]  extclkena,
    input         fbin,
    output [4:0]  clk,
    output        locked,
    output        activeclock,
    output [1:0]  clkbad,
    output        clkloss,
    output        c1, c2, c3, c4, c5,
    output [3:0]  extclk,
    output        fbmimicbidir,
    output        fbout,
    output        phasedone,
    output        scandataout,
    output        scandone,
    output        sclkbusy
);
    // Simple passthrough: clk[0] = inclk[0], locked when not in reset
    assign clk[0]  = inclk[0];
    assign clk[4:1] = 4'b0;
    assign locked  = ~areset;

    // Tie off unused outputs
    assign activeclock = 1'b0;
    assign clkbad = 2'b00;
    assign clkloss = 1'b0;
    assign c1 = 1'b0; assign c2 = 1'b0; assign c3 = 1'b0;
    assign c4 = 1'b0; assign c5 = 1'b0;
    assign extclk = 4'b0;
    assign fbmimicbidir = 1'b0;
    assign fbout = 1'b0;
    assign phasedone = 1'b0;
    assign scandataout = 1'b0;
    assign scandone = 1'b0;
    assign sclkbusy = 1'b0;
endmodule
