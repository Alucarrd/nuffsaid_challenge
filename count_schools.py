from helper import csv_dict_aggregator, read_school_csv


def print_counts():
    school_file = 'school_data.csv'
    my_school_list = read_school_csv(school_file)
    print(f"Total schools: {len(my_school_list)}")

    print("Schools by State:")
    my_state_data = csv_dict_aggregator(my_school_list,"LSTATE05" )
    { print(f"{key}: {value}") for key, value in my_state_data.items() }

    print("Schools by Metro-centric locale:")
    my_metro_data = csv_dict_aggregator(my_school_list,"MLOCALE" )
    for key in sorted(my_metro_data.keys()):
        print(f"{key}: {my_metro_data[key]}")

    #We are creating a new field since we do not wish to mix up cities with the same name in different state
    for document in my_school_list:
        document["STATE-CITY"] = document["LSTATE05"]+document["LCITY05"]

    my_city_data = csv_dict_aggregator(my_school_list,"STATE-CITY" )
    sorted_city = sorted(my_city_data.items(), key=lambda x: x[1], reverse=True)
    state_city, count = sorted_city[0]
    print(f"City with most schools: {state_city[2:]} ({count} schools)")
    print(f"Unique cities with at least one school: {len(my_city_data.keys())}")
            

