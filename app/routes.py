from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import pdb

app = Flask(__name__)

# Настройки подключения к базе данных PostgreSQL
DB_HOST = 'localhost'
DB_NAME = 'shop'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        return conn
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL:", e)
        return None

@app.route('/')
def index():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM presents")
        data = cursor.fetchall()
        conn.close()
        return render_template('index.html', data=data[:2])
    return "Failed to connect to database."

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/catalog')
def catalog():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM presents")
        data = cursor.fetchall()
        conn.close()
        return render_template('catalog.html', data=data)
    return "Failed to connect to database."

@app.route('/add_to_basket', methods=['POST'])
def add_to_cart():
    item_name = request.form['item_name']
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM presents WHERE name='{item_name}'")
        item_data = cursor.fetchone()
        cursor.execute(f"INSERT INTO baskets (product_name, price, quantity, total) VALUES ('{item_data[1]}', {item_data[3]}, 1, {item_data[3]});")
        conn.close()
        return redirect(url_for('catalog'))
    return "Failed to connect to database."

@app.route('/basket')
def basket():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM baskets")
        data = cursor.fetchall()
        if data:
            cursor.execute("SELECT product_name FROM baskets")
            presents_names = cursor.fetchall()

            presents_data = []
            total = 0
            for name in presents_names:
                cursor.execute(f"SELECT * FROM presents WHERE name='{name[0]}'")
                pr_data = cursor.fetchone()
                total += pr_data[3]
                presents_data.append(pr_data)
            
            # pdb.set_trace()
            return render_template('basket.html', data=data, presents_data=presents_data, total=total)
        # pdb.set_trace()
        conn.close()
        return render_template('basket.html', data=data)
    return "Failed to connect to database."

@app.route('/delete_from_basket', methods=['POST'])
def delete_from_basket():
    item_name = request.form['item_name']
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM baskets WHERE product_name='{item_name}';")
        conn.close()
        return redirect(url_for('basket'))
    return "Failed to connect to database."

@app.route('/delete_all', methods=['POST'])
def delete_all():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM baskets;")
        conn.close()
        return redirect(url_for('basket'))
    return "Failed to connect to database."

if __name__ == '__main__':
    app.run(debug=True, port=8000)
