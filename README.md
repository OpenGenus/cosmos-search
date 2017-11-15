# cosmos-search

[![Build Status](https://travis-ci.org/OpenGenus/cosmos-search.svg?branch=master)](https://travis-ci.org/OpenGenus/cosmos-search.svg?branch=master)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


This is the official search tool for cosmos, a library of every algorithm and data structure code that you will ever encounter.

[Website](http://search.opengenus.org/)


### Technologies Used

This project uses a number of open source projects:

* [Django](https://www.djangoproject.com/) - Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design.
* [Bootstrap](https://getbootstrap.com/) - Responsive frontend framework
* [Heroku](https://www.heroku.com/) - Webapp deployed here
* [Travis](travis-ci.org) - Continuous Integration of the project

## Installations
Run
```
pip install -r requirements.txt
```
to install everything required to run this project on heroku as well as on your local.


## To run this in your local

1. Clone this repository using
	```
	$ git clone https://github.com/OpenGenus/cosmos-search.git
	```

2. Go inside main Django app [Instructional video on installing Django](https://youtu.be/qgGIqRFvFFk)
	```
	$ cd cosmos-search
	```

3. Collectstatic files using
	```
	$ python manage.py collectstatic
	```

3. Migrating files using
	```
    $ python manage.py migrate
	```

4. Run the app
	```
	$ python manage.py runserver
	```
	
4. View the locally built site
	```
	localhost:8000
	```
	
	
To run the web app in Debug mode set the DEBUG environment variable.
In Linux, run the `export DEBUG=True` command in the terminal.

## Contributions, Bug Reports, Feature Requests

This is an Open Source project and we would be happy to see contributors who report bugs and file feature requests by submitting pull requests as well. Please report issues in the [issue tracker](https://github.com/OpenGenus/cosmos-search/issues).

## License

Built with ♥ by [OpenGenus](https://github.com/OpenGenus) under [GPL v3](https://www.gnu.org/licenses/gpl-3.0)

