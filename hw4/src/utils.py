
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix


def prefilter_items(data, take_n_popular=5000, item_features=None):
    # Уберем самые популярные товары (их и так купят)
    popularity = data.groupby('item_id')['user_id'].nunique().reset_index() / data['user_id'].nunique()
    popularity.rename(columns={'user_id': 'share_unique_users'}, inplace=True)

    top_popular = popularity[popularity['share_unique_users'] > 0.2].item_id.tolist()
    data = data[~data['item_id'].isin(top_popular)]

    # Уберем самые НЕ популярные товары (их и так НЕ купят)
    top_notpopular = popularity[popularity['share_unique_users'] < 0.02].item_id.tolist()
    data = data[~data['item_id'].isin(top_notpopular)]

    # Уберем товары, которые не продавались за последние 12 месяцев

    # Уберем не интересные для рекоммендаций категории (department)
    if item_features is not None:
        department_size = pd.DataFrame(item_features. \
                                       groupby('department')['item_id'].nunique(). \
                                       sort_values(ascending=False)).reset_index()

        department_size.columns = ['department', 'n_items']
        rare_departments = department_size[department_size['n_items'] < 150].department.tolist()
        items_in_rare_departments = item_features[
            item_features['department'].isin(rare_departments)].item_id.unique().tolist()

        data = data[~data['item_id'].isin(items_in_rare_departments)]

    # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб.
    data['price'] = data['sales_value'] / (np.maximum(data['quantity'], 1))
    data = data[data['price'] > 2]

    # Уберем слишком дорогие товарыs
    data = data[data['price'] < 50]

    # Возбмем топ по популярности
    popularity = data.groupby('item_id')['quantity'].sum().reset_index()
    popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)

    top = popularity.sort_values('n_sold', ascending=False).head(take_n_popular).item_id.tolist()

    # Заведем фиктивный item_id (если юзер покупал товары из топ-5000, то он "купил" такой товар)
    data.loc[~data['item_id'].isin(top), 'item_id'] = 999999

    # ...

    return data


def get_similar_users_recommendation(user, model,id_to_itemid, userid_to_id, N=5):
    """Рекомендуем топ-N товаров, среди купленных похожими юзерами"""

    # your_code
    similar_users = model.similar_users(userid_to_id[user], N=N + 1)
    res = [id_to_itemid[rec[0]] for rec in similar_users]
    return res[1:]


def get_similar_items_recommendation(user, model,userid_to_id, id_to_itemid, N=5):
    """Рекомендуем товары, похожие на топ-N купленных юзером товаров"""

    # your_code
    similar_items = model.similar_items(userid_to_id[user], N=3)
    res = [id_to_itemid[rec[0]] for rec in similar_items]

    return res

def get_recommendations(user, model, id_to_itemid, userid_to_id, user_item_matrix, itemid_to_id, N=5):
    res = [id_to_itemid[rec[0]] for rec in
                    model.recommend(userid=userid_to_id[user],
                                    user_items=csr_matrix(user_item_matrix).tocsr(),   # на вход user-item matrix
                                    N=N,
                                    filter_already_liked_items=False,
                                    filter_items=[itemid_to_id[999999]],  # !!!
                                    recalculate_user=False)]
    return res


def postfilter_items(user_id, recommednations):
    pass
