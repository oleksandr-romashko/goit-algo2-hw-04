"""Trie extension with suffix search and prefix existence check."""

from trie import Trie


class Homework(Trie):
    def count_words_with_suffix(self, pattern: str) -> int:
        """
        Return the number of words in the trie ending with pattern.
        Case-sensitive. Returns 0 if no words match.
        Raises TypeError if pattern is not a string.
        """
        if not isinstance(pattern, str):
            raise TypeError(
                f"Illegal argument for count_words_with_suffix:"
                f" pattern = {pattern} must be a string"
            )
        return sum(1 for word in self.keys() if word.endswith(pattern))

    def has_prefix(self, prefix: str) -> bool:
        """
        Return True if at least one word in the trie starts with prefix.
        Case-sensitive.
        Raises TypeError if prefix is not a string.
        """
        if not isinstance(prefix, str):
            raise TypeError(
                f"Illegal argument for has_prefix:"
                f" prefix = {prefix} must be a string"
            )
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True


if __name__ == "__main__":
    trie = Homework()
    words = ["apple", "application", "banana", "cat"]
    for i, word in enumerate(words):
        trie.put(word, i)

    # count_words_with_suffix
    assert trie.count_words_with_suffix("e") == 1    # apple
    assert trie.count_words_with_suffix("ion") == 1  # application
    assert trie.count_words_with_suffix("a") == 1    # banana
    assert trie.count_words_with_suffix("at") == 1   # cat
    assert trie.count_words_with_suffix("xyz") == 0

    # has_prefix
    assert trie.has_prefix("app") is True   # apple, application
    assert trie.has_prefix("bat") is False
    assert trie.has_prefix("ban") is True   # banana
    assert trie.has_prefix("ca") is True    # cat

    # Invalid input (type error is deliberately ignored)
    try:
        trie.count_words_with_suffix(123)  # type: ignore
        assert False, "Expected TypeError"
    except TypeError:
        pass
    try:
        trie.has_prefix(None)  # type: ignore
        assert False, "Expected TypeError"
    except TypeError:
        pass

    print("All tests passed.")
