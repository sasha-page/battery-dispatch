from pathlib import Path
from datetime import datetime
import csv
import requests
import pandas as pd
from data_streaming import CSVStream, clean_dayahead_price_row
from battery_dispatch import ThresholdBattery

def main():
    try:
        dayahead_price_url = "https://api.neso.energy/datastore/dump/4f27eea5-7038-4f73-9740-e3e4ad47c26a"
        dayahead_prices = CSVStream(dayahead_price_url)
    except requests.exceptions.ConnectionError:
        print("No connection.")
        return
    battery = ThresholdBattery(75, 175)
    output_folder = Path.cwd() / "output" / datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    output_folder.mkdir(parents=True, exist_ok=False)
    output_columns = ["start_date",
                      "end_date",
                      "price",
                      "energy_dispatched",
                      "profit",
                      "start_state_of_charge",
                      "end_state_of_charge"]

    new_chunk_label = None  # used to chunk and output data
    output_file = None
    row = dayahead_prices.get_next_row()
    while row:
        row_data = clean_dayahead_price_row(row, dayahead_prices.column_names)
        old_chunk_label = new_chunk_label
        new_chunk_label = datetime.strftime(row_data["start_date"], "%Y-%m")

        if new_chunk_label != old_chunk_label:
            data = pd.DataFrame(columns=output_columns)
            if output_file is not None:
                output_file.close()
            output_file_location = output_folder / f"{new_chunk_label}.csv"
            output_file = open(output_file_location, 'w', newline='')
            output_writer = csv.writer(output_file)
            output_writer.writerow(output_columns)

        row_data["start_state_of_charge"] = battery.current_state_of_charge
        row_data["energy_dispatched"] = battery.dispatch(row_data["price"])
        row_data["end_state_of_charge"] = battery.current_state_of_charge
        row_data["profit"] = row_data["price"] * row_data["energy_dispatched"]

        output_list = [row_data[column] for column in output_columns]
        data.loc[data.shape[0]] = output_list
        output_writer.writerow(output_list)

        row = dayahead_prices.get_next_row()

    if output_file is not None:
        output_file.close()

if __name__ == "__main__":
    main()
