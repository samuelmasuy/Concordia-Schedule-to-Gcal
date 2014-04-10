# Concordia schedule to Google calendar.

## Description

This is a web application that converts your University(Concordia) schedule to recurring Google calendar events, it uses the micro-framework [Flask][fl].
When you input the url of you schedule, you have the option to chose if you would like to create a secondary calendar.
This app also parses <http://www.concordia.ca/maps/sgw-campus.html> and <http://www.concordia.ca/maps/loyola-campus.html> to get each possible physical location on the two campus of Concordia.

## Installation

I strongly suggest to create a [virtualenv][ve] for this project.
Providing you have pip installed on your machine,
use `pip install -r requirements.txt` to install the required modules.

## Configuration file

Make sure to modify appropriately [config_example.py][conf], with the CLIENT_ID and CLIENT_SECRET of the app you will create in the [the Google API console][gapi]. This application also needs to have the Google calendar scope to be able to operate.


## Running

```bash
    python run.py
```
will start a Flask server locally.

## Contribute

Found a bug? Have a good idea for improving this app?
If you'd like to contribute or extend this project to another area where Google calendar recurring events would be helpful to have:

1. Clone your fork.
1. Create a branch to contain your change.
1. Hack!
1. Make sure everything is running well, run [test.py](/test.py) and closely follow [flake8][f8].
1. Document in a README your new functionalities.
1. Push the branch on GitHub.
1. Send a pull request to this project.

## License

GNU General Public License version 2.0
Please refer to [LICENSE](/LICENSE/).

[gapi]: https://developers.google.com/console/
[ve]: http://www.virtualenv.org/en/latest/virtualenv.html#installation
[fl]: http://flask.pocoo.org/docs/
[conf]: https://github.com/samuelmasuy/Concordia-Schedule-to-Gcal/blob/master/config_example.py
[f8]: https://pypi.python.org/pypi/flake8
