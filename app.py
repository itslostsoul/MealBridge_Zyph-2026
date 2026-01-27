from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key= 'mindflayers_secret_key'
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= '1975@'
app.config['MYSQL_DB']= 'mealbridge_db'

mysql= MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'users_id' not in session:
        return redirect(url_for('login'))
    if session['role']== 'donor':
        cur= mysql.connection.cursor()
        cur.execute("SELECT * FROM food_items WHERE donor_id = %s", [session['user_id']])
        my_food= cur.fetchall()
        return render_template('donor_dashboard.html', food=my_food)
    else:
        cur= mysql.connection.cursor()
        cur.execute("SELECT * FROM food_items WHERE status = 'available'")
        available_food= cur.fetchall()
        return render_template('recipient_dashboard.html', food=available_food)

@app.route('/post_food', methods=['POST'])
def post_food():
    if session['role']== 'donor':
        food_name= request.form['food_name']
        quantity= request.form['quantity']
        donor_id= session['user_id']
        cur= mysql.connection.cursor()
        cur.execute("INSERT INTO food_items (donor_id, name, quantity_kg) VALUES (%s, %s, %s)", (donor_id, food_name, quantity))
        cur.execute("UPDATE users SET green_points = green_points + 10 WHERE id = %s", [donor_id])
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('dashboard'))

@app.route('/claim_food/<int:food_id>')
def claim_food(food_id):
    if session['role']== 'recipient':
        recipient_id= session['user_id']
        cur= mysql.connection.cursor()
        cur.execute("UPDATE food_items SET status = 'claimed' WHERE id = %s", [food_id])
        cur.execute("INSERT INTO claims (food_id, recipient_id) VALUES (%s, %s)" (food_id, recipient_id))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('dashboard'))

if __name__== '__main__':

    app.run(debug=True)
