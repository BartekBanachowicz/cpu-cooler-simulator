from typing import Callable, Generator, Tuple
import functools
import itertools


def generate_parameters() -> dict:
    """Generates a dictionary filled with available parameters.

    :return:
    """
    result = {"assigned_temperature": 50.0, "fan_number": 1.0, "outside_temperature": 20.0, "generated_heat": 1.0}
    return result


def generate_constants() -> dict:
    """Generates a dictionary filled with available constants.

    :return:
    """
    result = {
        "k_kr": 0.3,
        "t_kr": 310,
        "p": 0.1,
        "q_c": 1.0,
        "s": 0.052,
        "k_p": 0.006,
        "t_d": 37.2,
        "t_i": 155,
        "rho_a": 1.293,
        "c_a": 721,
        "m_c": 0.01,
        "c_c": 706,
        "v_f": 0.04
    }
    return result


def import_data(
        _func: Callable[..., None] = None, *args, **kwargs
) -> Callable:
    """Passes necessary data into a function so it may be later used repeatedly without arguments.

    :param _func:
    :param parameters:
    :param constants:
    :param generator:
    :return:
    """
    def decorator_import_data(func: Callable[..., None]) -> Callable[[], None]:
        @functools.wraps(func)
        def wrapper_import_data():
            return func(**kwargs)
        return wrapper_import_data
    if _func is None:
        return decorator_import_data
    else:
        return decorator_import_data(_func)


def calculate_regulation_error(assigned_temperature: float, cpu_temperature: float) -> float:
    return assigned_temperature - cpu_temperature


def calculate_control_value(
        period: float, controller_gain: float, derivative_time: float, integral_time: float,
        regulation_error: float, previous_regulation_error: float, previous_control_value: float
) -> float:
    d_e = regulation_error - previous_regulation_error
    result = (
            previous_control_value + controller_gain * (
                d_e + period / integral_time * regulation_error + derivative_time / period * d_e**2
            )
    )
    result = max(min(0.0, result), -1.0)
    return result


def calculate_computer_transitive_volume(computer_volume: float, airflow_volume: float) -> float:
    return max(0.0, computer_volume - airflow_volume)


def calculate_air_transitive_temperature(
        airflow_volume: float, outside_temperature: float,
        computer_transitive_volume: float, computer_temperature: float
) -> float:
    result = (
        (airflow_volume * outside_temperature + computer_transitive_volume * computer_temperature) /
        (airflow_volume + computer_transitive_volume)
    )
    return result


def calculate_heat_received(
        period: float, airflow_volume: float, computer_transitive_volume: float,
        air_transitive_temperature: float, cpu_temperature: float
) -> float:
    result = (cpu_temperature - air_transitive_temperature) * (airflow_volume + computer_transitive_volume) * period
    return result


def calculate_airflow_volume(max_airflow_volume: float, control_value: float) -> float:
    result = -control_value * max_airflow_volume
    return max(min(max_airflow_volume, result), 0.0)


def calculate_computer_temperature(
        heat_received: float, computer_transitive_volume: float, air_density: float,
        air_specific_heat_capacity: float, air_transitive_temperature: float,
        airflow_volume: float
) -> float:
    result = heat_received / (
            (airflow_volume + computer_transitive_volume) * air_density * air_specific_heat_capacity
    ) + air_transitive_temperature
    return result


def calculate_cpu_temperature(
        heat_received: float, heat_generated: float, cpu_mass: float,
        cpu_specific_heat_capacity: float, previous_cpu_temperature: float
) -> float:
    result = (heat_generated - heat_received) / (cpu_mass * cpu_specific_heat_capacity) + previous_cpu_temperature
    return result


def data_generator(
        starting_computer_temperature: float, starting_cpu_temperature: float, constants: dict, parameters: dict
) -> Generator[Tuple[float, float, float, float, float], bool, None]:
    """Produces a generator that yields data sequences based on previous data and parameters.

    :param starting_computer_temperature:
    :param starting_cpu_temperature:
    :param constants:
    :param parameters:
    :return:
    """
    while True:
        previous_regulation_error = calculate_regulation_error(
            parameters["assigned_temperature"], starting_cpu_temperature
        )
        previous_control_value = 0.0
        previous_computer_temperature = starting_computer_temperature
        previous_cpu_temperature = starting_cpu_temperature
        yield 0.0, previous_control_value, 0.0, starting_computer_temperature, starting_cpu_temperature
        for i in itertools.count(1, 1):
            regulation_error = calculate_regulation_error(parameters["assigned_temperature"], previous_cpu_temperature)
            control_value = calculate_control_value(
                constants["p"], constants["k_p"], constants["t_d"], constants["t_i"],
                regulation_error, previous_regulation_error, previous_control_value
            )
            airflow_volume = calculate_airflow_volume(
                constants["s"] * parameters["fan_number"] * constants["p"], control_value
            )
            computer_transitive_volume = calculate_computer_transitive_volume(constants["v_f"], airflow_volume)
            air_transitive_temperature = calculate_air_transitive_temperature(
                airflow_volume, parameters["outside_temperature"],
                computer_transitive_volume, previous_computer_temperature
            )
            heat_received = calculate_heat_received(
                constants["p"], airflow_volume, computer_transitive_volume,
                air_transitive_temperature, previous_cpu_temperature
            )
            computer_temperature = calculate_computer_temperature(
                heat_received, computer_transitive_volume, constants["rho_a"],
                constants["c_a"], air_transitive_temperature, airflow_volume
            )
            cpu_temperature = calculate_cpu_temperature(
                heat_received, parameters["generated_heat"] * constants["p"],
                constants["m_c"], constants["c_c"], previous_cpu_temperature
            )
            stop = yield i * constants["p"] * 1000, control_value, airflow_volume, computer_temperature, cpu_temperature
            if stop:
                break
            previous_regulation_error = regulation_error
            previous_control_value = control_value
            previous_computer_temperature = computer_temperature
            previous_cpu_temperature = cpu_temperature
