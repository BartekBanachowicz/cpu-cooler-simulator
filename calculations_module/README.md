# calculations_module

This module provides basic functions that are used in the cpu_cooler_simulator project.

## Changes in version 0.1.0

The function which provides data, was renamed to `data_generator`. Now it also yields starting data and can be reset if necessary, with the `.send()` method.

## usage example

```python
import calculations

def main():
    # define basic structures
    constants = calculations.generate_constants()
    parameters = calculations.generate_parameters()
    # initialize the generator, using real data
    generator = calculations.data_generator(0.0, 0.0, constants, parameters)
    # create callback function, provide data that is needed by using keyword arguments
    # in the decorator
    @calculations.import_data(generator=generator)
    def callback(generator):
        """Provides data for visualization."""
        # get values from the generator by using
        next(generator)
        # you can also reset the generator with the send method
        generator.send(True)
    # calculation.import_data can be used for every other function
    # that needs access to global data.
    # Ensure that the data structure you are passing, doesn't get copied.
```
