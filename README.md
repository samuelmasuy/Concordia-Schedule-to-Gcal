# Concordia schedule to Google cal.

## Description

This is a web application that converts your University (Concordia) schedule to recurring Google calendar events, it uses the micro-framework [Flask][fl].
The app parses the academic schedule provided on the website of MyConcordia with the help of lxml using XPath.
It also parses <http://www.concordia.ca/maps/sgw-campus.html> and <http://www.concordia.ca/maps/loyola-campus.html> to get each possible physical location on the two campuses of Concordia.

## Installation

I strongly suggest you to create a [virtualenv][ve] for this project.
Then, providing you have pip installed on your machine,
use `pip install -r requirements.txt` to install the required modules.

## Configuration file

Make sure to modify appropriately [config_example.py](/config_example.py), with the CLIENT_ID and CLIENT_SECRET of the app you will create in the [the Google API console][gapi]. Then change the file name to *config.py*.


## Running

```bash
    python run.py
```
will start a Flask server locally. You can now go to http://localhost:5000/ to see the website.

## Contribute

Found a bug? Have a good idea for improving this app?
If you'd like to contribute or extend this project:

1. Clone your fork.
1. Create a branch to contain your change.
1. Hack!
1. Make sure everything is running well <del>run [test.py](/test.py)</del> and closely follow [flake8][f8].
1. Document in a README your new functionalities.
1. Push the branch on GitHub.
1. Send a pull request to this project.

## License

GNU General Public License version 2.0
Please refer to [LICENSE](/LICENSE/).

[gapi]: https://developers.google.com/console/
[ve]: http://www.virtualenv.org/en/latest/virtualenv.html#installation
[fl]: http://flask.pocoo.org/docs/
[f8]: https://pypi.python.org/pypi/flake8
