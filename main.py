from flask import Flask, render_template, redirect
import database

app = Flask(__name__)

# Главная страница (каталог)
@app.route('/')
def main():
   all_cars = database.get_all_cars()
   return render_template('catalog.html', cars=all_cars)


# Страница описания автомобиля
@app.route('/car/<car_id>')
def car(car_id):
   car_data = database.get_car(car_id)
   
   if car_data:
      return render_template('car.html', car=car_data)
   else:
      return render_template('404.html'), 404


# Страница менеджера
@app.route('/staff')
def staff():
   return render_template("staff.html")


# Информация о компании
@app.route('/about')
def about():
   return render_template('about.html')


# Страница регистрации пользователя
@app.route('/register')
def register():
   return render_template('register.html')


# Страница авторизации пользователя
@app.route('/login')
def login():
   return render_template('login.html')


@app.errorhandler(404)
def page_not_found(e):
   return render_template('404.html'), 404

# Запускаем приложение
if __name__ == '__main__':
   database.load_data()
   app.run(debug=True)