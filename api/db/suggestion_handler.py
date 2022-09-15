class FieldForSuggestionSearch:
    def __init__(self, name: str, is_digit: bool):
        self.name = name
        self.is_digit = is_digit

    def build(self, substring: str) -> str:
        ls = []
        if substring.isdigit() and self.is_digit:
            ls.append(f"{self.name} = {substring}")
        ls.append(f"{self.name} LIKE {substring}")
        return " OR ".join(ls)

    def get_name(self):
        return self.name


class FieldForSuggestionSearchList:
    def __init__(self, *fields):
        self.fields = fields

    def build(self, substring: str) -> str:
        ls = []
        for f in self.fields:
            ls.append(f.build(substring))
        return " OR ".join(ls)

    def get_names(self):
        return [f.get_name() for f in self.fields]


suggestion_request_builder = FieldForSuggestionSearchList(
    FieldForSuggestionSearch('id', True),
    FieldForSuggestionSearch('ensembl', False),
    FieldForSuggestionSearch('symbol', False),
    FieldForSuggestionSearch('name', False),
    FieldForSuggestionSearch('aliases', False),
)
