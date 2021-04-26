from environment import Environment
import lexer
import parser
from evaluator import NULL, eval_node, TRUE, FALSE
import pytest
import monkey_object


class TestEvaluator:
    def check_integer_object(self, obj, expected):
        assert isinstance(obj, monkey_object.Integer)
        assert obj.value == expected

    def check_boolean_object(self, obj, expected):
        assert obj is expected

    def check_null_object(self, obj):
        assert obj is NULL

    def eval_setup(self, text):
        l = lexer.Lexer(text)
        p = parser.Parser(l)
        program = p.parse_program()
        return eval_node(program, Environment())

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("5", 5),
            ("10", 10),
            ("-5", -5),
            ("-10", -10),
            ("5 + 5 + 5 + 5 - 10", 10),
            ("2 * 2 * 2 * 2 * 2", 32),
            ("-50 + 100 + -50", 0),
            ("5 * 2 + 10", 20),
            ("5 + 2 * 10", 25),
            ("20 + 2 * -10", 0),
            ("50 / 2 * 2 + 10", 60),
            ("2 * (5 + 10)", 30),
            ("3 * 3 * 3 + 10", 37),
            ("3 * (3 * 3) + 10", 37),
            ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
        ],
    )
    def test_eval_integer_expression(self, text, expected):
        evaluated = self.eval_setup(text)
        self.check_integer_object(evaluated, expected)

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("true", TRUE),
            ("false", FALSE),
            ("1 < 2", TRUE),
            ("1 > 2", FALSE),
            ("1 < 1", FALSE),
            ("1 > 1", FALSE),
            ("1 == 1", TRUE),
            ("1 != 1", FALSE),
            ("1 == 2", FALSE),
            ("1 != 2", TRUE),
            ("true == true", TRUE),
            ("false == false", TRUE),
            ("true == false", FALSE),
            ("true != false", TRUE),
            ("false != false", FALSE),
            ("false != true", TRUE),
            ("(1 < 2) == true", TRUE),
            ("(1 < 2) == false", FALSE),
            ("(1 > 2) == true", FALSE),
            ("(1 > 2) == false", TRUE),
        ],
    )
    def test_eval_boolean_expression(self, text, expected):
        evaluated = self.eval_setup(text)
        self.check_boolean_object(evaluated, expected)

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("!true", FALSE),
            ("!false", TRUE),
            ("!5", FALSE),
            ("!!true", TRUE),
            ("!!false", FALSE),
            ("!!5", TRUE),
        ],
    )
    def test_eval_bang_operator(self, text, expected):
        evaluated = self.eval_setup(text)
        self.check_boolean_object(evaluated, expected)

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("if (5 < 10) { 5 } else { 10 }", 5),
            ("if (5 > 10) { 5 } else { 10 }", 10),
            ("if (5 > 10) { 5 }", None),
        ],
    )
    def test_eval_if_expression(self, text, expected):
        evaluated = self.eval_setup(text)
        if isinstance(expected, int):
            self.check_integer_object(evaluated, expected)
        elif expected is None:
            self.check_null_object(evaluated)
        else:
            raise NotImplementedError("woops")

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("return;", None),
            ("return true;", TRUE),
            ("return 10;", 10),
            ("9; return 10;", 10),
            ("return 10; 9;", 10),
            ("9; return 10; 9;", 10),
            ("if (5 < 10) { if (6 > 4) { return 10; } return 1; }", 10),
        ],
    )
    def test_eval_return_statements(self, text, expected):
        evaluated = self.eval_setup(text)
        if isinstance(expected, int):
            self.check_integer_object(evaluated, expected)
        elif isinstance(expected, monkey_object.Boolean):
            self.check_boolean_object(evaluated, expected)
        else:
            self.check_null_object(evaluated)

    @pytest.mark.parametrize(
        "text,expected",
        [
            (
                "5 + true;",
                "type mismatch: INTEGER + BOOLEAN",
            ),
            (
                "5 + true; 5;",
                "type mismatch: INTEGER + BOOLEAN",
            ),
            (
                "-true",
                "unknown operator: -BOOLEAN",
            ),
            (
                "true + false;",
                "unknown operator: BOOLEAN + BOOLEAN",
            ),
            (
                "5; true + false; 5",
                "unknown operator: BOOLEAN + BOOLEAN",
            ),
            (
                "if (10 > 1) { true + false; }",
                "unknown operator: BOOLEAN + BOOLEAN",
            ),
            (
                "foobar",
                "identifier not found: foobar",
            ),
        ],
    )
    def test_error_handling(self, text, expected):
        evaluated = self.eval_setup(text)
        assert isinstance(evaluated, monkey_object.Error)
        assert evaluated.message == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("let a = 5; a;", 5),
            ("let a = 5 * 5; a;", 25),
            ("let a = 5; let b = a; b;", 5),
            ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
        ],
    )
    def test_let_statements(self, text, expected):
        self.check_integer_object(self.eval_setup(text), expected)

    def test_function_object(self):
        text = "fn(x) { x + 2; };"
        evaluated = self.eval_setup(text)
        assert isinstance(evaluated, monkey_object.Function)
        assert len(evaluated.parameters) == 1
        assert evaluated.parameters[0].string() == "x"
        assert evaluated.body.string() == "(x + 2)"

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("let identity = fn(x) { x; }; identity(5);", 5),
            ("let identity = fn(x) { return x; }; identity(5);", 5),
            ("let double = fn(x) { x * 2; }; double(5);", 10),
            ("let add = fn(x, y) { x + y; }; add(5, 5);", 10),
            ("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20),
            ("fn(x) { x; }(5)", 5),
        ],
    )
    def test_function_application(self, text, expected):
        self.check_integer_object(self.eval_setup(text), expected)

    def test_closures(self):
        text = """
            let newAdder = fn(x) {
                fn(y) { x + y; };
            };

            let addTwo = newAdder(2);
            addTwo(2);
        """
        self.check_integer_object(self.eval_setup(text), 4)
