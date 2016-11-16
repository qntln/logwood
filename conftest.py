import logwood.testing
import pytest



@pytest.fixture(autouse = True)
def reset_logwood():
	'''
	Reset logwood state after each test.
	'''
	yield
	logwood.testing.reset_state()
