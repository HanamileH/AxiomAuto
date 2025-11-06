import csv

car_data = {}

def load_data():
   """Загружаем данные о машинах из файла cars_data.csv
   (Заглушка, в будущем должна будет загружать данные из БД)
   """
   global car_data
   
   with open('cars_data.csv', newline='', encoding='utf-8') as csvfile:
      reader = csv.DictReader(csvfile, delimiter=';')
      for row in reader:
         car_data[row['id']] = row
      

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