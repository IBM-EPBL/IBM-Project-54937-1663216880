from flask import Flask,render_template,request,session,flash
import re
import ibm_db

app = Flask(__name__)
app.secret_key="ayan"


conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=125f9f61-9715-46f9-9399-c8177b21803b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30426;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=qtg16997;PWD=cMD8dkRCO5kH4gzu",'','')


@app.route('/')
def hello():
   return render_template('home.html')

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/signup')
def signup():
   return render_template('signup.html')

@app.route('/test')
def test():
       sql="SELECT * FROM Users"
       stmt = ibm_db.exec_immediate(conn,sql)
       dictionary=ibm_db.fetch_both(stmt)
       print(dictionary)

@app.route('/register',methods = ['POST'])
def register():
   user_name = request.form.get("username")
   email = request.form.get("email")
   password = request.form.get("password")

   sql="INSERT INTO Users (Name,Email,Pass) VALUES(?,?,?)"
   prep_stmt = ibm_db.prepare(conn, sql)
   ibm_db.bind_param(prep_stmt, 1, user_name)
   ibm_db.bind_param(prep_stmt, 2, email)
   ibm_db.bind_param(prep_stmt, 3, password)
   ibm_db.execute(prep_stmt)
    
   return render_template('login.html', msg="Student Data saved successfuly..")

@app.route('/comein',methods = ['POST'])
def comein():
   email = request.form.get("email")
   password = request.form.get("password")

   sql="SELECT * FROM Users WHERE Email=? AND Pass=?"
   prep_stmt = ibm_db.prepare(conn, sql)
   ibm_db.bind_param(prep_stmt, 1, email)
   ibm_db.bind_param(prep_stmt, 2, password)
   ibm_db.execute(prep_stmt)
   account = ibm_db.fetch_assoc(prep_stmt)

   if account:
      return render_template('welcome.html')
   else:
      return render_template('login.html')

@app.route('/add_stock',methods=['GET','POST'])
def add_stock():
    mg=''
    if request.method == "POST":
        prodname=request.form['prodname']
        quantity=request.form['quantity']
        warehouse_location=request.form['warehouse_location'] 
        sql='SELECT * FROM product WHERE prodname =?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,prodname)
        ibm_db.execute(stmt)
        acnt=ibm_db.fetch_assoc(stmt)
        print(acnt)
            
        if acnt:
            mg='Product already exits!!'
        else:
            insert_sql='INSERT INTO product VALUES (?,?,?)'
            pstmt=ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(pstmt,1,prodname)
            ibm_db.bind_param(pstmt,2,quantity)
            ibm_db.bind_param(pstmt,3,warehouse_location)
            ibm_db.execute(pstmt)
            mg='You have successfully added the products!!'
            return render_template("welcome.html")      

    else:
        msg="fill out the form first!"
        return render_template('add_stock.html',meg=mg) 
        
@app.route('/view_stock')
def view_stock():
   
    sql = "SELECT * FROM product"
    stmt = ibm_db.prepare(conn, sql)
    result=ibm_db.execute(stmt)
    print(result)

    products=[]
    row = ibm_db.fetch_assoc(stmt)
    print(row)
    while(row):
        products.append(row)
        row = ibm_db.fetch_assoc(stmt)
        print(row)
    products=tuple(products)
    print(products)

    if result>0:
        return render_template('view.html', products = products)
    else:
        msg='No products found'
        return render_template('view.html', msg=msg)


@app.route('/logout')
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return render_template("home.html")



@app.route('/delete_stock',methods=['GET','POST'])
def delete_stock():
    if(request.method=="POST"):
        prodname=request.form['prodname']
        sql2="DELETE FROM product WHERE prodname=?"
        stmt2 = ibm_db.prepare(conn, sql2)    
        ibm_db.bind_param(stmt2,1,prodname)
        ibm_db.execute(stmt2)

        flash("Product Deleted", "success")

        return render_template("welcome.html")




@app.route('/delete')
def delete():
    return render_template('delete_stock.html')

@app.route('/update')
def update():
    return render_template('update_stock.html')



@app.route('/update_stock',methods=['GET','POST'])
def update_stock():
    mg=''
    if request.method == "POST":
        prodname=request.form['prodname']
        quantity=request.form['quantity']
        quantity=int(quantity)
        print(quantity)
        print(type(quantity))
        warehouse_location=request.form['warehouse_location'] 
        sql='SELECT * FROM product WHERE prodname =?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,prodname)
        ibm_db.execute(stmt)
        acnt=ibm_db.fetch_assoc(stmt)
        print(acnt)
            
        if acnt:
            insert_sql='UPDATE product SET  quantity=?,warehouse_location=? WHERE prodname=? '
            pstmt=ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(pstmt,1,quantity)
            ibm_db.bind_param(pstmt,2,warehouse_location)
            ibm_db.bind_param(pstmt,3,prodname)
            ibm_db.execute(pstmt)
            mg='You have successfully updated the products!!'
            limit=5
            print(type(limit))
            if(quantity<=limit):
                  alert("Please update the quantity of the product {}, Atleast {} number of pieces must be added!".format(prodname,10))
            return render_template("welcome.html",meg=mg)   
            
        else:
             mg='Product not found!!'
               

    else:
         msg="fill out the form first!"
         return render_template('update_stock.html',meg=msg)


if __name__ == '__main__':
      app.run()
