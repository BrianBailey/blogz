from flask import Flask, request, redirect, render_template, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "root"

db = SQLAlchemy(app)


class Blog(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100))
	body = db.Column(db.String(500))
	# create owner_id/user_id
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	# from get it done app
	def __init__(self, title, body, user):
		self.title = title
		self.body = body
		self.user = user

# just like get it done.. username for email
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(50))
	blogs = db.relationship('Blog', backref='user')
	
	def __init__(self,username,password):
		self.username = username
		self.password = password




# just like get it done , blog signup index difference 
@app.before_request
def require_login():
	whitelist = ['login','blog','index','signup']
	# endpoint is name of view function, not the url path
	if request.endpoint not in whitelist and 'user' not in session:
		return redirect("/login")

	
@app.route("/blog")

def blog():
	

	#same as build a blog 
	if request.args.get('id'):
		blog_id = request.args.get('id')
		blog = Blog.query.filter_by(id=blog_id).first()
		# returning Post with the blog id
		return render_template("singleUser.html", blog = blog, title="Post #" + blog_id)
    
	#this is all key to making this all tie in properly
	elif request.args.get('user'):
		# should substitute owner_id for the user_id variable
		user_id = request.args.get('user')
		entries = Blog.query.filter_by(user_id=user_id).all()
		
		
		return render_template("blog.html", entries=entries, title="Posts by " + user_id)
	
	else:
		# same as build a blog but with entries, title
		entries = Blog.query.all()
		
		return render_template("blog.html", entries=entries, title="All Posts")
 
# similar to build a blog
@app.route("/newpost", methods=['POST', 'GET'])

def newpost():
	if request.method == 'POST':
		if not request.form['title'] or not request.form['body']:
			if not request.form['title']:
				flash("*'Title for new blog' text area cannot be blank.")
			if not request.form['body']:
				flash("*'Your new blog' text area can't be empty")
			return render_template("newpost.html", title="New Post")
		
		blog_title = request.form['title']
		blog_body = request.form['body']
        # very key filter query
		user = User.query.filter_by(username=session['user']).first()


		post = Blog(blog_title, blog_body,user)
		db.session.add(post)
		db.session.commit()

		flash("New post created")
		
		id = str(post.id)
		
		return redirect("/blog?id=" + id)
	
	return render_template("newpost.html", title="New Post")


#  Now going into user sign-up (check details)etc to tie all this together, check exact wording of demo app on flash errors

@app.route("/signup", methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		errors = 0
		if not request.form['username']:
			flash("Username cannot be blank.")
			errors+= 1
		if len(request.form['username']) < 3:
			flash("Invalid username")
			errors+= 1
		if not request.form['password']:
			flash("Password cannot be blank.")
			errors+= 1
		if len(request.form['password']) < 3:
			flash("invalid password")
			errors+= 1
		if not request.form['verify']:
			flash("Password verification cannot be blank.")
			errors+= 1
		if request.form['password'] != request.form['verify']:
			flash("Passwords do not match.")
			errors+= 1 
		if request.form['username'] and User.query.filter_by(username=request.form['username']).first():
			flash("Username already exists.")
			 
			errors+= 1
		if errors > 0:
			return render_template("signup.html", title="Signup")		
		else:					
			username = request.form['username']
			password = request.form['password']
			verify = request.form['verify']
			
			user = User(username, password)
			db.session.add(user)
			db.session.commit()
			
			session['user'] = username
			flash("Logged in as " + username)
			return redirect("/newpost")		
	
	return render_template("signup.html", title="Signup")
		
## login GET and POST routes
@app.route("/login", methods=['GET','POST'])
def login():
	if request.method == 'POST':
		errors = 0 # set error count to zero for each new POST request
		if not request.form['username']:
			flash("Username cannot be blank.")
			errors += 1
		if not request.form['password']:
			flash("Password cannot be blank.")
			errors += 1
		if request.form['username'] and not User.query.filter_by(username=request.form['username']).first():
			flash("Invalid username")
			errors += 1

		if errors > 0:
			return render_template("login.html", title="Login")		
		else:
			username = request.form['username']
			password = request.form['password']
			
			user = User.query.filter_by(username=username).first()
			if password != user.password:
				flash("Invalid password")
				return render_template("login.html", title="Login")
			
			session['user'] = username
			flash("Logged in as " + username)
			return redirect("/newpost")	
	
	return render_template("login.html", title="Login")

@app.route("/logout")
def logout():
	del session['user']
	return redirect("/blog")
	
@app.route("/")
def index():
	users = User.query.all()
	# user_index.html should be index.html 
	return render_template("index.html", users=users, title="blog users!")



if __name__ == "__main__":
	app.run()