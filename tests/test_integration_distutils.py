import distutils.dist

import mock
import pytest
import setuptools.dist

import readme_renderer.integration.distutils


def test_valid_rst():
    dist = distutils.dist.Distribution(attrs=dict(
        long_description="Hello, I am some text."))
    checker = readme_renderer.integration.distutils.Check(dist)
    checker.warn = mock.Mock()

    checker.check_restructuredtext()

    checker.warn.assert_not_called()


def test_invalid_rst():
    dist = distutils.dist.Distribution(attrs=dict(
        long_description="Hello, I am some `totally borked< text."))
    checker = readme_renderer.integration.distutils.Check(dist)
    checker.warn = mock.Mock()
    checker.announce = mock.Mock()

    checker.check_restructuredtext()

    # Should warn once for the syntax error, and finally to warn that the
    # overall syntax is invalid
    checker.warn.assert_called_once_with(mock.ANY)
    message = checker.warn.call_args[0][0]
    assert 'invalid markup' in message
    assert 'line 1: Warning:' in message
    assert 'start-string without end-string' in message

    # Should not have announced that it was valid.
    checker.announce.assert_not_called()


@pytest.mark.filterwarnings('ignore:::distutils.dist')
def test_markdown():
    dist = setuptools.dist.Distribution(attrs=dict(
        long_description="Hello, I am some text.",
        long_description_content_type="text/markdown"))
    checker = readme_renderer.integration.distutils.Check(dist)
    checker.warn = mock.Mock()

    checker.check_restructuredtext()

    checker.warn.assert_called()
    assert 'content type' in checker.warn.call_args[0][0]


def test_invalid_missing():
    dist = distutils.dist.Distribution(attrs=dict())
    checker = readme_renderer.integration.distutils.Check(dist)
    checker.warn = mock.Mock()

    checker.check_restructuredtext()

    checker.warn.assert_called_once_with(mock.ANY)
    assert 'missing' in checker.warn.call_args[0][0]


def test_invalid_empty():
    dist = distutils.dist.Distribution(attrs=dict(
        long_description=""))
    checker = readme_renderer.integration.distutils.Check(dist)
    checker.warn = mock.Mock()

    checker.check_restructuredtext()

    checker.warn.assert_called_once_with(mock.ANY)
    assert 'missing' in checker.warn.call_args[0][0]


def test_render_readme_default(capfd):
    dist_opts = {'long_description': "This is a simple README."}
    dist = distutils.dist.Distribution(attrs=dist_opts)

    renderer = readme_renderer.integration.distutils.RenderReadme(dist)
    renderer.no_color = True
    renderer.run()

    expected = "<p>This is a simple README.</p>\n"
    assert expected == capfd.readouterr().out


@pytest.mark.filterwarnings('ignore:::distutils.dist')
def test_render_readme_rst(capfd):
    dist_opts = {'long_description': "This is a simple README.",
                 'long_description_content_type': 'text/x-rst'}
    dist = setuptools.dist.Distribution(attrs=dist_opts)

    renderer = readme_renderer.integration.distutils.RenderReadme(dist)
    renderer.warn = mock.Mock()
    renderer.no_color = True
    renderer.run()

    expected = "<p>This is a simple README.</p>\n"
    assert expected == capfd.readouterr().out


@pytest.mark.filterwarnings('ignore:::distutils.dist')
def test_render_readme_md(capfd):
    dist_opts = {'long_description': "This is a simple README.",
                 'long_description_content_type': 'text/markdown'}
    dist = setuptools.dist.Distribution(attrs=dist_opts)

    renderer = readme_renderer.integration.distutils.RenderReadme(dist)
    renderer.warn = mock.Mock()
    renderer.no_color = True
    renderer.run()

    expected = "<p>This is a simple README.</p>\n"
    assert expected == capfd.readouterr().out


@pytest.mark.filterwarnings('ignore:::distutils.dist')
def test_render_readme_txt(capfd):
    dist_opts = {'long_description': "This is a simple README.",
                 'long_description_content_type': 'text/plain'}
    dist = setuptools.dist.Distribution(attrs=dist_opts)

    renderer = readme_renderer.integration.distutils.RenderReadme(dist)
    renderer.warn = mock.Mock()
    renderer.no_color = True
    renderer.run()

    expected = "This is a simple README."
    assert expected == capfd.readouterr().out
