class Commit:
    def __init__(self, author, message, repository, sha, timestamp):
        self.author = author
        self.message = message
        self.repository = repository
        self.sha = sha
        self. timestamp = timestamp

    
    def __str__(self):
        return f'{self.author} committed {self.message} to {self.repository} at {self.timestamp}'