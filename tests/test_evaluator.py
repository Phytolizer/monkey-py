import lexer
import parser
from evaluator import eval_node, TRUE, FALSE
import pytest
import monkey_object


class TestEvaluator:
    def check_integer_object(self, obj, expected):
        assert isinstance(obj, monkey_object.Integer)
        assert obj.value == expected

    def check_boolean_object(self, obj, expected):
        assert obj is expected

    def eval_setup(self, text):
        l = lexer.Lexer(text)
        p = parser.Parser(l)
        program = p.parse_program()
        return eval_node(program)

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
