
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, url_for, flash
import random
import math
from datetime import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y5L"F4Q3z\n\xec]/'


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@35.243.220.243/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.243.220.243/proj1part2"
#
DATABASEURI = "postgresql://aw3168:3060@35.231.103.173/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

def print_results(cursor):
    record = cursor.fetchone()
    second_record = cursor.fetchone()
    for row in cursor:
        print(list(row))


def randGen(n):
    random.seed(None)
    return random.randint(1, math.pow(10, n))

def generateRow(cursor, row):
    for result in cursor:
        row.append(result['product_name'])
        row.append(result['category'])
        row.append(result['cost'])
    cursor.close()
    print(row)
    return row

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/result',methods=['POST'])
def result():
    #cursor = g.conn.execute("""SELECT product_name, category, cost FROM product WHERE (product_name ='Crazy Rich Asians bok bok bitch') AND (category ='Sticker') AND (cost =3)""")

#error checking
    #if request.form['Qbutton'] == 'activeUser':

    n = request.form['pname']
    ca = request.form['category']
    co = request.form['cost']
    if (co == "range1"):
        co1 ="0"
        co2="3"
    elif (co =="range2"):
        co1="4"
        co2="13"
    elif (co =="range3"):
        co1="14"
        co2="19"
    elif (co=="range4"):
        co1="20"
        co2="28"
    #print(n,type(n),n=="")
    #print(ca,type(ca), ca=="")
    #print(co,type(co), co=="")
    
    if  (n=="" and ca!="" and co!=""):
        cursor = g.conn.execute("""SELECT product_id, product_name, category, cost FROM product WHERE category =%s AND cost>= %s AND cost <= %s;""",ca,co1,co2)
        print("cat and cost")
        #print(cursor.fetchone())
    elif (n!="" and ca=="" and co!=""):
        cursor = g.conn.execute("""SELECT product_id, product_name, category, cost FROM product WHERE product_name =%s AND cost >= %s AND cost <=%s;""",n,co1,co2)
        print("pname and cost")
    elif (n!="" and ca!="" and co==""):
        cursor = g.conn.execute("""SELECT product_id, product_name, category, cost FROM product WHERE product_name =%s AND category = %s;""",n,ca)
        print("cat and pname")
    elif (n=="" and ca=="" and co!=""):
        cursor = g.conn.execute("""SELECT product_id,product_name, category, cost FROM product WHERE cost >=%s AND cost <=%s;""",co1,co2)
        print("only cost")
    elif (n=="" and co=="" and ca!=""):
        cursor = g.conn.execute("""SELECT product_id, product_name, category, cost FROM product WHERE category = %s;""",ca)
        print("only category")
    elif (ca=="" and co=="" and n!=""): 
        cursor = g.conn.execute("""SELECT product_id, product_name, category, cost FROM product WHERE product_name = %s;""",n)
        print("only pname")
    elif(ca=="" and co=="" and n==""):
        cursor = g.conn.execute("SELECT product_id, product_name, category, cost FROM product;")
        print("all none")
    elif(n!="" and ca!="" and co!=""):
        cursor=g.conn.execute("""SELECT product_id, product_name, category, cost FROM product WHERE product_name=%s AND category = %s AND cost >=%s AND cost<=%s;"""%(n,ca,co1,co2))
        print("all have something")
    return render_template("result.html", content = cursor)

@app.route('/but', methods=["GET","POST"])
def but():
    if request.method=="POST":
        if request.form['action'] == 'activeUser':
            cursor = g.conn.execute(
                    """SELECT person.id, person.name, sum.total_item_pur, sum.orders
                FROM person INNER JOIN
                (SELECT id, SUM(quantity) as total_item_pur, COUNT(DISTINCT transaction_id) AS orders
                 FROM transaction
                 GROUP BY id)  sum
                ON(person.id=sum.id); """
                )
            return render_template("activeUser.html",cursor=cursor)
        elif request.form['action'] == 'avgCost':
            cursor = g.conn.execute(
                """SELECT transaction_id, SUM(product.cost * transaction.quantity) AS order_cost
                FROM product
                INNER JOIN transaction
                ON product.product_id = transaction.product_id
                GROUP BY transaction.transaction_id; """
                )
            return render_template("avgCost.html",cursor=cursor)
        elif request.form['action'] == 'noSale':
            cursor = g.conn.execute(
                """SELECT product_id, product_name
              FROM product
              WHERE product_id NOT IN
              (SELECT DISTINCT product_id
              FROM transaction);"""
              )
            return render_template("noSale.html",cursor=cursor)
    return render_template("but.html")
# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/product/<product_id>', methods=['GET', 'POST'])
def product(product_id):
    # show all product content
    cursor1=g.conn.execute("SELECT person.id, person.name, product_id, product_name, category, cost, description, picture_url FROM product INNER JOIN person ON  product.id = person.id WHERE product_id=%s;",product_id)
    #show all reviews
    cursor2=g.conn.execute("SELECT review_content, review_timestamp, person.id, product_id, person.name FROM review INNER JOIN person ON person.id = review.id WHERE product_id=%s;",product_id)

