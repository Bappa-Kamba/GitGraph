class Pull_Request:
    def __init__(self, author, description, repository, state, timestamp, title):
        self.author = author
        self.description = description
        self.repository = repository
        self.state = state
        self.timestamp = timestamp
        self.title = title

    def __str__(self):
        return f'{self.author} opened pull request "{self.title}" on {self.repository} at {self.timestamp}'