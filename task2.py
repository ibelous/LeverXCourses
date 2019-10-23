import functools


@functools.total_ordering
class Version:
    def __init__(self, version: str):
        self.version = version.replace('-', '')

    def __eq__(self, other):
        return self.version == other.version

    def __lt__(self, other):
        ver = self.version.split('.')
        oth = other.version.split('.')
        for v, ot in zip(ver, oth):
            if v.isnumeric() and ot.isnumeric():
                if v != ot:
                    return int(v) < int(ot)
                else:
                    continue
            maxlenght = max(v.__len__(), ot.__len__())
            v = v.ljust(maxlenght, 'z')
            ot = ot.ljust(maxlenght, 'z')
            for a, b in zip(list(v), list(ot)):
                if a == b:
                    continue
                elif b.isnumeric() and not a.isnumeric():
                    return True
                elif a.isnumeric() and not b.isnumeric():
                    return False
                else:
                    return a < b
        return False
    

def main():
    to_test = [
        ('1.0.0', '2.0.0'),
        ('1.0.0', '1.42.0'),
        ('1.2.0', '1.2.42'),
        ('1.1.0-alpha', '1.2.0-alpha.1'),
        ('1.0.1b', '1.0.10-alpha.beta'),
        ('1.0.0-rc.1', '1.0.0'),
        ('1.2.0', '1.12.0'),
    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), 'le failed'
        assert Version(version_2) > Version(version_1), 'ge failed'
        assert Version(version_2) != Version(version_1), 'neq failed'


if __name__ == "__main__":
    main()
