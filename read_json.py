import json
from dhondt import dhondt, dhondt_ittifak

def read_json(filename:str):
    with open(filename, "r",encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_city_data(city_id):
    data = read_json("data.json")
    return data[str(city_id)]


def get_cities():
    data = read_json("iller.json")
    return data


def get_mv_counts():
    data = read_json("mv.json")
    return data


def get_cities_with_cevres():
    data = read_json("cevre.json")
    return data

def calculate(data: dict, seats: int):
    pt_data = data["PartiSecimSonuclari"]
    vote_count = data["MilletVekiliGenelSecimSonuclari"]["GecerliOy"]
    count = len(pt_data)
    votes = []
    ittifak_ids = []
    ittifak_names = []
    oy_oranlari = []
    for i in range(count):
        ittifak_id = pt_data[i]["IttifakKod"]
        oran,oranStr = pt_data[i]["OyOrani"],pt_data[i]["OyOraniStr"]
        oy_oranlari.append(oranStr)
        vote = int(vote_count * oran / 100)
        if ittifak_id not in ittifak_ids:
            ittifak_ids.append(ittifak_id)
        
        elif ittifak_id == 0:
            kod = pt_data[i]["Kod"]
            ittifak_id = kod
            ittifak_ids.append(kod)
        
        index = ittifak_ids.index(ittifak_id)
        if len(votes) < index + 1:
            votes.append([vote])
            ittifak_names.append([pt_data[i]["Adi"]])
        else:
            votes[index].append(vote)
            ittifak_names[index].append(pt_data[i]["Adi"])

    flatten_votes = [item for sublist in votes for item in sublist]

    result = dhondt(flatten_votes, seats)
    result_ittifak = dhondt_ittifak(votes, seats)

    context = {}
    context["ittifak_names"] = ittifak_names
    context["votes"] = votes
    context["result_ittifak"] = result_ittifak
    context["result"] = result
    context["oy_oranlari"] = oy_oranlari

    return context


def calculate_total():
    data = read_json("data.json")
    cities = get_cities()
    cities_with_cevres = get_cities_with_cevres()
    mv_counts = get_mv_counts()
    parties_mv = {}
    for i in range(1,82):
        city_name = cities[str(i)]
        if city_name not in cities_with_cevres:
            mv_count = mv_counts[city_name]
            context = calculate(data[str(i)], mv_count)
            ittifak_names = context["ittifak_names"]
            mvs = context["result_ittifak"]
            for j in range(len(ittifak_names)):
                ittifak_name = ittifak_names[j]
                mv = mvs[j]
                for k,party_name in enumerate(ittifak_name):
                    if party_name not in parties_mv:
                        parties_mv[party_name] = mv[k]
                    else:
                        parties_mv[party_name] += mv[k]
        else:
            cevre_count = cities_with_cevres[city_name]["CevreSayisi"]
            for j in range(1,cevre_count+1):
                context = calculate_cevre(i,j)
                ittifak_names = context["ittifak_names"]
                mvs = context["result_ittifak"]
                for k in range(len(ittifak_names)):
                    ittifak_name = ittifak_names[k]
                    mv = mvs[k]
                    for l,party_name in enumerate(ittifak_name):
                        if party_name not in parties_mv:
                            parties_mv[party_name] = mv[l]
                        else:
                            parties_mv[party_name] += mv[l]

    # delete parties with 0 mv
    parties_mv = {k: v for k, v in parties_mv.items() if v != 0}
    return parties_mv


def calculate_cevre(il:int, cevre:int):
    cities = get_cities()
    city_data = get_city_data(il)
    cities_with_cevres = get_cities_with_cevres()

    city_name = cities[str(il)]

    if city_name not in cities_with_cevres:
        raise Exception("This city does not have cevre")
    
    try:
        cevre_data = cities_with_cevres[city_name]["Cevreler"][str(cevre)]
    except KeyError:
        raise Exception("This city does not have this cevre")
    
    ilceler = cevre_data["İlceler"]

    ilce_results = city_data["IlceSonuclari"]
    filtered_ilce_results = [
        ilce_result for ilce_result in ilce_results if ilce_result["Adi"] in ilceler
    ]


    votes = []
    ittifak_ids = []
    ittifak_names = []
    total_vote = 0
    for ilce_result in filtered_ilce_results:
        parti_results = ilce_result["PartiSecimSonuclari"]
        vote_count = ilce_result["MilletVekiliGenelSecimSonuclari"]["GecerliOy"]
        total_vote += vote_count
        for parti_result in parti_results:
            vote = int(vote_count * parti_result["OyOrani"] / 100)
            ittifak_location = None, None
            for sublist in ittifak_names:
                for item in sublist:
                    if item == parti_result["Adi"]:
                        ittifak_location1 = ittifak_names.index(sublist)
                        ittifak_location2 = sublist.index(item)
                        ittifak_location = ittifak_location1, ittifak_location2
                        break
            if ittifak_location == (None, None):
                ittifak_id = parti_result["IttifakKod"]
                if ittifak_id not in ittifak_ids:
                    ittifak_ids.append(ittifak_id)
                    ittifak_names.append([parti_result["Adi"]])
                    votes.append([vote])
                elif ittifak_id == 0:
                    kod = parti_result["Kod"]
                    ittifak_id = kod
                    ittifak_ids.append(kod)
                    ittifak_names.append([parti_result["Adi"]])
                    votes.append([vote])
                else:
                    ittifak_location = ittifak_ids.index(ittifak_id), 0
                    votes[ittifak_location[0]].append(vote)
                    ittifak_names[ittifak_location[0]].append(parti_result["Adi"])
            else:
                # increase vote count
                votes[ittifak_location[0]][ittifak_location[1]] += int(
                    vote_count * parti_result["OyOrani"] / 100
                )

    flatten_votes = [item for sublist in votes for item in sublist]

    mv = cevre_data["MilletvekiliSayisi"]
    result = dhondt(flatten_votes, mv)
    result_ittifak = dhondt_ittifak(votes, mv)

    context = {}
    context["ittifak_names"] = ittifak_names
    context["votes"] = votes
    context["result_ittifak"] = result_ittifak
    context["result"] = result

    oy_oranlari = []
    for i in range(len(votes)):
        oy_oranlari.append([])
        for j in range(len(votes[i])):
            oy_oranlari[i].append(votes[i][j]/total_vote*100)

    flatten_oy_oranlari = [item for sublist in oy_oranlari for item in sublist]
    context["oy_oranlari"] = flatten_oy_oranlari

    return context


def main():
    # city_id = 6
    # cevre = 1
    # result = calculate_cevre(city_id, cevre)
    # print(result)

    result = calculate_total()
    print(result)
    



if __name__ == "__main__":
    main()