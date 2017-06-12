# i2x BuildYourTeam

### Project Setup
```
$ virtualenv labs  # create virtual environment
$ source labs/bin/activate  # activating virtual environment
$ mkdir mcblabs  # create directory for coding
$ cd mcblabs
$ git clone https://github.com/rajan-vivek/drf.git  # cloning the code
$ pip install -r requirements.txt  # installing dependencies
$ python manage.py migrate  #
$ python manage.py createsuperuser
$ python manage.py runserver  # running development server
```

### Deployment Steps

##### Install Heroku-cli
```
$ sudo apt-get install software-properties-common # debian only
$ sudo add-apt-repository "deb https://cli-assets.heroku.com/branches/stable/apt ./"
$ curl -L https://cli-assets.heroku.com/apt/release.key | sudo apt-key add -
$ sudo apt-get update
$ sudo apt-get install heroku
$ heroku login  # enter login & password
$ heroku config:set APP='i2x.buildmyteam'
$ heroku create --buildpack heroku/python
$ git push heroku master
```


### Feature complete
```
1. Login
    url: /login
    type: GET
    params: username, password
    return: auth-token
2. Logout
    url: /logout
    type: POST
    params:
    return:
3. Registration
    url: /register
    type: POST
    params: username, enauk & password
    return: registered user and status for mail success
4. Reset password
    url: /reset
    type: POST
    params: email
    return: 200 OK for success else error message in case of failure
5. Change password
    url: /password
    type: POST
    params: email, password & code
    return: status of operation as true/false
6. Create Team
    url: /team
    type: POST
    params: name, description, owner, members_email
    return: Team object of successfuly created team
7. Update team
    url: /team/1
    type: PUT
    params: same as params of Team create
    return: Team oject of successfuly updated team
```

### Tests
```
python manage.py test
```
