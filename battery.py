from abc import ABC, abstractmethod
import math


class Battery(ABC):
    """A generic battery object with a state of charge between 0 and 1 and no
    limits on the rate of dispatch.
    """
    def __init__(self, initial_state_of_charge: float = 0):
        self.initial_state_of_charge = initial_state_of_charge
        self.check_initial_state_of_charge()
        self.current_state_of_charge = self.initial_state_of_charge

    def check_initial_state_of_charge(self):
        if math.isnan(self.initial_state_of_charge):
            raise ValueError("Initial state of charge must not be nan")
        if self.initial_state_of_charge < 0 or self.initial_state_of_charge > 1:
            raise ValueError("Initial state of charge must be between 0 and 1")

    @abstractmethod
    def dispatch(self, price: float) -> float:
        """Return the energy dispatched at this price (negative when charging)
        and update the current state of charge.
        """

class ThresholdBattery(Battery):
    """A battery that dispatches based on fixed price thresholds."""
    def __init__(self,
                 lower_threshold: float,
                 upper_threshold: float,
                 initial_state_of_charge: float = 0):
        super().__init__(initial_state_of_charge)
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold
        self.check_threshold()

    def check_threshold(self):
        if not (math.isfinite(self.lower_threshold) and math.isfinite(self.upper_threshold)):
            raise ValueError("Thresholds must not be infinite or nan")
        if self.upper_threshold <= self.lower_threshold:
            raise ValueError("Upper threshold must be strictly greater than lower threshold")

    def dispatch(self, price: float) -> float:
        energy_to_dispatch = 0
        if price >= self.upper_threshold:
            energy_to_dispatch = self.current_state_of_charge
            self.current_state_of_charge = 0
        elif price <= self.lower_threshold:
            energy_to_dispatch = - (1 - self.current_state_of_charge)
            self.current_state_of_charge = 1
        return energy_to_dispatch
