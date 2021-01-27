def prefilter_items(data_train):
    # Оставим только 5000 самых популярных товаров
    popularity = data_train.groupby('item_id')['quantity'].sum().reset_index()
    popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)
    top_5000 = popularity.sort_values('n_sold', ascending=False).head(5000).item_id.tolist()
    #добавим, чтобы не потерять юзеров
    data_train.loc[~data_train['item_id'].isin(top_5000), 'item_id'] = 999999 
    
    
    
    # Уберем самые популярные 
    
    # Уберем самые непопулряные 
    
    # Уберем товары, которые не продавались за последние 12 месяцев
    
    # Уберем не интересные для рекоммендаций категории (department)
    
    # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб. 
    
    # Уберем слишком дорогие товарыs
    
    # ...
    
    return data_train
def postfilter_items():
    pass


def get_similar_users_recommendation(user, model1, model2, N):
    """Рекомендуем топ-N товаров, среди купленных похожими юзерами"""
    users = model1.similar_users(userid_to_id[user], 6)  # выбираем 6 похожих юзеров
    sim_users = []
    for i in range(6):
        sim_users.append(users[i][0])
    res = []
    for i in sim_users:
        res.append(
            get_recommendations(user=i, model=model2, sparse_user_item=csr_matrix(user_item_matrix).T.tocsr(), N=1)[0])

    res = res[:N]  # просто берем первые по списку, так как первые юзеры идут наиболее похожие
    return res