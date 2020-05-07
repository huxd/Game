#include <Python.h>

static PyObject *
hello(PyObject *self, PyObject *args)
{
    return PyString_FromString("Hello pyd!");
}

static PyMethodDef SpamMethods[] = {
    { "hello", hello, METH_VARARGS, "Print something." },
    { NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initspam(void)
{
    (void)Py_InitModule("spam", SpamMethods);
}