#show all tags
    cursor3=g.conn.execute("""SELECT * FROM tags WHERE product_id=%s;""",product_id)
    #product.html will show make own review box if user is signed in 
    # writes review 
    if request.method == 'POST':
        review = request.form['review']
        print (review);
        review_id = randGen(8)
        #cursor = g.conn.execute("SELECT CURRENT_DATE;")
        #dateTime=cursor.fetchone()
        now=datetime.now()
        dateTime = now.strftime("%Y-%m-%d")
        g.conn.execute("""INSERT INTO review (review_id, review_content,
            review_timestamp, id, product_id)
            VALUES (%s, %s, %s, %s, %s);""", review_id, review, dateTime, session['id'],product_id)
        return render_template("product.html",pinfo=cursor1, rinfo=cursor2, tinfo=cursor3, review=review_id)
   

    return render_template("product.html",pinfo=cursor1, rinfo=cursor2, tinfo=cursor3)

@app.route('/design',methods=["POST","GET"])
def design():
    if "id" in session:
        if request.method == 'POST':
            # same designer can't submit the same product twice
            pid = randGen(6)
            pname = request.form['pname']
            category = request.form['category']
            cost = request.form['cost']
            description = request.form['description']
            pic = request.form['ppic']
            id = session["id"]
            tag = request.form['tag']

            # if condition to check if insertion is successful
            g.conn.execute(
                """INSERT INTO product (product_id, product_name, category, cost, description, picture_url, id)VALUES (%s, %s, %s, %s, %s, %s, %s);""", pid, pname, category, cost, description, pic, id)
            g.conn.execute("""INSERT INTO tags (product_id, tag_name) VALUES(%s,%s);""", pid, tag)
            return redirect(url_for("user", usr=session['username']))
        else:
            return render_template('design.html')
    else:
        return render_template('login.html')


@app.route('/<usr>user', methods=['GET', 'POST'])
def user(usr):
    if "id" in session:# and session["username"]==usr: --> has an error that whatever handle it is renders logged in user porofile
        #print(session["id"])
        #print(session["username"])
        if request.method == 'POST':
            if request.form["action"] == "upUname":
                uName = request.form["uname"]
                g.conn.execute(
                    """UPDATE person SET username=%s WHERE id = %s;""", uName, session["id"])
                flash("Username updated successfully!")
                return render_template("user.html",value=session["name"])
            elif request.form["action"] == "upEmail":
                email = request.form["email"]
                g.conn.execute(
                    """UPDATE person SET email=%s WHERE id = %s;""", email, session["id"])
                flash("Email updated successfully!")
                return render_template("user.html",value=session["name"])
            elif request.form["action"] == "upURL":
                pic = request.form["picURL"]
                g.conn.execute(
                    """UPDATE person SET profile_picture_url=%s WHERE id = %s;""", pic, session["id"])
                flash("Picture URL updated successfully!")
                return render_template("user.html",value=session["name"])
        else:
            return render_template('user.html', value=session["name"])
    else:
        return render_template('login.html')


@app.route('/<usr>mail', methods=['GET', 'POST'])
def mail(usr):
    if "id" in session:
        cursor1 = g.conn.execute(
                "SELECT person.name, mail_id FROM bubble_mail INNER JOIN person ON person.id=bubble_mail.p2 WHERE p1=%s;", session['id'])
        cursor2 = g.conn.execute(
            "SELECT person.name, mail_id FROM bubble_mail INNER JOIN person ON person.id=bubble_mail.p1 WHERE p2=%s;", session['id'])
        return render_template('mail.html', name=session['name'], content1=cursor1, content2=cursor2)

    else:
        return render_template("login.html")


@app.route('/<mail_id>message', methods=['GET', 'POST'])
def message(mail_id):
    if "id" in session:
        cursor = g.conn.execute(
            """SELECT message_timestamp, name, message_content FROM person INNER JOIN 
            (SELECT message_content, message_timestamp, id FROM message 
            WHERE mail_id = %s ORDER BY message_timestamp ASC) X 
            ON X.id=person.id;""", mail_id)
        if request.method == 'POST':
            message = request.form['msg']
            message_id = randGen(8)
            g.conn.execute("""INSERT INTO message (message_id, message_content, mail_id, id)
                VALUES (%s, %s, %s, %s);""", message_id, message,  mail_id, session['id'])
            return render_template("message.html", content=cursor,mail=mail_id)
        else:
            return render_template('message.html', content=cursor, mail=mail_id)
    else:
        return render_template("login.html")

@app.route('/transaction<usr>')
def transaction(usr):
    if "id" in session:
        sid = session['id']
        cursor = g.conn.execute(
            """SELECT transaction_id, trans_timestamp, product_name,category, quantity, delivered
            from product INNER JOIN
            (SELECT transaction_id, trans_timestamp, product_id, vendor_name as delivered, quantity
            FROM transaction WHERE id=%s ORDER BY trans_timestamp ASC) X ON X.product_id = product.product_id;""",
            sid)
        return render_template('transaction.html', content=cursor)
    else:
        return render_template("login.html")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        cursor = g.conn.execute("""SELECT *  FROM person WHERE (username = '%s') AND (password ='%s')""" %(request.form['user'],request.form['password']))
        #header
        record = cursor.fetchone()
        print(record);
        if (record !=None):
            session['id'] = record[0]
            session['username'] = record[1]
            session['name'] = record[2]
            session['password'] = record[3]
            session['email'] = record[4]
            print("signed in!")
            print(request.form['user'])
            print(request.form['password'])
            return redirect(url_for('index'))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('id', None) 
    session.pop('username', None)
    session.pop('name', None)
    session.pop('password', None)
    session.pop('email',None)
    
    return redirect(url_for('index'))

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
