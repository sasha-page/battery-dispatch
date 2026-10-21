from abc import ABC, abstractmethod
import math


class Battery(ABC):
    """A generic battery object with a state of charge between 0 and 1 and no
    limits on the rate of dispatch.
    """
    def __init__(self, initial_state_of_charge: float = 0):
        self._set_state_of_charge(initial_state_of_charge)

    @property
    def current_state_of_charge(self) -> float:
        return self._current_state_of_charge

    def _set_state_of_charge(self, value: float) -> None:
        """Set the current state of charge.

        Raises ValueError if the value is not between 0 and 1, which includes
        nan since every comparison with nan is false.
        """
        if not 0 <= value <= 1:
            raise ValueError("State of charge must be between 0 and 1")
        self._current_state_of_charge = value

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
        self._upper_threshold = upper_threshold
        self._lower_threshold = lower_threshold
        self._check_threshold()

    def _check_threshold(self) -> None:
        if not (math.isfinite(self._lower_threshold) and math.isfinite(self._upper_threshold)):
            raise ValueError("Thresholds must not be infinite or nan")
        if self._upper_threshold <= self._lower_threshold:
            raise ValueError("Upper threshold must be strictly greater than lower threshold")

    def dispatch(self, price: float) -> float:
        energy_to_dispatch = 0
        if price >= self._upper_threshold:
            energy_to_dispatch = self.current_state_of_charge
            self._set_state_of_charge(0)
        elif price <= self._lower_threshold:
            energy_to_dispatch = - (1 - self.current_state_of_charge)
            self._set_state_of_charge(1)
        return energy_to_dispatch
