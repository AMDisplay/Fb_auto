import requests

def get_all_price(rate=None):
    """Получение списка стран с ценой"""
    product = 'instagram'

    headers = {
        'Accept': 'application/json',
    }

    params = (
        ('product', product),
    )



    response = requests.get('https://5sim.net/v1/guest/prices', headers=headers, params=params)
    response = response.json()
    result = get_value_country(response['instagram'], rate)
    print(result)
    return result


def get_value_country(json, rate=None):
    """Получение выгодной и качественной страны"""
    country_emp = ''
    operator_emp = ''
    count_emp = 0 

    # if rate is None:
    #     rate = 20
    # else:
    #     rate=rate
    for country, operator_list in json.items():
        for operator, price_and_count_list in operator_list.items():
            # if price_and_count_list.get('rate') is not None:
                price_and_count_list_with_rate = price_and_count_list
                # current_rate = price_and_count_list_with_rate['rate']
                if price_and_count_list_with_rate['count'] < 1000 and price_and_count_list_with_rate['count'] > 50:
                    current_cost = price_and_count_list_with_rate['cost']
                    if current_cost < 10:
                        cost = current_cost
                        country_emp = country
                        operator_emp = operator
                        count_emp = price_and_count_list_with_rate['count']
                        result = {
                            'country' : country_emp,
                            'operator' : operator_emp,
                            'cost' : cost,
                            'count' : count_emp,
                            # 'rate' : current_rate,
                        }
                        print(result)
                        return result

# get_all_price()