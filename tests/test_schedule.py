import sys, os
testdir = os.path.dirname(__file__)
srcdir = '../app/scheduletogcal'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

from course import Course
c = Course()
c.summary = "xxx xxx"
def test_integer():
    assert c.summary == "xxx xxx"

#@pytest.fixture
#def tree(urls):


