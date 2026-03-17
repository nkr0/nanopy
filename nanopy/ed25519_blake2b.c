#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <blake2.h>
#include <ed25519-hash-custom.h>
#include <ed25519.h>

void ed25519_randombytes_unsafe(void *out, size_t outlen) {}

void ed25519_hash_init(ed25519_hash_context *ctx) { blake2b_init(ctx, 64); }

void ed25519_hash_update(ed25519_hash_context *ctx, uint8_t const *in,
                         size_t inlen) {
  blake2b_update(ctx, in, inlen);
}

void ed25519_hash_final(ed25519_hash_context *ctx, uint8_t *out) {
  blake2b_final(ctx, out, 64);
}

void ed25519_hash(uint8_t *out, uint8_t const *in, size_t inlen) {
  ed25519_hash_context ctx;
  ed25519_hash_init(&ctx);
  ed25519_hash_update(&ctx, in, inlen);
  ed25519_hash_final(&ctx, out);
}

static PyObject *publickey(PyObject *self, PyObject *args) {
  const unsigned char *sk;
  Py_ssize_t p0;
  ed25519_public_key pk;

  if (!PyArg_ParseTuple(args, "y#", &sk, &p0))
    return NULL;
  assert(p0 == 32);
  ed25519_publickey(sk, pk);
  return Py_BuildValue("y#", &pk, 32);
}

static PyObject *signature(PyObject *self, PyObject *args) {
  const unsigned char *m, *randr, *sk, *pk;
  Py_ssize_t p0, p1, p2, p3;
  ed25519_signature sig;

  if (!PyArg_ParseTuple(args, "y#y#y#y#", &m, &p0, &randr, &p1, &sk, &p2, &pk,
                        &p3))
    return NULL;
  assert(p1 == 32);
  assert(p2 == 32);
  assert(p3 == 32);
  ed25519_sign(m, p0, randr, sk, pk, sig);
  return Py_BuildValue("y#", &sig, 64);
}

static PyObject *checkvalid(PyObject *self, PyObject *args) {
  const unsigned char *sig, *m, *pk;
  Py_ssize_t p0, p1, p2;

  if (!PyArg_ParseTuple(args, "y#y#y#", &sig, &p0, &m, &p1, &pk, &p2))
    return NULL;
  assert(p0 == 64);
  assert(p2 == 32);
  return Py_BuildValue("i", ed25519_sign_open(m, p1, pk, sig) == 0);
}

static PyMethodDef m_methods[] = {
    {"publickey", publickey, METH_VARARGS, NULL},
    {"signature", signature, METH_VARARGS, NULL},
    {"checkvalid", checkvalid, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef ed25519_blake2b_module = {PyModuleDef_HEAD_INIT,
                                                    "ed25519_blake2b",
                                                    NULL,
                                                    -1,
                                                    m_methods,
                                                    NULL,
                                                    NULL,
                                                    NULL,
                                                    NULL};

PyMODINIT_FUNC PyInit_ed25519_blake2b(void) {
  return PyModule_Create(&ed25519_blake2b_module);
}
