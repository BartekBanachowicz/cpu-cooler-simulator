# calculations_module

This module provides basic functions that are used in the cpu_cooler_simulator project.

## usage example

```python
import calculations

def main():
    # define basic structures
    constants = calculations.generate_constants()
    parameters = calculations.generate_parameters()
    # initialize the generator, using real data
    generator = calculations.data_iterator(0.0, 0.0, 0.0, 0.0, constants, parameters)
    # create callback function, provide data that is needed by using keyword arguments
    # in the decorator
    @calculations.import_data(generator=generator)
    def callback(generator):
        """Provides data for visualization."""
        # get values from the generator by using
        next(generator)
    # You can also use calculation.import_data decorator for every other function
    # that needs access to global data.
    # Ensure that the data structure you are passing, doesn't get copied.
```