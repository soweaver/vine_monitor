from dataclasses import dataclass

@dataclass(frozen=True)
class VineItem:
    """A class to hold information about a Vine item."""
    asin: str
    title: str
    url: str
    image_url: str
    queue_url: str

    def __eq__(self, other):
        if not isinstance(other, VineItem):
            return NotImplemented
        return self.asin == other.asin

    def __hash__(self):
        return hash(self.asin)
