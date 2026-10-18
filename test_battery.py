import pytest
from battery import Battery, ThresholdBattery


class TestCheckInitialStateOfCharge:
    def test_raises_value_error_when_below_zero(self):
        with pytest.raises(ValueError):
            Battery(initial_state_of_charge=-0.1)

    def test_raises_value_error_when_above_one(self):
        with pytest.raises(ValueError):
            Battery(initial_state_of_charge=1.1)

    def test_does_not_raise_when_exactly_zero(self):
        battery = Battery(initial_state_of_charge=0)
        battery.check_initial_state_of_charge()

    def test_does_not_raise_when_exactly_one(self):
        battery = Battery(initial_state_of_charge=1)
        battery.check_initial_state_of_charge()

    def test_does_not_raise_when_between_zero_and_one(self):
        battery = Battery(initial_state_of_charge=0.5)
        battery.check_initial_state_of_charge()


class TestCheckThreshold:
    def test_raises_value_error_when_upper_below_lower(self):
        with pytest.raises(ValueError):
            ThresholdBattery(lower_threshold=50, upper_threshold=40)

    def test_raises_value_error_when_upper_equal_to_lower(self):
        with pytest.raises(ValueError):
            ThresholdBattery(lower_threshold=50, upper_threshold=50)

    def test_does_not_raise_when_upper_above_lower(self):
        battery = ThresholdBattery(lower_threshold=40, upper_threshold=50)
        battery.check_threshold()
