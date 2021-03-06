import pytest

from myst_parser import text_to_tokens
from myst_parser.ast_renderer import AstRenderer
from myst_parser.block_tokens import Document


@pytest.fixture
def ast_renderer():
    renderer = AstRenderer()
    with renderer:
        yield renderer


def test_render_tokens():
    root = text_to_tokens("abc")
    assert isinstance(root, Document)
    assert root.children, root.children


@pytest.mark.parametrize(
    "name,strings",
    [
        ("basic", ["{name}`some content`"]),
        ("indent_2", ["  {name}`some content`"]),
        ("indent_4", ["    {name}`some econtent`"]),
        ("escaped", ["\\{name}`some content`"]),
        ("inline", ["a {name}`some content`"]),
        ("multiple", ["{name}`some content`  {name2}`other`"]),
        ("internal_emphasis", ["{name}`*content*`"]),
        ("external_emphasis", ["*{name}`content`*"]),
        ("internal_math", ["{name}`some $content$`"]),
        ("external_math", ["${name}`some content`$"]),
        ("internal_code", ["{name}` ``some content`` `"]),
        ("external_code", ["`` {name}`some content` ``"]),
    ],
)
def test_role(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


@pytest.mark.parametrize(
    "name,strings",
    [
        ("basic", ["$a$"]),
        ("contains_special_chars", ["$a`{_*-%$"]),
        ("preceding_special_chars", ["{_*-%`$a$"]),
        ("multiple", ["$a$ $b$"]),
        ("escaped_opening", ["\\$a $b$"]),
        ("no_closing", ["$a"]),
        ("internal_emphasis", ["$*a*$"]),
        ("external_emphasis", ["*$a$*"]),
        ("multiline", ["$$a", "c", "b$$"]),
        (
            "issue_51",
            [
                "Math can be called in-line with single `$` characters around math.",
                "For example, `$x_{hey}=it+is^{math}$` renders $x_{hey}=it+is^{math}$.",
            ],
        ),
        ("in_link_content", ["[$a$](link)"]),
        ("in_link_target", ["[a]($b$)"]),
        ("in_image", ["![$a$]($b$)"]),
    ],
)
def test_math(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


@pytest.mark.parametrize(
    "name,strings",
    [
        ("basic", ["(target)="]),
        ("indent_2", ["  (target)="]),
        ("indent_4", ["    (target)="]),
        ("escaped", ["\\(target)="]),
        ("inline", ["a (target)="]),
        ("internal_emphasis", ["(*target*)="]),
        ("external_emphasis", ["*(target)=*"]),
    ],
)
def test_target(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


@pytest.mark.parametrize(
    "name,strings",
    [
        ("basic", [r"% comment"]),
        ("indent_2", [r"  % comment"]),
        ("indent_4", [r"    % comment"]),
        ("escaped", [r"\% comment"]),
        ("inline", [r"a % comment"]),
        ("follows_list", ["- item", r"% comment"]),
    ],
)
def test_comment(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


@pytest.mark.parametrize(
    "name,strings",
    [
        ("basic", ["+++"]),
        ("indent_2", ["  +++"]),
        ("indent_4", ["    +++"]),
        ("escaped", [r"\+++"]),
        ("inline", ["a +++"]),
        ("following_content", ["+++ a"]),
        ("following_space", ["+++   "]),
        ("follows_list", ["- item", "+++"]),
        ("following_content_no_space", ["+++a"]),
    ],
)
def test_block_break(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


@pytest.mark.parametrize("name,strings", [("basic", ["---", "a: b", "---"])])
def test_front_matter(name, ast_renderer, data_regression, strings):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))


@pytest.mark.parametrize(
    "name,strings",
    [
        ("ref_first", ["[ref]", "", '[ref]: https://google.com "title"']),
        ("ref_last", ['[ref]: https://google.com "title"', "", "[ref]"]),
        ("ref_syntax", ["[*syntax*]", "", '[*syntax*]: https://google.com "title"']),
        ("ref_escape", ["[ref]", "", '\\[ref]: https://google.com "title"']),
    ],
)
def test_link_references(name, strings, ast_renderer, data_regression):
    document = Document(strings)
    data_regression.check(ast_renderer.render(document))
