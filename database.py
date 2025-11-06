# Данные автомобилей (заглушка)
car_data = {
   "0001": {
      "id": "0001",
      "image_path": "bmw_3_series.png",
      "title": "BMW 3 Series",
      "subtitle": "2.0 л • 2018 год • Автомат",
      "price": "2 000 000 ₽",
      "VIN": "1HGCM82633A123456",
      "brand": "BMW",
      "model": "3 Series",
      "year": 2018,
      "color": "Чёрный",
      "engine_type": "Бензиновый",
      "engine_volume": "2.0 л",
      "engine_power": "184 л.с.",
      "transmission": "Автоматическая",
      "configuration": "Sport Line",
      "description": "BMW 3 Series — спортивный седан с мощным двигателем и динамичным управлением. В нём сочетаются спортивный стиль и высокий уровень комфорта, что делает его идеальным выбором для тех, кто ценит активный образ жизни."
   },

   "0002": {
      "id": "0002",
      "image_path": "audi_a4.png",
      "title": "Audi A4",
      "subtitle": "2.0 л • 2022 год • Механика",
      "price": "1 800 000 ₽",
      "VIN": "1HGCM82633A123456",
      "brand": "Audi",
      "model": "A4",
      "year": 2022,
      "color": "Красный",
      "engine_type": "Бензиновый",
      "engine_volume": "2.0 л",
      "engine_power": "190 л.с.",
      "transmission": "Механическая",
      "configuration": "Premium Edition",
      "description": "Audi A4 — современный седан с высокими показателями безопасности, комфорта и динамики. В нём сочетаются спортивный стиль и премиальные материалы отделки салона, что делает его идеальным выбором для тех, кто ценит качество и роскошь."
   },

   
   "0003": {
      "id": "0003",
      "image_path": "mercedes_benz.png",
      "title": "Mercedes-Benz",
      "subtitle": "2.0 л • 2020 год • Автомат",
      "price": "2 200 000 ₽",
      "VIN": "1HGCM82633A123456",
      "brand": "Mercedes-Benz",
      "model": "E-class",
      "year": 2020,
      "color": "Белый",
      "engine_type": "Бензиновый",
      "engine_volume": "2.0 л",
      "engine_power": "184 л.с.",
      "transmission": "Автоматическая",
      "configuration": "AMG Line",
      "description": "Mercedes-Benz E-Class — представительский седан с высоким уровнем комфорта, оснащённый современными системами безопасности, адаптивной подвеской и премиальными материалами отделки салона. Отличное сочетание мощности, динамики и элегантности."
   },

   "0004": {
      "id": "0004",
      "image_path": "nissan_quashqai.png",
      "title": "Nissan Quashqai",
      "subtitle": "2.0 л • 2021 год • Полуавтомат",
      "price": "1 500 000 ₽",
      "VIN": "1HGCM82633A123456",
      "brand": "Nissan",
      "model": "Quashqai",
      "year": 2021,
      "color": "Серый",
      "engine_type": "Бензиновый",
      "engine_volume": "2.0 л",
      "engine_power": "184 л.с.",
      "transmission": "Полуавтоматическая",
      "configuration": "Sport Edition",
      "description": "Nissan Quashqai — кроссовер с высокими показателями безопасности, комфорта и динамики. В нём сочетаются спортивный стиль и премиальные материалы отделки салона, что делает его идеальным выбором для тех, кто ценит качество и роскошь."
   }
}

def get_car(car_id):
   """Получение данных автомобиля по идентификатору
   Args:
      car_id (str): Идентификатор автомобиля
   
   Returns:
      dict: Данные автомобиля (или None, если не найден)
   """
   return car_data.get(car_id, None)


def get_all_cars():
   """Получение данных всех автомобилей
   Returns:
      list: Данные всех автомобилей
   """

   return list(car_data.values())