class FilterModule(object):

    def filters(self):
        return {
            'ensure_dict': self.ensure_dict,
        }

    @staticmethod
    def ensure_dict(data: (str, dict), key: str) -> dict:
        if type(data) != dict:
            return {key: data}

        return data
