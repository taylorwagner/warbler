Part 1 Step 7 Research and Understand Login Strategy

- How is the logged in user being kept track of?
- The logged in user is being kept track of in a Flask storage object, g.

- What is Flask's "g" object?
- Flask provides a "g" (global) object to store common data during a request. In this case, g is referencing the data being global within a context; thus, data on g is lost after the context ends and isn't an appopriate place to store data between requests. Session is needed to store data across requests.
- source: https://flask.palletsprojects.com/en/2.0.x/appcontext/#storing-data

- What is the purpose of add_user_to_g?
- The purpose of the add_user_to_g is to add and keep the user in the Flask g object when the user logs in until the user logs out. The user is stored across requests to avoid requiring the user to continually log in to keep authorization in app.

- What does @app.before_request mean?
- This decorator function is to be ran before each request; in the case of this app, to load the logged in user from the session.
- source: https://flask.palletsprojects.com/en/2.0.x/api/#flask.Flask.before_request