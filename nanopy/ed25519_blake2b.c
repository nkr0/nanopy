#include <Python.h>
#include "blake2b/blake2.h"
#include "ed25519-donna/ed25519-hash-custom.h"
#include "ed25519-donna/ed25519.h"

void ed25519_randombytes_unsafe(void *out, size_t outlen) {}

blake2b_state b2b;

void ed25519_hash_init(ed25519_hash_context *ctx) {
  ctx->blake2 = &b2b;
  blake2b_init(ctx->blake2, 64);
}

void ed25519_hash_update(ed25519_hash_context *ctx, uint8_t const *in,
                         size_t inlen) {
  blake2b_update(ctx->blake2, in, inlen);
}

void ed25519_hash_final(ed25519_hash_context *ctx, uint8_t *out) {
  blake2b_final(ctx->blake2, out, 64);
}

void ed25519_hash(uint8_t *out, uint8_t const *in, size_t inlen) {
  ed25519_hash_context ctx;
  ed25519_hash_init(&ctx);
  ed25519_hash_update(&ctx, in, inlen);
  ed25519_hash_final(&ctx, out);
}

static PyObject *publickey(PyObject *self, PyObject *args) {
  const unsigned char *sk;
  int i = 0;
  ed25519_public_key pk;

  if (!PyArg_ParseTuple(args, "y#", &sk, &i)) return NULL;
  ed25519_publickey(sk, pk);
  return Py_BuildValue("y#", &pk, 32);
}

static PyObject *signature(PyObject *self, PyObject *args) {
  const unsigned char *m, *sk, *pk;
  int i = 0, j = 0, k = 0;
  ed25519_signature sig;

  if (!PyArg_ParseTuple(args, "y#y#y#", &m, &i, &sk, &j, &pk, &k)) return NULL;
  ed25519_sign(m, i, sk, pk, sig);
  return Py_BuildValue("y#", &sig, 64);
}

static PyObject *checkvalid(PyObject *self, PyObject *args) {
  const unsigned char *sig, *m, *pk;
  int i = 0, j = 0, k = 0;

  if (!PyArg_ParseTuple(args, "y#y#y#", &sig, &i, &m, &j, &pk, &k)) return NULL;
  return Py_BuildValue("i", ed25519_sign_open(m, j, pk, sig));
}

static PyMethodDef m_methods[] = {
    {"publickey", publickey, METH_VARARGS, NULL},
    {"signature", signature, METH_VARARGS, NULL},
    {"checkvalid", checkvalid, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef ed25519_blake2b_module = {
    PyModuleDef_HEAD_INIT, "ed25519_blake2b", NULL, -1, m_methods};

PyMODINIT_FUNC PyInit_ed25519_blake2b(void) {
  PyObject *m = PyModule_Create(&ed25519_blake2b_module);
  if (m == NULL) return NULL;
  return m;
}
