import pytest
from battery import Battery, ThresholdBattery


class TestCheckInitialStateOfCharge:
    def test_raises_value_error_when_below_zero(self):
        with pytest.raises(ValueError):
            Battery(initial_state_of_charge=-0.1)

    def test_raises_value_error_when_above_one(self):
        with pytest.raises(ValueError):
            Battery(initial_state_of_charge=1.1)

    def test_raises_value_error_when_nan(self):
        with pytest.raises(ValueError):
            Battery(initial_state_of_charge=float("nan"))

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
    def test_raises_value_error_when_upper_threshold_below_lower_threshold(self):
        with pytest.raises(ValueError):
            ThresholdBattery(lower_threshold=50, upper_threshold=40)

    def test_raises_value_error_when_upper_threshold_equal_to_lower_threshold(self):
        with pytest.raises(ValueError):
            ThresholdBattery(lower_threshold=50, upper_threshold=50)

    @pytest.mark.parametrize(
        "lower_threshold, upper_threshold",
        [
            pytest.param(40, float("inf"), id="upper_inf"),
            pytest.param(float("-inf"), 50, id="lower_negative_inf"),
            pytest.param(40, float("nan"), id="upper_nan"),
            pytest.param(float("nan"), 50, id="lower_nan"),
            pytest.param(float("-inf"), float("nan"), id="lower_negative_inf_upper_nan"),
            pytest.param(float("nan"), float("inf"), id="lower_nan_upper_inf"),
            pytest.param(float("nan"), float("nan"), id="both_nan"),
        ],
    )
    def test_raises_value_error_when_threshold_not_finite(self, lower_threshold: float, upper_threshold: float):
        with pytest.raises(ValueError):
            ThresholdBattery(lower_threshold=lower_threshold, upper_threshold=upper_threshold)

    def test_does_not_raise_when_upper_threshold_above_lower_threshold(self):
        battery = ThresholdBattery(lower_threshold=40, upper_threshold=50)
        battery.check_threshold()


class TestDispatch:
    @staticmethod
    def battery(initial_state_of_charge: float) -> ThresholdBattery:
        return ThresholdBattery(lower_threshold=40,
                                upper_threshold=50,
                                initial_state_of_charge=initial_state_of_charge)

    def test_dispatches_nothing_when_price_between_thresholds(self):
        battery = self.battery(0.5)
        assert battery.dispatch(45) == 0
        assert battery.current_state_of_charge == 0.5

    def test_dispatches_nothing_when_price_above_upper_threshold_and_battery_empty(self):
        battery = self.battery(0)
        assert battery.dispatch(60) == 0
        assert battery.current_state_of_charge == 0

    def test_dispatches_nothing_when_price_below_lower_threshold_and_battery_full(self):
        battery = self.battery(1)
        assert battery.dispatch(30) == 0
        assert battery.current_state_of_charge == 1

    def test_dispatches_all_energy_when_price_above_upper_threshold(self):
        battery = self.battery(0.5)
        assert battery.dispatch(60) == 0.5
        assert battery.current_state_of_charge == 0

    def test_dispatches_all_energy_when_price_equal_to_upper_threshold(self):
        battery = self.battery(0.5)
        assert battery.dispatch(50) == 0.5
        assert battery.current_state_of_charge == 0

    def test_charges_fully_when_price_below_lower_threshold(self):
        battery = self.battery(0.25)
        assert battery.dispatch(30) == -0.75
        assert battery.current_state_of_charge == 1

    def test_charges_fully_when_price_equal_to_lower_threshold(self):
        battery = self.battery(0.25)
        assert battery.dispatch(40) == -0.75
        assert battery.current_state_of_charge == 1
