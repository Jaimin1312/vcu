""" Tests various methods relating to parsing responses from the VCU.
"""
#pylint: disable=protected-access


from vcs.model import vcu


class DummyConnection():                                #pylint: disable=too-few-public-methods
    """ Stand-in to simulate the connection class during testing.

    Takes in a series of responses that will be retrieved for everytime
    the run() method is called.
    """
    def __init__(self, responses: list[str]):
        self._responses: list = responses

    def run(self, cmd):
        """ Pops the first response out of the queue and returns as a DummyResponse.
        """
        return DummyResponse(cmd, self._responses.pop(0))


class DummyResponse():                                  #pylint: disable=too-few-public-methods
    """ Stand-in to simulate the response class returned by Connection.run() during testing.
    """
    def __init__(self, cmd, response):
        self.cmd = cmd
        self.stdout = response


def test_get_hashes():
    """ Test that vcu._get_hashes() results in dictionary with expected content.
    """
    connection = DummyConnection(responses=[
        '1234567812345678123456781234567812345678 /usr/bin/symbot_server-0.4',
        '8765432187654321876543218765432187654321 /usr/bin/symbot_client-0.4',
    ])
    hashes = vcu._get_hashes(connection, [
        '/usr/bin/symbot_server-0.4',
        '/usr/bin/symbot_client-0.4']
    )

    assert hashes == {
        '/usr/bin/symbot_client-0.4': '8765432187654321876543218765432187654321',
        '/usr/bin/symbot_server-0.4': '1234567812345678123456781234567812345678',
        }, hashes


def test_get_temperatures():
    """ Test that vcu._get_temperatures() results in dictionary with expected content.
    """
    connection = DummyConnection(responses=[
        'tempA\ntempB\ntempC\n',
        '35000\n31234\n50921\n',
    ])
    temperatures = vcu._get_temperatures(connection)

    assert temperatures == {
       'tempA':35.0,
       'tempB':31.234,
       'tempC':50.921,
        }, temperatures


def test_poll_i2c_device():
    """ Test that vcu.poll_i2c_device results in array indicating connected positions.
    """
    connection = DummyConnection(responses=[
'''
30: UU -- UU UU UU
40: UU UU -- UU UU
50: UU UU UU -- UU
''',
    ])
    devices = vcu.poll_i2c_device(connection, 9)
    assert devices == [True, True, False, True], devices
