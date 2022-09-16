import Settings
import DailyWACOutput as dwaco
import numpy as np

def main():
    dailywacouput = dwaco.DailyWACOutput(Settings.lat,
        Settings.long, 180, 10, 31, 15, Settings.api_key)

    
    #rurl = dailywacouput.generate_request_url( 0, 10 )
    #ac_out = dailywacouput.query_acoutput_from_nrel( rurl )
    #wacav = dailywacouput.calculate_daily_ac_average(ac_out, 0, 0)
    #print( wacav )
    dailywacouput.scan_azimuths_tilts()
    #dailywacouput.calculate_daily_ac_average_full_output()
    dailywacouput.write_average_ac_to_csv()
    return 0

if __name__ == "__main__":
    main()
