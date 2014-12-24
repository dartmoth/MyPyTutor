class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        self.defined_get_digits = False
        self.args = None
        self._in_get_digits = False

        self.has_for_loop = False
        self.for_target_id = None
        self.iterates_over_arg = False

        self.uses_isdigit = False
        self.checks_correct_var = False

    @TutorialNodeVisitor.visit_recursively
    def visit_FunctionDef(self, node):
        if TutorialNodeVisitor.identifier(node) == 'get_digits':
            self.defined_get_digits = True
            self._in_get_digits = True
            self.args = list(map(
                TutorialNodeVisitor.identifier, node.args.args
            ))

    @TutorialNodeVisitor.visit_recursively
    def visit_For(self, node):
        if not self._in_get_digits:
            return

        self.has_for_loop = True
        self.for_target_id = TutorialNodeVisitor.identifier(node.target)

        if self.args is not None and len(self.args) == 1:
            iterable_id = TutorialNodeVisitor.identifier(node.iter)
            self.iterates_over_arg = iterable_id == self.args[0]

    @TutorialNodeVisitor.visit_recursively
    def visit_Call(self, node):
        if not self._in_get_digits:
            return

        function_name = TutorialNodeVisitor.identifier(node.func)

        if function_name == 'isdigit':
            self.uses_isdigit = True

            identifiers = TutorialNodeVisitor.involved_identifiers(node)

            if self.for_target_id in identifiers:
                self.checks_correct_var = True


class Analyser(CodeAnalyser):
    def analyse(self, text):
        astree = ast.parse(text)
        self.visitor.visit(astree)

        if not self.visitor.defined_get_digits:
            self.add_error('You need to define the function get_digits')
        elif len(self.visitor.args) != 1:
            self.add_error('get_digits should accept exactly one argument')

        if not self.visitor.has_for_loop:
            self.add_warning('You should use a for loop in get_digits')
        elif not self.visitor.iterates_over_arg \
                and self.visitor.args is not None \
                and len(self.visitor.args) > 0:
            self.add_warning(
                'Your for loop should iterate over {}'.format(
                    self.visitor.args[0]
                )
            )

        if not self.visitor.uses_isdigit:
            self.add_error('You should use str.isdigit')
        elif not self.visitor.checks_correct_var:
            self.add_warning(
                'You should be checking if {} is a digit'.format(
                    self.visitor.for_target_id
                )
            )

ANALYSER = Analyser(CodeVisitor)