class InvalidJournal(Exception):
    def __init__(self, journal_id, *args):
        super().__init__(args)
        self.journal_id = journal_id

    def __str__(self):
        return f"Couldn't verify journal with id {self.journal_id}"
