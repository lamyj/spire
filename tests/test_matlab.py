import unittest

import numpy
import spire.spm

class TestMATLAB(unittest.TestCase):
    def test_normalize_list(self):
        array = spire.spm.matlab.normalize([])
        self.assertTrue(isinstance(array, numpy.ndarray))
        self.assertEqual(array.shape, (0,))
        self.assertEqual(array.dtype, object)
        
        array = spire.spm.matlab.normalize([1, 1])
        self.assertTrue(isinstance(array, numpy.ndarray))
        self.assertEqual(array.shape, (2,))
        self.assertEqual(array.dtype, int)
        
        array = spire.spm.matlab.normalize([1., 1.])
        self.assertTrue(isinstance(array, numpy.ndarray))
        self.assertEqual(array.shape, (2,))
        self.assertEqual(array.dtype, float)
        
        array = spire.spm.matlab.normalize(["foo", "bar"])
        self.assertTrue(isinstance(array, numpy.ndarray))
        self.assertEqual(array.shape, (2,))
        self.assertEqual(array.dtype, numpy.dtype("U3"))
        
        array = spire.spm.matlab.normalize(["foo", 1])
        self.assertTrue(isinstance(array, numpy.ndarray))
        self.assertEqual(array.shape, (2,))
        self.assertEqual(array.dtype, object)
    
    def test_normalize_list_of_dicts(self):
        array = spire.spm.matlab.normalize([])
        self.assertTrue(isinstance(array, numpy.ndarray))
        self.assertEqual(array.shape, (0,))
        self.assertEqual(array.dtype, object)
        
        array = spire.spm.matlab.normalize(
            [ {"foo": 1, "bar": "a"}, {"foo": "b", "bar": 2} ])
        self.assertTrue(isinstance(array, numpy.ndarray))
        self.assertEqual(array.shape, (2,))
        self.assertEqual(
            array.dtype, numpy.dtype([("foo", object), ("bar", object)]))
        
        with self.assertRaises(Exception):
            spire.spm.matlab.normalize(
                [ {"foo": 1, "bar": "a"}, {"plip": "b", "plop": 2} ])
    
    def test_normalize_other(self):
        self.assertEqual(1234, spire.spm.matlab.normalize(1234))
        self.assertEqual("abcd", spire.spm.matlab.normalize("abcd"))
    
    def test_convert_scalar(self):
        self.assertEqual(spire.spm.matlab.to_matlab(3.1416), "3.1416")
        self.assertEqual(spire.spm.matlab.to_matlab("abcd"), "'abcd'")
    
    def test_convert_number_array(self):
        self.assertEqual(spire.spm.matlab.to_matlab([123, 456]), "[ 123 456 ]")
        self.assertEqual(
            spire.spm.matlab.to_matlab([[123, 456]]), "[ 123 456 ]")
        self.assertEqual(
            spire.spm.matlab.to_matlab([[123], [456]]), "[ \n123\n456\n ]")
        self.assertEqual(
            spire.spm.matlab.to_matlab([[1, 2], [3, 4]]), "[ \n1 2\n3 4\n ]")
    
    def test_convert_string_array(self):
        self.assertEqual(
            spire.spm.matlab.to_matlab(["abc", "def"]), "{ 'abc' 'def' }")
        self.assertEqual(
            spire.spm.matlab.to_matlab([["abc", "def"]]), "{ 'abc' 'def' }")
        self.assertEqual(
            spire.spm.matlab.to_matlab([["abc", "def"], ["ghi", "jkl"]]), 
            "{ \n'abc' 'def'\n'ghi' 'jkl'\n }")
    
    def test_convert_heterogeneous_array(self):
        self.assertEqual(
            spire.spm.matlab.to_matlab([123, "abc"]), "{ 123 'abc' }")
        self.assertEqual(
            spire.spm.matlab.to_matlab([[123, "abc"]]), "{ 123 'abc' }")
        self.assertEqual(
            spire.spm.matlab.to_matlab([[123], ["abc"]]), "{ \n123\n'abc'\n }")
        self.assertEqual(
            spire.spm.matlab.to_matlab([[1, "abc"], ["def", 4]]), 
            "{ \n1 'abc'\n'def' 4\n }")
    
    def test_convert_array_of_dicts(self):
        # Empty
        self.assertEqual(
            spire.spm.matlab.to_matlab(
                numpy.empty((), [("foo", object), ("bar", object)])),
            "struct('foo', {  }, 'bar', {  })")
            
        # Homogeneous fields
        self.assertEqual(
            spire.spm.matlab.to_matlab(
                [{"foo": 123, "bar": "abc"}, {"foo": 456, "bar": "def"}]),
            "struct('foo', { 123 456 }, 'bar', { 'abc' 'def' })")
        
        # Heterogeneous fields
        self.assertEqual(
            spire.spm.matlab.to_matlab(
                [{"foo": 123, "bar": "abc"}, {"foo": "def", "bar": 456}]),
            "struct('foo', { 123 'def' }, 'bar', { 'abc' 456 })")
        self.assertEqual(
            spire.spm.matlab.to_matlab(
                [[{"foo": 123, "bar": "abc"}, {"foo": "def", "bar": 456}]]),
            "struct('foo', { 123 'def' }, 'bar', { 'abc' 456 })")
        self.assertEqual(
            spire.spm.matlab.to_matlab(
                [[{"foo": 123, "bar": "abc"}], [{"foo": "def", "bar": 456}]]),
            "struct('foo', { \n123\n'def'\n }, 'bar', { \n'abc'\n456\n })")
        self.assertEqual(
            spire.spm.matlab.to_matlab(
                [[{"foo": 123, "bar": "abc"}, {"foo": "abc", "bar": 123}],
                    [{"foo": 456, "bar": "def"}, {"foo": "def", "bar": 456}]]),
            "struct("
                "'foo', { \n123 'abc'\n456 'def'\n }, "
                "'bar', { \n'abc' 123\n'def' 456\n })")
    
if __name__ == "__main__":
    unittest.main()
