from read_json import (
    get_city_data,
    get_cities,
    get_cities_with_cevres,
    get_mv_counts,
    calculate,
    calculate_total,
    calculate_cevre
    )
import streamlit as st


def main():
    st.title("Seçim Simülasyon")
    city_id = st.slider("İl", 1, 81, 1)

    data = get_city_data(city_id)
    cities = get_cities()
    cities_with_cevres = get_cities_with_cevres()
    mv_counts = get_mv_counts()

    city_name = cities[str(city_id)]
    st.write("Seçilen il: ", city_name)
    if city_name not in cities_with_cevres:
        mv_count = mv_counts[city_name]
        context = calculate(data, mv_count)
        st.write("Milletvekili sayısı: ", mv_count)
    else:
        cevre_count = cities_with_cevres[city_name]["CevreSayisi"]
        cevre_id = st.slider("Çevre", 1, cevre_count, 1)
        context = calculate_cevre(city_id, cevre_id)
        st.write("Çevre sayısı: ", cevre_count)

    # prepare table
    ittifak_names = context["ittifak_names"]
    votes = context["votes"]
    result_ittifak = context["result_ittifak"]
    result = context["result"]
    oy_oranlari = context["oy_oranlari"]

    dict_headers = {
        "Parti": [item for sublist in ittifak_names for item in sublist],
        "Oy": [item for sublist in votes for item in sublist],
        "Oran": oy_oranlari,
        "Eski": [item for sublist in result_ittifak for item in sublist],
        "Yeni": result
    }

    st.table(dict_headers)

    result_ittifak_sums = [sum(x) for x in result_ittifak]
    ittifak_table_data = []
    for i in range(len(result_ittifak_sums)):
        ittifak_table_data.append([ittifak_names[i],result_ittifak_sums[i]])

    st.table(ittifak_table_data)

    ittifak_lengths = [len(x) for x in ittifak_names]
    new_system_ittifak_table_data = []
    for i,l in enumerate(ittifak_lengths):
        s = 0
        start = sum(ittifak_lengths[:i])
        end = sum(ittifak_lengths[:i+1])
        for j in range(start,end):
            s += result[j]
        new_system_ittifak_table_data.append([ittifak_names[i],s])
        
    st.table(new_system_ittifak_table_data)    

    total_data = calculate_total()
    st.table(total_data)


if __name__ == "__main__":
    main()