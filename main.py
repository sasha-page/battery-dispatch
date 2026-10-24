from pathlib import Path
from datetime import datetime, date
import csv
import requests
import pandas as pd
from input import month_ranges, clean_dayahead_prices
from battery import ThresholdBattery

def main():
    start_date = date.strptime("2026-01-01", "%Y-%m-%d")
    end_date = date.strptime("2026-10-31", "%Y-%m-%d")

    dayahead_price_url = "https://api.neso.energy/api/3/action/datastore_search_sql"
    dayahead_resource_id = "4f27eea5-7038-4f73-9740-e3e4ad47c26a"
    dayahead_columns = ["Date", "Delivery Period", "Price"]

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

    chunks = month_ranges(start_date, end_date)
    for chunk in chunks:
        chunk_label = chunk["label"]
        chunk_start_date = chunk["start_date"]
        chunk_end_date = chunk["end_date"]
        try:
            dayahead_sql = f"""
                SELECT "{'", "'.join(dayahead_columns)}" FROM "{dayahead_resource_id}"
                WHERE "Date" >= '{chunk_start_date.strftime("%Y-%m-%d")}'
                AND "Date" <= '{chunk_end_date.strftime("%Y-%m-%d")}'
            """
            dayahead_request = requests.get(dayahead_price_url, {"sql": dayahead_sql})
            dayahead_rows = dayahead_request.json()["result"]["records"]
        except requests.exceptions.ConnectionError:
            print("no connection")
            return

        data = pd.DataFrame(columns=output_columns)
        output_file_location = output_folder / f"{chunk_label}.csv"
        output_file = open(output_file_location, 'w', newline='')
        output_writer = csv.writer(output_file)
        output_writer.writerow(output_columns)
        for row in dayahead_rows:
            row_data = clean_dayahead_prices(row)
            row_data["start_state_of_charge"] = battery.current_state_of_charge
            row_data["energy_dispatched"] = battery.dispatch(row_data["price"])
            row_data["end_state_of_charge"] = battery.current_state_of_charge
            row_data["profit"] = row_data["price"] * row_data["energy_dispatched"]
            output_list = [row_data[column] for column in output_columns]
            data.loc[data.shape[0]] = output_list
            output_writer.writerow(output_list)
        output_file.close()

if __name__ == "__main__":
    main()
