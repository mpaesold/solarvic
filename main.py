import Settings
from classes import DailyWACOutput
import numpy as np

def main():
    dailywacouput = DailyWACOutput(Settings.lat,
        Settings.long, 180, 10, 31, 15)

    dailywacouput.scan_azimuths_tilts()
    dailywacouput.calculate_daily_ac_average()
    dailywacouput.write_average_ac_to_csv()
    return 0

if __name__ == "__main__":
    main()
