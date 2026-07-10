#
# Example showing SEI resistivity as a function of electrode temperature
#
import pybamm

pybamm.set_logging_level("NOTICE")


def sei_resistivity(T):
    """SEI resistivity equal to R_ref at T_ref, increasing at lower temperature."""
    R_ref = 200000.0
    T_ref = 298.15
    E_a = 15000.0
    return R_ref * pybamm.exp(
        E_a / pybamm.constants.R * (1 / T - 1 / T_ref)
    )


model_options = {
    "SEI": "constant",
    "thermal": "lumped",
}
parameter_values = pybamm.ParameterValues("Marquis2019")

constant_resistivity_params = parameter_values.copy()
constant_resistivity_params.update({"SEI resistivity [Ohm.m]": 200000.0})

temperature_dependent_params = parameter_values.copy()
temperature_dependent_params.update({"SEI resistivity [Ohm.m]": sei_resistivity})

simulations = [
    pybamm.Simulation(
        pybamm.lithium_ion.SPM(model_options, name="constant SEI rho"),
        parameter_values=constant_resistivity_params,
    ),
    pybamm.Simulation(
        pybamm.lithium_ion.SPM(model_options, name="temperature-dependent SEI rho"),
        parameter_values=temperature_dependent_params,
    ),
]

t_eval = [0, 3600]
for simulation in simulations:
    simulation.solve(t_eval)

final_time = t_eval[-1]
for simulation in simulations:
    solution = simulation.solution
    temperature = solution["X-averaged cell temperature [K]"](final_time).item()
    resistance = solution[
        "X-averaged negative electrode resistance [Ohm.m2]"
    ](final_time).item()
    print(
        f"{simulation.model.name}: T={temperature:.2f} K, "
        f"R_sei*L_sei={resistance:.3e} Ohm.m2"
    )

pybamm.dynamic_plot(
    simulations,
    [
        "Voltage [V]",
        "X-averaged cell temperature [K]",
        "X-averaged negative electrode resistance [Ohm.m2]",
    ],
)
