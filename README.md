# Cosmos Search

This is the real-time code search engine for all. We aim to revolutionize the way people interact and search for code. This is evident in our on-going work. Cosmos Search is privacy-focussed as we do not store any data. 

Some of our **core beliefs** that drive the development of this search engine:

* Searching is more of a social act.
* The Divide between programming languages and native languages must be minimized. 
* Time spend on searching must be minimized.
* Time spend on learning, discussing and socializing must be maximized. 

Link: [**search.opengenus.org**](http://search.opengenus.org)

Cosmos Search is one of the most impactful sister projects of [**Cosmos**](https://github.com/OpenGenus/cosmos) powered by [**OpenGenus Foundation**](https://github.com/OpenGenus).

This is the official search tool for cosmos, a library of every algorithm and data structure code that you will ever encounter.

[![Build Status](https://travis-ci.org/OpenGenus/cosmos-search.svg?branch=master)](https://travis-ci.org/OpenGenus/cosmos-search.svg?branch=master)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


## Maintainers

This is a very ambitious project based on a massive collaboration and to keep the quality intact and drive the vision in the proper direction, we have maintainers.

> Maintainers are your friends forever. They are vastly different from moderators.

Currently, we have 3 active maintainers and we are expanding quickly.

The task of maintainers is to review pull requests, suggest further quality additions and keep the work up to date with the current state of the world. 🌍

Let us know if you would like to be a maintainer and we will review and add you upon subsequent contributions. To join our massive community at Slack open an issue [here](https://github.com/OpenGenus/OpenGenus-Slack).

## Contributors

The success of our vision depends on you. Even a small contribution helps. All forms of contributions are highly welcomed and valued.

When you contribute, your name with a link (if available) is added to our [**contributors list**](https://github.com/OpenGenus/cosmos-search/wiki/Contributors).

You can contribute by writing code, documentation, making Cosmos search friendly and many others. There are endless possibilities.

You might, also, like to take a look at our [Ideas List](https://github.com/OpenGenus/cosmos-search/wiki/Idea-List). You can take up a task from the list or suggest your own. Open a pull request to indicate the work you are doing. 

Feel free to discuss anything with us. 💭 

### Technologies Used

This project uses a number of open source projects:

* [Django](https://www.djangoproject.com/) - Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design.
* [Bootstrap](https://getbootstrap.com/) - Responsive frontend framework
* [Heroku](https://www.heroku.com/) - Webapp deployed here
* [Travis](travis-ci.org) - Continuous Integration of the project

## Run this search engine locally

1. Clone this repository using
	```
	$ git clone https://github.com/OpenGenus/cosmos-search.git
 	```

2. Go inside main Django app 

	```
	$ cd cosmos-search
	```

3.  Install local dependencies

       ```
        pip install -r requirements.txt
       ```

4. Collectstatic files using
	```
	$ python manage.py collectstatic
	```

5. Migrating files using
	```
    $ python manage.py migrate
	```

6. Run the app
	```
	$ python manage.py runserver
	```
	
7. View the locally built site
	```
	localhost:8000
	```
To run the web app in Debug mode set the DEBUG environment variable.
In Linux, run the `export DEBUG=True` command in the terminal.


## License

We believe in freedom and improvement. Cosmos Search is built with ♥ by [OpenGenus Community](https://github.com/OpenGenus) under [GPL v3](https://www.gnu.org/licenses/gpl-3.0)
