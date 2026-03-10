from .sink import Sink
from ..utils.result import Ok


class InteractiveSink(Sink):
    def write(self, item, sample, i):
        start = (self.args.page - 1) * self.args.per_page
        currentItem = (i + 1) + start

        print(sample)
        print("Current item", currentItem)
        print("Repository:", item["repository"]["name"])
        print("File path:", item["path"])
        print("Link:", item["html_url"])
        input("Press ENTER to continue...")
        return Ok()
