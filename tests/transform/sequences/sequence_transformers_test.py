import numpy as np
import pytest
from keras.utils import Sequence

from transform.sequences import RandomRotationTransformer, RandomShiftTransformer


class TestSequence(Sequence):
    """Create a X,Y tuple"""

    def __getitem__(self, index):
        return np.arange(5 * 20 * 20 * 3).reshape([5, 20, 20, 3]), np.arange(5 * 20 * 20 * 3).reshape([5, 20, 20, 3])

    def __len__(self):
        return 10


class TestTreeSequence(Sequence):
    """Create a [X1,X2],Y1 tuple."""

    def __getitem__(self, index):
        return [np.arange(5 * 20 * 20 * 3).reshape([5, 20, 20, 3]),
                np.arange(5 * 12 * 12 * 3).reshape([5, 12, 12, 3])], np.arange(
            5 * 10 * 10 * 3).reshape([5, 10, 10, 3])

    def __len__(self):
        return 10


def test_random_rot():
    inner_transformer(RandomRotationTransformer, rg=25)


def test_random_shift():
    inner_transformer(RandomShiftTransformer, wrg=0.5, hrg=0.5)


def inner_transformer(transformer_cls, **kwargs):
    np.random.seed(1337)
    transformer = transformer_cls(TestSequence(), **kwargs)
    assert np.any(np.not_equal(transformer[0][0], transformer[1][0])) and np.all(
        np.equal(transformer[0][1], transformer[1][1]))

    transformer = transformer_cls(TestTreeSequence(), **kwargs)

    assert all([np.any(np.not_equal(t0, t1)) for t0, t1 in zip(transformer[0][0], transformer[1][0])]) and all(
        [np.all(np.equal(t0, t1)) for t0, t1 in zip(transformer[0][1], transformer[1][1])])

    # Test Mask
    transformer = transformer_cls(TestTreeSequence(), mask=False, **kwargs)

    assert all([np.any(np.equal(t0, t1)) for t0, t1 in zip(transformer[0][0], transformer[1][0])]) and np.equal(
        transformer[0][1], transformer[1][1]).all()

    transformer = transformer_cls(TestTreeSequence(), mask=[True, True], **kwargs)

    assert all([np.any(np.not_equal(t0, t1)) for t0, t1 in zip(transformer[0][0], transformer[1][0])]) and np.not_equal(
        transformer[0][1], transformer[1][1]).any()

    # Should rotate the same way for X and y
    transformer = transformer_cls(TestSequence(), mask=[True, True], **kwargs)
    assert (np.equal(*transformer[0])).all()

    # Common case where we augment X but not y
    transformer = transformer_cls(TestSequence(), mask=[True, False], **kwargs)
    assert (np.not_equal(*transformer[0])).any()


if __name__ == '__main__':
    pytest.main([__file__])
